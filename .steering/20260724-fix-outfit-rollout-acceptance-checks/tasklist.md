# タスクリスト

## 🚨 タスク完全完了の原則

**このファイルの全タスクが完了するまで作業を継続すること**

- 完了・スキップは実態に合わせて即時記録する。
- 技術的理由のないスキップは禁止する。
- 過去steeringの対象6項目以外を変更しない。
- GitHub Actions自動runや有料LLM headless modeを起動しない。

## フェーズ0: Issue・計画・承認

- [x] platform-harness Issue #22を作成する
- [x] `main`から`docs/fix-outfit-rollout-acceptance-checks`ブランチを作成する
- [x] `requirements.md`を作成し、ユーザー承認を得る
- [x] `design.md`を作成し、ユーザー承認を得る
- [x] `tasklist.md`を作成し、ユーザー承認を得る（2026-07-24「承認します」）

## フェーズ1: 完了根拠の確認と記録補正

- [x] 過去tasklistと完了証拠から受け入れ条件6/6件の充足を再確認する
- [x] Git履歴からPR #21のマージ記録を再確認する（merge commit `d25b919`）
- [x] `.steering/20260715-zzzz-record-outfit-v1-3-0-rollout/requirements.md`の対象6項目だけを`[x]`へ変更する

## フェーズ2: 差分・品質検証

- [x] 対象6項目がすべて`[x]`であることを静的に確認する（6/6件）
- [x] 対象6項目の文言と周辺の過去steering記録が不変であることを確認する（`git diff --unified=0`）
- [x] 今回のsteering記録を除き、変更対象が元の`requirements.md`だけであることを確認する
- [x] ~~`uv run python3 scripts/steering_lint.py`が成功する~~（実装順序を変更: 未完了タスクを拒否するC3規則との自己参照を避けるため、最終ローカル品質ゲート内で実行する）
- [x] ~~`uv run python3 scripts/local_quality_gate.py`が成功する~~（実装順序を変更: 最終完了記録状態での品質ゲートへ統合する）
## フェーズ3: 完了処理

> PR URLを記録した後に全完了状態を固定し、最終ローカル品質ゲートを再実行して最終記録をpushする。

- [ ] Issue #22を参照するConventional Commitを作成する
- [ ] ブランチをpushし、Issue #22を参照するPRを作成する
- [ ] PR URLと完了証拠を記録する
- [ ] GitHub Actions自動runと有料LLM headless mode起動が0件であることを確認する
- [ ] 今回の`requirements.md`の受け入れ条件を実態に合わせて更新する
- [ ] 実装後の振り返りを記録する
- [ ] tasklistの全項目が`[x]`であることを確認する
- [ ] 最終完了記録状態で`uv run python3 scripts/local_quality_gate.py`が成功する
- [ ] 最終記録をcommitしてpushする

---

## 完了証拠

- 関連Issue: https://github.com/kanan4gh/platform-harness/issues/22
- 補正対象: `.steering/20260715-zzzz-record-outfit-v1-3-0-rollout/requirements.md`
- 補正PR: 実装後に記録
- ローカル品質ゲート: 実装後に記録
- GitHub Actions自動run: 実装後に記録
- 有料LLM headless mode: 実装後に記録

## 実装後の振り返り

### 実装完了日

実装後に記録する。

### 計画と実績の差分

実装後に記録する。

### 学んだこと

実装後に記録する。

### 次回への改善提案

実装後に記録する。

### リリース判断

| 観点 | 評価 |
|---|---|
| 今回の変更はユーザーにとって価値のあるまとまりか | 実装後に評価 |
| 未解決の重大バグはないか | 実装後に評価 |
| 適切なバージョン種別 | 実装後に評価 |

**提案**: 実装後に記録する。
