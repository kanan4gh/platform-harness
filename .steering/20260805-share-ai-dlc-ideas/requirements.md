# 要求内容

## 概要

派生プロジェクト`project-uroboros-neo`で整理したAI-DLC Workflows 2.0との比較、およびuroborosをAI開発ライフサイクル・フレームワークとして捉え直す議論を、本家`platform-harness`の`docs/ideas/`へ共有する。

- **関連Issue**: https://github.com/kanan4gh/platform-harness/issues/50
- **使用ハーネス**: Codex
- **軽量パス**: 適用
- **G3受け入れ**: 不要（アイデア文書2件の追加のみで、ハーネスのアダプタ構成・権限・フック・設定を変更しない）

## パス判定（通常パス・軽量パスのどちらでも必ず記載する。基準の正は add-feature 手順のステップ4）

- [x] 1. 既存パターンの踏襲のみで、新しいアーキテクチャ要素・新規依存を導入しない
- [x] 2. 変更対象が3ファイル以下(テスト除く)
- [x] 3. 対象文書の更新が不要
- [x] 4. データ形式・API契約の破壊的変更がない

**判定理由**:

- 基準1: **満たす**。既存の`docs/ideas/`へMarkdownの議論メモを追加する既存パターンだけを踏襲し、新しいアーキテクチャ要素・依存を導入しない
- 基準2: **満たす**。変更の実体は`docs/ideas/ai-dlc-uroboros-comparison.md`と`docs/ideas/uroboros-lifecycle-framework-architecture.md`の2ファイル
- 基準3: **満たす**。追加先は下書き・アイデアを置く`docs/ideas/`であり、`AGENTS.md`、ハーネスアダプタ、AGENTS.mdが列挙する永続ドキュメント、`docs/procedures/`、テンプレートの更新は不要
- 基準4: **満たす**。議論メモの追加だけで、データ形式・API契約を変更しない

4項目すべてを満たすため軽量パスを適用する。設計判断が発生しないため`design.md`は作成しない。

## 背景

`project-uroboros-neo`では、AI-DLC Workflows 2.0の方法論・実行制御・承認ゲートをuroborosのSDDプロセスと比較し、その議論を踏まえてuroborosのカテゴリ、アーキテクチャ、学習ループ、将来像を整理した。内容は派生プロジェクト固有の実装ではなく、本家の方法論・用語・アーキテクチャを今後検討する際の材料として有用である。

## ユースケースの軸

**platform-harnessの利用者・保守者が、AI-DLCとの比較およびuroborosの再定義に関する議論を本家リポジトリ内で参照し、今後の仕様検討に利用できる。**

## 実装対象の機能

### 1. AI-DLC比較文書の共有

- `docs/ideas/ai-dlc-uroboros-comparison.md`を派生プロジェクトから内容を維持して追加する
- AI-DLCの5フェーズ、制御モデル、uroborosとの対応・差分・示唆を本家で参照可能にする

### 2. ライフサイクル・フレームワーク再定義文書の共有

- `docs/ideas/uroboros-lifecycle-framework-architecture.md`を派生プロジェクトから追加し、本家に存在しない`docs/harness-swap-design.md`参照を対応する`docs/ideas/harness-swap.md`へ正規化する。また、表示上の改行は保ったまま行末2空白を`<br>`へ正規化する
- 前項の比較を踏まえたアーキテクチャ、用語体系、学習ループ、将来像の議論を本家で参照可能にする

## 受け入れ条件

### 文書の追加と参照整合性

- [ ] 2文書が本家の`docs/ideas/`に追加されている
- [ ] 派生側の元文書との差分が、本家固有の参照先1件とMarkdownハード改行5件の正規化だけである
- [ ] 文書間および既存文書への相対参照先が本家に存在する

### 品質と共有

- [ ] Markdownの空白・競合マーカー等の機械的な問題がない
- [ ] ローカル品質ゲートが成功する
- [ ] フィーチャーブランチからIssue #50を閉じるPRが作成される

## 成功指標

- 本家のPR差分から2文書をレビューできる
- 本家のローカル品質ゲートが全検査を通過する
- 派生側の既存作業ブランチや本家の別作業ブランチを変更しない

## スコープ外

以下はこの作業では実施しない。

- 議論内容を正式仕様・用語として確定すること
- `AGENTS.md`や`docs/procedures/`へAI-DLC由来の仕組みを実装すること
- 派生プロジェクト固有のプロダクト設定を本家へ取り込むこと
- リリース作成

## 参照ドキュメント

- `docs/ideas/harness-engineering.md` - ハーネスエンジニアリングの既存議論
- `docs/ideas/harness-swap.md` - ハーネス換装の既存議論
- `docs/procedures/steering.md` - ステアリング状態と検証手順
- https://github.com/kanan4gh/project-uroboros-neo/commit/904370b17abf29bce6d36273879d1e3d3caec76f - 共有元の追加コミット
