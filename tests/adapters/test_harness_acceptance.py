"""対話型ハーネス受け入れ手順の安全境界を検証する。"""

from pathlib import Path

ROOT = Path(__file__).parents[2]
PROCEDURE = ROOT / "docs" / "procedures" / "harness-acceptance.md"


def section(text: str, heading: str, next_heading: str) -> str:
    start = text.index(f"## {heading}")
    end = text.index(f"## {next_heading}", start)
    return text[start:end]


def assert_in_order(text: str, markers: tuple[str, ...]) -> None:
    positions: list[int] = []
    for marker in markers:
        found = text.find(marker)
        assert found >= 0, f"{marker!r} が見つかりません"
        positions.append(found)
    assert positions == sorted(positions), f"順序が崩れています: {markers}"


def test_acceptance_connects_to_add_feature_step8b_without_a_cycle() -> None:
    text = PROCEDURE.read_text(encoding="utf-8")
    connection = section(text, "add-feature ステップ8-Bとの接続", "自動検証との境界")

    assert_in_order(
        connection,
        (
            "**候補ゲート**",
            "**候補コミット**",
            "**G3実施**",
            "**結果記録**",
            "**最終ゲート**",
            "**記録コミット**",
            "**push / PR作成**",
        ),
    )
    # 循環しない根拠・やり直しの起点・G3不要時の既定フロー維持
    assert "受け入れ記録が製品ファイルを変更しない" in connection
    assert "1回で緑になる" in connection
    assert "手順1(候補ゲート)からやり直す" in connection
    assert "ステップ8-Aの既定フロー" in connection


def test_claude_uses_current_subagent_discovery_instead_of_agents_wizard() -> None:
    text = PROCEDURE.read_text(encoding="utf-8")
    claude = section(text, "Claude Code", "Codex")

    assert "`/agents`一覧wizardを前提にせず" in claude
    assert "`@`候補" in claude
    assert "対話型依頼で実起動" in claude


def test_stop_acceptance_preserves_the_human_owned_sentinel() -> None:
    text = PROCEDURE.read_text(encoding="utf-8")
    claude = section(text, "Claude Code", "Codex")
    codex = section(text, "Codex", "Kiro IDE")
    kiro_cli = section(text, "Kiro CLI", "判定")

    for harness in (claude, codex, kiro_cli):
        assert "sentinel" in harness
        assert "`Ctrl+C`" in harness

    assert "agentにsentinelを完了・更新させない" in claude
    assert "agentにsentinelを完了・更新させない" in codex
    assert "連続ブロックガードを実機で最後まで消費させない" in kiro_cli
