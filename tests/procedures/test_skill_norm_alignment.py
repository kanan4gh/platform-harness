"""スキルの例・ガイドが、AGENTS.md と外部自動化ポリシーに反する既定を書かない契約。

派生プロジェクト task3 の R1 で、development-guidelines のガイドが Git Flow(develop ブランチ)と
CI 必須を既定にしており、AGENTS.md(作業ブランチから PR で main へ)と外部自動化ポリシー
(GitHub Actions は任意・``workflow_dispatch`` のみ・成功を PR 完了条件にしない)に反していた。
また「優先度」が、機能の優先順位(P0〜P2)とタスクの属性(高/中/低)の両方の意味で使われていた
(https://github.com/kanan4gh/project-uroboros-neo/issues/58)。

スキルの例はそのまま派生プロジェクトの永続ドキュメントになるため、次を機械的に検査する。

- Git Flow を「採用」「推奨」と既定にする表現
- ``develop`` をブランチとして書いた箇所(バッククォート、「develop ブランチ」、ツリー図、
  ``develop から/へ/→`` 等)。``development-guidelines`` 等の部分一致は対象外
- コードブロック内の GitHub Actions の例が push / pull_request で自動起動すること
- タスクの属性を「優先度」と呼んでいた旧識別子(``TaskPriority`` / ``PriorityEstimator`` /
  ``--priority`` / 「優先度(高/中/低)」)。「優先度」は機能の優先順位(P0〜P2)に固定し、
  タスクの属性は「重要度」(importance)と呼ぶ。``priority`` の単独の語は検査しない
- development-guidelines の SKILL.md が、AGENTS.md を優先する旨を書いていること

検査は「既定として書かれているか」の意味までは判定しない。Git Flow の説明で否定が要る場合は、
「Git Flow を採用しない」ではなく「Git Flow は使わない」等、検査語を避けた言い回しにする。
"""

from __future__ import annotations

from pathlib import Path
import re

import pytest

ROOT = Path(__file__).parents[2]

# 各ハーネスのスキル(設計スキルの例・ガイドと、手順書の薄いラッパ)。
TARGET_GLOBS: tuple[str, ...] = (
    ".claude/skills/**/*.md",
    ".agents/skills/**/*.md",
    ".kiro/skills/**/*.md",
)

DEVELOPMENT_GUIDELINES_SKILL = (
    ROOT / ".claude" / "skills" / "development-guidelines" / "SKILL.md"
)

# ASCII の語境界。日本語の文字は \w に含まれるため、\b や (?![\w-]) では
# 「developから」を取りこぼす。英数字・下線・ハイフンだけを語の続きとみなす。
_DEVELOP = r"(?<![A-Za-z0-9_-])develop(?![A-Za-z0-9_-])"

LINE_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("git-flow-default", re.compile(r"git\s*-?\s*flow\s*を?\s*(採用|推奨)", re.IGNORECASE)),
    ("develop-branch", re.compile(rf"`{_DEVELOP}`")),
    ("develop-branch", re.compile(rf"\*\*{_DEVELOP}\*\*")),
    ("develop-branch", re.compile(rf"{_DEVELOP}\s*ブランチ")),
    ("develop-branch", re.compile(rf"[└├│]\s*[─-]*\s*{_DEVELOP}")),
    ("develop-branch", re.compile(rf"{_DEVELOP}\s*(から|へ|に|→|->)")),
    ("develop-branch", re.compile(rf"(→|->)\s*{_DEVELOP}")),
    (
        "develop-branch",
        re.compile(rf"git\s+(checkout|switch|merge|pull|push|rebase|branch)\b.*{_DEVELOP}"),
    ),
    ("old-task-priority", re.compile(r"TaskPriority")),
    ("old-task-priority", re.compile(r"PriorityEstimator")),
    ("old-task-priority", re.compile(r"--priority(?![A-Za-z0-9_-])")),
    ("old-task-priority", re.compile(r"優先度\s*[(（]\s*高\s*/\s*中\s*/\s*低")),
)

# 外部自動化ポリシーが許す workflow のトリガーは手動実行だけ。これ以外のイベント
# (push / pull_request / pull_request_target / schedule 等)はすべて自動起動として扱う。
ALLOWED_WORKFLOW_EVENTS: frozenset[str] = frozenset({"workflow_dispatch"})

