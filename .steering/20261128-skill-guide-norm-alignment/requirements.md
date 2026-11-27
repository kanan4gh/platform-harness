# 要求内容

## 概要

設計スキル(development-guidelines ほか)の例・ガイドを、AGENTS.md と外部自動化ポリシー(`docs/external-automation-policy.md`)に整合させる(U8)。スキルの側を規範に合わせる作業であり、規範(AGENTS.md・手順書)は変更しない。

- **関連Issue**: https://github.com/kanan4gh/project-uroboros-neo/issues/58 (別リポジトリのため Closes ではなく Refs で参照する)
- **使用ハーネス**: Claude Code
- **軽量パス**: 非適用

## パス判定（**通常パス・軽量パスのどちらでも必ず記載する**。基準の正は add-feature 手順のステップ4）

- [x] 1. 既存パターンの踏襲のみで、新しいアーキテクチャ要素・新規依存を導入しない
- [ ] 2. 変更対象が3ファイル以下(テスト除く)
- [ ] 3. 対象文書(`AGENTS.md` とハーネスアダプタの規範記述・AGENTS.md プロダクト固有層が列挙する永続ドキュメント・`docs/procedures/` の手順書とテンプレート)の更新が不要
- [x] 4. データ形式・API契約の破壊的変更がない

**判定理由**（満たさない項目はその理由、記録例外を使った項目はその内容を書く）:

- 基準1: 満たす。スキル本文の文言・例の改訂と、既存の文書検査テスト(`tests/procedures/test_guard_forbidden_words.py`)と同型の pytest の追加だけで、新しいスクリプト・依存・層を導入しない
- 基準2: 満たさない。変更対象(テスト除く)は8ファイル: `.claude/skills/development-guidelines/` の `SKILL.md`・`template.md`・`guides/process.md`・`guides/implementation.md`、`.claude/skills/functional-design/guide.md`、`.claude/skills/glossary-creation/guide.md`、`.claude/skills/architecture-design/guide.md`、`.claude/skills/prd-writing/SKILL.md`
- 基準3: 満たさない(保守的に判定)。`.claude/skills/` の設計スキルは基準3の列挙(`CLAUDE.md` / `.claude/commands/` / `.agents/skills/` / `.kiro/skills/` 等)に明示されていないが、派生プロジェクトの永続ドキュメントの既定(ブランチ戦略・CI・用語)を定める**ハーネスアダプタ配下の規範的記述**であり、その**方針そのもの**(既定のブランチ戦略、CI の位置づけ、用語の意味)を変えるため、対象文書の方針変更とみなした。「等」に設計スキルが含まれるかが読み取れない点は、手順書の不備候補として記録する(design.md「記録事項」)
- 基準4: 満たす。データ形式・API 契約に当たるもの(steering の機械可読書式、スクリプトの入出力、スキルの frontmatter)は変えない。用語の変更はスキルの例の中だけで、派生プロジェクトの既存文書は変わらない

結論: **通常パス**(基準2・3を満たさない)。

## G3受け入れの要否判定

- **不要**。
- 変更するのはスキル本文(`SKILL.md` の本文、`guide.md`・`template.md`・`guides/*.md`)とテストだけである。`SKILL.md` の frontmatter(`name`・`description`・`allowed-tools`)、ファイル名、配置は変えない(add-feature ステップ4「不要: アダプタ本文の手順記述だけを書き換えた変更」に当たる)。
- `.claude/settings.json`、フック、MCP 設定、エージェント・コマンド定義は変更しない。表示・実読込・承認境界・Stop 挙動のいずれも変わらない。
- frontmatter を変えていないことは、段1でテスト(frontmatter の差分がないことの確認)と `git diff` で確認する。

## 背景

- 派生プロジェクト task3 の R1(2026-11-18)で、development-guidelines のガイドが「ブランチ戦略(Git Flow採用)」を既定とし、`develop` を「CI での自動テスト実施」としていた。AGENTS.md は feature ブランチから main への PR を基本とし、外部自動化ポリシーは GitHub Actions を必須の経路にしない(成功を PR 完了条件にしない)
- 同じく、スキルの例の中で「優先度」が、タスクの属性(高/中/低)と機能の優先順位(P0〜P2)の両方の意味で使われ、task3 の PRD で衝突した
- スキルの例をそのまま使うと、ハーネスの規範と食い違う文書ができ、利用者(人と AI)が毎回どちらに従うかを判断する必要がある

## ユースケースの軸

派生プロジェクトの AI が設計スキルの例・ガイドをそのまま使って永続ドキュメントを作っても、AGENTS.md と外部自動化ポリシーに食い違わず、用語の意味が一つに定まった文書ができる。

## 実装対象の機能

### 1. ブランチ戦略・CI の記述を規範に合わせる(#58 項目1)
- development-guidelines の既定を「feature ブランチ + PR で main へ」にし、Git Flow は承認した方針どおりに扱う
- CI(GitHub Actions)を必須とせず、成功を完了条件にしないことを書く。必須の品質確認はローカル品質ゲートとする
- スキルのガイドが AGENTS.md と食い違う場合は AGENTS.md を優先する、と読み取れるようにする

