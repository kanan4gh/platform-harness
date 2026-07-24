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
