"""Stopフック(Codex CLI): 進行中ステアリング作業のtasklist.mdに未完了タスクが残っていれば終了をブロックする。

判定ロジックは scripts/steering_lint.py(ハーネス中立のlint CLI)と共有する。
このフックを他プロジェクトへ配布する場合は scripts/steering_lint.py とセットで移植すること。

Claude Code版(.claude/hooks/check_tasklist_complete.py)との相違点:
- プロジェクトルートはstdinイベントの `cwd` フィールドで解決する(なければカレントディレクトリ)。
  CodexにはCLAUDE_PROJECT_DIR相当の環境変数がないため
- ループ防止は `stop_hook_active` の代わりに連続ブロックガード(同一tasklist内容への
  ブロックが MAX_CONSECUTIVE_BLOCKS 回続いたらfail-open)で行う。Codexのフックイベントに
  同フィールドがないため
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

# 判定ロジックの解決はフック自身の位置基準(リポジトリ直下/scripts)。
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
try:
    from steering_lint import find_incomplete_tasks, find_latest_tasklist  # noqa: E402
except ImportError:
    # fail-open: scripts/steering_lint.py 不在の環境ではフックを無効化する
    # (規律の最終ゲートはCIのlintが担う)
    sys.exit(0)

MAX_LISTED_TASKS = 5
MAX_CONSECUTIVE_BLOCKS = 3
STATE_FILE = Path(".codex") / "hooks" / "state" / "stop_guard.json"


def load_state(state_path: Path) -> dict[str, Any]:
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        if isinstance(data.get("tasklist_hash"), str) and isinstance(
            data.get("consecutive_blocks"), int
        ):
            return data
    except Exception:
        pass  # fail-open: 状態が読めなければ初期化して継続
    return {"tasklist_hash": "", "consecutive_blocks": 0}


def save_state(state_path: Path, tasklist_hash: str, consecutive_blocks: int) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"tasklist_hash": tasklist_hash, "consecutive_blocks": consecutive_blocks}),
        encoding="utf-8",
    )


def check(event: dict[str, Any], project_root: Path) -> dict[str, Any] | None:
    """未完了タスクが残っていればblock判定のJSONを、なければNoneを返す。"""
    tasklist = find_latest_tasklist(project_root)
    if tasklist is None:
        return None

    content = tasklist.read_text(encoding="utf-8")
    incomplete = find_incomplete_tasks(content)
    state_path = project_root / STATE_FILE

    if not incomplete:
        # ブロック履歴がある場合のみリセットする(クリーンな環境に状態ファイルを作らない)
        if state_path.is_file():
            save_state(state_path, "", 0)
        return None

    # 連続ブロックガード: 同一内容へのブロックが続く場合はfail-open(無限ループ防止)
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    state = load_state(state_path)
    blocks = state["consecutive_blocks"] if state["tasklist_hash"] == content_hash else 0
    if blocks >= MAX_CONSECUTIVE_BLOCKS:
        return None
    save_state(state_path, content_hash, blocks + 1)

    listed = "\n".join(f"- [ ] {task}" for task in incomplete[:MAX_LISTED_TASKS])
    more = len(incomplete) - MAX_LISTED_TASKS
    if more > 0:
        listed += f"\n(ほか{more}件)"
    reason = (
        f"{tasklist} に未完了タスクが{len(incomplete)}件残っています:\n"
        f"{listed}\n"
        "タスクを完了させるか、大きすぎる場合はサブタスクに分割(ルールA)、"
        "技術的理由で不要になった場合は理由を明記してスキップ(ルールB)してください。"
    )
    return {"decision": "block", "reason": reason}


def main() -> None:
    try:
        event = json.load(sys.stdin)
        cwd = event.get("cwd") if isinstance(event, dict) else None
        project_root = Path(cwd) if cwd else Path.cwd()
        result = check(event if isinstance(event, dict) else {}, project_root)
        if result is not None:
            print(json.dumps(result, ensure_ascii=False))
    except Exception:
        pass  # fail-open: フックの不具合でユーザーの作業を止めない
    sys.exit(0)


if __name__ == "__main__":
    main()
