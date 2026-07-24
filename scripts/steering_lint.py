"""ステアリング規律のlint CLI(ハーネス中立の決定論的チェック)。

`.steering/[YYYYMMDD]-*/` の全ディレクトリに対して以下をチェックする:

- C1: requirements.md / design.md / tasklist.md の3ファイルが存在する
      (requirements.md に軽量パス宣言(`軽量パス: 適用`)がある場合は design.md を省略できる)
- C2: requirements.md に GitHub Issue URL が記載されている
- C3: tasklist.md に未完了タスク(`- [ ]`)が残っていない
- C4: 完了済み(未完了タスクなし)のtasklist.mdの「実装後の振り返り」セクションに
      テンプレートプレースホルダ(`{...}`)が残っていない

違反があれば一覧を出力して exit 1、なければ exit 0。
Stopフック(.claude/hooks/check_tasklist_complete.py)は本モジュールの純関数を再利用する。
"""

import re
import sys
from pathlib import Path
from typing import NamedTuple

STEERING_DIR_PATTERN = re.compile(r"^\d{8}-")
INCOMPLETE_PATTERN = re.compile(r"^\s*- \[ \] (.+)$", re.MULTILINE)
# 完了タスク(スキップ表記 `- [x] ~~...~~` を含む)。Stopフックの未着手判定に用いる。
COMPLETED_PATTERN = re.compile(r"^\s*- \[[xX]\] ", re.MULTILINE)
# Markdownフェンス付きコードブロックの開始・終了行(バッククォート/チルダ、3文字以上)。
FENCE_PATTERN = re.compile(r"^[ \t]*(`{3,}|~{3,})")
ISSUE_URL_PATTERN = re.compile(r"github\.com/[^/\s]+/[^/\s]+/issues/\d+")
PLACEHOLDER_PATTERN = re.compile(r"\{[^{}\n]+\}")
# 行末アンカーにより「非適用」「適用外」や後続テキスト付きは宣言と見なさない。
LIGHTWEIGHT_PATTERN = re.compile(r"軽量パス\**\s*[:：]\s*適用\s*$", re.MULTILINE)
RETROSPECTIVE_HEADING = "## 実装後の振り返り"
REQUIRED_FILES = ("requirements.md", "design.md", "tasklist.md")


class Violation(NamedTuple):
    directory: str
    check_id: str
    message: str


def iter_steering_dirs(project_root: Path) -> list[Path]:
    """日付接頭辞を持つステアリングディレクトリを名前昇順で返す。"""
    steering = project_root / ".steering"
    if not steering.is_dir():
        return []
    return sorted(
        (p for p in steering.iterdir() if p.is_dir() and STEERING_DIR_PATTERN.match(p.name)),
        key=lambda p: p.name,
    )


def find_latest_tasklist(project_root: Path) -> Path | None:
    """最新(日付降順の先頭)のステアリングディレクトリのtasklist.mdを返す。"""
    dirs = iter_steering_dirs(project_root)
    if not dirs:
        return None
    tasklist = dirs[-1] / "tasklist.md"
    return tasklist if tasklist.is_file() else None


def strip_code_fences(text: str) -> str:
    """Markdownフェンス付きコードブロック内の行を空行に置換したテキストを返す。

    テンプレート等が記法の**例示**をコードフェンス内に持つため、例示のチェックボックスを
    実タスクと取り違えないための前処理。行番号を保つため除去ではなく空行化する。

    終了フェンスは開始と同じ文字種・開始以上の長さで、マーカー以降に非空白文字がない行。
    閉じられていないフェンスは以降すべてを例示扱いにして終了する(例外を投げない)。
    """
    lines = text.split("\n")
    stripped: list[str] = []
    open_marker: str | None = None
    for line in lines:
        match = FENCE_PATTERN.match(line)
        if open_marker is None:
            if match is None:
                stripped.append(line)
            else:
                # info string(```markdown 等)を許容して開始フェンスとみなす
                open_marker = match.group(1)
                stripped.append("")
            continue
        if match is not None and _closes_fence(match, line, open_marker):
            open_marker = None
        stripped.append("")
    return "\n".join(stripped)


def _closes_fence(match: re.Match[str], line: str, open_marker: str) -> bool:
    """フェンス記号にマッチした行が、開いているフェンスの終了行かを返す。"""
    marker = match.group(1)
    if marker[0] != open_marker[0] or len(marker) < len(open_marker):
        return False
    # 終了フェンスはinfo stringを持てない
    return not line[match.end() :].strip()