FENCE_PATTERN = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
# `on:` / `"on":` / `'on':` の後に値(インライン形式)または何もない(ブロック形式)。行末コメントは除く。
ON_KEY = re.compile(r"""^(\s*)["']?on["']?\s*:\s*(.*?)\s*(?:#.*)?$""")
EVENT_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
BLOCK_EVENT = re.compile(r"""^\s*(?:-\s*)?["']?([A-Za-z_][A-Za-z0-9_]*)["']?\s*(?::|$)""")


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _fence_transition(stack: list[str], token: str, info: str) -> None:
    """フェンスの開閉を更新する。

    スキルのガイドは ```markdown の例の中に ```typescript 等を入れ子にしている。
    開いたフェンスの中で情報文字列付きのフェンスが現れたら入れ子の開始、
    情報文字列のない同種・同長以上のフェンスなら最も内側の終了とみなす。
    """
    if not stack:
        stack.append(token)
    elif not info and token[0] == stack[-1][0] and len(token) >= len(stack[-1]):
        stack.pop()
    elif info:
        stack.append(token)


def find_violations(text: str) -> list[tuple[int, str, str]]:
    """(行番号, 規則ID, 行) を返す。CI の自動起動はコードブロック内だけを検査する。"""
    violations: list[tuple[int, str, str]] = []
    stack: list[str] = []
    on_indent: int | None = None  # ブロック形式の `on:` の字下げ(その配下を検査中)
    event_indent: int | None = None  # `on:` 直下のイベント名の字下げ
    for number, line in enumerate(text.splitlines(), start=1):
        for rule_id, pattern in LINE_RULES:
            if pattern.search(line):
                violations.append((number, rule_id, line.strip()))
                break
        marker = FENCE_PATTERN.match(line)
        if marker is not None:
            _fence_transition(stack, marker.group(1), marker.group(2).strip())
            on_indent = event_indent = None
            continue
        if not stack or not line.strip():
            continue
        if on_indent is not None:
            indent = _indent(line)
            if indent <= on_indent:
                on_indent = event_indent = None
            else:
                if event_indent is None:
                    event_indent = indent
                if indent == event_indent:
                    event = BLOCK_EVENT.match(line)
                    if event is not None and event.group(1) not in ALLOWED_WORKFLOW_EVENTS:
                        violations.append((number, "ci-auto-trigger", line.strip()))
                continue
        on_key = ON_KEY.match(line)
        if on_key is None:
            continue
        value = on_key.group(2)
        if value:
            events = set(EVENT_NAME.findall(value))
            if events - ALLOWED_WORKFLOW_EVENTS:
                violations.append((number, "ci-auto-trigger", line.strip()))
        else:
            on_indent = len(on_key.group(1))
    return violations


def target_files(root: Path = ROOT) -> list[Path]:
    files: set[Path] = set()
    for pattern in TARGET_GLOBS:
        files.update(path for path in root.glob(pattern) if path.is_file())
    return sorted(files)


def test_targets_cover_design_skills_and_every_harness() -> None:
    relative = {path.relative_to(ROOT).as_posix() for path in target_files()}
    for expected in (
        ".claude/skills/development-guidelines/SKILL.md",
        ".claude/skills/development-guidelines/guides/process.md",
        ".claude/skills/development-guidelines/template.md",
        ".claude/skills/functional-design/guide.md",
        ".claude/skills/glossary-creation/guide.md",
        ".claude/skills/prd-writing/SKILL.md",
        ".agents/skills/setup-project/SKILL.md",
        ".kiro/skills/setup-project/SKILL.md",
    ):
        assert expected in relative


@pytest.mark.parametrize(
    "path", target_files(), ids=lambda path: path.relative_to(ROOT).as_posix()
)
def test_skills_do_not_default_to_norm_violations(path: Path) -> None:
    violations = find_violations(path.read_text(encoding="utf-8"))
    assert not violations, "\n".join(
        f"{path.relative_to(ROOT)}:{number}: [{rule}] {line}"
        for number, rule, line in violations
    )


def test_development_guidelines_skill_gives_agents_md_precedence() -> None:
    lines = DEVELOPMENT_GUIDELINES_SKILL.read_text(encoding="utf-8").splitlines()
    assert any("AGENTS.md" in line and "優先" in line for line in lines), (
        "development-guidelines の SKILL.md に、AGENTS.md を優先する旨の記述がない"
    )


# --- 検査器自身の健全性(陽性例・陰性例) ---


