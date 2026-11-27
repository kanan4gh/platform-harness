#!/bin/bash
set -e

# ハーネスの道具(uv・ruff・basedpyright)を入れる。プロダクトの技術スタックの道具は
# docs/procedures/tech-stack-switch.md のチェックリストに従って足す

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

export PATH="$HOME/.local/bin:$PATH"

# Python開発ツール
uv tool install ruff
uv tool install basedpyright

# バージョン確認
claude --version || true
uv --version || true
