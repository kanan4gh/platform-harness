"""add-feature、tasklistテンプレート、validatorの順序契約。

チェックボックスは実装・4段検証・振り返りの3フェーズだけに置き、
状態遷移・最終品質ゲート・PRは手順が管理する契約を固定する。
"""

import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
NEUTRAL = ROOT / "docs" / "procedures" / "add-feature.md"
CLAUDE_ADAPTER = ROOT / ".claude" / "commands" / "add-feature.md"
TEMPLATE = ROOT / "docs" / "procedures" / "templates" / "tasklist.md"
VALIDATOR = ROOT / "docs" / "procedures" / "validate-implementation.md"

STEP_HEADING_PATTERN = re.compile(r"^## ステップ([\d.]+)", re.MULTILINE)
TERMINATION_PATTERN = re.compile(r"全タスクが `\[x\]` になるまで")


def workflow_files() -> tuple[Path, Path]:
    """中立手順書とClaudeアダプタ。順序契約は両方に同一で存在する必要がある。"""
    return (NEUTRAL, CLAUDE_ADAPTER)


def step_section(path: Path, number: str) -> str:
    """`## ステップ{number}:` 見出しから次の `## ` 見出し直前までを切り出す。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    heading = f"## ステップ{number}:"
    starts = [i for i, line in enumerate(lines) if line.startswith(heading)]
    assert len(starts) == 1, f"{path.name}: {heading} が1つだけ存在するはず"
    start = starts[0]
    for end in range(start + 1, len(lines)):
        if lines[end].startswith("## "):
            return "\n".join(lines[start:end])
    return "\n".join(lines[start:])


def assert_in_order(text: str, markers: tuple[str, ...]) -> None:
    """markers が text 内でこの順に現れることを確認する。"""
    positions: list[int] = []
    for marker in markers:
        found = text.find(marker)
        assert found >= 0, f"{marker!r} が見つかりません"
        positions.append(found)
    assert positions == sorted(positions), f"順序が崩れています: {markers}"


def test_neutral_and_claude_adapter_share_the_same_step_sequence() -> None:
    sequences = [
        STEP_HEADING_PATTERN.findall(path.read_text(encoding="utf-8")) for path in workflow_files()
    ]
    assert sequences[0] == sequences[1]
    assert sequences[0] == ["0", "1", "2", "3", "4", "4.5", "5", "6", "7", "8"]


def test_step4_judges_whether_g3_acceptance_is_required() -> None:
    for path in workflow_files():
        plan = step_section(path, "4")
        assert "G3受け入れの要否判定" in plan
        assert "requirements.md" in plan
        assert "実施はステップ8-Bで行う" in plan or "判定結果を `requirements.md` に記録する" in plan
        # 判定はステアリング作成前に置き、tasklistのフェーズ分割規約も指示する
        assert "消化するステップごとに排他的に分割する" in plan

        approval = step_section(path, "4.5")
        assert "G3受け入れの要否判定" in approval


def test_step5_loop_consumes_the_implementation_phase_only() -> None:
    for path in workflow_files():
        step5 = step_section(path, "5")
        assert "実装フェーズの全タスクが `[x]` になるまで" in step5
        assert "このループが消化するのは実装フェーズだけで" in step5
        assert "4段検証フェーズ・振り返りとドキュメント更新フェーズ" in step5
        assert "それぞれステップ6 / 7が消化" in step5
        assert "ステップ5で先行して消化して" in step5
        # ループの進捗確認そのものが実装フェーズに限定されていること
        assert "**実装フェーズに**未完了タスク" in step5


def test_step5_has_no_unqualified_termination_condition() -> None:
    """ステップ5内の終了条件は、どの表現であっても実装フェーズに限定されている。"""
    for path in workflow_files():
        step5 = step_section(path, "5")
        occurrences = list(TERMINATION_PATTERN.finditer(step5))
        assert occurrences, f"{path.name}: ステップ5に終了条件の記述が必要"
        for match in occurrences:
            prefix = step5[max(0, match.start() - 12) : match.start()]
            assert "実装フェーズ" in prefix, (
                f"{path.name}: 無限定の終了条件が残っています: {step5[match.start() - 20:match.end()]!r}"
            )
        # 未完了タスクの有無を判定する行も実装フェーズに限定されていること
        checks = [line for line in step5.splitlines() if "未完了タスク" in line and "[ ]" in line]
        assert checks, f"{path.name}: 未完了タスクの判定行が必要"
        for line in checks:
            assert "実装フェーズ" in line, f"{path.name}: 無限定の判定行が残っています: {line!r}"


def test_step6_entry_condition_and_gate_phase_consumption() -> None:
    for path in workflow_files():
        step6 = step_section(path, "6")
        assert "実装フェーズの全タスクが `[x]` になったこと" in step6
        assert "このステップが消化するのは4段検証フェーズのチェックボックスである" in step6
        assert "段4の実行中に自分自身の行が `[ ]` であるのは正しい状態である" in step6
        # 終端ゲートをこのステップで前倒し実行しない契約
        assert "はこのステップでは実行しない" in step6
        # 旧・無限定の開始条件が残っていないこと
        assert "全タスク完了を確認してから" not in step6
        assert "全タスクが完了したことを最終確認" not in step6


def test_step7_consumes_the_retrospective_and_docs_phase() -> None:
    for path in workflow_files():
        step7 = step_section(path, "7")
        assert "このステップが消化するのは振り返りとドキュメント更新フェーズのチェックボックスである" in step7
        assert "全チェックボックスが`[x]`" in step7
        assert "steering_state.py finish" in step7
        assert "状態が`complete`" in step7


def test_step7_reviews_docs_it_updates_without_returning_to_step6() -> None:
    """ステップ7で更新したdocsは段3・段4を通っていないため、このステップ内でレビューする。"""
    for path in workflow_files():
        step7 = step_section(path, "7")
        assert "ステップ6の段3・段4のレビューを受けていない" in step7
        assert "review-docs" in step7 or "doc-reviewer" in step7
        assert "循環" in step7


def test_step8_keeps_the_default_flow_and_branches_only_for_g3() -> None:
    for path in workflow_files():
        step8 = step_section(path, "8")
        assert "ステップ4のG3受け入れ要否判定に従って分岐する" in step8
        assert "### ステップ8-A: G3不要の場合(既定)" in step8
        assert "### ステップ8-B: G3受け入れが必要な場合" in step8
        assert "--steering" in step8
        assert "現在のステアリング名" in step8
        assert "分岐内だけで行う" in step8
        # 8-A(既定)は終端ゲートを1回だけ実行する
        assert_in_order(
            step8,
            ("### ステップ8-A", "**最終ゲート**", "### ステップ8-B"),
        )
        default_branch = step8[
            step8.index("### ステップ8-A") : step8.index("### ステップ8-B")
        ]
        assert "1回実行" in default_branch
        assert "ゲート1回目" not in default_branch
        assert "ゲート2回目" not in default_branch


def test_step8b_defines_a_noncircular_g3_order() -> None:
    for path in workflow_files():
        step8 = step_section(path, "8")
        branch = step8[step8.index("### ステップ8-B") :]
        assert_in_order(
            branch,
            (
                "**候補ゲート**",
                "**候補コミット**",
                "**G3実施**",
                "**結果記録**",
                "**最終ゲート**",
                "**記録コミット**",
                "G3の判定結果を含める",
            ),
        )
        # 循環しない根拠と、やり直しの起点が明示されていること
        assert "製品ファイルを変更しない" in branch
        assert "1回で全緑" in branch
        assert "手順1(候補ゲート)からやり直す" in branch
        # 記録先は複製ではなく元リポジトリ側のステアリング
        assert "複製ではなく元リポジトリ側" in branch
        # 受け入れ記録はC3対象のチェックボックスにしない
        assert "コミット・PR作成・G3受け入れ記録" in step8
        assert "チェックボックスにしない" in step8


def test_step8b_retry_reruns_the_verification_stages() -> None:
    """G3不合格で製品ファイルを直した場合、4段検証を古い `[x]` のまま通過させない。"""
    for path in workflow_files():
        step8 = step_section(path, "8")
        branch = step8[step8.index("### ステップ8-B") :]
        assert "`active`へ戻し" in branch
        assert "影響を受ける段の行を`[ ]`へ戻す" in branch
        assert "ステップ6の該当段から再実行する" in branch


def test_step4_g3_criterion_excludes_prose_only_adapter_edits() -> None:
    """要否基準は「アダプタ構成・権限・フックの変更」であり、本文の書き換えは含まない。"""
    for path in workflow_files():
        plan = step_section(path, "4")
        assert "ハーネスのアダプタ構成・権限・フックを変更したか" in plan
        assert "手順記述だけを書き換えた変更" in plan


def test_template_phase_headings_declare_their_owning_step() -> None:
    text = TEMPLATE.read_text(encoding="utf-8")
    assert "### フェーズとadd-featureステップ" in text
    assert "消化するステップごとに排他的に分割する" in text
    assert "ステップ5の実装ループが消化するのは実装フェーズだけ" in text

    assert text.count("（実装フェーズ / ステップ5）") >= 1
    assert_in_order(
        text,
        (
            "（実装フェーズ / ステップ5）",
            "## フェーズ3: 4段検証（ステップ6）",
            "## フェーズ4: 振り返りとドキュメント更新（ステップ7）",
        ),
    )
    assert "最終品質ゲート（add-feature ステップ8で消化）" not in text


def test_template_verification_phase_lists_the_four_stages() -> None:
    text = TEMPLATE.read_text(encoding="utf-8")
    assert_in_order(
        text,
        (
            "- [ ] 段1: 静的検証",
            "- [ ] 段2: 実挙動検証",
            "- [ ] 段3: コードレビュー",
            "- [ ] 段4: スペック準拠検証",
        ),
    )


def test_template_keeps_procedural_actions_out_of_checkboxes() -> None:
    text = TEMPLATE.read_text(encoding="utf-8")
    checkbox_lines = [line for line in text.splitlines() if "- [ ]" in line]
    assert checkbox_lines, "テンプレートにチェックボックスが必要"
    for procedural_action in ("steering_state.py finish", "最終品質ゲート", "コミット", "PR作成"):
        assert all(procedural_action not in line for line in checkbox_lines)
    assert "steering_state.py finish" in text
    assert "最終品質ゲートを1回実行" in text


def test_validator_scopes_task_check_to_the_implementation_phase() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    assert "- **実装フェーズ**の全タスクが `[x]` になっているか" in text
    # 無限定の「全タスクが `[x]`」要求が残っていないこと
    assert "- 全タスクが `[x]` になっているか" not in text


def test_validator_does_not_flag_legitimately_pending_tasks() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    marker = "**検証時点で未完了が正当な後続タスク**"
    assert marker in text
    # 許容リストは、この宣言から次の見出しまでの箇条書きに閉じて確認する
    allow_list = text[text.index(marker) :].split("\n## ", maxsplit=1)[0]
    assert "乖離として報告しない" in allow_list
    for pending in (
        "段4(=本検証)の行",
        "段3(コードレビュー)の行",
        "振り返りとドキュメント更新フェーズ",
    ):
        assert pending in allow_list, f"許容リストに {pending} が必要"


def test_validator_flags_a_premature_complete_state() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    assert "状態が段4より前に`complete`へ変更された痕跡" in text
    assert "乖離として指摘する" in text


# --- U3: 段2の代替観察・確認方法・コミット単位・G3範囲・見本(neo#59 / neo#60) ---

HARNESS_ACCEPTANCE = ROOT / "docs" / "procedures" / "harness-acceptance.md"
REQUIREMENTS_TEMPLATE = ROOT / "docs" / "procedures" / "templates" / "requirements.md"
TEMPLATES_DIR = ROOT / "docs" / "procedures" / "templates"
EXAMPLE_DIR = ROOT / ".steering" / "example"
PR_TEMPLATE = ROOT / ".github" / "pull_request_template.md"


def stage2_section(path: Path) -> str:
    """ステップ6の `### 段2` 見出しから次の `### ` 見出し直前までを切り出す。"""
    step6 = step_section(path, "6")
    start = step6.index("### 段2")
    end = step6.index("### ", start + 1)
    return step6[start:end]


def test_stage2_replaces_skipping_with_alternative_observation() -> None:
    """検証支援機能がなくても段2をスキップせず、代替観察と未確認の記録で引き渡す。"""
    for path in workflow_files():
        stage2 = stage2_section(path)
        assert "画面のあるアプリ" in stage2
        assert "観察手段がない場合はスキップしない" in stage2
        assert "未確認" in stage2
        assert "人の確認が必要な項目" in stage2
        assert "段2の行を `[x]` にする条件" in stage2
        # スキップが許されるのは観察対象がない純ドキュメントだけ
        skip_lines = [line for line in stage2.splitlines() if "段2をスキップ" in line]
        assert skip_lines, f"{path.name}: 純ドキュメントのスキップ規定が必要"
        assert all("純ドキュメント" in line for line in skip_lines)


def test_claude_adapter_does_not_depend_on_a_specific_verify_skill() -> None:
    """特定のビルトインスキルへの依存が、検証漏れ(スキップ)の根本原因だった。"""
    text = CLAUDE_ADAPTER.read_text(encoding="utf-8")
    assert "Skill('verify')" not in text
    assert "`verify` / `code-review`" not in text
    assert "`Bash` で直接起動" in stage2_section(CLAUDE_ADAPTER)


def test_acceptance_criteria_verification_methods_are_planned_without_a_new_gate() -> None:
    for path in workflow_files():
        plan = step_section(path, "4")
        for method in ("自動テスト", "エージェントの実機操作", "人の確認"):
            assert method in plan, f"{path.name}: 確認方法 {method} が必要"
        assert "承認後の実行を止めない" in plan or "承認後の実行を止めず" in plan
        approval = step_section(path, "4.5")
        assert "受け入れ条件ごとの確認方法" in approval
        assert "新たな承認ゲートは設けない" in approval
        step8 = step_section(path, "8")
        assert "人の確認が必要な項目" in step8
        assert "マージ前の人の確認で不合格だった場合" in step8
    template = REQUIREMENTS_TEMPLATE.read_text(encoding="utf-8")
    assert "(確認方法:" in template
    assert "## 人の確認が必要な項目" in PR_TEMPLATE.read_text(encoding="utf-8")


def test_commit_unit_and_timing_match_between_procedure_and_adapter() -> None:
    for path in workflow_files():
        assert "ローカルコミット" in step_section(path, "5")
        assert "pushはステップ8まで行わない" in step_section(path, "5")
        step8 = step_section(path, "8")
        default_branch = step8[
            step8.index("### ステップ8-A") : step8.index("### ステップ8-B")
        ]
        g3_branch = step8[step8.index("### ステップ8-B") :]
        assert "**未コミットの変更すべて**" in default_branch
        assert "全変更をコミット" not in step8
        candidate = g3_branch[g3_branch.index("**候補コミット**") :].splitlines()[0]
        assert "未コミットの変更すべて" in candidate
        assert "HEAD" in candidate
    connection = HARNESS_ACCEPTANCE.read_text(encoding="utf-8")
    candidate = connection[connection.index("**候補コミット**") :].splitlines()[0]
    assert "未コミットの変更すべて" in candidate


def test_g3_criterion_enumerates_included_and_excluded_settings() -> None:
    """「ハーネス設定ファイル」の範囲を、含める / 含めないで具体化する。"""
    for path in workflow_files():
        plan = step_section(path, "4")
        assert "G3が観察する対象" in plan
        # 含める: 権限・フックの設定と、settings側のMCPサーバーの有効化・許可
        assert ".claude/settings.json" in plan
        assert "MCPサーバーの有効化・許可" in plan
        # 含めない: 品質ゲートが検証する開発ツール設定、MCPサーバー定義、サンプル
        assert "pyproject.toml" in plan
        assert "`.mcp.json`" in plan
        assert ".mcp.json.example" in plan
    neutral_plan = step_section(NEUTRAL, "4")
    assert "同じ基準" not in neutral_plan
    rollout = (ROOT / "docs" / "procedures" / "derived-project-rollout.md").read_text(
        encoding="utf-8"
    )
    assert "`add-feature.md`ステップ4の基準" in rollout


FULLWIDTH_ANNOTATION = re.compile(r"（.*$")
PLACEHOLDER = re.compile(r"\{[^{}\n]+\}")
PHASE_NUMBER = re.compile(r"^フェーズ\d+: ")


def heading_stems(text: str) -> list[str]:
    """`## ` 見出しの語幹。

    フェーズ見出しは番号だけを除き、消化ステップの注記(「（実装フェーズ / ステップ5）」等)を残す
    (注記まで除くと `{フェーズ名}` が任意の見出しに一致し、フェーズの欠落を検出できない)。
    それ以外の見出しは全角括弧の説明注記を除く。
    """
    stems: list[str] = []
    for line in text.splitlines():
        if not line.startswith("## "):
            continue
        heading = line[3:].strip()
        if PHASE_NUMBER.match(heading):
            stems.append(PHASE_NUMBER.sub("", heading))
        else:
            stems.append(FULLWIDTH_ANNOTATION.sub("", heading).strip())
    return stems


def test_example_steering_follows_the_current_templates() -> None:
    """見本はテンプレートの `##` 見出しを網羅する(実装フェーズの数・名前は自由)。"""
    for name in ("requirements.md", "design.md", "tasklist.md"):
        template_stems = heading_stems((TEMPLATES_DIR / name).read_text(encoding="utf-8"))
        example_text = (EXAMPLE_DIR / name).read_text(encoding="utf-8")
        example_stems = heading_stems(example_text)
        for stem in template_stems:
            pattern = re.compile(
                "".join(
                    ".+" if PLACEHOLDER.fullmatch(part) else re.escape(part)
                    for part in re.split(r"(\{[^{}\n]+\})", stem)
                    if part
                )
            )
            assert any(pattern.fullmatch(s) for s in example_stems), (
                f"example/{name} にテンプレートの見出し「{stem}」がない"
            )
        assert not PLACEHOLDER.search(example_text), f"example/{name} に未記入のプレースホルダ"


def test_example_tasklist_records_the_work_state_in_the_fixed_format() -> None:
    text = (EXAMPLE_DIR / "tasklist.md").read_text(encoding="utf-8")
    assert re.search(r"(?m)^- \*\*状態\*\*: (active|paused|complete)$", text)
    assert re.search(r"(?m)^- \*\*状態更新日時\*\*: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$", text)
    assert re.search(r"(?m)^- \*\*使用ハーネス\*\*: \S", text)
    assert "### フェーズとadd-featureステップ" in text
    assert "未確認" in text
