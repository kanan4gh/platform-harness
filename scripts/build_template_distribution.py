"""Build a clean template distribution from a tagged canonical Git tree."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT_ROOT / "distribution" / "template-manifest.json"
METADATA_PATH = ".platform-harness-source.json"
TAG_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class DistributionError(ValueError):
    """Raised when the source or distribution contract is invalid."""


@dataclass(frozen=True)
class Transformation:
    path: str
    kind: str
    old: str | None = None
    new: str | None = None
    marker: str | None = None


@dataclass(frozen=True)
class Manifest:
    schema_version: int
    source_repository: str
    include_paths: tuple[str, ...]
    required_paths: tuple[str, ...]
    forbidden_paths: tuple[str, ...]
    forbidden_prefixes: tuple[str, ...]
    transformations: tuple[Transformation, ...]


@dataclass(frozen=True)
class TreeEntry:
    mode: str
    object_type: str
    object_id: str
    path: str


def _require_object(value: object, *, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise DistributionError(f"{label} must be a JSON object")
    return value


def _require_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise DistributionError(f"{label} must be a non-empty string")
    return value


def _require_string_list(value: object, *, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise DistributionError(f"{label} must be an array of strings")
    items = tuple(value)
    if len(items) != len(set(items)):
        raise DistributionError(f"{label} contains duplicate values")
    if items != tuple(sorted(items)):
        raise DistributionError(f"{label} must be sorted")
    return items


def _validate_relative_path(value: str, *, label: str) -> str:
    if not value or "\\" in value:
        raise DistributionError(f"{label} is not a POSIX relative path: {value!r}")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or path.as_posix() != value
        or any(part in {".", ".."} for part in path.parts)
    ):
        raise DistributionError(f"{label} is not a normalized relative path: {value!r}")
    return value


def _validate_prefix(value: str, *, label: str) -> str:
    core = value[:-1] if value.endswith("/") else value
    _validate_relative_path(core, label=label)
    return value


def _load_transformation(value: object, *, index: int) -> Transformation:
    data = _require_object(value, label=f"transformations[{index}]")
    kind = _require_string(data.get("kind"), label=f"transformations[{index}].kind")
    path = _validate_relative_path(
        _require_string(data.get("path"), label=f"transformations[{index}].path"),
        label=f"transformations[{index}].path",
    )
    if kind == "replace_exact_once":
        expected = {"path", "kind", "old", "new"}
        if set(data) != expected:
            raise DistributionError(
                f"transformations[{index}] keys must be {sorted(expected)}"
            )
        old = _require_string(data.get("old"), label=f"transformations[{index}].old")
        new = data.get("new")
        if not isinstance(new, str):
            raise DistributionError(f"transformations[{index}].new must be a string")
        return Transformation(path=path, kind=kind, old=old, new=new)
    if kind == "truncate_at_marker":
        expected = {"path", "kind", "marker"}
        if set(data) != expected:
            raise DistributionError(
                f"transformations[{index}] keys must be {sorted(expected)}"
            )
        marker = _require_string(
            data.get("marker"), label=f"transformations[{index}].marker"
        )
        return Transformation(path=path, kind=kind, marker=marker)
    raise DistributionError(f"transformations[{index}] has unsupported kind: {kind}")


def load_manifest(path: Path) -> Manifest:
    """Read and validate the distribution manifest."""
    try:
        parsed: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DistributionError(f"could not read manifest {path}: {exc}") from exc
    data = _require_object(parsed, label="manifest")
    expected_keys = {
        "schema_version",
        "source_repository",
        "include_paths",
        "required_paths",
        "forbidden_paths",
        "forbidden_prefixes",
        "transformations",
    }
    if set(data) != expected_keys:
        raise DistributionError(f"manifest keys must be {sorted(expected_keys)}")
    if data.get("schema_version") != 1:
        raise DistributionError("manifest schema_version must be 1")
    source_repository = _require_string(
        data.get("source_repository"), label="source_repository"
    )
    include_paths = _require_string_list(data.get("include_paths"), label="include_paths")
    required_paths = _require_string_list(
        data.get("required_paths"), label="required_paths"
    )
    forbidden_paths = _require_string_list(
        data.get("forbidden_paths"), label="forbidden_paths"
    )
    forbidden_prefixes = _require_string_list(
        data.get("forbidden_prefixes"), label="forbidden_prefixes"
    )
    for label, values in (
        ("include_paths", include_paths),
        ("required_paths", required_paths),
        ("forbidden_paths", forbidden_paths),
    ):
        for item in values:
            _validate_relative_path(item, label=label)
    for prefix in forbidden_prefixes:
        _validate_prefix(prefix, label="forbidden_prefixes")
    missing_required = sorted(set(required_paths) - set(include_paths))
    if missing_required:
        raise DistributionError(
            f"required_paths are not included: {', '.join(missing_required)}"
        )
    forbidden_included = sorted(set(forbidden_paths) & set(include_paths))
    if forbidden_included:
        raise DistributionError(
            f"forbidden_paths are included: {', '.join(forbidden_included)}"
        )
    reserved_declarations = sorted(
        set(include_paths) | set(required_paths) | set(forbidden_paths)
    )
    if METADATA_PATH in reserved_declarations:
        raise DistributionError(
            f"{METADATA_PATH} is reserved for generated provenance metadata"
        )
    transformations_raw = data.get("transformations")
    if not isinstance(transformations_raw, list):
        raise DistributionError("transformations must be an array")
    transformations = tuple(
        _load_transformation(value, index=index)
        for index, value in enumerate(transformations_raw)
    )
    transformed_paths = [item.path for item in transformations]
    missing_transforms = sorted(set(transformed_paths) - set(include_paths))
    if missing_transforms:
        raise DistributionError(
            f"transformation paths are not included: {', '.join(missing_transforms)}"
        )
    return Manifest(
        schema_version=1,
        source_repository=source_repository,
        include_paths=include_paths,
        required_paths=required_paths,
        forbidden_paths=forbidden_paths,
        forbidden_prefixes=forbidden_prefixes,
        transformations=transformations,
    )


def _run_git(repository: Path, args: Sequence[str]) -> bytes:
    command = ("git", "-C", str(repository), *args)
    try:
        result = subprocess.run(
            command,
            check=False,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        raise DistributionError(f"git could not start: {exc}") from exc
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise DistributionError(
            f"git command failed ({' '.join(args)}): {message or 'no diagnostic'}"
        )
    return result.stdout


def resolve_tag(repository: Path, tag: str) -> str:
    """Resolve an exact local tag to a commit SHA."""
    if not TAG_PATTERN.fullmatch(tag):
        raise DistributionError(f"source tag has invalid syntax: {tag!r}")
    ref = f"refs/tags/{tag}"
    _run_git(repository, ("show-ref", "--verify", ref))
    commit = _run_git(repository, ("rev-parse", "--verify", f"{ref}^{{commit}}"))
    value = commit.decode("ascii", errors="strict").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise DistributionError(f"source tag did not resolve to a full commit SHA: {tag}")
    return value


def read_tree(repository: Path, commit: str) -> dict[str, TreeEntry]:
    """Read a commit tree without consulting the working tree."""
    raw = _run_git(repository, ("ls-tree", "-rz", "--full-tree", commit))
    entries: dict[str, TreeEntry] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            header, raw_path = record.split(b"\t", maxsplit=1)
            mode, object_type, object_id = header.decode("ascii").split()
            path = raw_path.decode("utf-8", errors="strict")
        except (ValueError, UnicodeError) as exc:
            raise DistributionError("git tree contains an undecodable entry") from exc
        _validate_relative_path(path, label="git tree path")
        if path in entries:
            raise DistributionError(f"git tree contains a duplicate path: {path}")
        entries[path] = TreeEntry(mode, object_type, object_id, path)
    return entries


def _apply_transformation(content: bytes, transformation: Transformation) -> bytes:
    try:
        text = content.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise DistributionError(
            f"transformation target is not UTF-8: {transformation.path}"
        ) from exc
    if transformation.kind == "replace_exact_once":
        assert transformation.old is not None and transformation.new is not None
        count = text.count(transformation.old)
        if count != 1:
            raise DistributionError(
                f"transformation expected one match in {transformation.path}, found {count}"
            )
        return text.replace(transformation.old, transformation.new, 1).encode("utf-8")
    if transformation.kind == "truncate_at_marker":
        assert transformation.marker is not None
        count = text.count(transformation.marker)
        if count != 1:
            raise DistributionError(
                f"transformation expected one marker in {transformation.path}, found {count}"
            )
        return (text.split(transformation.marker, maxsplit=1)[0].rstrip() + "\n").encode(
            "utf-8"
        )
    raise DistributionError(f"unsupported transformation kind: {transformation.kind}")


def _is_forbidden(path: str, manifest: Manifest) -> bool:
    return path in manifest.forbidden_paths or any(
        path.startswith(prefix) for prefix in manifest.forbidden_prefixes
    )


def _write_metadata(
    root: Path,
    *,
    manifest: Manifest,
    source_tag: str,
    source_commit: str,
    publisher_repository: str,
    publisher_revision: str,
) -> None:
    metadata = {
        "manifest_version": manifest.schema_version,
        "publisher_repository": publisher_repository,
        "publisher_revision": publisher_revision,
        "source_commit": source_commit,
        "source_repository": manifest.source_repository,
        "source_tag": source_tag,
    }
    (root / METADATA_PATH).write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _validate_publisher_identity(repository: str, revision: str) -> None:
    if re.fullmatch(r"[^/\s]+/[^/\s]+", repository) is None:
        raise DistributionError(
            f"publisher repository must use OWNER/REPOSITORY syntax: {repository!r}"
        )
    if re.fullmatch(r"[0-9a-f]{40}", revision) is None:
        raise DistributionError(
            f"publisher revision must be a full commit SHA: {revision!r}"
        )


def _validate_output(root: Path, manifest: Manifest) -> None:
    files: set[str] = set()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise DistributionError(
                f"distribution output contains a symlink: {path.relative_to(root)}"
            )
        if path.is_file():
            files.add(path.relative_to(root).as_posix())
    expected = set(manifest.include_paths) | {METADATA_PATH}
    missing = sorted(expected - files)
    unexpected = sorted(files - expected)
    if missing or unexpected:
        details: list[str] = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected: {', '.join(unexpected)}")
        raise DistributionError("output file set mismatch (" + "; ".join(details) + ")")
    missing_required = sorted(set(manifest.required_paths) - files)
    if missing_required:
        raise DistributionError(
            f"output is missing required paths: {', '.join(missing_required)}"
        )
    forbidden = sorted(path for path in files if _is_forbidden(path, manifest))
    if forbidden:
        raise DistributionError(f"output contains forbidden paths: {', '.join(forbidden)}")
    steering_paths = sorted(path for path in files if path.startswith(".steering/"))
    invalid_steering = [
        path for path in steering_paths if not path.startswith(".steering/example/")
    ]
    if invalid_steering:
        raise DistributionError(
            f"output contains non-example steering: {', '.join(invalid_steering)}"
        )


def build_distribution(
    *,
    source_repository: Path,
    source_tag: str,
    manifest_path: Path,
    output: Path,
    publisher_repository: str,
    publisher_revision: str,
) -> str:
    """Build and atomically install a template distribution."""
    manifest = load_manifest(manifest_path)
    if not source_repository.is_dir():
        raise DistributionError(
            f"source repository is not a directory: {source_repository}"
        )
    source_identity = detect_github_repository(source_repository)
    if source_identity != manifest.source_repository:
        raise DistributionError(
            "source repository origin does not match manifest "
            f"({source_identity} != {manifest.source_repository})"
        )
    if output.exists():
        if not output.is_dir():
            raise DistributionError(f"output exists and is not a directory: {output}")
        if any(output.iterdir()):
            raise DistributionError(f"output directory is not empty: {output}")
    if not output.parent.is_dir():
        raise DistributionError(f"output parent is not a directory: {output.parent}")
    _validate_publisher_identity(publisher_repository, publisher_revision)
    source_commit = resolve_tag(source_repository, source_tag)
    tree = read_tree(source_repository, source_commit)
    transformations: dict[str, list[Transformation]] = {}
    for item in manifest.transformations:
        transformations.setdefault(item.path, []).append(item)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{output.name}.staging-", dir=output.parent)
    )
    try:
        for path in manifest.include_paths:
            entry = tree.get(path)
            if entry is None:
                raise DistributionError(f"included path is absent from source: {path}")
            if entry.object_type != "blob" or entry.mode not in {"100644", "100755"}:
                raise DistributionError(
                    f"included path is not a regular file: {path} "
                    f"(mode={entry.mode}, type={entry.object_type})"
                )
            content = _run_git(source_repository, ("cat-file", "blob", entry.object_id))
            for transformation in transformations.get(path, []):
                content = _apply_transformation(content, transformation)
            destination = staging / PurePosixPath(path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            os.chmod(destination, 0o755 if entry.mode == "100755" else 0o644)
        _write_metadata(
            staging,
            manifest=manifest,
            source_tag=source_tag,
            source_commit=source_commit,
            publisher_repository=publisher_repository,
            publisher_revision=publisher_revision,
        )
        _validate_output(staging, manifest)
        if output.exists():
            output.rmdir()
        staging.replace(output)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return source_commit


def detect_github_repository(repository: Path) -> str:
    """Return OWNER/REPOSITORY from a Git checkout's GitHub origin URL."""
    url = _run_git(repository, ("remote", "get-url", "origin")).decode(
        "utf-8", errors="strict"
    ).strip()
    match = re.fullmatch(
        r"(?:https://github\.com/|git@github\.com:)([^/]+)/([^/]+?)(?:\.git)?", url
    )
    if match is None:
        raise DistributionError(f"origin is not a GitHub repository: {url}")
    return f"{match.group(1)}/{match.group(2)}"


