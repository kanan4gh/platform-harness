# 要求内容

## 概要

各応答の終了を妨げるStopフックを廃止し、ステアリングのライフサイクル状態と用途別検査を`tasklist.md`、共通状態遷移CLI、steering lint、ローカル品質ゲートで決定論的に管理する。project-uroboros-neo PR #38の先行検証を入力とし、platform-harness v1.5.1をbaseにプロジェクト固有値を除去して正典化する。

- **関連Issue**: https://github.com/kanan4gh/platform-harness/issues/46
- **使用ハーネス**: Codex
- **軽量パス**: 非適用

## パス判定

- [ ] 1. 既存パターンの踏襲のみで、新しいアーキテクチャ要素・新規依存を導入しない
- [ ] 2. 変更対象が3ファイル以下（テスト除く）
- [ ] 3. 対象文書の更新が不要
- [ ] 4. データ形式・API契約の破壊的変更がない

**判定理由**:

- 基準1: 満たさない。`active / paused / complete`の状態モデルと`steering_state.py`を新しい中立コアとして導入する
- 基準2: 満たさない。lint、状態遷移、品質ゲート、3ハーネスのアダプタ、手順、テンプレート、正典文書を横断する
- 基準3: 満たさない。steering、add-feature、harness acceptance、派生展開手順、tasklistテンプレート、AGENTS汎用層の方針と順序を変更する
- 基準4: 満たさない。旧tasklistを後方互換で読み込む一方、状態ブロックを新設し、Stop blockと2回ゲートを状態遷移・完了検査・単一ゲートへ置き換える契約変更である

**結論**: 通常パス

## G3受け入れ判定

- **判定**: 要
- **理由**: Claude Code、Codex、Kiro CLIのStopフック定義・登録・状態ファイルを削除し、ハーネスの終了時挙動と設定面を変更するため
- **受け入れ観点**: 未完了の`active` tasklistがあっても通常応答が終了すること、Stop block・自動継続・trust確認が発生しないこと、状態遷移と通常/完了lintが共通の決定論的経路として機能すること

## 正典化の入力と権限境界

- 正典baseはplatform-harness v1.5.1 / `bb125b52eaf7c603c612f363bbd5960f46f3d367`とする
- 先行検証の入力はproject-uroboros-neo PR #38、release v0.10.0、蒸留PR #40とする
- neoの実装を正典とみなして一括コピーせず、platform-harnessのテンプレート構造、派生展開手順、外部自動化ポリシー、アダプタ構成へ適合させる
- neo固有のIssue URL、プロダクト固有層、`docs/harness-swap-design.md`、既存steering履歴は移植しない
- platform-harnessの空のプロダクト用テンプレート文書（product requirements、functional design、architecture等）は利用先が具体化する領域なので、今回の正典内部設計を書き込まない
- 正典PRのマージとrelease後に、リリース済み正典を派生プロジェクトへ同期する。未リリースmainを派生側へ先行同期しない

## 背景

platform-harness v1.5.1は、最新tasklistに完了タスクが1件以上あり未完了が残る場合、Claude Code、Codex、Kiro CLIのStopフックで応答終了をブロックする。steering lint C3は全日付付きsteeringの未完了を一律違反とし、tasklist自身に最終品質ゲートの未完了行を置くため、PR前ゲートを意図的に2回実行する。

この契約には次の問題がある。

- 読み取り依頼、学習途中、承認後の正当な作業中断まで完了要求として扱う
- Stopフックはループ防止のため最終的にfail-openし、完全性の最終保証にはならない
- 3ハーネス固有のフックプロトコル・揮発状態・受け入れを保守する必要がある
- 過去の正当な中断が、別の完了済み作業のPRを妨げる
- 最終ゲート行がゲート自身の違反原因になる自己参照を持つ

neo PR #38では、状態契約、状態遷移CLI、状態対応lint、明示対象の単一完了ゲート、Stop不在契約を一体で実装し、171件のテスト、ローカル品質ゲート、3ハーネスの対話型G3に合格した。この実績を正典側で再設計・再検証する。

## ユースケースの軸

開発者がステアリング作業を開始・中断・再開・完了として明示的に遷移させ、作業中は通常応答を終了でき、PR前には指定した作業だけを1回の決定論的検査で完了確認できる。

## 実装対象の機能

### 1. ステアリング状態モデル

- `tasklist.md`に`active / paused / complete`とタイムゾーン付き更新日時を持つ状態ブロックを追加する
- `paused`は必須項目を持つ中断記録と未完了タスクを保持できる
- `complete`は未完了ゼロ、振り返り記入済み、プレースホルダーなしの場合だけ成立する
- 状態なしの旧tasklistは、未完了ゼロなら`complete`相当、未完了ありなら状態分類要求として扱う

### 2. 決定論的な状態遷移

- `scripts/steering_state.py`に`pause / resume / complete`を実装する
- 対象未指定時は最新の日付付きsteeringを選び、明示対象も受け付ける
- `pause`は中断日時、使用ハーネス、完了済み範囲、未コミット変更、再開位置、中断理由を記録する
- `resume`は`paused → active`と、最終ゲート失敗後の`complete → active`を理由付きで記録する
- `complete`は完了前提をすべて検証してから1回だけ書き込み、不正遷移ではtasklistを変更しない

