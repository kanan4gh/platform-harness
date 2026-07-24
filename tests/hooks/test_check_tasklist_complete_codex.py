"""check_tasklist_complete.py(Codex版Stopフック)のユニットテスト。"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HOOK_PATH = Path(__file__).parents[2] / ".codex" / "hooks" / "check_tasklist_complete.py"

spec = importlib.util.spec_from_file_location("check_tasklist_complete_codex", HOOK_PATH)
assert spec is not None and spec.loader is not None
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

STATE_PATH = Path(".codex") / "hooks" / "state" / "stop_guard.json"


def make_steering(tmp_path: Path, dirname: str, tasklist: str | None) -> Path:
    d = tmp_path / ".steering" / dirname
    d.mkdir(parents=True)
    if tasklist is not None:
        (d / "tasklist.md").write_text(tasklist, encoding="utf-8")
    return d


def test_check_incomplete_tasks_blocks(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260714-foo", "- [x] done\n- [ ] not yet\n")
    result = hook.check({}, tmp_path)
    assert result is not None
    assert result["decision"] == "block"
    assert "not yet" in result["reason"]


def test_check_all_complete_returns_none(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260714-foo", "- [x] done\n")
    assert hook.check({}, tmp_path) is None


def test_check_no_steering_dir_returns_none(tmp_path: Path) -> None:
    assert hook.check({}, tmp_path) is None


def test_check_unstarted_tasklist_returns_none(tmp_path: Path) -> None:
    # 未着手(完了タスクゼロ)は計画承認ゲート/作業前とみなしfail-openし、状態ファイルも作らない
    make_steering(tmp_path, "20260714-foo", "- [ ] a\n- [ ] b\n")
    assert hook.check({}, tmp_path) is None
    assert not (tmp_path / STATE_PATH).exists()


def test_consecutive_block_guard_fails_open(tmp_path: Path) -> None:
    # 同一内容へのブロックが MAX_CONSECUTIVE_BLOCKS 回続いたら fail-open する
    make_steering(tmp_path, "20260714-foo", "- [x] done\n- [ ] stuck\n")
    for _ in range(hook.MAX_CONSECUTIVE_BLOCKS):
        assert hook.check({}, tmp_path) is not None
    assert hook.check({}, tmp_path) is None


def test_guard_resets_when_tasklist_changes(tmp_path: Path) -> None:
    # tasklist内容が変わればカウンタはリセットされ、再びブロックする
    d = make_steering(tmp_path, "20260714-foo", "- [x] done\n- [ ] first\n")
    for _ in range(hook.MAX_CONSECUTIVE_BLOCKS):
        assert hook.check({}, tmp_path) is not None
    assert hook.check({}, tmp_path) is None
    (d / "tasklist.md").write_text("- [x] done\n- [ ] first\n- [ ] second\n", encoding="utf-8")
    assert hook.check({}, tmp_path) is not None


def test_guard_state_resets_on_completion(tmp_path: Path) -> None:
    # 完了状態を観測したら状態ファイルをリセットする
    d = make_steering(tmp_path, "20260714-foo", "- [x] done\n- [ ] wip\n")
    assert hook.check({}, tmp_path) is not None
    (d / "tasklist.md").write_text("- [x] done\n- [x] wip\n", encoding="utf-8")
    assert hook.check({}, tmp_path) is None
    state = json.loads((tmp_path / STATE_PATH).read_text(encoding="utf-8"))
    assert state["consecutive_blocks"] == 0


def test_no_state_file_created_on_clean_run(tmp_path: Path) -> None:
    # クリーンな環境(ブロック履歴なし)では状態ファイルを作らない
    make_steering(tmp_path, "20260714-foo", "- [x] done\n")
    assert hook.check({}, tmp_path) is None
    assert not (tmp_path / STATE_PATH).exists()


def run_hook(stdin_text: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_main_resolves_root_from_cwd_field(tmp_path: Path) -> None:
    # プロジェクトルートはstdinイベントの cwd フィールドで解決する
    make_steering(tmp_path, "20260714-foo", "- [x] done\n- [ ] not yet\n")
    proc = run_hook(json.dumps({"cwd": str(tmp_path)}), Path.cwd())
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert out["decision"] == "block"


def test_main_no_output_when_complete(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260714-foo", "- [x] done\n")
    proc = run_hook(json.dumps({"cwd": str(tmp_path)}), Path.cwd())
    assert proc.returncode == 0
    assert proc.stdout == ""


def test_main_fail_open_on_invalid_stdin(tmp_path: Path) -> None:
    proc = run_hook("not json", tmp_path)
    assert proc.returncode == 0
    assert proc.stdout == ""
