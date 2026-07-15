# ハーネス実機受け入れ手順

## 目的

Claude Code、Codex、KiroのUI・対話・承認・Stop挙動を、従量課金型headless modeを使わずに確認する。構造や形式の検査はpytestへ寄せ、本手順では実セッションでしか確認できない項目だけを扱う。

## 実施条件

- 利用を許可されたIDEまたは対話型CLIを使う
- 対象リポジトリとcommitまたはtagを固定する
- 書き込み確認は`/private/tmp`等の使い捨て複製で行う
- ポリシーで禁止された非対話LLM実行を代替手段にしない
- 実施前に`uv run python3 scripts/local_quality_gate.py`が成功している

## 自動検証との境界

| 観点 | 検証方法 |
|---|---|
| ファイル存在、JSON / Markdown構造 | pytest |
| フックstdin / stdout、block判定、fail-open | pytest |
| 禁止headlessシグネチャの不在 | metered automation lint |
| スキル・エージェントの画面表示 | 対話型実機確認 |
| 指定ファイルの実読込 | 対話型実機確認 |
| read / write / shellの承認UI | 対話型実機確認 |
| Stopフックのランタイム発火 | 対話型実機確認 |

表示、読込、実行、権限、Stopは別の確認段階とする。表示されたことを読込・実行の証拠にせず、実際の出力またはUIを個別に記録する。

## 共通準備

1. 対象commitまたはtagを`/private/tmp`配下へ複製する
2. 未コミット変更がないことを確認する
3. 既存ステアリングより辞書順で後になる確認専用の最小steeringを人が作る
4. `find .steering -mindepth 1 -maxdepth 1 -type d -name '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-*' -print | sort | tail -1`で、lintと同じ日付接頭辞の選択対象を確認する
5. 記録テンプレートを対象ステアリング内の`acceptance-record.md`へ複製する
6. ハーネス名、バージョン、IDE / CLI、設定、対象commitを記録する
7. プロンプトは読み取り確認と安全な一時ファイル操作に限定する

受け入れ用steeringの作成をハーネスへ依頼しない。対象製品全体へ計画が拡大する可能性があるため、fixtureは人が最小形を固定する。

## Claude Code

1. 複製環境をClaude Code IDEまたは対話型CLIで開く
2. `AGENTS.md`と`CLAUDE.md`、主要スキルが表示されることを確認する
3. 指定した安全なファイルを読ませ、内容に基づく確認文字列を回答させる
4. 読み取り、書き込み、shellを別々に依頼して承認境界を観察する
5. 未完了tasklistに対するStopフックのblockまたはfeedbackを確認する
6. 実結果と証跡を記録する

## Codex

1. 複製環境をCodex IDEまたは対話型CLIで開く
2. `AGENTS.md`と`.agents/skills/`、必要なagentsが表示されることを確認する
3. `.codex/hooks.json`のtrust確認が必要なら対話画面で承認する
4. 指定した安全なファイルの実読込を確認する
5. 読み取り、書き込み、shellを別々に依頼してsandbox / approvalを観察する
6. 未完了tasklistに対するStopフックのblockまたはfeedbackを確認する
7. 実結果と証跡を記録する

## Kiro IDE

1. 複製環境をKiro IDEで開く
2. Agent Steering & Skillsに5 skills、Agent selectorに2 agentsが表示されることを確認する
3. `/steering`を選択し、SKILL.mdの実読込を確認する
4. 指定ファイルの実読込とread / write / shellの承認UIを個別に確認する
5. IDEのStop triggerはblock不可であることを記録する
6. steering lintとローカル品質ゲートが未完了tasklistを検出する代替経路を確認する
7. 実結果と証跡を記録する

## Kiro CLI

1. agent validate後、`kiro-cli --agent sdd`で対話型起動する
2. `/context`で`AGENTS.md`と5 skillsが各1回だけ表示されることを確認する
3. 指定ファイルの実読込を確認する
4. read事前許可とwrite / shellの承認UIを個別に確認する
5. 未完了tasklistに対してStopフックがstdout block decisionを返すことを確認する
6. 入力異常・状態破損のfail-openはpytest結果と照合する
7. 実結果と証跡を記録する

## 判定

- **合格**: 必須項目が期待どおりで、禁止headless modeを起動していない
- **不合格**: 期待結果と異なる、意図しない変更・権限・起動がある
- **保留**: 製品バージョン差、権限不足、利用不能により観察できない
- **対象外**: その実行面が能力を提供しない。能力差と代替経路を記録する

未観察を推測で合格にしない。保留・対象外には理由と再確認条件または代替経路を記録する。

## 誤起動時

課金対象の可能性があるheadless実行に気づいたら直ちに停止し、時刻、呼び出し元、到達点、変更ファイルを記録する。別のheadless実行で再現せず、静的テストまたは対話型確認へ切り替える。
