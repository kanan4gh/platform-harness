"""配布テンプレートの既定が、特定の技術スタックに結びつかない契約。

派生プロジェクト task3 の R1 で、配布テンプレート(v1.8.0)に AWS・TypeScript・npm・lint の既定への
前提が多数のファイルに分散して残っていた(https://github.com/kanan4gh/project-uroboros-neo/issues/54)。
決定 D4 に従い、既定は「クラウドに結びつけない中立な記入欄 + 具体例1つ」とし、AWS の記述は
``docs/procedures/tech-stack-switch.md`` の付録「AWS を使う場合の例」の1か所に集約する。

このテストは正典の既定を守るためのもので、配布しない(``distribution/template-manifest.json`` の
``include_paths`` に入れない)。派生プロジェクトが技術スタックを切り替えた後は成り立たないため。
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import tomllib
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parents[2]
AGENTS = ROOT / "AGENTS.md"
SWITCH = ROOT / "docs" / "procedures" / "tech-stack-switch.md"
MANIFEST = ROOT / "distribution" / "template-manifest.json"
SKILLS = ROOT / ".claude" / "skills"
THIS_TEST = "tests/procedures/test_tech_stack_neutrality.py"

# AWS を指す語。lambda(Python の構文)は対象にしない
AWS_TERMS = re.compile(
    r"(?i)(?<![A-Za-z0-9_])(aws|cdk|sam|s3|dynamodb)(?![A-Za-z0-9_])|cloudformation|amazon"
)
# 配布対象のうち、AWS の語を置いてよいのは切り替え手順書だけ
AWS_ALLOWED = frozenset({"docs/procedures/tech-stack-switch.md"})
# テキストとして検査しないファイル
NON_TEXT = frozenset({"uv.lock"})

EXAMPLE_NOTE = "既定の技術スタックではない"


def load_builder() -> ModuleType:
    path = ROOT / "scripts" / "build_template_distribution.py"
    spec = importlib.util.spec_from_file_location("build_template_distribution_u5", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


def distributed_text(relative: str) -> str:
    """作業ツリーのファイルに manifest の変換を適用した、配布物での内容。"""
    manifest = builder.load_manifest(MANIFEST)
    content = (ROOT / relative).read_bytes()
    for transformation in manifest.transformations:
        if transformation.path == relative:
            content = builder._apply_transformation(content, transformation)  # pyright: ignore[reportPrivateUsage]
    return content.decode("utf-8")


def tech_stack_layer() -> str:
    text = AGENTS.read_text(encoding="utf-8")
    start = text.index("\n# 技術スタック固有層\n")
    end = text.index("\n# 補足", start)
    return text[start:end]


def strip_jsonc_comments(text: str) -> str:
    """文字列の外にある // 行コメントを取り除く(devcontainer.json は JSONC)。"""
    out: list[str] = []
    in_string = False
    escaped = False
    i = 0
    while i < len(text):
        char = text[i]
        if in_string:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
            continue
        if char == '"':
            in_string = True
            out.append(char)
            i += 1
            continue
        if text.startswith("//", i):
            newline = text.find("\n", i)
            i = len(text) if newline == -1 else newline
            continue
        out.append(char)
        i += 1
    return "".join(out)


def distributed_paths() -> list[str]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return [path for path in data["include_paths"] if path not in NON_TEXT]


# --- AGENTS.md 技術スタック固有層 -------------------------------------------


def test_tech_stack_layer_is_a_neutral_form_with_one_example() -> None:
    layer = tech_stack_layer()
    assert not AWS_TERMS.search(layer)
    assert "## ハーネスの道具（固定）" in layer
    assert "## プロダクトの技術スタック（記入欄）" in layer
    assert "既定は決めていない。特定のクラウドにも結びつけない。" in layer
    assert "例であって既定ではない" in layer
    example = layer[layer.index("記入の例") :]
    for tool in ("Python 3.12", "uv", "pytest", "basedpyright", "ruff"):
        assert tool in example
    assert "インフラ(クラウド等): なし" in example
    assert "docs/procedures/tech-stack-switch.md" in layer


def test_every_fill_in_field_is_found_by_the_checklist_grep() -> None:
    # 切り替えチェックリストの順1は `grep -n '\\[記入' AGENTS.md` で記入欄の残りを検出する
    layer = tech_stack_layer()
    form = layer[
        layer.index("## プロダクトの技術スタック（記入欄）") : layer.index("> **記入の例")
    ]
    commands = layer[layer.index("## プロダクトの確認コマンド（記入欄）") :]
    placeholders = re.findall(r"\[[^\]]*\]", form + commands)
    assert placeholders
    assert all(item.startswith("[記入") for item in placeholders), placeholders
    assert "grep -n '\\[記入' AGENTS.md" in SWITCH.read_text(encoding="utf-8")


def test_harness_required_commands_stay_in_the_tech_stack_layer() -> None:
    # add-feature 段1と最終ゲートは、技術スタック固有層のコマンドを参照する
    layer = tech_stack_layer()
    for command in (
        "uv run pytest",
        "uv run ruff check .",
        "uv run basedpyright",
        "uv run python3 scripts/local_quality_gate.py",
    ):
        assert command in layer


def test_agents_md_states_that_steering_is_tracked_by_git() -> None:
    text = AGENTS.read_text(encoding="utf-8")
    assert "`.steering/` の作業ディレクトリは Git で追跡し、履歴として保持する" in text


