# 要求内容

## 概要

metered automation lint が `.claude/worktrees/` 配下のリポジトリcheckoutまで走査し、PRマージ待ちの worktree が残っている間はローカル品質ゲートが恒常的に誤検出で落ちる問題を解消する。

- **関連Issue**: https://github.com/kanan4gh/platform-harness/issues/38
- **使用ハーネス**: Claude Code
- **軽量パス**: 非適用
- **G3受け入れ**: 不要（policy JSON・永続ドキュメント・テストのみの変更であり、アダプタ構成・権限・フックのいずれも変更しない）

## 軽量パス非適用の理由

適用基準4項目のうち「`docs/` 永続ドキュメントの更新が不要」を満たさない。`docs/external-automation-policy.md` は除外リストを明示的に列挙する正典であり、除外の追加には同ドキュメントの更新が必須である（同ドキュメント自身が「除外を追加する場合は、技術的理由と誤検出しないテストを同時に追加する」と要求している）。

## 背景

v1.4.2 のリリース作業中、main のクリーンな作業ツリーで `uv run python3 scripts/local_quality_gate.py` が metered automation lint (5/5) で落ちた。

```
[codex-non-interactive] .claude/worktrees/feature+terminal-gate-ordering/tests/lint/test_metered_automation_lint.py:110
[claude-print-short]    .claude/worktrees/feature+terminal-gate-ordering/tests/lint/test_metered_automation_lint.py:117
[claude-print-short]    .claude/worktrees/feature+terminal-gate-ordering/tests/lint/test_metered_automation_lint.py:177
```

検出されたのは PR #37 の作業で使った worktree に残っていた**lint自身のテストfixture**であり、main の内容は健全だった。worktree ディレクトリを削除したら全5検査が緑になった。

### 原因

`scripts/metered_automation_lint.py` の `iter_target_files` は `include_paths` の各エントリを `rglob("*")` で再帰的に走査する。`include_paths` には `.claude` が含まれるため、`.claude/worktrees/<名前>/` 配下の**リポジトリのcheckout全体**が対象に入る。

一方 `_is_excluded` はリポジトリルート相対パスの前方一致で判定するため、除外エントリはルート直下の実体にしか効かない。結果、worktree 内の以下が除外から漏れる:

- `tests/lint/test_metered_automation_lint.py`（違反fixtureを保持する専用テスト）
- `.steering/`（監査履歴）、`docs/ideas/`、policy本体、lint本体
- `.venv/`（worktree 内で `uv run` すると生成される。走査コストも増える）

### 影響

worktree はPR作成後に後片付けする決まりだが（`docs/procedures/add-feature.md` ステップ8-A手順6。マージまで残すのは**ブランチ**であって worktree ではない）、**worktree が存在する期間そのものは正当に発生する**:

- 作業中の worktree があるまま、親リポジトリ側で別の確認としてゲートを回す
- 複数の作業を並行させ、一方が未完了のまま他方のゲートを回す
- 中断・クラッシュ・後片付けの失敗で worktree が残る（Issue #38 の再現は、PR #37 の worktree が残っていたケース）

いずれの場合も、親リポジトリでゲートを回すと worktree 内の**lint自身のテストfixture**を違反として報告して落ちる。ローカル品質ゲートは全ハーネス共通の必須ゲートであり、作業ツリーの残存という無関係な状態で結果が変わるのは、「落ちても無視してよい」という運用を招く点で有害である。

> **訂正記録**: 本ステアリング初版と Issue #38 本文は、手順書を「worktree をPRマージまで残す」と誤読し、「手順と機構が矛盾している」と記述していた。実際に手順書がマージまで残すと定めているのはブランチである。段3のコードレビューで指摘され、上記に訂正した。修正の必要性そのものは変わらない。

## ユースケースの軸

**PRマージ待ちの worktree を手順どおり残したまま、同一リポジトリで次の作業のローカル品質ゲートを全緑にできる。**

## 実装対象の機能

### 1. `.claude/worktrees/` の走査除外

- `scripts/metered_automation_policy.json` の `exclude_paths` に `.claude/worktrees` を追加する
- `.claude` は `include_paths` に残し、**`.claude/` 直下の現行指示面（コマンド・スキル・エージェント・設定・フック）は引き続き走査対象とする**（実行手順を隠す抜け穴にしない）

### 2. 除外理由の正典への記録

- `docs/external-automation-policy.md` の除外リストに `.claude/worktrees/` を追記し、技術的理由（同一リポジトリの別checkoutであり、その worktree 自身のゲート実行で検査済み。現行指示面の重複であって新たな指示面ではない）を記録する

### 3. 誤検出しないテスト

- `.claude/worktrees/` 配下の違反シグネチャが報告されないことを検証する
- **過剰除外になっていないこと**（`.claude/` 直下の違反は引き続き報告されること）を同時に検証する
- 実リポジトリのpolicyが上記の契約（`.claude` を include、`.claude/worktrees` を exclude）を保持していることを固定する

## 受け入れ条件

### 走査除外

- [ ] `scripts/metered_automation_policy.json` の `exclude_paths` に `.claude/worktrees` が含まれる
- [ ] `include_paths` に `.claude` が残っている
- [ ] policyの読み込みが `PolicyError`（過剰除外ガード・include/exclude重複）を出さない

### 正典への記録

- [ ] `docs/external-automation-policy.md` の除外リストに `.claude/worktrees/` と技術的理由が記載されている

### テスト

- [ ] `.claude/worktrees/` 配下の違反が報告されないテストがある
- [ ] `.claude/` 直下の違反は報告される（過剰除外でない）テストがある
- [ ] 実policyの include / exclude 契約を固定するテストがある
- [ ] `uv run pytest` が緑になる

### 実挙動

- [ ] worktree が存在する状態のmainで `uv run python3 scripts/local_quality_gate.py` が全5検査パスする

## 成功指標

- PRマージ待ちの worktree を残したまま次の作業を開始しても、ローカル品質ゲートが誤検出で落ちない
- 除外が「実行手順を隠す」方向に働いていないことをテストが決定論的に保証する

## スコープ外

以下はこのフェーズでは実装しません:

- `_is_excluded` の判定ロジック変更（ネストしたcheckoutを一般的に検出する仕組みの導入等）。policy駆動という既存設計を維持し、最小の除外追加で解決する
- `PROTECTED_EXCLUDES`（1階層パスの過剰除外ガード）の変更。`.claude/worktrees` は2階層のため緩和不要
- steering lint 側の同種問題の調査（`.steering` はルート相対で完結しており、worktree 内のステアリングは lint 対象外になる。別途必要なら独立Issueとする）
- add-feature 手順の「worktree はPRマージまで残す」規定の変更（機構側で解決するため手順は変えない）

## 参照ドキュメント

- `docs/external-automation-policy.md` - 外部自動化ポリシー（除外リストの正典）
- `docs/procedures/add-feature.md` - ステップ8-A手順6（worktreeをマージまで残す規定）
- `docs/harness-guide.md` - ローカル品質ゲートの位置づけ
