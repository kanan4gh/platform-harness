"""Contract tests for the clean template distribution builder."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from types import ModuleType
import pytest


ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "scripts" / "build_template_distribution.py"
MANIFEST = ROOT / "distribution" / "template-manifest.json"
STEERING_IGNORE_BLOCK = (
    "\n# ステアリング作業ディレクトリはテンプレート複製対象外\n"
    ".steering/*\n"
    "!.steering/example/\n"
)


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_template_distribution", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_module()


def git(repository: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(repository), *args),
        check=True,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def write_manifest(path: Path, **overrides: object) -> Path:
    data: dict[str, object] = {
        "schema_version": 1,
        "source_repository": "example/canonical",
        "include_paths": [
            ".gitignore",
            ".steering/example/tasklist.md",
            "procedure.md",
            "script.sh",
        ],
        "required_paths": [
            ".gitignore",
            ".steering/example/tasklist.md",
            "procedure.md",
            "script.sh",
        ],
        "forbidden_paths": ["docs/derived-projects.md"],
        "forbidden_prefixes": [".steering/20", "docs/ideas/"],
        "transformations": [
            {
                "path": ".gitignore",
                "kind": "replace_exact_once",
                "old": STEERING_IGNORE_BLOCK,
                "new": "\n",
            },
            {
                "path": "procedure.md",
                "kind": "truncate_at_marker",
                "marker": "\n## Internal appendix\n",
            },
        ],
    }
    data.update(overrides)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return path


def source_repository(tmp_path: Path) -> tuple[Path, str]:
    repository = tmp_path / "source"
    repository.mkdir()
    git(repository, "init", "-b", "main")
    git(repository, "config", "user.name", "Distribution Test")
    git(repository, "config", "user.email", "distribution@example.com")
    git(repository, "remote", "add", "origin", "https://github.com/example/canonical.git")
    (repository / ".gitignore").write_text(
        "__pycache__/\n" + STEERING_IGNORE_BLOCK,
        encoding="utf-8",
    )
    steering = repository / ".steering" / "example"
    steering.mkdir(parents=True)
    (steering / "tasklist.md").write_text("# Example\n", encoding="utf-8")
    (repository / "procedure.md").write_text(
        "# Public procedure\n\nKept.\n\n## Internal appendix\n\nRemoved.\n",
        encoding="utf-8",
    )
    script = repository / "script.sh"
    script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    os.chmod(script, 0o755)
    git(repository, "add", "-A")
    git(repository, "commit", "-m", "fixture")
    git(repository, "tag", "v1.0.0")
    return repository, git(repository, "rev-parse", "v1.0.0^{commit}")


def build(
    *,
    source: Path,
    manifest: Path,
    output: Path,
    tag: str = "v1.0.0",
) -> str:
    return builder.build_distribution(
        source_repository=source,
        source_tag=tag,
        manifest_path=manifest,
        output=output,
        publisher_repository="example/publisher",
        publisher_revision="a" * 40,
    )


def file_snapshot(root: Path) -> dict[str, tuple[bytes, int]]:
    snapshot: dict[str, tuple[bytes, int]] = {}
    for path in root.rglob("*"):
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            mode = stat.S_IMODE(path.stat().st_mode)
            snapshot[relative] = (path.read_bytes(), mode)
    return snapshot


def test_real_manifest_is_exact_and_keeps_only_example_steering() -> None:
    manifest = builder.load_manifest(MANIFEST)
    steering = [path for path in manifest.include_paths if path.startswith(".steering/")]
    assert steering == [
        ".steering/example/design.md",
        ".steering/example/requirements.md",
        ".steering/example/tasklist.md",
    ]
    assert "docs/derived-projects.md" in manifest.forbidden_paths
    assert "distribution/template-manifest.json" in manifest.forbidden_paths
    assert "docs/procedures/template-distribution.md" in manifest.forbidden_paths
    assert "scripts/build_template_distribution.py" in manifest.forbidden_paths
    assert "tests/distribution/test_template_distribution.py" in manifest.forbidden_paths
    assert "docs/ideas/" in manifest.forbidden_prefixes
    assert "tests/procedures/test_derived_project_rollout.py" in manifest.forbidden_paths
    assert (
        "tests/procedures/test_template_distribution_procedure.py"
        in manifest.forbidden_paths
    )


def test_real_manifest_paths_and_transform_preconditions_match_worktree() -> None:
    manifest = builder.load_manifest(MANIFEST)

    for relative in manifest.include_paths:
        assert (ROOT / relative).is_file(), relative
    contents: dict[str, bytes] = {}
    for transformation in manifest.transformations:
        content = contents.get(
            transformation.path, (ROOT / transformation.path).read_bytes()
        )
        contents[transformation.path] = builder._apply_transformation(
            content, transformation
        )


def test_real_manifest_removes_references_to_canonical_only_documents() -> None:
    manifest = builder.load_manifest(MANIFEST)
    contents: dict[str, bytes] = {}
    for transformation in manifest.transformations:
        content = contents.get(
            transformation.path, (ROOT / transformation.path).read_bytes()
        )
        contents[transformation.path] = builder._apply_transformation(
            content, transformation
        )

    for path in (
        "AGENTS.md",
        "CLAUDE.md",
        "docs/procedures/derived-project-rollout.md",
    ):
        output = contents[path].decode("utf-8")
        assert "`docs/ideas/harness-engineering.md`" not in output
        assert "`docs/ideas/harness-swap.md`" not in output
        assert "`docs/derived-projects.md`" not in output


def test_build_uses_tagged_blobs_applies_transforms_and_preserves_mode(
    tmp_path: Path,
) -> None:
    source, source_commit = source_repository(tmp_path)
    manifest = write_manifest(tmp_path / "manifest.json")
    output = tmp_path / "output"

    assert build(source=source, manifest=manifest, output=output) == source_commit

    assert STEERING_IGNORE_BLOCK not in (output / ".gitignore").read_text(encoding="utf-8")
    assert (output / "procedure.md").read_text(encoding="utf-8") == (
        "# Public procedure\n\nKept.\n"
    )
    assert stat.S_IMODE((output / "script.sh").stat().st_mode) == 0o755
    metadata = json.loads(
        (output / builder.METADATA_PATH).read_text(encoding="utf-8")
    )
    assert metadata == {
        "manifest_version": 1,
        "publisher_repository": "example/publisher",
        "publisher_revision": "a" * 40,
        "source_commit": source_commit,
        "source_repository": "example/canonical",
        "source_tag": "v1.0.0",
    }


def test_same_inputs_produce_identical_files_and_modes(tmp_path: Path) -> None:
    source, _source_commit = source_repository(tmp_path)
    manifest = write_manifest(tmp_path / "manifest.json")
    first = tmp_path / "first"
    second = tmp_path / "second"

    build(source=source, manifest=manifest, output=first)
    build(source=source, manifest=manifest, output=second)

    assert file_snapshot(first) == file_snapshot(second)


def test_generated_project_tracks_new_steering_with_plain_git_add(
    tmp_path: Path,
) -> None:
    source, _source_commit = source_repository(tmp_path)
    manifest = write_manifest(tmp_path / "manifest.json")
    output = tmp_path / "output"
    build(source=source, manifest=manifest, output=output)
    git(output, "init", "-b", "main")
    git(output, "config", "user.name", "Distribution Test")
    git(output, "config", "user.email", "distribution@example.com")
    git(output, "add", "-A")
    git(output, "commit", "-m", "generated")
    task = output / ".steering" / "20261117-user-work" / "tasklist.md"
    task.parent.mkdir(parents=True)
    task.write_text("# User work\n", encoding="utf-8")

    git(output, "add", "-A")

    assert ".steering/20261117-user-work/tasklist.md" in git(
        output, "ls-files"
    ).splitlines()


@pytest.mark.parametrize("tag", ["main", "../v1.0.0", "-v1.0.0", "missing"])
def test_build_rejects_non_tag_or_invalid_ref(tmp_path: Path, tag: str) -> None:
    source, _source_commit = source_repository(tmp_path)
    manifest = write_manifest(tmp_path / "manifest.json")

    with pytest.raises(builder.DistributionError):
        build(
            source=source,
            manifest=manifest,
            output=tmp_path / f"output-{tag.replace('/', '-')}",
            tag=tag,
        )


def test_build_rejects_nonempty_output_without_modifying_it(tmp_path: Path) -> None:
    source, _source_commit = source_repository(tmp_path)
    manifest = write_manifest(tmp_path / "manifest.json")
    output = tmp_path / "output"
    output.mkdir()
    existing = output / "keep.txt"
    existing.write_text("keep\n", encoding="utf-8")

    with pytest.raises(builder.DistributionError, match="not empty"):
        build(source=source, manifest=manifest, output=output)

    assert existing.read_text(encoding="utf-8") == "keep\n"


def test_build_rejects_unverifiable_publisher_identity(tmp_path: Path) -> None:
    source, _source_commit = source_repository(tmp_path)
    manifest = write_manifest(tmp_path / "manifest.json")

    with pytest.raises(builder.DistributionError, match="full commit SHA"):
        builder.build_distribution(
            source_repository=source,
            source_tag="v1.0.0",
            manifest_path=manifest,
            output=tmp_path / "output",
            publisher_repository="example/publisher",
            publisher_revision="working-tree",
        )


def test_build_rejects_source_origin_that_disagrees_with_manifest(
    tmp_path: Path,
) -> None:
    source, _source_commit = source_repository(tmp_path)
    git(source, "remote", "set-url", "origin", "https://github.com/example/other.git")
    manifest = write_manifest(tmp_path / "manifest.json")

    with pytest.raises(builder.DistributionError, match="does not match manifest"):
        build(source=source, manifest=manifest, output=tmp_path / "output")


def test_build_rejects_missing_included_path(tmp_path: Path) -> None:
    source, _source_commit = source_repository(tmp_path)
    manifest = write_manifest(
        tmp_path / "manifest.json",
        include_paths=[
            ".gitignore",
            ".steering/example/tasklist.md",
            "missing.md",
            "procedure.md",
            "script.sh",
        ],
        required_paths=[
            ".gitignore",
            ".steering/example/tasklist.md",
            "procedure.md",
            "script.sh",
        ],
    )

    with pytest.raises(builder.DistributionError, match="absent from source"):
        build(source=source, manifest=manifest, output=tmp_path / "output")


def test_build_rejects_transform_precondition_mismatch(tmp_path: Path) -> None:
    source, _source_commit = source_repository(tmp_path)
    transformations: list[dict[str, str]] = [
        {
            "path": ".gitignore",
            "kind": "replace_exact_once",
            "old": "not present",
            "new": "",
        }
    ]
    manifest = write_manifest(
        tmp_path / "manifest.json", transformations=transformations
    )

    with pytest.raises(builder.DistributionError, match="expected one match"):
        build(source=source, manifest=manifest, output=tmp_path / "output")


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        (
            {
                "include_paths": [
                    ".gitignore",
                    ".steering/example/tasklist.md",
                    "docs/derived-projects.md",
                    "procedure.md",
                    "script.sh",
                ]
            },
            "forbidden_paths are included",
        ),
        (
            {
                "include_paths": [
                        "../escape",
                    ".gitignore",
                    ".steering/example/tasklist.md",
                    "procedure.md",
                    "script.sh",
                ]
            },
            "normalized relative path",
        ),
        ({"required_paths": ["missing.md"]}, "required_paths are not included"),
        (
            {
                "include_paths": [
                    ".gitignore",
                    ".platform-harness-source.json",
                    ".steering/example/tasklist.md",
                    "procedure.md",
                    "script.sh",
                ]
            },
            "reserved for generated provenance metadata",
        ),
    ],
)
def test_manifest_rejects_unsafe_contract(
    tmp_path: Path, overrides: dict[str, object], message: str
) -> None:
    manifest = write_manifest(tmp_path / "manifest.json", **overrides)

    with pytest.raises(builder.DistributionError, match=message):
        builder.load_manifest(manifest)


def test_build_rejects_symlink_included_by_manifest(tmp_path: Path) -> None:
    source, _source_commit = source_repository(tmp_path)
    link = source / "link"
    link.symlink_to("script.sh")
    git(source, "add", "link")
    git(source, "commit", "-m", "add symlink")
    git(source, "tag", "v1.1.0")
    manifest = write_manifest(
        tmp_path / "manifest.json",
        include_paths=[
            ".gitignore",
            ".steering/example/tasklist.md",
            "link",
            "procedure.md",
            "script.sh",
        ],
    )

    with pytest.raises(builder.DistributionError, match="not a regular file"):
        build(
            source=source,
            manifest=manifest,
            output=tmp_path / "output",
            tag="v1.1.0",
        )


def test_detect_publisher_repository_supports_https_and_ssh(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "publisher"
    repository.mkdir()
    git(repository, "init", "-b", "main")
    git(repository, "remote", "add", "origin", "https://github.com/owner/project.git")
    assert builder.detect_publisher_repository(repository) == "owner/project"
    git(repository, "remote", "set-url", "origin", "git@github.com:owner/project.git")
    assert builder.detect_publisher_repository(repository) == "owner/project"


def test_detect_publisher_revision_rejects_dirty_worktree(tmp_path: Path) -> None:
    repository = tmp_path / "publisher"
    repository.mkdir()
    git(repository, "init", "-b", "main")
    git(repository, "config", "user.name", "Distribution Test")
    git(repository, "config", "user.email", "distribution@example.com")
    tracked = repository / "tracked.txt"
    tracked.write_text("clean\n", encoding="utf-8")
    git(repository, "add", "tracked.txt")
    git(repository, "commit", "-m", "initial")
    assert builder.detect_publisher_revision(repository) == git(
        repository, "rev-parse", "HEAD"
    )
    tracked.write_text("dirty\n", encoding="utf-8")

    with pytest.raises(builder.DistributionError, match="working tree is dirty"):
        builder.detect_publisher_revision(repository)
