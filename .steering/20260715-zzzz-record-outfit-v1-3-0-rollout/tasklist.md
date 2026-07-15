# タスクリスト

## 🚨 タスク完全完了の原則

**このファイルの全タスクが完了するまで作業を継続すること**

- 完了・スキップは実態に合わせて即時記録する。
- 技術的理由のないスキップは禁止する。
- outfit-studio本体、通常checkout、運用コピーを編集しない。
- 台帳更新を他候補の自動展開開始にしない。

## フェーズ0: マージ証拠と計画

- [x] outfit-studio PR #26がMERGEDであることを確認する（merge commit `ed6baaaeb5d57e8b5c07dcd64ce2464b64647587`）
- [x] outfit-studio Issue #25がCLOSEDであることを確認する
- [x] platform-harness Issue #20を作成する
- [x] `origin/main`のv1.3.0 merge commit `bd2cd8c`から専用branchを作成する
- [x] requirements.mdを作成し、ユーザー承認を得る
- [x] design.mdを作成し、ユーザー承認を得る
- [x] tasklist.mdを作成し、ユーザー承認を得る（2026-07-15「承認して実装開始」）

## フェーズ1: 台帳と構造テストの更新

- [x] `docs/derived-projects.md`のoutfit-studio行だけを更新する
  - [x] Lineage evidenceをPR #26での3ハーネス移行完了へ更新する
  - [x] Harness generationを`current-neutral`へ更新する
  - [x] Strategyを`direct-sync`へ更新する
  - [x] Stateを`synced`へ更新する
  - [x] Last sourceを`v1.3.0 / bd2cd8c`へ更新する
  - [x] Local cautionへ通常checkoutの未追跡資産とclean clone / worktree継続利用を記録する
  - [x] Decision / next actionへPR #22の不要close、PR #26完了、次回direct-syncを記録する
- [x] `tests/procedures/test_derived_project_rollout.py`のoutfit-studio期待値を更新する
  - [x] outfit-studioのremote行が1件だけであることを維持する
  - [x] `current-neutral` / `direct-sync` / `synced` / `v1.3.0 / bd2cd8c`を固定する
  - [x] 他候補の期待値を変更しない

## フェーズ2: 4段検証

- [ ] 段1・静的検証
  - [x] `uv run pytest tests/procedures/test_derived_project_rollout.py`（14 passed）
  - [x] `uv run pytest`（143 passed）
  - [x] `uv run ruff check .`（合格）
  - [x] `uv run basedpyright`（0 errors / 0 warnings）
  - [ ] `uv run python3 scripts/local_quality_gate.py`
- [x] 段2・台帳を表解析し、outfit-studioの完了状態とremote一意性を観察する（14件の構造テストで合格）
- [x] 段3・変更差分を独立レビューし、正当な指摘を修正する（PR #22裁定記録の不足を修正し、再レビューでマージ阻害指摘0件）
- [x] 段4・steeringと台帳更新のスペック準拠を独立検証する（実装済み範囲は準拠、未記録の設計変更・スコープ外逸脱なし）
- [x] `git diff`でoutfit-studio以外の台帳行が不変であることを確認する
- [x] outfit-studio本体・通常checkout・運用コピーへ変更がないことを確認する（通常checkoutは既存未追跡4件・ahead/behind 0、運用コピーはclean）
- [x] GitHub Actions自動runと有料LLM headless mode起動が0件であることを記録する

## フェーズ3: 完了処理

> steering lintの自己参照を解消するため、commit・PR URL記録後に全完了状態を固定し、最終ローカル品質ゲートを実行して再pushする。

- [ ] requirements.mdの受け入れ条件がすべて満たされたことを確認する
- [ ] 実装後の振り返りを記録する
- [ ] Issue #20を参照するConventional Commitを作成する
- [ ] branchをpushして台帳更新専用PRを作成する
- [ ] PR URLと最終検証結果を記録・報告する

---

## 完了証拠

- outfit-studio PR: https://github.com/kanan4gh/outfit-studio/pull/26
- outfit-studio merge commit: `ed6baaaeb5d57e8b5c07dcd64ce2464b64647587`
- outfit-studio Issue: https://github.com/kanan4gh/outfit-studio/issues/25
- 同期元: platform-harness `v1.3.0 / bd2cd8c537fe257353e3efd19c1ea2407d6d6e66`
- 台帳更新Issue: https://github.com/kanan4gh/platform-harness/issues/20
- ローカル品質ゲート: 未実行
- GitHub Actions自動run: 0件
- 有料LLM headless mode: 0件
- 台帳更新PR: 未作成

## 実装後の振り返り

### 実装完了日

未定

### 計画と実績の差分

- 未記入

### 学んだこと

- 未記入

### 次回への改善提案

- 未記入

### リリース判断

| 観点 | 評価 |
|---|---|
| ユーザー価値 | 未評価 |
| 重大バグ | 未評価 |
| バージョン種別 | 未評価 |

**提案**: 未定
