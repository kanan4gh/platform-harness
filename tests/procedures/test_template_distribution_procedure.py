"""Structural contracts for the canonical template distribution procedure."""

from pathlib import Path


ROOT = Path(__file__).parents[2]
PROCEDURE = ROOT / "docs" / "procedures" / "template-distribution.md"


def procedure_text() -> str:
    return PROCEDURE.read_text(encoding="utf-8")


def test_procedure_defers_repository_creation_until_after_merge_and_release() -> None:
    text = procedure_text()
    prohibition = text.index("この手順または配布生成機構を正典化するPRがマージされる前")
    merged_condition = text.index("正典化PRが`platform-harness`のdefault branchへマージ済み")
    release_condition = text.index("releaseとtagが作成済み")
    create_repository = text.index("gh repo create kanan4gh/platform-harness-template")

    assert prohibition < merged_condition < create_repository
    assert prohibition < release_condition < create_repository


def test_procedure_enables_new_template_before_disabling_canonical_template() -> None:
    text = procedure_text()
    enable_new = text.index(
        "gh api --method PATCH repos/kanan4gh/platform-harness-template "
        "-F is_template=true"
    )
    disable_old = text.index(
        "gh api --method PATCH repos/kanan4gh/platform-harness "
        "-F is_template=false"
    )

    assert enable_new < disable_old
    assert "旧設定を先に解除しない" in text


def test_procedure_covers_initial_update_and_rollback_without_history_rewrite() -> None:
    text = procedure_text()

    assert "## 初回公開" in text
    assert "## 継続更新" in text
    assert "## ロールバック" in text
    assert "git revert" in text
    assert "force-pushは使わない" in text
    assert "release tagの差し替え" in text


def test_procedure_requires_local_deterministic_and_tracking_evidence() -> None:
    text = procedure_text()

    assert "path、内容、実行bitが一致" in text
    assert "uv run python3 scripts/local_quality_gate.py --steering <fixture名>" in text
    assert "通常の`git add -A`でindexへ入る" in text
    assert "GitHub Actions自動run: 0件" in text
    assert "従量課金LLM headless mode: 0件" in text


def test_procedure_initializes_safe_parameters_and_shows_initial_push() -> None:
    text = procedure_text()
    parameters = text.index("## 実行パラメータ")
    preflight = text.index("## 共通preflight")
    first_tag_use = text.index('refs/tags/${SOURCE_TAG}^{commit}')

    assert parameters < preflight < first_tag_use
    assert "SOURCE_TAG=vX.Y.Z" in text
    assert (
        "PUBLISH_ROOT=$(mktemp -d "
        "/private/tmp/platform-harness-template-publish.XXXXXX)" in text
    )
    assert 'checkout --detach "refs/tags/${SOURCE_TAG}"' in text
    assert (
        'git -C "${PUBLISHER_CHECKOUT}" rev-parse --verify '
        '"refs/tags/${SOURCE_TAG}^{commit}"' in text
    )
    assert (
        'git -C "${PUBLISHER_CHECKOUT}" status '
        "--porcelain --untracked-files=all" in text
    )
    assert 'git -C "${DISTRIBUTION_OUTPUT}" init -b main' in text
    assert "https://github.com/kanan4gh/platform-harness-template.git" in text
    assert 'git -C "${DISTRIBUTION_OUTPUT}" push -u origin main' in text
