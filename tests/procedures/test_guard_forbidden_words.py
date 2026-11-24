"""手順書・アダプタのコマンド例に、ハーネスのガードが拒否する語を含めない契約。

Claude Codeのworktree隔離ガードは、引数がちょうど単語 complete(単独の語)である
コマンドを「worktree内に留まることを検証できない」として拒否する。派生プロジェクトでは
手順書どおりの完了遷移コマンドが拒否され、手順が停止した
(https://github.com/kanan4gh/project-uroboros-neo/issues/59)。

実験で判明した挙動:
- 拒否: 単独の語(``echo complete`` / ``steering_state.py complete --help``)
- 許可: 部分的に含む語(``--require-complete`` / ``completed`` / ``completion``)

そのため、エージェントがそのまま実行しうる「コマンド例」に限って禁止語を検査する。
tasklistの状態値としての complete(地の文や ``状態: complete``)はコマンドではないため対象外。
ガードが拒否する語が新たに判明したら ``FORBIDDEN_COMMAND_WORDS`` に追加する。
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).parents[2]

# ハーネスのガードが拒否すると判明した語(単独の語として現れた場合のみ拒否される)。
FORBIDDEN_COMMAND_WORDS: tuple[str, ...] = ("complete",)

# 手順書・ハーネスアダプタと、エージェントが参照する配布文書(コマンド例の置き場所)。
TARGET_GLOBS: tuple[str, ...] = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "docs/*.md",
    ".steering/example/*.md",
    "docs/procedures/**/*.md",
    ".claude/**/*.md",
    ".codex/**/*.md",
    ".kiro/**/*.md",
    ".agents/**/*.md",
)

# コード片がコマンド起動を含むとみなす目印。状態値だけのコードスパン(`complete`)は対象外になる。
COMMAND_MARKERS: tuple[str, ...] = (
    "python3",
    "uv run",
    "steering_state.py",
    "steering_lint.py",
    "grep",
    "echo",
    "Bash(",
)

FENCE_PATTERN = re.compile(r"^\s*(`{3,}|~{3,})")
INLINE_CODE_PATTERN = re.compile(r"(`+)(.+?)\1")


def forbidden_word_pattern(word: str) -> re.Pattern[str]:
    """単独の語として現れる場合だけに一致する(`--require-complete`等の部分一致は除外)。"""
    return re.compile(rf"(?<![\w-]){re.escape(word)}(?![\w-])")


def code_fragments(text: str) -> Iterator[tuple[int, str]]:
    """フェンスドコードブロックの論理行(行末`\\`の継続を結合)と、インラインコードを返す。"""
    fence: str | None = None  # 開いているフェンスの記号列(閉じるのは同種・同長以上の記号列だけ)
    pending: list[str] = []
    pending_line = 0
    for number, line in enumerate(text.splitlines(), start=1):
        marker = FENCE_PATTERN.match(line)
        if marker is not None:
            token = marker.group(1)
            closes = (
                fence is not None
                and token[0] == fence[0]
                and len(token) >= len(fence)
                and not line.strip()[len(token):].strip()
            )
            if fence is None or closes:
                if pending:
                    yield pending_line, " ".join(pending)
                    pending = []
                fence = None if closes else token
                continue
        if fence is not None:
            if not pending:
                pending_line = number
            pending.append(line.rstrip().removesuffix("\\").strip())
            if not line.rstrip().endswith("\\"):
                yield pending_line, " ".join(pending)
                pending = []
            continue
        for match in INLINE_CODE_PATTERN.finditer(line):
            yield number, match.group(2)
    if pending:
        yield pending_line, " ".join(pending)


def is_command(fragment: str) -> bool:
    return any(marker in fragment for marker in COMMAND_MARKERS)


def find_violations(text: str) -> list[tuple[int, str, str]]:
    violations: list[tuple[int, str, str]] = []
    for number, fragment in code_fragments(text):
        if not is_command(fragment):
            continue
        for word in FORBIDDEN_COMMAND_WORDS:
            if forbidden_word_pattern(word).search(fragment):
                violations.append((number, word, fragment))
    return violations


def target_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in TARGET_GLOBS:
        files.update(path for path in ROOT.glob(pattern) if path.is_file())
    return sorted(files)


def test_targets_cover_procedures_and_every_adapter() -> None:
    relative = {path.relative_to(ROOT).as_posix() for path in target_files()}
    for expected in (
        "AGENTS.md",
        "CLAUDE.md",
        "docs/procedures/steering.md",
        "docs/procedures/templates/tasklist.md",
        ".claude/commands/add-feature.md",
        ".codex/README.md",
        ".kiro/skills/steering/SKILL.md",
        ".agents/skills/steering/SKILL.md",
    ):
        assert expected in relative


@pytest.mark.parametrize(
    "path", target_files(), ids=lambda path: path.relative_to(ROOT).as_posix()
)
def test_command_examples_avoid_guard_forbidden_words(path: Path) -> None:
    violations = find_violations(path.read_text(encoding="utf-8"))
    assert not violations, "\n".join(
        f"{path.relative_to(ROOT)}:{number}: 禁止語 {word!r} を含むコマンド例: {fragment}"
        for number, word, fragment in violations
    )


# --- 検査器自身の健全性(陽性例・陰性例) ---

LEGACY = FORBIDDEN_COMMAND_WORDS[0]


@pytest.mark.parametrize(
    "text",
    [
        f"`python3 scripts/steering_state.py {LEGACY} --harness Codex`",
        f"`python3 scripts/steering_state.py pause / resume / {LEGACY}`",
        f"```bash\npython3 scripts/steering_state.py {LEGACY} --harness Codex\n```",
        f"```bash\npython3 scripts/steering_state.py \\\n  {LEGACY} \\\n  --harness Codex\n```",
        f"`grep {LEGACY} tasklist.md`",
        f"`Bash('echo {LEGACY}')`",
        # 外側の4連フェンス内に3連フェンスを含んでも、内側で状態が反転しない
        f"````markdown\n```bash\necho ok\n```\npython3 scripts/steering_state.py {LEGACY}\n````",
        f"~~~text\n```\n~~~\n`python3 scripts/steering_state.py {LEGACY}`",
    ],
)
def test_detector_flags_standalone_word_in_commands(text: str) -> None:
    assert find_violations(text)


@pytest.mark.parametrize(
    "text",
    [
        "`python3 scripts/steering_lint.py --require-complete 20261125-x`",
        "`python3 scripts/steering_state.py finish --harness Codex`",
        "`echo completed` と `echo completion`",
        f"状態を`{LEGACY}`へ遷移する",
        f"```markdown\n- **状態**: {LEGACY}\n```",
        f"tasklistの`active / paused / {LEGACY}`を遷移する",
        f"地の文の {LEGACY} はコマンド例ではない",
    ],
)
def test_detector_ignores_state_values_and_partial_words(text: str) -> None:
    assert not find_violations(text)