### 3. 通常lintと完了lint

- 引数なしのsteering lintは全履歴を通常プロファイルで単一走査する
- `active`と有効な`paused`の未完了は通常lintで許容する
- `--require-complete [対象]`は同じ走査で指定対象だけに完了規則を追加する
- 状態整合性、中断記録、完了対象を別規則として報告し、同じ原因を重複報告しない
- 既存の軽量パス、Issue URL、振り返り、worktree除外契約を維持する

### 4. Stopフック廃止

- Claude Code、Codex、Kiro CLIのStop登録・実装・揮発状態・専用テストを削除する
- Claude Codeの非強制PostToolUse tasklistリマインドは維持する
- 3ハーネスの構造テストを「Stop登録・実装が存在しない」契約へ変更する
- 通常応答の終了を妨げないことをG3で確認する

### 5. 単一最終品質ゲート

- tasklistから最終品質ゲートの自己参照チェックボックスを削除する
- 実装、4段検証、振り返り、文書更新の完了後に状態を`complete`へ遷移する
- `local_quality_gate.py --steering [対象]`が完了プロファイルのsteering lintを1回起動する
- ゲート失敗後は`resume`で`active`へ戻し、影響範囲を再検証して再度`complete`へ遷移する
- G3が必要な場合の候補ゲートと記録後最終ゲートは、それぞれの最終ファイル状態に対する1回のゲートとして区別する

### 6. 正典手順・アダプタ・派生展開の整合

- steering、add-feature、harness acceptance、validate implementation、派生展開手順を新契約へ更新する
- tasklistとharness acceptance recordテンプレートを状態契約へ更新する
- AGENTS汎用層、CLAUDE、各ハーネスREADME・薄いスキル/コマンドを更新する
- `docs/harness-guide.md`とリポジトリ構造・外部自動化の説明を新契約へ整合させる
- 派生展開manifestからStop専用状態を外し、`steering_state.py`と状態遷移テストを正典配布対象に含める

## 受け入れ条件

### 状態モデルと通常lint

- [ ] `active`かつ未完了ありは通常lintで合格する
- [ ] `paused`かつ有効な中断記録ありは通常lintで合格する
- [ ] `paused`かつ中断記録不備は専用規則で不合格になる
- [ ] `complete`かつ未完了ありは状態整合性違反を1件だけ報告する
- [ ] 状態なし・完了済みの旧tasklistは後方互換で合格する
- [ ] 状態なし・未完了の旧tasklistは状態分類を要求される

### 完了lint

- [ ] 完了対象が`active`または`paused`なら完了対象規則を1件だけ報告する
- [ ] 完了対象が整合した`complete`なら合格する
- [ ] 過去の有効な`paused`は別の`complete`対象の完了lintを妨げない
- [ ] 完了検査は単一プロセス・単一走査で通常規則と対象追加規則を評価する

### 状態遷移

- [ ] `pause`が必須項目を持つ中断記録と`paused`状態を生成する
- [ ] `resume`が再開記録を追加して`active`へ戻す
- [ ] `complete`は未完了、空の振り返り、プレースホルダー、重複状態ブロックがあれば変更しない
- [ ] 不正遷移、対象解決失敗、プロジェクト外パスは非0終了しtasklistを変更しない

### Stop廃止と品質ゲート

- [ ] 3ハーネスのアダプタにStop登録・実装・専用状態が残っていない
- [ ] Claude CodeのPostToolUseリマインドが維持される
- [ ] ローカル品質ゲートが指定steeringを1回の完了lintで検査する
- [ ] 手順、テンプレート、正典文書、派生展開manifest、構造テストが新契約と一致する
- [ ] 対話型G3で未完了`active`による応答終了ブロックがないことを確認する

## 成功指標

- Stopフック実装・登録・専用揮発状態が0件
- 正常系の最終品質ゲート内でsteering lintの起動が1回
- 1 lint実行につき各steeringの状態整合性評価が1回
- 状態3種、旧tasklist互換、正常・異常遷移が自動テストで再現される
- ローカル品質ゲートが合格する
- GitHub Actions自動runと有料LLM headless modeの起動が0件

## スコープ外

- `superseded`等、3状態以外のライフサイクル追加
- 強制終了時や各応答終了時の自動`paused`遷移
- project-uroboros-neoや他の派生プロジェクトへの未リリース正典の同期
- 派生同期manifest検査CLIの新設（蒸留候補2として別Issueで扱う）
- GitHub Actionsの自動起動

## 参照ドキュメント

- `AGENTS.md`
- `docs/harness-guide.md`
- `docs/external-automation-policy.md`
- `docs/procedures/steering.md`
- `docs/procedures/add-feature.md`
- `docs/procedures/harness-acceptance.md`
- `docs/procedures/derived-project-rollout.md`
- `docs/procedures/templates/tasklist.md`
- project-uroboros-neo `.steering/20260728-steering-lifecycle-lint/`
