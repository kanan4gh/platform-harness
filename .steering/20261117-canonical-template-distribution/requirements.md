# 要求内容

## 概要

`platform-harness`を正典の開発・リリース元として維持しながら、リリースtagから利用者向け成果物だけを決定論的に生成し、配布専用の`platform-harness-template`へ公開できる境界を実装する。

- **関連Issue**: https://github.com/kanan4gh/platform-harness/issues/64
- **使用ハーネス**: Codex
- **軽量パス**: 非適用

## パス判定

- [ ] 1. 既存パターンの踏襲のみで、新しいアーキテクチャ要素・新規依存を導入しない
- [ ] 2. 変更対象が3ファイル以下(テスト除く)
- [ ] 3. 対象文書の更新が不要
- [x] 4. データ形式・API契約の破壊的変更がない

**判定理由**:

- 基準1: 満たさない。exact allowlist manifest、Git objectベースの生成CLI、source/publisher provenanceという新しい配布アーキテクチャを導入する。外部依存は追加しない。
- 基準2: 満たさない。テストを除いて`README.md`、`docs/harness-guide.md`、`docs/procedures/setup-project.md`、`docs/procedures/template-distribution.md`、`distribution/template-manifest.json`、`scripts/build_template_distribution.py`の6ファイル以上を変更する。
- 基準3: 満たさない。永続文書`docs/harness-guide.md`と手順書`docs/procedures/setup-project.md`を更新し、新しい公開・更新・ロールバック手順を追加する。記述そのものが配布境界と運用条件を定める変更の実体である。
- 基準4: 満たす。既存のデータ形式・外部APIは変更せず、新しいmanifest schemaとCLIを追加する。既存の正典checkoutおよび派生プロジェクトの契約を破壊しない。

## G3受け入れ判定

- **不要**。ハーネスのアダプタ定義メタデータ、配置、権限設定、フック、ハーネス設定ファイルは変更しない。生成対象として既存アダプタを読み取るだけである。

## 背景

現状の`platform-harness`は正典開発repositoryとGitHub Template Repositoryを兼ね、正典側の`.steering/`履歴、`docs/ideas/`、派生プロジェクト台帳が新規プロジェクトへ混入する。`.gitignore`では追跡済みファイルやGitHubのtemplate生成を制御できず、利用者が作成する新しい日付付きsteeringまで通常のGit操作から除外される。

## ユースケースの軸

正典保守者が、リリース済みtagから検証可能な利用者向け配布物を生成・公開でき、利用者は正典の開発履歴を受け取らずに自分のsteeringを通常のGit操作で追跡できる。

## 実装対象の機能

### 1. 決定論的な配布生成

- exact allowlist manifestを配布集合の正とする。
- branchやdirty working treeではなく、検証済みrelease tagのGit treeから生成する。
- source tag/commitとpublisher revisionを生成metadataへ記録する。
- path traversal、symlink、未対応Git mode、manifest不整合、origin不一致をfail-closedにする。
- 同じ入力からpath、内容、実行bitが一致する成果物を生成する。

### 2. 正典専用資産の分離

- 配布物の`.steering/`は`example/`の3ファイルだけにする。
- 日付付きsteering、distill履歴、`docs/ideas/`、`docs/derived-projects.md`、配布管理用manifest・CLI・テストを含めない。
- 配布先の`.gitignore`から日付付きsteeringを除外する規則を除去する。
- 正典専用文書への必須参照は公開URLまたは配布向け文面へ変換し、ローカルの欠落参照を残さない。

### 3. 公開・更新・ロールバック手順

- 正典化PRのマージとrelease作成より前は、配布repository作成・push・settings変更を禁止する。
- 初回公開、継続更新、rollbackのpreflight、検証、証跡、操作順を定義する。
- 新templateを有効化してから現行`platform-harness`のtemplate設定を解除する。
- GitHub Actions自動runと従量課金LLM headless modeを必須経路にしない。

## 受け入れ条件

- [ ] `distribution/template-manifest.json`と`build_template_distribution.py`で、tag固定の正典Git treeから配布物を生成できる。
- [ ] manifestはexact allowlist、必須path、禁止path/prefix、明示変換を検証し、不正入力をfail-closedにする。
- [ ] 生成物にsource/publisher provenanceが含まれ、同じ入力からの再生成が決定的である。
- [ ] 生成物の`.steering/`は`example/`の3ファイルだけで、正典開発専用資産は0件である。
- [ ] 生成物で新しい日付付きsteeringを作成し、通常の`git add -A`でindexへ追加できる。
- [ ] 生成物へ完了済みfixture steeringを追加し、ローカル品質ゲートを成功させられる。
- [ ] README、harness guide、setup手順が正典と配布専用repositoryの境界を一貫して案内する。
- [ ] 初回公開・更新・rollback手順が、マージ前の外部変更禁止、release tag固定、検証、settings変更順、証跡を定める。
- [ ] 正典化PRのマージ前には`platform-harness-template`の作成・push・settings変更を実行しない。
- [ ] GitHub Actions自動runと従量課金LLM headless modeの起動は0件である。

## 成功指標

- 配布生成・契約テストが全件成功する。
- 生成物の禁止path/prefix検出件数が0件である。
- 同一入力の2回生成でpath、内容、実行bitの差分が0件である。
- 利用者steeringの通常Git追跡契約が成功する。

## スコープ外

- 正典化PRのマージ・release前にGitHub上の`platform-harness-template`を作成または変更すること。
- Claude Code / Codex / Kiroごとの個別配布repositoryへの再編。
- 既存派生プロジェクトへの一括自動展開。
- `platform-harness`の既存steering履歴を削除すること。

## 参照ドキュメント

- `AGENTS.md`
- `docs/harness-guide.md`
- `docs/external-automation-policy.md`
- `docs/procedures/add-feature.md`
- `docs/procedures/derived-project-rollout.md`
- `docs/procedures/setup-project.md`
- `docs/procedures/steering.md`
- Issue #64、および同Issueに記録された`project-uroboros-neo`の配布分離プロトタイプ
