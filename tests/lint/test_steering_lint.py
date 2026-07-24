"""steering_lint.py(ステアリング規律lint)のユニットテスト。"""

import importlib.util
import subprocess
import sys
from pathlib import Path

LINT_PATH = Path(__file__).parents[2] / "scripts" / "steering_lint.py"

spec = importlib.util.spec_from_file_location("steering_lint", LINT_PATH)
assert spec is not None and spec.loader is not None
lint_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint_mod)

ISSUE_URL = "https://github.com/example/repo/issues/1"

COMPLETE_TASKLIST = """# タスクリスト

- [x] done

## 実装後の振り返り

### 実装完了日
2026-07-14

### 学んだこと
- 具体的な学び
"""

REQUIREMENTS = f"""# 要求内容

関連Issue: {ISSUE_URL}
"""


def make_steering(
    tmp_path: Path,
    dirname: str,
    requirements: str | None = REQUIREMENTS,
    design: str | None = "# 設計書\n",
    tasklist: str | None = COMPLETE_TASKLIST,
) -> Path:
    d = tmp_path / ".steering" / dirname
    d.mkdir(parents=True)
    if requirements is not None:
        (d / "requirements.md").write_text(requirements, encoding="utf-8")
    if design is not None:
        (d / "design.md").write_text(design, encoding="utf-8")
    if tasklist is not None:
        (d / "tasklist.md").write_text(tasklist, encoding="utf-8")
    return d


def check_ids(violations: list) -> set[str]:
    return {v.check_id for v in violations}


# --- 正常系 ---