def detect_publisher_repository(repository: Path) -> str:
    """Return OWNER/REPOSITORY from the publisher's origin URL."""
    return detect_github_repository(repository)


def detect_publisher_revision(repository: Path) -> str:
    """Resolve a clean publisher HEAD to a full commit SHA."""
    status = _run_git(repository, ("status", "--porcelain", "--untracked-files=all"))
    if status:
        raise DistributionError(
            "publisher working tree is dirty; commit the manifest and builder first"
        )
    revision = _run_git(repository, ("rev-parse", "--verify", "HEAD^{commit}")).decode(
        "ascii", errors="strict"
    ).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise DistributionError("publisher HEAD did not resolve to a full commit SHA")
    return revision


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repository", required=True, type=Path)
    parser.add_argument("--source-tag", required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        publisher_repository = detect_publisher_repository(PROJECT_ROOT)
        publisher_revision = detect_publisher_revision(PROJECT_ROOT)
        commit = build_distribution(
            source_repository=args.source_repository.resolve(),
            source_tag=args.source_tag,
            manifest_path=args.manifest.resolve(),
            output=args.output.resolve(),
            publisher_repository=publisher_repository,
            publisher_revision=publisher_revision,
        )
    except (DistributionError, OSError, UnicodeError) as exc:
        print(f"template distribution: {exc}", file=sys.stderr)
        return 1
    print(
        f"template distribution: built {args.output.resolve()} "
        f"from {args.source_tag} ({commit})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
