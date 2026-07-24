"""Kiro CLI Stopフック: 最新tasklist.mdの未完了タスクがあれば終了をブロックする。

判定ロジックは scripts/steering_lint.py と共有する。Kiro CLIのStopフックは
stdinのイベントJSONに ``cwd`` を含み、stdoutの ``decision: block`` で会話を継続する。
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
try:
    from steering_lint import (  # noqa: E402
        find_incomplete_tasks,
        find_latest_tasklist,
        has_completed_tasks,
    )
except ImportError:
    sys.exit(0)

MAX_LISTED_TASKS = 5
MAX_CONSECUTIVE_BLOCKS = 3
STATE_FILE = Path(".kiro") / "hooks" / "state" / "stop_guard.json"


def load_state(state_path: Path) -> dict[str, Any] | None:
    if not state_path.is_file():
        return {"tasklist_hash": "", "consecutive_blocks": 0}
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        if isinstance(data.get("tasklist_hash"), str) and isinstance(
            data.get("consecutive_blocks"), int
        ):
            return data
    except Exception:
        pass
    return None


def save_state(state_path: Path, tasklist_hash: str, consecutive_blocks: int) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"tasklist_hash": tasklist_hash, "consecutive_blocks": consecutive_blocks}),
        encoding="utf-8",
    )


def check(event: dict[str, Any], project_root: Path) -> dict[str, Any] | None:
    """未完了タスクがあればKiroのblock decisionを返す。"""
    tasklist = find_latest_tasklist(project_root)
    if tasklist is None:
        return None

    content = tasklist.read_text(encoding="utf-8")
    incomplete = find_incomplete_tasks(content)
    state_path = project_root / STATE_FILE

    if not incomplete:
        if state_path.is_file():
            save_state(state_path, "", 0)
        return None

    # 未着手(完了タスクゼロ)のtasklistは計画承認ゲート/作業前とみなしfail-openする。
    # 状態ファイルより前に判定し、未着手時に状態ファイルを作らない。
    if not has_completed_tasks(content):
        return None

    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    state = load_state(state_path)
    if state is None:
        return None
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
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
