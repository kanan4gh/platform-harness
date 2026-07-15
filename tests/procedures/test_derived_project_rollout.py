"""Structural contracts for the derived-project rollout catalog and procedure."""

from pathlib import Path
import re

ROOT = Path(__file__).parents[2]
CATALOG = ROOT / "docs" / "derived-projects.md"
PROCEDURE = ROOT / "docs" / "procedures" / "derived-project-rollout.md"
CATALOG_COLUMNS = (
    "Remote",
    "Repository URL",
    "Lineage evidence",
    "Harness generation",
    "Strategy",
    "Priority",
    "State",
    "Last source",
    "Last inspected",
    "Local caution",
    "Decision / next action",
)


def catalog_text() -> str:
    return CATALOG.read_text(encoding="utf-8")


def procedure_text() -> str:
    return PROCEDURE.read_text(encoding="utf-8")


def catalog_rows() -> list[dict[str, str]]:
    section = catalog_text().split("## 展開候補", maxsplit=1)[1].split(
        "## 重複ローカルコピーの除外", maxsplit=1
    )[0]
    lines = [line for line in section.splitlines() if line.startswith("|")]
    headers = tuple(cell.strip() for cell in lines[0].strip("|").split("|"))
    assert headers == CATALOG_COLUMNS
    return [
        dict(zip(headers, (cell.strip() for cell in line.strip("|").split("|")), strict=True))
        for line in lines[2:]
    ]


def outfit_manifest() -> dict[str, str]:
    section = procedure_text().split("### 初期manifest", maxsplit=1)[1].split(
        "### 移行順序", maxsplit=1
    )[0]
    lines = [line for line in section.splitlines() if line.startswith("|")]
    return {
        cells[0]: cells[1]
        for line in lines[2:]
        if len(cells := [cell.strip() for cell in line.strip("|").split("|")]) == 2
    }


def test_catalog_uses_remote_as_unique_key_and_defines_classifications() -> None:
    text = catalog_text()
    assert "一意キーは`OWNER/REPOSITORY`形式のGitHub remote" in text
    for value in ("direct-sync", "migrate-then-sync", "decision-required", "excluded"):
        assert value in text
    for field in ("Last source", "Last inspected", "Local caution", "Decision / next action"):
        assert field in text


def test_every_catalog_row_has_unique_remote_and_required_values() -> None:
    rows = catalog_rows()
    remotes = [row["Remote"].strip("`") for row in rows]
    assert len(remotes) == len(set(remotes))
    assert all(re.fullmatch(r"[\w.-]+/[\w.-]+", remote) for remote in remotes)
    assert all(
        row["Repository URL"] == f"https://github.com/{remote}"
        for row, remote in zip(rows, remotes, strict=True)
    )

    allowed_generations = {
        "`current-neutral`",
        "`legacy-platform-claude`",
        "`legacy-sdd`",
        "`distribution-asset`",
    }
    allowed_strategies = {
        "`direct-sync`",
        "`migrate-then-sync`",
        "`decision-required`",
        "`excluded`",
    }
    allowed_states = {
        "`candidate`",
        "`approved`",
        "`planned`",
        "`in-progress`",
        "`verified`",
        "`synced`",
        "`on-hold`",
        "`decision-required`",
        "`excluded`",
    }
    assert all(row["Harness generation"] in allowed_generations for row in rows)
    assert all(row["Strategy"] in allowed_strategies for row in rows)
    assert all(row["State"] in allowed_states for row in rows)
    last_source_pattern = re.compile(
        r"^`(?:none|unknown \(investigate\)|v\d+\.\d+\.\d+ / [0-9a-f]{7,40})`$"
    )
    assert all(last_source_pattern.fullmatch(row["Last source"]) for row in rows)
    assert all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["Last inspected"]) for row in rows)
    for row in rows:
        for field in ("Lineage evidence", "Last source", "Local caution", "Decision / next action"):
            assert row[field]


