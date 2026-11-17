# platform-harness

AIコーディングエージェントと協働するスペック駆動開発(SDD)ハーネスの中立な正典です。Claude Code、Codex、Kiro向けアダプタ、共通手順、ローカル品質ゲートを開発・リリースします。

## 正典と配布の境界

- このrepositoryは正典の開発、Issue・PR、releaseを管理します。
- 新規プロジェクト向けの生成済み成果物は [platform-harness-template](https://github.com/kanan4gh/platform-harness-template) へ公開します。
- 配布物はrelease tagからexact allowlistで生成し、正典のsteering履歴、ideas、派生台帳、配布管理資産を含めません。
- 公開・更新・ロールバックは [`docs/procedures/template-distribution.md`](docs/procedures/template-distribution.md) に従います。

## 開発

通常の変更はGitHub Issueとフィーチャーブランチを作り、`add-feature`と`steering`の手順で実装します。PR前の必須ゲートは次です。

```bash
uv run python3 scripts/local_quality_gate.py --steering <YYYYMMDD-task-name>
```

GitHub Actions自動runや従量課金LLM headless modeを標準検証に使いません。

## 利用者向けガイド

生成済みテンプレートのセットアップと使い方は [`docs/harness-guide.md`](docs/harness-guide.md) を参照してください。
