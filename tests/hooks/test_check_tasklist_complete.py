"""check_tasklist_complete.py(Stopフック)のユニットテスト。"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HOOK_PATH = Path(__file__).parents[2] / ".claude" / "hooks" / "check_tasklist_complete.py"

spec = importlib.util.spec_from_file_location("check_tasklist_complete", HOOK_PATH)
assert spec is not None and spec.loader is not None
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def make_steering(tmp_path: Path, dirname: str, tasklist: str | None) -> Path:
    d = tmp_path / ".steering" / dirname
    d.mkdir(parents=True)
    if tasklist is not None:
        (d / "tasklist.md").write_text(tasklist, encoding="utf-8")
    return d


def test_check_incomplete_tasks_blocks(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260709-foo", "- [x] done\n- [ ] not yet\n")
    result = hook.check({}, tmp_path)
    assert result is not None
    assert result["decision"] == "block"
    assert "not yet" in result["reason"]
    assert "1件" in result["reason"]


def test_check_indented_subtask_blocks(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260709-foo", "- [x] parent\n  - [ ] subtask\n")
    result = hook.check({}, tmp_path)
    assert result is not None
    assert "subtask" in result["reason"]


def test_check_all_complete_returns_none(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260709-foo", "- [x] done\n- [x] ~~skipped~~（理由: 方針変更）\n")
    assert hook.check({}, tmp_path) is None


def test_check_no_steering_dir_returns_none(tmp_path: Path) -> None:
    assert hook.check({}, tmp_path) is None


def test_check_empty_steering_dir_returns_none(tmp_path: Path) -> None:
    (tmp_path / ".steering").mkdir()
    assert hook.check({}, tmp_path) is None


def test_check_missing_tasklist_returns_none(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260709-foo", None)
    assert hook.check({}, tmp_path) is None


def test_check_stop_hook_active_returns_none(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260709-foo", "- [ ] not yet\n")
    assert hook.check({"stop_hook_active": True}, tmp_path) is None


def test_check_only_latest_dir_is_inspected(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260101-old", "- [ ] old incomplete\n")
    make_steering(tmp_path, "20260709-new", "- [x] all done\n")
    assert hook.check({}, tmp_path) is None


def test_check_latest_dir_incomplete_blocks(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260101-old", "- [x] done\n")
    make_steering(tmp_path, "20260709-new", "- [ ] new incomplete\n")
    result = hook.check({}, tmp_path)
    assert result is not None
    assert "new incomplete" in result["reason"]


def test_check_reason_lists_at_most_five_tasks(tmp_path: Path) -> None:
    tasks = "\n".join(f"- [ ] task{i}" for i in range(7))
    make_steering(tmp_path, "20260709-foo", tasks + "\n")
    result = hook.check({}, tmp_path)
    assert result is not None
    assert "task4" in result["reason"]
    assert "task5" not in result["reason"]
    assert "ほか2件" in result["reason"]


def test_check_ignores_non_dated_dirs(tmp_path: Path) -> None:
    # example/ 等のサンプルディレクトリは日付接頭辞を持たないため対象外
    make_steering(tmp_path, "example", "- [ ] サンプルタスク\n")
    assert hook.check({}, tmp_path) is None


def test_check_non_dated_dir_does_not_shadow_dated_dir(tmp_path: Path) -> None:
    # 名前降順で example が 20260709-* より後でも、日付ディレクトリが優先される
    make_steering(tmp_path, "example", "- [x] done\n")
    make_steering(tmp_path, "20260709-foo", "- [ ] real incomplete\n")
    result = hook.check({}, tmp_path)
    assert result is not None
    assert "real incomplete" in result["reason"]


def test_check_ignores_plain_files_in_steering(tmp_path: Path) -> None:
    (tmp_path / ".steering").mkdir()
    (tmp_path / ".steering" / "distill-20260709.md").write_text("- [ ] x\n", encoding="utf-8")
    assert hook.check({}, tmp_path) is None


def run_hook(stdin_text: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=cwd,
        env={"CLAUDE_PROJECT_DIR": str(cwd)},
    )


def test_main_blocks_via_stdout(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260709-foo", "- [ ] not yet\n")
    proc = run_hook("{}", tmp_path)
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert out["decision"] == "block"


def test_main_no_output_when_complete(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260709-foo", "- [x] done\n")
    proc = run_hook("{}", tmp_path)
    assert proc.returncode == 0
    assert proc.stdout == ""


def test_main_fail_open_on_invalid_stdin(tmp_path: Path) -> None:
    proc = run_hook("not json", tmp_path)
    assert proc.returncode == 0
    assert proc.stdout == ""