def test_catalog_defines_state_model_and_on_demand_boundary() -> None:
    text = catalog_text()
    for state in ("candidate", "approved", "planned", "in-progress", "verified", "synced"):
        assert state in text
    assert "ユーザーが対象remoteを明示" in text
    assert "候補登録だけで展開を開始しない" in text
    assert "複数remoteへの一括Issue・一括branch・一括PRも作らない" in text
    assert "`on-hold`は阻害要因をG0で裁定・解消" in text
    assert "`decision-required`は人の裁定を記録" in text
    assert "履歴を確定できない場合を`unknown (investigate)`" in text


def test_catalog_contains_initial_candidates_and_priorities() -> None:
    text = catalog_text()
    expected = (
        "kanan4gh/project-uroboros-neo",
        "kanan4gh/outfit-studio",
        "kanan4gh/dev-tasks2-py",
        "kanan4gh/agentcore-work",
        "kanan4gh/dev-tasks2",
        "kanan4gh/project-ouroboros",
        "kanan4gh/platform-harness-engineering",
    )
    assert all(remote in text for remote in expected)
    assert re.search(r"project-uroboros-neo.*`direct-sync`.*P0", text)
    assert re.search(r"outfit-studio.*`direct-sync`.*P0", text)


def test_catalog_does_not_duplicate_operated_outfit_remote() -> None:
    text = catalog_text()
    rows = [line for line in text.splitlines() if line.startswith("| `kanan4gh/outfit-studio`")]
    assert len(rows) == 1
    assert "/Users/akiraishihara/aiwork/operated/outfit-studio" in text
    assert "運用コピー" in text


def test_catalog_records_completed_outfit_v1_3_0_rollout() -> None:
    rows = catalog_rows()
    outfit_rows = [row for row in rows if row["Remote"] == "`kanan4gh/outfit-studio`"]
    assert len(outfit_rows) == 1
    row = outfit_rows[0]
    assert row["Harness generation"] == "`current-neutral`"
    assert row["Strategy"] == "`direct-sync`"
    assert row["State"] == "`synced`"
    assert row["Last source"] == "`v1.3.0 / bd2cd8c`"
    assert "PR #26" in row["Lineage evidence"]
    assert "PR #22は不要としてclose" in row["Decision / next action"]
    assert "PR #26" in row["Decision / next action"]
    assert "clean clone / worktree" in row["Local caution"]


def test_procedure_defines_unit_preflight_and_manifest() -> None:
    text = procedure_text()
    assert "1 platform-harness release × 1 GitHub remote × 1 feature branch × 1 PR" in text
    for value in (
        "対象remote",
        "default branch / OID",
        "dirty / ahead / behind",
        "同期元: platform-harness",
        "作業隔離",
    ):
        assert value in text
    for category in (
        "Preserve",
        "Replace from canonical",
        "Add from canonical",
        "Merge manually",
        "Exclude",
    ):
        assert category in text


def test_preflight_fixes_remote_freshness_and_concurrency_contracts() -> None:
    text = procedure_text()
    for contract in (
        "archive / template状態",
        "remote-tracking refをfetchした日時・方法とcommit OID",
        "active Issue / PR / branch",
        "同期元platform-harness release tagとcommit",
        "clean worktreeまたはclean clone",
    ):
        assert contract in text
    assert "G0で既存PRをマージする、破棄する、新移行へ引き継ぐ" in text
    assert "引継ぎを選んだ後のファイル単位の統合方法だけをG2" in text


def test_procedure_defines_bootstrap_authority_and_handoff() -> None:
    text = procedure_text()
    assert "旧Claude専用ハーネスの通常実行者はClaude Code" in text
    assert "ユーザーがG0とG1で承認した本展開手順" in text
    assert "bootstrap executor" in text
    assert "旧ハーネスを実行したことにしない" in text
    assert "Authority handoff" in text
    assert "新しい`AGENTS.md`と対象エージェント用アダプタ" in text


def test_procedure_protects_dirty_worktrees_and_target_history() -> None:
    text = procedure_text()
    assert "dirtyな既存checkoutを清掃・stash・上書きして移行を始めない" in text
    assert "clean worktreeまたはclean clone" in text
    assert "対象リポジトリ内に独立Issue・steering・feature branch" in text
    assert "プロダクト固有層、技術スタック固有層" in text