### 2. 「優先度」の二重の意味を解消する(#58 項目2)
- 承認した方針どおり、機能の優先順位とタスクの属性を区別できる語に分ける
- 説明の本文と、例のコードの型名・フィールド名・関数名・CLI オプションをそろえる

### 3. 全スキルの同種の矛盾を調査し、一覧にする(#58 の「未確認」)
- 調査結果を design.md に一覧で記録し、本作業で直す範囲と別 Issue にする範囲を分ける

### 4. 整合性の機械的な担保(#58 の提案)
- 承認した方針どおり、スキルのガイドが規範に反する既定を書いていないかを検査するテストを追加する(または見送りの理由を記録する)

## 受け入れ条件

各条件に確認方法を付記する(add-feature 手順のステップ4)。

### 1. ブランチ戦略・CI
- [ ] development-guidelines の `SKILL.md`・`template.md`・`guides/process.md` が feature ブランチ + PR(main へ)を既定とし、`develop` ブランチを既定にしない(確認方法: 自動テスト / エージェントの実機操作)
- [ ] 同ガイドが CI を必須とせず、ローカル品質ゲートを必須の経路、GitHub Actions を任意(成功を完了条件にしない)として記述し、例の workflow が push / pull_request で起動しない(確認方法: 自動テスト)
- [ ] development-guidelines の `SKILL.md` に、ガイドと AGENTS.md が食い違う場合は AGENTS.md を優先する旨がある(確認方法: 自動テスト)

### 2. 「優先度」
- [ ] 設計スキル(prd-writing を含む)で「優先度」が機能の優先順位(P0〜P2)だけを指し、タスクの属性は「重要度」(importance)で書かれている(確認方法: 自動テスト / エージェントの実機操作)
- [ ] 説明の本文と、例の型名・フィールド名・関数名・CLI オプションがずれていない(確認方法: 自動テスト / エージェントの実機操作)

### 3. 調査
- [ ] 全スキル(`.claude/skills/`・`.agents/skills/`・`.kiro/skills/`、あわせて `.claude/commands/`・エージェント定義)の調査結果が design.md に一覧で記録され、直す範囲と別 Issue にする範囲が分かれている(確認方法: エージェントの実機操作(段4の検証で照合))

### 4. 機械的な担保
- [ ] 承認した方針(4-B を絞った案)どおり、テストが追加されている。テストは陽性例・陰性例(`development-guidelines.md` を含む行を含む)で検査器自身の健全性を確認する(確認方法: 自動テスト)
- [ ] 追加したテストが、現在の全スキルで誤検知なく通り、main の旧ファイルに当てたときは旧い記述の箇所だけで失敗する(`development-guidelines` を含む行は失敗に含まれない)(確認方法: エージェントの実機操作)

### 共通
- [ ] スキルの `SKILL.md` の frontmatter、ファイル名、配置を変えていない(確認方法: 自動テスト(`git diff` の確認を段1で実施))
- [ ] U5 の対象(`AGENTS.md`)と setup-project の手順・アダプタ(`docs/procedures/setup-project.md`、`.claude/commands/setup-project.md`、`.agents/skills/setup-project/`)を変更していない。prd-writing は U6 マージ済みのため、タスク属性の3行だけを変更してよい(計画承認時の決定)(確認方法: 自動テスト(`git diff --name-only` の確認を段1で実施))
- [ ] 関連テストがすべて通り、ローカル品質ゲートが全緑(確認方法: 自動テスト)

「人の確認」とした項目: なし(用語の選択は計画承認で確定する)。

## 成功指標

- 設計スキルの例・ガイドの中に、AGENTS.md・外部自動化ポリシーと矛盾する既定の記述が残らない(本作業の範囲内)
- 「優先度」の意味が一つに定まる(prd-writing の残件は U6 へ引き渡す)

## スコープ外

- `AGENTS.md` の変更(U5 の範囲。規範側の不備は記録のみ)
- setup-project の手順・アダプタ(`docs/procedures/setup-project.md`、`.claude/commands/setup-project.md`、`.agents/skills/setup-project/`。U6 の範囲。prd-writing はタスク属性の3行だけを本作業で直す)
- `repository-structure/template.md` の `.gitignore` 例(S7。規範側の明文化が先に要るため別 Issue)
- 例の技術スタック(TypeScript・ESLint・Vitest 等)を本プラットフォームの技術スタック(Python)へ揃えること(規範との矛盾ではなく、例の汎用性の問題)
- リリース、GitHub への書き込み(承認なし)

## 参照ドキュメント

- `AGENTS.md` - SDD プロセス正典(基本フロー6: feature ブランチから PR、品質ゲートと実機受け入れ)
- `docs/external-automation-policy.md` - 外部自動化ポリシー(GitHub Actions は任意、`workflow_dispatch` のみ、成功を PR 完了条件にしない)
- `docs/procedures/add-feature.md` - パス判定・G3 判定の基準
- `tests/procedures/test_guard_forbidden_words.py` - 文書検査テストの既存パターン
