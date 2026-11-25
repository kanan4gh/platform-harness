"""Tests for the single-entry local quality gate."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from collections.abc import Callable
from typing import Any

import pytest

SCRIPT_PATH = Path(__file__).parents[2] / "scripts" / "local_quality_gate.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("local_quality_gate", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gate = load_module()


def project_root(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "steering_lint.py").write_text("", encoding="utf-8")
    return tmp_path


def test_run_gate_runs_all_commands_in_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = project_root(tmp_path)
    monkeypatch.setattr(gate.shutil, "which", lambda _name: "/usr/bin/uv")
    calls: list[tuple[tuple[str, ...], Path, bool, bool]] = []

    def runner(
        argv: tuple[str, ...], *, cwd: Path, check: bool, shell: bool
    ) -> subprocess.CompletedProcess[bytes]:
        calls.append((argv, cwd, check, shell))
        return subprocess.CompletedProcess(argv, 0)

    assert gate.run_gate(root, runner=runner) == 0
    assert [call[0] for call in calls] == [command.argv for command in gate.COMMANDS]
    assert all(call[1:] == (root, False, False) for call in calls)


def test_run_gate_stops_after_first_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = project_root(tmp_path)
    monkeypatch.setattr(gate.shutil, "which", lambda _name: "/usr/bin/uv")
    calls: list[tuple[str, ...]] = []

    def runner(argv: tuple[str, ...], **_kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 7 if len(calls) == 2 else 0)

    assert gate.run_gate(root, runner=runner) == 7
    assert calls == [gate.COMMANDS[0].argv, gate.COMMANDS[1].argv]


def test_run_gate_does_not_start_process_when_uv_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = project_root(tmp_path)
    monkeypatch.setattr(gate.shutil, "which", lambda _name: None)
    called = False

    def runner(*_args: Any, **_kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        nonlocal called
        called = True
        raise AssertionError("runner must not be called")

    assert gate.run_gate(root, runner=runner) == 1
    assert called is False


def test_run_gate_rejects_invalid_project_root(tmp_path: Path) -> None:
    assert gate.run_gate(tmp_path) == 1


def test_run_gate_returns_one_when_runner_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = project_root(tmp_path)
    monkeypatch.setattr(gate.shutil, "which", lambda _name: "/usr/bin/uv")

    def runner(*_args: Any, **_kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        raise OSError("cannot execute")

    assert gate.run_gate(root, runner=runner) == 1


def test_command_list_has_no_llm_github_or_network_commands() -> None:
    forbidden = {"claude", "codex", "kiro", "gh", "curl", "wget"}
    executables = {token for command in gate.COMMANDS for token in command.argv}
    assert executables.isdisjoint(forbidden)
    assert all("http://" not in token and "https://" not in token for token in executables)


def test_command_list_runs_completion_steering_lint_once() -> None:
    steering_commands = [
        command
        for command in gate.COMMANDS
        if "scripts/steering_lint.py" in command.argv
    ]
    assert len(steering_commands) == 1
    assert steering_commands[0].argv[-1] == "--require-complete"


def test_commands_for_appends_explicit_completion_target_once() -> None:
    commands = gate.commands_for("20260728-explicit")
    steering_commands = [
        command for command in commands if "scripts/steering_lint.py" in command.argv
    ]
    assert len(steering_commands) == 1
    assert steering_commands[0].argv[-2:] == (
        "--require-complete",
        "20260728-explicit",
    )
    assert len(commands) == len(gate.COMMANDS)


REAL_STEERING_LINT = SCRIPT_PATH.parent / "steering_lint.py"


def zero_dated_steering_project(tmp_path: Path) -> Path:
    """日付付きのステアリングが0件(example/だけ)で、実物のsteering lintを置いた状態。"""
    root = project_root(tmp_path)
    (root / "scripts" / "steering_lint.py").write_text(
        REAL_STEERING_LINT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    example = root / ".steering" / "example"
    example.mkdir(parents=True)
    (example / "tasklist.md").write_text("# タスクリスト\n\n- [ ] 例\n", encoding="utf-8")
    return root


def real_steering_lint_runner(
    outputs: list[str],
) -> Callable[..., subprocess.CompletedProcess[bytes]]:
    """steering lintだけ実物を実行し、他のコマンドは成功を返すrunner。"""

    def runner(
        argv: tuple[str, ...], *, cwd: Path, check: bool, shell: bool
    ) -> subprocess.CompletedProcess[bytes]:
        if "scripts/steering_lint.py" not in argv:
            return subprocess.CompletedProcess(argv, 0)
        script_index = argv.index("scripts/steering_lint.py")
        result = subprocess.run(
            [sys.executable, *argv[script_index:]],
            cwd=cwd,
            check=check,
            shell=shell,
            capture_output=True,
            text=True,
        )
        outputs.append(result.stdout + result.stderr)
        return subprocess.CompletedProcess(argv, result.returncode)

    return runner


def test_run_gate_passes_with_real_steering_lint_without_dated_steering(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = zero_dated_steering_project(tmp_path)
    monkeypatch.setattr(gate.shutil, "which", lambda _name: "/usr/bin/uv")
    outputs: list[str] = []
    assert gate.run_gate(root, runner=real_steering_lint_runner(outputs)) == 0
    assert outputs == ["steering lint: 完了検査をスキップしました（日付付きのステアリングが0件）\n"]


def test_run_gate_fails_for_missing_explicit_steering_without_dated_steering(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = zero_dated_steering_project(tmp_path)
    monkeypatch.setattr(gate.shutil, "which", lambda _name: "/usr/bin/uv")
    outputs: list[str] = []
    commands = gate.commands_for("20260728-missing")
    assert gate.run_gate(root, commands=commands, runner=real_steering_lint_runner(outputs)) == 2
    assert len(outputs) == 1
    assert "見つかりません" in outputs[0]


def test_main_rejects_too_many_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    assert gate.main(["one", "two"]) == 2
    assert "usage:" in capsys.readouterr().err
