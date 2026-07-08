"""Stopフック: 進行中ステアリング作業のtasklist.mdに未完了タスクが残っていれば終了をブロックする。"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

MAX_LISTED_TASKS = 5
INCOMPLETE_PATTERN = re.compile(r"^\s*- \[ \] (.+)$", re.MULTILINE)
# 日付接頭辞を持つ作業ディレクトリのみが対象(example/ 等のサンプルを誤検出しない)
STEERING_DIR_PATTERN = re.compile(r"^\d{8}-")


def find_latest_tasklist(project_root: Path) -> Path | None:
    """最新(日付降順の先頭)のステアリングディレクトリのtasklist.mdを返す。"""
    steering = project_root / ".steering"
    if not steering.is_dir():
        return None
    dirs = sorted(
        (p for p in steering.iterdir() if p.is_dir() and STEERING_DIR_PATTERN.match(p.name)),
        key=lambda p: p.name,
        reverse=True,
    )
    if not dirs:
        return None
    tasklist = dirs[0] / "tasklist.md"
    return tasklist if tasklist.is_file() else None


def check(event: dict[str, Any], project_root: Path) -> dict[str, Any] | None:
    """未完了タスクが残っていればblock判定のJSONを、なければNoneを返す。"""
    # フックプロトコル: 前回のStopフックがすでにブロック済みの場合は通す(無限ループ防止)
    if event.get("stop_hook_active"):
        return None

    tasklist = find_latest_tasklist(project_root)
    if tasklist is None:
        return None

    incomplete = INCOMPLETE_PATTERN.findall(tasklist.read_text(encoding="utf-8"))
    if not incomplete:
        return None

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
        project_root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
        result = check(event, project_root)
        if result is not None:
            print(json.dumps(result, ensure_ascii=False))
    except Exception:
        pass  # fail-open: フックの不具合でユーザーの作業を止めない
    sys.exit(0)


if __name__ == "__main__":
    main()
