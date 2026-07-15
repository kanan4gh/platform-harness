"""Run the complete local, deterministic quality gate without network or LLM calls."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Callable, Sequence


@dataclass(frozen=True)
class Command:
    name: str
    argv: tuple[str, ...]


COMMANDS: tuple[Command, ...] = (
    Command("pytest", ("uv", "run", "pytest")),
    Command("ruff", ("uv", "run", "ruff", "check", ".")),
    Command("basedpyright", ("uv", "run", "basedpyright")),
    Command("steering lint", ("uv", "run", "python3", "scripts/steering_lint.py")),
    Command(
        "metered automation lint",
        ("uv", "run", "python3", "scripts/metered_automation_lint.py"),
    ),
)

Runner = Callable[..., subprocess.CompletedProcess[bytes]]


def validate_environment(root: Path) -> str | None:
    if not root.is_dir():
        return f"project root is not a directory: {root}"
    required = (root / "pyproject.toml", root / "scripts" / "steering_lint.py")
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    if missing:
        return f"project root is missing required files: {', '.join(missing)}"
    if shutil.which("uv") is None:
        return "uv was not found on PATH"
    return None


def run_gate(
    root: Path,
    *,
    commands: Sequence[Command] = COMMANDS,
    runner: Runner = subprocess.run,
) -> int:
    error = validate_environment(root)
    if error is not None:
        print(f"local quality gate: {error}", file=sys.stderr)
        return 1

    print(f"local quality gate: running {len(commands)} checks")
    for index, command in enumerate(commands, start=1):
        print(f"[{index}/{len(commands)}] {command.name}: {' '.join(command.argv)}", flush=True)
        try:
            result = runner(command.argv, cwd=root, check=False, shell=False)
        except Exception as exc:
            print(f"local quality gate: {command.name} could not start: {exc}", file=sys.stderr)
            return 1
        if result.returncode != 0:
            print(
                f"local quality gate: {command.name} failed (exit {result.returncode})",
                file=sys.stderr,
            )
            return result.returncode if result.returncode > 0 else 1
        print(f"[{index}/{len(commands)}] {command.name}: passed")
    print("local quality gate: all checks passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1:
        print("usage: local_quality_gate.py [PROJECT_ROOT]", file=sys.stderr)
        return 2
    root = Path(args[0]).resolve() if args else Path.cwd().resolve()
    return run_gate(root)


if __name__ == "__main__":
    raise SystemExit(main())
