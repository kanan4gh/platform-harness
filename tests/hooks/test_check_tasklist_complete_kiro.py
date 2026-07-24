"""Kiro CLI版Stopフックのユニットテスト。"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HOOK_PATH = Path(__file__).parents[2] / ".kiro" / "hooks" / "check_tasklist_complete.py"

spec = importlib.util.spec_from_file_location("check_tasklist_complete_kiro", HOOK_PATH)
assert spec is not None and spec.loader is not None
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

STATE_PATH = Path(".kiro") / "hooks" / "state" / "stop_guard.json"


def make_steering(tmp_path: Path, dirname: str, tasklist: str) -> Path:
    directory = tmp_path / ".steering" / dirname
    directory.mkdir(parents=True)
    (directory / "tasklist.md").write_text(tasklist, encoding="utf-8")
    return directory


def test_check_incomplete_tasks_blocks(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260715-foo", "- [x] done\n- [ ] not yet\n")
    result = hook.check({}, tmp_path)
    assert result is not None
    assert result["decision"] == "block"
    assert "not yet" in result["reason"]


def test_check_all_complete_returns_none(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260715-foo", "- [x] done\n")
    assert hook.check({}, tmp_path) is None


def test_check_no_steering_returns_none(tmp_path: Path) -> None:
    assert hook.check({}, tmp_path) is None


def test_check_unstarted_tasklist_returns_none(tmp_path: Path) -> None:
    # 未着手(完了タスクゼロ)は計画承認ゲート/作業前とみなしfail-openし、状態ファイルも作らない
    make_steering(tmp_path, "20260715-foo", "- [ ] a\n- [ ] b\n")
    assert hook.check({}, tmp_path) is None
    assert not (tmp_path / STATE_PATH).exists()


def test_consecutive_block_guard_fails_open(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260715-foo", "- [x] done\n- [ ] stuck\n")
    for _ in range(hook.MAX_CONSECUTIVE_BLOCKS):
        assert hook.check({}, tmp_path) is not None
    assert hook.check({}, tmp_path) is None


def test_guard_resets_when_tasklist_changes(tmp_path: Path) -> None:
    directory = make_steering(tmp_path, "20260715-foo", "- [x] done\n- [ ] first\n")
    for _ in range(hook.MAX_CONSECUTIVE_BLOCKS):
        assert hook.check({}, tmp_path) is not None
    assert hook.check({}, tmp_path) is None
    (directory / "tasklist.md").write_text(
        "- [x] done\n- [ ] first\n- [ ] second\n", encoding="utf-8"
    )
    assert hook.check({}, tmp_path) is not None


def test_guard_state_resets_on_completion(tmp_path: Path) -> None:
    directory = make_steering(tmp_path, "20260715-foo", "- [x] done\n- [ ] wip\n")
    assert hook.check({}, tmp_path) is not None
    (directory / "tasklist.md").write_text("- [x] done\n- [x] wip\n", encoding="utf-8")
    assert hook.check({}, tmp_path) is None
    state = json.loads((tmp_path / STATE_PATH).read_text(encoding="utf-8"))
    assert state["consecutive_blocks"] == 0


def test_missing_state_starts_from_first_block(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260715-foo", "- [x] done\n- [ ] wip\n")
    assert not (tmp_path / STATE_PATH).exists()
    assert hook.check({}, tmp_path) is not None
    state = json.loads((tmp_path / STATE_PATH).read_text(encoding="utf-8"))
    assert state["consecutive_blocks"] == 1


def test_corrupt_state_fails_open(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260715-foo", "- [x] done\n- [ ] wip\n")
    state_path = tmp_path / STATE_PATH
    state_path.parent.mkdir(parents=True)
    state_path.write_text("not json", encoding="utf-8")
    assert hook.check({}, tmp_path) is None


def run_hook(stdin_text: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_main_resolves_root_from_cwd_field(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260715-foo", "- [x] done\n- [ ] not yet\n")
    process = run_hook(json.dumps({"cwd": str(tmp_path)}), Path.cwd())
    assert process.returncode == 0
    assert json.loads(process.stdout)["decision"] == "block"


def test_main_uses_process_cwd_when_field_is_missing(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260715-foo", "- [x] done\n- [ ] not yet\n")
    process = run_hook("{}", tmp_path)
    assert process.returncode == 0
    assert json.loads(process.stdout)["decision"] == "block"


def test_main_no_output_when_complete(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260715-foo", "- [x] done\n")
    process = run_hook(json.dumps({"cwd": str(tmp_path)}), Path.cwd())
    assert process.returncode == 0
    assert process.stdout == ""


def test_main_fail_open_on_invalid_stdin(tmp_path: Path) -> None:
    process = run_hook("not json", tmp_path)
    assert process.returncode == 0
    assert process.stdout == ""


def test_main_fail_open_outside_repository(tmp_path: Path) -> None:
    process = run_hook(json.dumps({"cwd": str(tmp_path)}), tmp_path)
    assert process.returncode == 0
    assert process.stdout == ""