def test_outfit_pilot_defines_legacy_state_isolation_and_mapping() -> None:
    text = procedure_text()
    assert "UPDATED: 2026-05-27" in text
    assert "`AGENTS.md`、中立`docs/procedures/`、`.agents/`、`.codex/`、`.kiro/`" in text
    assert "feature/sync-platform-harness-v1-2-0" in text
    assert "/Users/akiraishihara/aiwork/operated/outfit-studio" in text
    assert "preflight・編集・同期対象から除外" in text
    assert "open PR #22" in text
    assert "状態は`on-hold`" in text
    assert "`.devcontainer/devcontainer-lock.json`" in text
    assert "既存テスト中のCodexサービスをCodex CLIアダプタと同じ概念として置換しない" in text
    isolation = text.split("### 隔離戦略", maxsplit=1)[1].split("### 初期manifest", maxsplit=1)[0]
    assert isolation.index("独立Issueを作成") < isolation.index("feature/sync-platform-harness")
    assert isolation.index("feature/sync-platform-harness") < isolation.index("Issue URLを含む")


def test_outfit_manifest_defines_concrete_non_overlapping_boundaries() -> None:
    text = procedure_text()
    for contract in (
        "`src/`、`tests/conftest.py`、`tests/integration/`、`tests/unit/`",
        "`docs/{architecture,development-guidelines,functional-design,glossary,product-requirements,repository-structure}.md`",
        "`CLAUDE.md`の「汎用層」「補足：この文書の運用方法」section",
        "`CLAUDE.md`の「プロジェクトメモリ」section",
        "`.claude/commands/{add-feature,review-docs,setup-project}.md`",
        "`.claude/skills/steering/`",
        "`AGENTS.md`、`docs/procedures/`",
        "`.claude/skills/`のうち`steering/`以外",
        "再生成可能な`.devcontainer/devcontainer-lock.json`",
        "各具体pathまたは明示した文書sectionをちょうど1分類",
    ):
        assert contract in text

    assert outfit_manifest() == {
        "Preserve": "`src/`、`tests/conftest.py`、`tests/integration/`、`tests/unit/`、"
        "`docs/{architecture,development-guidelines,functional-design,glossary,"
        "product-requirements,repository-structure}.md`、`CLAUDE.md`の"
        "「プロダクト固有層」「技術スタック固有層」section",
        "Replace from canonical": "`CLAUDE.md`の「汎用層」「補足：この文書の運用方法」section、"
        "`.claude/commands/{add-feature,review-docs,setup-project}.md`、"
        "`.claude/skills/steering/`と旧steering templates",
        "Add from canonical": "`AGENTS.md`、`docs/procedures/`とtemplates、`.agents/skills/`、"
        "`.codex/`（`hooks/state/`を除く）、`.kiro/`（`hooks/state/`を除く）、"
        "`scripts/{steering_lint,metered_automation_lint,"
        "local_quality_gate}.py`、対応する`tests/{adapters,hooks,lint,procedures,"
        "scripts}/`のうち対象に存在しないpath",
        "Merge manually": "`CLAUDE.md`の「プロジェクトメモリ」section、"
        "`.claude/settings.json`、`.claude/README.md`、`.claude/agents/`、"
        "`.claude/skills/`のうち`steering/`以外、`.claude/hooks/*.py`、"
        "`docs/ideas/harness-engineering.md`、`.gitignore`、`pyproject.toml`、"
        "`uv.lock`、`.devcontainer/devcontainer.json`、"
        "`.devcontainer/postCreate.sh`、`.mcp.json.example`",
        "Exclude": "`.coverage`、`.playwright-mcp/`、`.claude/hooks/state/`、"
        "`.codex/hooks/state/`、`.kiro/hooks/state/`、`**/__pycache__/`、"
        "再生成可能な`.devcontainer/devcontainer-lock.json`",
    }


def test_procedure_requires_local_and_interactive_validation_without_paid_automation() -> None:
    text = procedure_text()
    assert "local_quality_gate.py" in text
    assert "人がIDEまたは対話型CLI受け入れ" in text
    assert "GitHub Actions自動runと有料LLM headless mode起動が0件" in text
    assert "従量課金型headless mode" in text


def test_platform_issue_does_not_modify_derived_project() -> None:
    text = procedure_text()
    assert "outfit-studio本体を変更しない" in text
    assert "実展開はoutfit-studio側の独立Issue" in text