def find_incomplete_tasks(text: str) -> list[str]:
    """未完了タスク(`- [ ]`)の内容を出現順に返す。

    **コードフェンスを除外しない**のは意図的である。除外機構は未完了タスクを隠す抜け穴に
    なり得るのに対し、過検出はPR前に人が気づける安全側の失敗であるため。
    """
    return INCOMPLETE_PATTERN.findall(text)


def has_completed_tasks(text: str) -> bool:
    """完了タスク(`- [x]`/`- [X]`)が1つ以上あるかを返す。

    Stopフックの「未着手フェイルオープン」判定に用いる補助関数。lint本体(C3)は
    未完了の有無だけを見るため本関数を使わない(CIゲートは未着手でも未完了を検出する)。

    こちらは `find_incomplete_tasks` と異なりコードフェンスを除外する。例示を完了タスクと
    誤認すると、作りたての未着手tasklistが「着手済み」と判定され、計画承認待ちの停止に
    Stopフックが割り込んでしまうため(実害のある誤判定)。
    """
    return bool(COMPLETED_PATTERN.search(strip_code_fences(text)))


def has_lightweight_declaration(steering_dir: Path) -> bool:
    """requirements.md に軽量パス宣言(`軽量パス: 適用`)があるかを返す。"""
    requirements = steering_dir / "requirements.md"
    if not requirements.is_file():
        return False
    return bool(LIGHTWEIGHT_PATTERN.search(requirements.read_text(encoding="utf-8")))


def check_required_files(steering_dir: Path) -> list[Violation]:
    """C1: 3ファイルの存在チェック。軽量パス宣言がある場合は design.md を省略できる。"""
    missing = [name for name in REQUIRED_FILES if not (steering_dir / name).is_file()]
    if "design.md" in missing and has_lightweight_declaration(steering_dir):
        missing.remove("design.md")
    return [Violation(steering_dir.name, "C1", f"{name} がありません") for name in missing]


def check_issue_url(steering_dir: Path) -> list[Violation]:
    """C2: requirements.md への GitHub Issue URL 記載チェック。"""
    requirements = steering_dir / "requirements.md"
    if not requirements.is_file():
        return []  # ファイル欠落はC1が報告する
    if ISSUE_URL_PATTERN.search(requirements.read_text(encoding="utf-8")):
        return []
    return [Violation(steering_dir.name, "C2", "requirements.md に GitHub Issue URL がありません")]


def check_incomplete_tasks(steering_dir: Path) -> list[Violation]:
    """C3: tasklist.md の未完了タスクチェック。"""
    tasklist = steering_dir / "tasklist.md"
    if not tasklist.is_file():
        return []  # ファイル欠落はC1が報告する
    incomplete = find_incomplete_tasks(tasklist.read_text(encoding="utf-8"))
    if not incomplete:
        return []
    return [
        Violation(
            steering_dir.name,
            "C3",
            f"tasklist.md に未完了タスクが{len(incomplete)}件残っています(先頭: {incomplete[0]})",
        )
    ]


def check_retrospective_placeholders(steering_dir: Path) -> list[Violation]:
    """C4: 完了済みtasklist.mdの振り返りセクションのプレースホルダ残存チェック。

    未完了タスクが残っている(=作業中)間は対象外とし、C3に報告を委ねる。
    プレースホルダ検索を振り返りセクションに限定するのは、本文中のコード片等の
    波括弧を誤検出しないため。
    """
    tasklist = steering_dir / "tasklist.md"
    if not tasklist.is_file():
        return []
    text = tasklist.read_text(encoding="utf-8")
    if find_incomplete_tasks(text):
        return []
    _, separator, retrospective = text.partition(RETROSPECTIVE_HEADING)
    if not separator:
        return [Violation(steering_dir.name, "C4", "「実装後の振り返り」セクションがありません")]
    placeholders = PLACEHOLDER_PATTERN.findall(retrospective)
    if not placeholders:
        return []
    return [
        Violation(
            steering_dir.name,
            "C4",
            f"振り返りにプレースホルダが{len(placeholders)}件残っています(先頭: {placeholders[0]})",
        )
    ]


def lint(project_root: Path) -> list[Violation]:
    """全ステアリングディレクトリにC1〜C4を適用し、違反を集約する。"""
    violations: list[Violation] = []
    for steering_dir in iter_steering_dirs(project_root):
        violations.extend(check_required_files(steering_dir))
        violations.extend(check_issue_url(steering_dir))
        violations.extend(check_incomplete_tasks(steering_dir))
        violations.extend(check_retrospective_placeholders(steering_dir))
    return violations


def main() -> int:
    project_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    violations = lint(project_root)
    if not violations:
        return 0
    print(f"steering lint: {len(violations)}件の違反があります")
    for v in violations:
        print(f"  [{v.check_id}] .steering/{v.directory}/: {v.message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