def test_agents_md_refers_to_the_setup_project_exception() -> None:
    text = AGENTS.read_text(encoding="utf-8")
    assert "初回セットアップの setup-project は例外で、Issue とステアリングを作らない" in text


# --- AWS の集約 ---------------------------------------------------------------


@pytest.mark.parametrize("relative", distributed_paths())
def test_aws_appears_only_in_the_switch_procedure(relative: str) -> None:
    if relative in AWS_ALLOWED:
        return
    hits = [
        line
        for line in distributed_text(relative).splitlines()
        if AWS_TERMS.search(line)
    ]
    assert hits == [], f"{relative}: {hits[:3]}"


def test_switch_procedure_has_checklist_and_aws_example() -> None:
    text = SWITCH.read_text(encoding="utf-8")
    checklist = text[text.index("## 切り替えチェックリスト") : text.index("## 付録")]
    assert "| 順 | 対象ファイル | 変える内容 | 確認コマンド |" in checklist
    for target in (
        "`AGENTS.md`",
        "`pyproject.toml`",
        "`.devcontainer/devcontainer.json`",
        "`.mcp.json.example`",
        "`docs/harness-guide.md`",
        "scripts/local_quality_gate.py",
        "`uv lock`",
    ):
        assert target in checklist
    assert "## いつ行うか（順序）" in text
    appendix = text[text.index("## 付録: AWS を使う場合の例") :]
    for item in ("aws-cli", "~/.aws", "AWS_PROFILE", "aws-cdk", "aws-sam-cli", "aws-mcp"):
        assert item in appendix
    # 付録の AGENTS.md 記入例は、記入欄と同じ見出しと項目で書く
    start = appendix.index("### AGENTS.md の記入例")
    example = appendix[start : appendix.index("### `.devcontainer")]
    for heading in (
        "## プロダクトの技術スタック（記入欄）",
        "## プロダクトの確認コマンド（記入欄）",
    ):
        assert heading in example
    form = tech_stack_layer()
    form = form[form.index("## プロダクトの技術スタック（記入欄）") : form.index("> **記入の例")]
    for field in re.findall(r"(?m)^- ([^:]+): ", form):
        assert f"- {field}: " in example, field


def test_devcontainer_has_no_aws_defaults() -> None:
    raw = (ROOT / ".devcontainer" / "devcontainer.json").read_text(encoding="utf-8")
    data = json.loads(strip_jsonc_comments(raw))
    assert not any("aws" in feature.lower() for feature in data.get("features", {}))
    assert not any(".aws" in mount.lower() for mount in data.get("mounts", []))
    assert not any(key.upper().startswith("AWS_") for key in data.get("containerEnv", {}))
    extensions = data["customizations"]["vscode"]["extensions"]
    assert not any(
        "aws" in extension.lower() or "amazon" in extension.lower() for extension in extensions
    )
    # Claude Code の feature は残す(G3 の観察対象を変えない)
    assert "ghcr.io/anthropics/devcontainer-features/claude-code:1.0" in data["features"]


def test_post_create_installs_harness_tools_only() -> None:
    text = (ROOT / ".devcontainer" / "postCreate.sh").read_text(encoding="utf-8")
    assert not AWS_TERMS.search(text)
    for tool in ("uv tool install ruff", "uv tool install basedpyright"):
        assert tool in text


def test_switch_procedure_is_distributed_and_this_test_is_not() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert "docs/procedures/tech-stack-switch.md" in data["include_paths"]
    assert THIS_TEST not in data["include_paths"]


# --- pyproject.toml -----------------------------------------------------------


def test_ruff_rule_selection_is_explicit() -> None:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    select = data["tool"]["ruff"]["lint"]["select"]
    assert {"E", "F", "I"} <= set(select)


# --- 設計スキル -----------------------------------------------------------------


def skill_markdown_files() -> list[Path]:
    return sorted(SKILLS.rglob("*.md"))


@pytest.mark.parametrize(
    "path", skill_markdown_files(), ids=lambda path: path.relative_to(ROOT).as_posix()
)
def test_typescript_examples_are_marked_as_examples(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "```typescript" not in text:
        return
    assert EXAMPLE_NOTE in text, "TypeScript のコード例を持つファイルには、例である旨の注記を置く"


def test_architecture_template_has_no_default_language() -> None:
    text = (SKILLS / "architecture-design" / "template.md").read_text(encoding="utf-8")
    stack = text[text.index("### 言語・ランタイム") : text.index("### フレームワーク")]
    for name in ("Node.js", "TypeScript", "npm"):
        assert name not in stack
    assert "[言語・ランタイム]" in stack


def test_process_guide_does_not_adopt_specific_tools_by_default() -> None:
    text = (SKILLS / "development-guidelines" / "guides" / "process.md").read_text(
        encoding="utf-8"
    )
    assert "採用ツール" not in text
    assert "以下は TypeScript の場合の例である" in text


def test_gitignore_example_keeps_steering_tracked() -> None:
    text = (SKILLS / "repository-structure" / "template.md").read_text(encoding="utf-8")
    start = text.index("### .gitignore")
    end = text.index("\n### ", start + 1)
    section = text[start:end]
    assert not re.search(r"(?m)^\s*-\s*`\.steering/`", section)
    assert "`.steering/` は除外しない" in section
