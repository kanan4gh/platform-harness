#!/bin/bash
set -e

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

export PATH="$HOME/.local/bin:$PATH"

# Python開発ツール
uv tool install ruff
uv tool install basedpyright

# AWS CDK
npm install -g aws-cdk

# AWS SAM CLI
pip install aws-sam-cli

# バージョン確認
claude --version || true
aws --version || true
cdk --version || true
sam --version || true
