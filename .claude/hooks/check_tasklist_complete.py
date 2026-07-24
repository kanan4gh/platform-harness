"""Stopフック: 進行中ステアリング作業のtasklist.mdに未完了タスクが残っていれば終了をブロックする。

判定ロジックは scripts/steering_lint.py(ハーネス中立のlint CLI)と共有する。
このフックを他プロジェクトへ配布する場合は scripts/steering_lint.py とセットで移植すること。
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

# 判定ロジックの解決はフック自身の位置基準(リポジトリ直下/scripts)。
# CLAUDE_PROJECT_DIR 基準にしないのは、検査対象プロジェクトとフック設置場所が別になる
# テスト環境でも動作させるため。
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
try:
    from steering_lint import (  # noqa: E402
        find_incomplete_tasks,
        find_latest_tasklist,
        has_completed_tasks,
    )
except ImportError:
    # fail-open: scripts/steering_lint.py 不在の環境ではフックを無効化する
    # (規律の最終ゲートはCIのlintが担う)
    sys.exit(0)

MAX_LISTED_TASKS = 5


def check(event: dict[str, Any], project_root: Path) -> dict[str, Any] | None:
    """未完了タスクが残っていればblock判定のJSONを、なければNoneを返す。"""
    # フックプロトコル: 前回のStopフックがすでにブロック済みの場合は通す(無限ループ防止)
    if event.get("stop_hook_active"):
        return None

    tasklist = find_latest_tasklist(project_root)
    if tasklist is None:
        return None

    content = tasklist.read_text(encoding="utf-8")
    incomplete = find_incomplete_tasks(content)
    if not incomplete:
        return None

    # 未着手(完了タスクゼロ)のtasklistは計画承認ゲート/作業前とみなしfail-openする。
    # hookは着手済み作業の放置を防ぐためのもので、未着手の計画を強制実行させない。
    # PR前の未完了検出はCIのsteering lint(C3)が担う。
    if not has_completed_tasks(content):
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
