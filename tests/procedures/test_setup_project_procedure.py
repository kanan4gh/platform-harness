"""setup-project手順書と、各ハーネスのアダプタ・prd-writingスキルの整合を検証する。

手順書が正であり、作業単位(ブランチ・コミット・PR)、承認済みドキュメントの訂正、
入力がない場合の聞き取り(プロジェクトの目的を含む)、空テンプレートの扱いを
アダプタとスキルが同じ内容で持つことを固定する。
"""

import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
PROCEDURE = ROOT / "docs" / "procedures" / "setup-project.md"
CLAUDE_ADAPTER = ROOT / ".claude" / "commands" / "setup-project.md"
CODEX_ADAPTER = ROOT / ".agents" / "skills" / "setup-project" / "SKILL.md"
KIRO_ADAPTER = ROOT / ".kiro" / "skills" / "setup-project" / "SKILL.md"
PRD_SKILL = ROOT / ".claude" / "skills" / "prd-writing" / "SKILL.md"
PRD_TEMPLATE = ROOT / ".claude" / "skills" / "prd-writing" / "template.md"

# 手順書とClaudeアダプタの両方に同じ文言で存在すべき節見出し(見出しレベルは問わない)
SHARED_HEADINGS = (
    "作業単位(ブランチ・コミット・PR)",
    "ステップ0: 作業ブランチの作成とインプットの読み込み",
    "承認ゲート(全ドキュメント共通)",
    "承認済みドキュメントの訂正",
    "ステップ7: 品質ゲートとPR",
    "完了条件",
)

INTERVIEW_ITEMS = (
    "プロジェクトの目的",
    "解決したい課題",
    "ターゲットユーザー",
    "主要機能",
    "MVPの範囲",
)

HEADING_PATTERN = re.compile(r"^#{2,4} (.+)$", re.MULTILINE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def headings(text: str) -> list[str]:
    return [match.strip() for match in HEADING_PATTERN.findall(text)]


def section(text: str, heading: str) -> str:
    """見出し `heading` から、同じかより上位の次の見出しの直前までを返す。"""
    lines = text.splitlines()
    for start, line in enumerate(lines):
        match = re.match(r"^(#{2,4}) (.+)$", line)
        if match and match.group(2).strip() == heading:
            level = len(match.group(1))
            for end in range(start + 1, len(lines)):
                other = re.match(r"^(#{1,4}) ", lines[end])
                if other and len(other.group(1)) <= level:
                    return "\n".join(lines[start:end])
            return "\n".join(lines[start:])
    raise AssertionError(f"見出しがない: {heading}")


def assert_in_order(text: str, markers: tuple[str, ...]) -> None:
    position = -1
    for marker in markers:
        found = text.find(marker, position + 1)
        assert found > position, f"順序が崩れている、または存在しない: {marker}"
        position = found


def test_procedure_and_claude_adapter_share_sections() -> None:
    for path in (PROCEDURE, CLAUDE_ADAPTER):
        found = headings(read(path))
        for heading in SHARED_HEADINGS:
            assert heading in found, f"{path.name}: {heading}"


def test_work_unit_defines_branch_commit_pr_and_exception() -> None:
    for path in (PROCEDURE, CLAUDE_ADAPTER):
        work_unit = section(read(path), "作業単位(ブランチ・コミット・PR)")
        assert "feature/setup-project" in work_unit
        assert "mainへ直接コミットしない" in work_unit
        assert "承認」された文書ごとに1コミット" in work_unit
        assert "スキップ" in work_unit
        assert "ユーザーに確認してからpush" in work_unit
        # Issue・ステアリングを作らないことと、規約の例外であること、その理由
        assert "GitHub Issueとステアリング(`.steering/`)を作らない" in work_unit
        assert "規約の例外" in work_unit
        assert "初期化" in work_unit


def test_correction_requires_approval_before_edit_and_separate_commit() -> None:
    for path in (PROCEDURE, CLAUDE_ADAPTER):
        correction = section(read(path), "承認済みドキュメントの訂正")
        assert "承認を求める前に、承認済みドキュメントを編集しない" in correction
        assert "独立のコミット" in correction
        assert "訂正対象のファイルだけ" in correction
        assert "見送った訂正" in correction
        assert_in_order(
            correction,
            ("訂正案", "訂正を承認する", "承認された場合だけ編集", "独立のコミット"),
        )


def test_step0_has_interview_path_with_project_purpose() -> None:
    for path in (PROCEDURE, CLAUDE_ADAPTER):
        step0 = section(read(path), "ステップ0: 作業ブランチの作成とインプットの読み込み")
        assert "対話形式で要求を聞き取る" in step0
        assert "docs/ideas/initial-requirements.md" in step0
        for item in INTERVIEW_ITEMS:
            assert item in step0, f"{path.name}: {item}"
        assert "プロダクト以外の目的" in step0
        # 未コミットの入力を引き継ぐため、作業ツリー分離は使わない
        assert "作業ツリー分離" in step0
        assert "は使わない" in step0


def test_empty_template_is_not_treated_as_existing_document() -> None:
    for path in (PROCEDURE, CLAUDE_ADAPTER, PRD_SKILL):
        text = read(path)
        assert "HTMLコメント" in text, path.name
        assert "新規作成として扱" in text, path.name
        assert "配布時のテンプレートから変更されていない" in text, path.name


def test_step7_runs_gate_without_steering_and_confirms_before_push() -> None:
    for path in (PROCEDURE, CLAUDE_ADAPTER):
        step7 = section(read(path), "ステップ7: 品質ゲートとPR")
        assert "local_quality_gate.py" in step7
        assert "`--steering` を付けずに" in step7
        assert "完了検査の対象がない" in step7
        assert "見送った訂正" in step7
        assert "1を再実行" in step7
        assert_in_order(
            step7, ("local_quality_gate.py", "可否を", "承認されたらブランチをpush")
        )
        assert "ブランチを残す" in step7


def test_claude_adapter_declares_its_differences() -> None:
    declaration = read(CLAUDE_ADAPTER).split("\n\n")[2]
    assert "docs/procedures/setup-project.md" in declaration
    assert "AskUserQuestion" in declaration
    assert "スキルロード" in declaration


def test_codex_and_kiro_adapters_follow_the_whole_procedure() -> None:
    for path in (CODEX_ADAPTER, KIRO_ADAPTER):
        text = read(path)
        assert "docs/procedures/setup-project.md" in text
        assert "ステップ0〜7" in text
        assert "作業単位" in text
        assert "承認済みドキュメントの訂正" in text


def test_codex_adapter_note_has_no_undistributed_plan_reference() -> None:
    text = read(CODEX_ADAPTER)
    # 「換装第6弾」は配布物に含まれないdocs/ideas/の用語
    assert "第6弾" not in text
    assert "置き場所だけがClaude側" in text
    assert "ハーネス中立" in text


def test_prd_skill_does_not_require_initial_requirements_file() -> None:
    text = read(PRD_SKILL)
    assert "作成されている必要があります" not in text
    assert "docs/procedures/setup-project.md" in text
    assert "対話形式で要求を聞き取ります" in text
    for item in ("プロジェクトの目的", "ターゲットユーザー", "主要機能", "MVPの範囲"):
        assert item in text
    assert "プロダクト以外の目的" in text


def test_prd_template_has_project_purpose_and_its_metrics() -> None:
    names = headings(read(PRD_TEMPLATE))
    assert "プロジェクトの目的(プロダクト以外を含む)" in names
    assert "プロジェクトの目的の達成指標" in names