@pytest.mark.parametrize(
    ("text", "rule"),
    [
        ("### ブランチ戦略（Git Flow採用）", "git-flow-default"),
        ("- [ ] ブランチ戦略が決まっている（Git Flow推奨）", "git-flow-default"),
        ("Git Flow を採用する", "git-flow-default"),
        ("- `develop`: 開発の最新状態", "develop-branch"),
        ("- **develop**: 次期リリースに向けた最新の開発コードを統合", "develop-branch"),
        ("develop ブランチへマージする", "develop-branch"),
        ("```\nmain\n  └─ develop\n```", "develop-branch"),
        ("```\nmain (本番環境)\n└── develop (開発・統合環境)\n```", "develop-branch"),
        ("- **feature/\\***: developから分岐し、PRでdevelopへマージ", "develop-branch"),
        ("feature→develop は squash merge", "develop-branch"),
        ("develop→main は merge commit", "develop-branch"),
        ("```yaml\nname: CI\non: [push, pull_request]\n```", "ci-auto-trigger"),
        ("```yaml\non: push\n```", "ci-auto-trigger"),
        ("```yaml\non:\n  push:\n    branches: [main]\n```", "ci-auto-trigger"),
        ("```yaml\non:\n  workflow_dispatch:\n  pull_request:\n```", "ci-auto-trigger"),
        ("```yaml\non:\n  schedule:\n    - cron: '0 0 * * *'\n```", "ci-auto-trigger"),
        ("```yaml\non: [pull_request_target]\n```", "ci-auto-trigger"),
        ('```yaml\n"on": [push]\n```', "ci-auto-trigger"),
        ("```yaml\non: # trigger\n  push:\n```", "ci-auto-trigger"),
        ("```yaml\non:\n  push: {branches: [main]}\n```", "ci-auto-trigger"),
        ("```yaml\non:\n  - push\n```", "ci-auto-trigger"),
        # 入れ子のフェンス(```markdown の中の ```yaml)でも検査する
        ("```markdown\n説明\n```yaml\non: [push]\n```\n```", "ci-auto-trigger"),
        ("```bash\ngit checkout -b feature/foo develop\n```", "develop-branch"),
        ("```bash\ngit merge develop\n```", "develop-branch"),
        ("  priority: TaskPriority;", "old-task-priority"),
        ("class PriorityEstimator {", "old-task-priority"),
        ('devtask add "タスク名" --priority high', "old-task-priority"),
        ("ユーザーがタスクに優先度(高/中/低)を設定できる", "old-task-priority"),
        ("タスクに優先度（高/中/低）を設定", "old-task-priority"),
    ],
)
def test_detector_flags_norm_violations(text: str, rule: str) -> None:
    assert rule in {found for _, found, _ in find_violations(text)}


@pytest.mark.parametrize(
    "text",
    [
        # development-guidelines を含む実在の行の形(develop の部分一致で誤検知しない)
        "5. **docs/development-guidelines.md** (開発ガイドライン)",
        "- [開発ガイドライン](./development-guidelines.md#TypeScript規約)",
        "**参考**: [開発ガイドライン](./development-guidelines.md#TDD)",
        "- `development-guidelines.md`: 開発ガイドライン",
        "├── development-guidelines.md   # 開発ガイドライン",
        "1. **development-guidelinesスキル**をロード",
        "`.claude/skills/development-guidelines/`(prd-writing / development-guidelines / glossary-creation)",
        "name: development-guidelines",
        "We develop features on short-lived branches.",
        # 現行の規範どおりの記述
        "### ブランチ戦略（作業ブランチ + PR → main）",
        "統合用ブランチを置くモデルは、本ガイドで上書きして導入しない",
        "Git Flow は使わない",
        "```yaml\nname: CI\non:\n  workflow_dispatch:\njobs:\n  test:\n    runs-on: ubuntu-latest\n```",
        "```yaml\non: workflow_dispatch\n```",
        "```yaml\non: workflow_dispatch # 手動実行のみ\n```",
        '```yaml\n"on":\n  workflow_dispatch:\n```',
        # workflow_dispatch の入力名など、イベントより深い字下げのキーは対象外
        "```yaml\non:\n  workflow_dispatch:\n    inputs:\n      push:\n        type: boolean\njobs:\n```",
        # 入れ子のフェンスが閉じた後の地の文は、コードとして扱わない
        "```markdown\n```typescript\nconst a = 1;\n```\n```\n\non: [push] とはしない",
        "```bash\ngit checkout main\ngit merge feature/x\n```",
        "push・pull_request では自動起動せず、CIの成功をPRの完了条件にしない",
        "on: [push, pull_request] とはしない(コードブロック外の地の文)",
        "```bash\ngit push origin feature/x\n```",
        # 機能の優先順位(P0〜P2)としての「優先度」と、priority の単独の語
        "**優先度**: P0(必須)",
        "- 優先度(P0/P1/P2)",
        "特に優先度P0(MVP)の機能に焦点を当ててください。",
        "  importance: TaskImportance;",
        "class ImportanceEstimator {",
        'devtask add "タスク名" --importance high',
        "priority queue を使う",
    ],
)
def test_detector_ignores_compliant_text(text: str) -> None:
    assert not find_violations(text)
