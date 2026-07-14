# .codex/ ディレクトリ ガイド(Codexアダプタ)

このディレクトリと `.agents/skills/` は、SDDハーネスの **Codex CLI 用アダプタ**です。SDDプロセスの正典は `AGENTS.md`、手順の正は `docs/procedures/` にあり(ハーネス中立)、ここにはCodex固有の実装のみを置きます(換装の構想と経緯は `docs/ideas/harness-swap.md` を参照)。

## 構成

```
.codex/
├── README.md              # このファイル
├── hooks.json             # Stopフック登録
├── hooks/
│   ├── check_tasklist_complete.py  # Codex適合版Stopフック(判定はscripts/steering_lint.pyを共有)
│   └── state/             # 連続ブロックガードの揮発状態(Git管理外)
└── agents/                # サブエージェント定義(手順書を参照する役割宣言のみ)
    ├── implementation-validator.toml
    └── doc-reviewer.toml
.agents/
└── skills/                # スキル(docs/procedures/の手順書を参照する薄いラッパ)
    ├── steering/ ├── distill/ ├── add-feature/
    ├── review-docs/ └── setup-project/
```

スキルの呼び出しはチャットで「steeringを実行して」「add-featureを実行して」等(スラッシュコマンドではない)。

## trust要件

`.codex/` 配下のフック・エージェント定義は、**Codex CLIでプロジェクトをtrust(信頼)した場合のみ**ロードされます。初回起動時のtrust確認に同意してください。

**重要(実地検証 2026-07-14 での発見)**: フックは hooks.json 単位のtrust承認(`~/.codex/config.toml` にハッシュ登録)が必要で、承認は**対話セッションでの確認**によって行われます。`codex exec`(非対話)では未承認のフックは**無言でロードされません**。換装・併用の初回は、対話セッションを一度起動してフックの承認を済ませてから使ってください(未承認でも steering lint+CI の最終ゲートは機能します)。

## 推奨設定

`~/.codex/config.toml`(ユーザーレベル設定)には、Claude Code側の settings.json と同じ「**読み取り・検証=自動 / 書き込み・外部操作=都度確認**」の境界を推奨します:

- 承認ポリシーは「失敗時・要求時に確認」相当を既定とし、完全自動(確認なし)とサンドボックス無効の組み合わせは避ける
- 完全自動フロー(add-feature)を使う場合も、ステップ4.5の計画承認(テキスト方式)は必ず経る

## Claude Codeアダプタとの差分(既知の劣化)

| 項目 | Claude Code | Codex |
|------|-------------|-------|
| Stopフック(未完了タスクの終了ブロック) | あり(`stop_hook_active` でループ防止) | **あり**(連続ブロックガードでループ防止) |
| 編集中のtasklistリマインド(PostToolUse) | あり | **なし**(既知の劣化。Stopフックとlint+CIが最終捕捉) |
| 承認UI | AskUserQuestion(選択式) | テキスト方式(AGENTS.md正文) |
| サブエージェント | .claude/agents/*.md | .codex/agents/*.toml |

## フックの配布時の注意

`check_tasklist_complete.py` は判定ロジックを `scripts/steering_lint.py` からimportします。他プロジェクトへ移植する場合は必ずセットでコピーしてください(不在の環境ではfail-openによりフックが無言で無効化されます。最終ゲートはCIのlintが担います)。
