# ハーネス実機受け入れ記録

## 実施情報

| 項目 | 内容 |
|---|---|
| 実施日時 | 2026-07-28 07:42–07:46 JST |
| 担当者 | Codex |
| ハーネス | Claude Code / Codex / Kiro CLI |
| バージョン | Claude Code 2.1.220 / Codex CLI 0.145.0 / Kiro CLI 2.14.2 |
| 実行面 | 対話型CLI |
| OS | macOS 26.5.2 |
| 対象リポジトリ | kanan4gh/platform-harness |
| commit / tag | `623bba4b73632ad192b3016c960648a29336602d` |
| 一時環境 | `/private/tmp/platform-harness-issue46-g3`（detached HEADのclean clone） |
| 設定・承認ポリシー | Claude CodeはリポジトリtrustとWriteの単回承認、Codexはworkspace-write sandbox、Kiroは`sdd` agentのread事前許可とWrite / Shellの単回承認を使用 |

## 事前条件

- [x] ローカル品質ゲートが成功している
- [x] 一時環境はclean cloneから開始した
- [x] 実施時点の未コミット変更は意図した確認fixtureだけである
- [x] 意図しないファイル変更がない
- [x] 従量課金型headless modeを使用しないことを確認した

## 確認結果

| # | 操作 | 期待結果 | 実結果 | 証跡 | 判定 |
|---|---|---|---|---|---|
| 1 | 文脈・スキル認識 | 各ハーネスがリポジトリ規範とアダプタを認識する | Claude Codeはtrust画面で`.claude/settings.json`を表示、CodexはAGENTS文脈を読込、Kiroは`sdd` agentを読込 | 各対話型CLIの起動画面 | 合格 |
| 2 | 読み取り専用指示 | fixtureを変更せず、状態・先頭の未完了タスク・再開位置を返す | 3ハーネスとも`active`、`応答終了を妨げない未完了タスク`、`対話型読み取り確認`を返し、製品ファイルを変更しなかった | Claude session `c435d752-7ba1-41c6-93d9-93b288f4ef09`、Codex session `019fa5ba-becc-7742-8b60-ec3cb3ca73e9`、Kiro session `2f081257-3196-4c6f-9c80-9fdaf6683483` | 合格 |
| 3 | 承認UI | read / write / shellが各設定の境界どおり動作する | Claude CodeはWriteで単回承認、Codexはworkspace-write内で作成を許可、KiroはWriteとShellを別々の単回承認UIで許可。各プローブ以外の変更なし | 使い捨てclone内の`.g3-write-probe*`と`git status --short`出力 | 合格 |
| 4 | 未完了active応答の終了非ブロック | 未完了taskがあっても通常応答を終了し、Stop blockや自動継続を起こさない | 3ハーネスとも正常終了。Stop hook固有のtrust、feedback、block decision、自動継続は発生しなかった | 各対話型CLIの読み取り応答 | 合格 |
| 5 | pause / resume / complete状態遷移 | 状態と中断・再開記録が決定論的に遷移する | `active → paused → active → complete`が成功し、完了前の未完了taskを人が完了した | `scripts/steering_state.py`の各終了コード0とfixture tasklist | 合格 |
| 6 | 通常lint / 完了lint | active / pausedは通常lint成功、未完了activeの完了lintはG1のみ、完了後は完了lint成功 | 期待どおり。最終`--require-complete`はexit 0 | `scripts/steering_lint.py`の出力と終了コード | 合格 |

## 総合判定

- [x] 合格: 必須項目が期待どおりで、禁止headless modeの起動は0回

不合格・保留・対象外には該当しない。

## 差異・保留・対象外理由

- 差異: なし
- 再確認条件: 対象ハーネスの権限モデルまたは対話UIが変更された場合
- 代替経路: 構造・状態・lint・Stop hook不在はpytestとローカル品質ゲートで継続検証する

## 監査メモ

- GitHub Actions自動run: 0件（G3はローカルの固定commitだけで実施）
- 従量課金型LLM headless mode: 0件
- 対話型実行: Claude Code、Codex、Kiro CLIのみ。Kiroはセッション合計0.13 creditsを表示
- headless誤起動: なし
- 意図しないファイル変更: なし
- 後片付け結果: 3つの書き込みプローブを削除し、`git status --short --untracked-files=all`が空であることを確認。確認fixtureはignore対象のまま使い捨てclone内に保持