def test_clean_steering_has_no_violations(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260714-foo")
    assert lint_mod.lint(tmp_path) == []


def test_no_steering_dir_has_no_violations(tmp_path: Path) -> None:
    assert lint_mod.lint(tmp_path) == []


def test_non_dated_dirs_are_ignored(tmp_path: Path) -> None:
    # example/ 等の規約外ディレクトリは全チェックの対象外
    make_steering(tmp_path, "example", requirements="no url", tasklist="- [ ] x\n")
    assert lint_mod.lint(tmp_path) == []


def test_plain_files_in_steering_are_ignored(tmp_path: Path) -> None:
    (tmp_path / ".steering").mkdir()
    (tmp_path / ".steering" / "distill-20260709.md").write_text("- [ ] x\n", encoding="utf-8")
    assert lint_mod.lint(tmp_path) == []


# --- C1: 3ファイル存在 ---


def test_c1_missing_files_detected(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260714-foo", design=None, tasklist=None)
    violations = lint_mod.lint(tmp_path)
    assert [v.check_id for v in violations] == ["C1", "C1"]
    assert "design.md" in violations[0].message
    assert "tasklist.md" in violations[1].message


# --- C1: 軽量パス宣言による design.md 省略 ---

LIGHTWEIGHT_REQUIREMENTS = f"""# 要求内容

- **関連Issue**: {ISSUE_URL}
- **軽量パス**: 適用
"""


def test_c1_lightweight_declaration_allows_missing_design(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260716-foo", requirements=LIGHTWEIGHT_REQUIREMENTS, design=None)
    assert lint_mod.lint(tmp_path) == []


def test_c1_lightweight_declaration_with_design_present_is_allowed(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260716-foo", requirements=LIGHTWEIGHT_REQUIREMENTS)
    assert lint_mod.lint(tmp_path) == []


def test_c1_no_declaration_still_requires_design(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260716-foo", design=None)
    assert check_ids(lint_mod.lint(tmp_path)) == {"C1"}


def test_c1_non_applied_declaration_still_requires_design(tmp_path: Path) -> None:
    # 「非適用」「適用外」を宣言と誤判定しない(行末アンカーで担保)
    for i, value in enumerate(("非適用", "適用外")):
        d = tmp_path / f"case{i}"
        requirements = f"# 要求内容\n\n- 関連Issue: {ISSUE_URL}\n- **軽量パス**: {value}\n"
        make_steering(d, "20260716-foo", requirements=requirements, design=None)
        assert check_ids(lint_mod.lint(d)) == {"C1"}


def test_c1_declaration_with_trailing_text_is_not_recognized(tmp_path: Path) -> None:
    # 宣言行は「適用」で行を完結させる仕様(テンプレートに明記)。
    # 後続テキストがあると宣言と見なされないことを回帰テストで固定する。
    requirements = (
        f"# 要求内容\n\n- 関連Issue: {ISSUE_URL}\n"
        "- **軽量パス**: 適用。基準4項目をすべて満たすため\n"
    )
    make_steering(tmp_path, "20260716-foo", requirements=requirements, design=None)
    assert check_ids(lint_mod.lint(tmp_path)) == {"C1"}


def test_c1_missing_requirements_not_excused_by_lightweight(tmp_path: Path) -> None:
    # requirements.md 自体の欠落は宣言判定以前の問題として従来どおり報告する
    make_steering(tmp_path, "20260716-foo", requirements=None, design=None)
    violations = lint_mod.lint(tmp_path)
    assert [v.check_id for v in violations] == ["C1", "C1"]
    assert "requirements.md" in violations[0].message
    assert "design.md" in violations[1].message


# --- C2: Issue URL ---


def test_c2_missing_issue_url_detected(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260714-foo", requirements="# 要求内容\nIssueなし\n")
    assert check_ids(lint_mod.lint(tmp_path)) == {"C2"}


def test_c2_not_reported_when_requirements_missing(tmp_path: Path) -> None:
    # ファイル欠落はC1が報告し、C2は重複報告しない
    make_steering(tmp_path, "20260714-foo", requirements=None)
    assert check_ids(lint_mod.lint(tmp_path)) == {"C1"}


# --- C3: 未完了タスク ---


def test_c3_incomplete_tasks_detected(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260714-foo", tasklist="- [x] done\n- [ ] not yet\n- [ ] more\n")
    violations = [v for v in lint_mod.lint(tmp_path) if v.check_id == "C3"]
    assert len(violations) == 1
    assert "2件" in violations[0].message
    assert "not yet" in violations[0].message


def test_c3_checks_all_dirs_not_only_latest(tmp_path: Path) -> None:
    # フック(最新のみ)と異なり、lintは全ディレクトリを検査する
    make_steering(tmp_path, "20260101-old", tasklist="- [ ] old incomplete\n")
    make_steering(tmp_path, "20260714-new")
    violations = [v for v in lint_mod.lint(tmp_path) if v.check_id == "C3"]
    assert len(violations) == 1
    assert violations[0].directory == "20260101-old"


# --- has_completed_tasks(Stopフックの未着手判定ヘルパ) ---


def test_has_completed_tasks_detects_lowercase() -> None:
    assert lint_mod.has_completed_tasks("- [x] done\n- [ ] not yet\n") is True


def test_has_completed_tasks_detects_uppercase() -> None:
    assert lint_mod.has_completed_tasks("- [X] done\n") is True


def test_has_completed_tasks_detects_skipped_notation() -> None:
    assert lint_mod.has_completed_tasks("- [x] ~~タスク~~（理由: 方針変更）\n") is True


def test_has_completed_tasks_false_when_all_incomplete() -> None:
    assert lint_mod.has_completed_tasks("- [ ] a\n- [ ] b\n") is False


def test_has_completed_tasks_false_when_empty() -> None:
    assert lint_mod.has_completed_tasks("") is False


# --- strip_code_fences(フェンス除去の前処理) ---


def test_strip_code_fences_blanks_fenced_lines_and_keeps_line_count() -> None:
    text = "before\n```\ninside\n```\nafter\n"
    assert lint_mod.strip_code_fences(text) == "before\n\n\n\nafter\n"


def test_strip_code_fences_keeps_text_without_fences() -> None:
    text = "- [x] done\n- [ ] todo\n"
    assert lint_mod.strip_code_fences(text) == text


def test_strip_code_fences_handles_indented_fence() -> None:
    text = "- タスク\n  ```\n  - [x] example\n  ```\n- [x] real\n"
    assert "example" not in lint_mod.strip_code_fences(text)
    assert "- [x] real" in lint_mod.strip_code_fences(text)


# --- コードフェンス内の例示を完了タスクと数えない ---


def test_has_completed_tasks_ignores_backtick_fence() -> None:
    assert lint_mod.has_completed_tasks("```\n- [x] example\n```\n") is False


def test_has_completed_tasks_ignores_tilde_fence() -> None:
    assert lint_mod.has_completed_tasks("~~~\n- [x] example\n~~~\n") is False


def test_has_completed_tasks_ignores_fence_with_info_string() -> None:
    assert lint_mod.has_completed_tasks("```markdown\n- [x] example\n```\n") is False


def test_has_completed_tasks_detects_task_after_closing_fence() -> None:
    text = "```markdown\n- [x] example\n```\n- [x] real task\n"
    assert lint_mod.has_completed_tasks(text) is True


def test_has_completed_tasks_ignores_shorter_fence_inside_longer_one() -> None:
    # 終了フェンスは開始と同じ長さ以上であることを要する(内側の``` では閉じない)
    text = "````\n```\n- [x] example\n```\n````\n"
    assert lint_mod.has_completed_tasks(text) is False


def test_has_completed_tasks_ignores_different_marker_as_closer() -> None:
    # チルダで開いたフェンスはバッククォートでは閉じない
    text = "~~~\n```\n- [x] example\n"
    assert lint_mod.has_completed_tasks(text) is False


def test_has_completed_tasks_unclosed_fence_does_not_raise() -> None:
    # 閉じられていないフェンスは以降を例示扱いにして終了する(安全側=未着手)
    assert lint_mod.has_completed_tasks("```\n- [x] example\n") is False


def test_c3_still_detects_incomplete_task_inside_fence(tmp_path: Path) -> None:
    # 非対称性の固定: C3はフェンスを除外しない(未完了を隠す抜け穴を作らないため)
    make_steering(tmp_path, "20260714-foo", tasklist="```\n- [ ] example\n```\n")
    violations = [v for v in lint_mod.lint(tmp_path) if v.check_id == "C3"]
    assert len(violations) == 1


# --- 実テンプレートの回帰(作りたての標準tasklistは未着手と判定される) ---

TEMPLATE_TASKLIST = Path(__file__).parents[2] / "docs" / "procedures" / "templates" / "tasklist.md"


def test_template_tasklist_is_unstarted() -> None:
    """テンプレートにスキップ記法の例示が戻っても未着手判定が壊れないことを固定する。

    例示 `- [x] ~~タスク名~~` はコードフェンス内にあり、完了タスクとして数えてはならない。
    数えてしまうと、計画承認待ちの未着手tasklistにStopフックが割り込む。
    """
    text = TEMPLATE_TASKLIST.read_text(encoding="utf-8")
    assert lint_mod.has_completed_tasks(text) is False


def test_template_tasklist_has_incomplete_tasks() -> None:
    """同じテンプレートに対し、C3は従来どおり未完了タスクを検出する。"""
    text = TEMPLATE_TASKLIST.read_text(encoding="utf-8")
    assert len(lint_mod.find_incomplete_tasks(text)) > 0


# --- C4: 振り返りプレースホルダ ---


def test_c4_placeholder_in_retrospective_detected(tmp_path: Path) -> None:
    tasklist = "- [x] done\n\n## 実装後の振り返り\n\n### 実装完了日\n{YYYY-MM-DD}\n"
    make_steering(tmp_path, "20260714-foo", tasklist=tasklist)
    violations = [v for v in lint_mod.lint(tmp_path) if v.check_id == "C4"]
    assert len(violations) == 1
    assert "{YYYY-MM-DD}" in violations[0].message


def test_c4_missing_retrospective_section_detected(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260714-foo", tasklist="- [x] done\n")
    violations = [v for v in lint_mod.lint(tmp_path) if v.check_id == "C4"]
    assert len(violations) == 1
    assert "セクションがありません" in violations[0].message


def test_c4_skipped_while_tasks_incomplete(tmp_path: Path) -> None:
    # 作業中(C3違反あり)の間はC4を報告しない(C3に委ねる)
    tasklist = "- [ ] wip\n\n## 実装後の振り返り\n\n{YYYY-MM-DD}\n"
    make_steering(tmp_path, "20260714-foo", tasklist=tasklist)
    assert check_ids(lint_mod.lint(tmp_path)) == {"C3"}


def test_c4_braces_outside_retrospective_are_ignored(tmp_path: Path) -> None:
    # 本文中のコード片({"count": 0} 等)はセクション限定により誤検出しない
    tasklist = (
        '- [x] done ({"count": 0} を保存)\n\n## 実装後の振り返り\n\n### 実装完了日\n2026-07-14\n'
    )
    make_steering(tmp_path, "20260714-foo", tasklist=tasklist)
    assert lint_mod.lint(tmp_path) == []


# --- CLI ---


def run_cli(project_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LINT_PATH), str(project_root)],
        capture_output=True,
        text=True,
    )


def test_cli_exit_zero_when_clean(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260714-foo")
    proc = run_cli(tmp_path)
    assert proc.returncode == 0
    assert proc.stdout == ""


def test_cli_exit_one_with_report_on_violation(tmp_path: Path) -> None:
    make_steering(tmp_path, "20260714-foo", tasklist="- [ ] x\n")
    proc = run_cli(tmp_path)
    assert proc.returncode == 1
    assert "[C3]" in proc.stdout
    assert "20260714-foo" in proc.stdout
