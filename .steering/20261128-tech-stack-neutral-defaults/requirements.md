# 要求内容

## 概要

配布テンプレートに分散している特定の技術スタック（AWS、TypeScript・npm、lint の既定）への前提を集約し、既定を「クラウドに結びつけない中立な記入欄 + 具体例1つ」にする（U5）。AWS 用の記述は削除せず、「AWS を使う場合の例」として技術スタック切り替えの手順書1か所へ集約する。

- **関連Issue**: https://github.com/kanan4gh/project-uroboros-neo/issues/54 （別リポジトリのため Closes ではなく Refs で参照する）
- **使用ハーネス**: Claude Code
- **軽量パス**: 非適用

## パス判定（**通常パス・軽量パスのどちらでも必ず記載する**。基準の正は add-feature 手順のステップ4）

- [ ] 1. 既存パターンの踏襲のみで、新しいアーキテクチャ要素・新規依存を導入しない
- [ ] 2. 変更対象が3ファイル以下(テスト除く)
- [ ] 3. 対象文書(`AGENTS.md` とハーネスアダプタの規範記述・AGENTS.md プロダクト固有層が列挙する永続ドキュメント・`docs/procedures/` の手順書とテンプレート)の更新が不要
- [x] 4. データ形式・API契約の破壊的変更がない

**判定理由**:

- 基準1: 満たさない。手順書を1本新設する（技術スタック切り替え手順書）。新規依存は導入しないが、手順書群への新しい要素の追加である
- 基準2: 満たさない。変更対象は20ファイル超（AGENTS.md、docs/harness-guide.md、docs/architecture.md、.claude/README.md、.devcontainer/ 2ファイル、.mcp.json.example、pyproject.toml、設計スキル12ファイル、manifest、新規手順書、ruff 違反修正の Python ファイル群）
- 基準3: 満たさない。AGENTS.md の技術スタック固有層の方針（既定を中立にする）と、`.steering/` の Git 管理の明文化そのものが変更の実体であり、記録例外に当たらない
- 基準4: 満たす。データ形式・API 契約は変えない。品質ゲートのコマンドと manifest のスキーマも変えない

結論: **通常パス**（基準1・2・3を満たさない）。

## G3受け入れの要否判定

**不要**。理由:

- `.claude/skills/` の変更は本文（例・ガイドの記述）だけで、frontmatter・ファイル名・配置を変えない
- `.claude/README.md` は説明文書であり、表示・実読込・承認境界・Stop 挙動を変えない
- `.claude/settings.json`、`.claude/hooks/`、`.kiro/agents/*.json`、`.codex/` は変更しない
- `pyproject.toml` の変更は lint・型検査の設定であり、手順書の基準で不要（結果は品質ゲートで確認する）
- `.mcp.json.example` は有効でないサンプル設定であり、手順書の基準で不要
- `.devcontainer/` は開発環境の定義であり、ハーネスのアダプタ構成・権限・フックではない。Claude Code の devcontainer feature 自体は変更しないため、G3 の観察対象（スキル・エージェントの表示と実読込、承認境界、Stop 挙動）を変えない

## 背景

派生プロジェクト task3 の R1 で、配布テンプレート（v1.8.0）に AWS、TypeScript・npm、lint の既定への前提が多数のファイルに分散して残っていた。AGENTS.md の「技術スタックを変更するときは技術スタック固有層だけ書き換える」という設計と実態が合わず、task3 では解消に1コミット・5ファイル（+20/−142行）を要した。

決定済みの方針 D4（石原さん、2026-11-28）: テンプレートの既定の技術スタックは「特定のクラウドに結びつけない中立な記入欄 + 具体例1つ」とする。例は Python + uv + pytest + ruff + basedpyright（クラウドなし）で、例であって既定ではない旨を明記する。AWS 用の記述は削除せず「AWS を使う場合の例」として切り替えの手順書へ集約する。

## ユースケースの軸

> 派生プロジェクトの利用者が、テンプレートを複製した直後に、技術スタック固有層と切り替えチェックリストだけを見て、自分の技術スタックへ漏れなく書き換えられる。

## 実装対象の機能

### 1. 技術スタック固有層の中立化（AGENTS.md）
- 技術スタック固有層を、記入欄 + 具体例1つ（Python + uv + pytest + ruff + basedpyright、クラウドなし）にする
- ハーネスが必須とするコマンド（ローカル品質ゲート、steering lint 等）は記入欄と区別して残す

### 2. AWS 前提の集約と切り替え手順書（#54 項目1）
- 技術スタック切り替えの手順書を新設し、書き換える対象のファイル一覧・順序・確認コマンドのチェックリストと、「AWS を使う場合の例」を置く
- `.devcontainer/`、`.mcp.json.example`、`docs/harness-guide.md`、`docs/architecture.md`、`.claude/README.md` から AWS 前提を除く

### 3. 設計スキルの中立化（#54 項目2）
- 既定の前提として読める TypeScript・npm の記述を、技術スタック中立の記述または「例」と明示した記述にする。例のコードは例として残す

### 4. pyproject.toml の既定（#54 項目3）
- ruff の `select` を明示し、ハーネスのファイルの違反を0にする
- name / description、アプリのコードの対象ディレクトリを書き換える手順を切り替えチェックリストに置く

### 5. .gitignore の例と `.steering/` の Git 管理（#54 項目4、U8 の S7）
- 規範側で、`.steering/` を履歴として Git で追跡することを明文化する
- repository-structure スキルの `.gitignore` の例から `.steering/` の除外を除く

### 6. 申し送りの処理（U6 の2点）
- AGENTS.md の Issue・ステアリング規約から setup-project の例外を参照する
- harness-guide の手順順序（AGENTS.md の技術スタック書き換えと setup-project の architecture 決定）を整理する

## 受け入れ条件

### 技術スタック固有層
- [ ] AGENTS.md の技術スタック固有層が、中立な記入欄 + 具体例1つ（Python + uv + pytest + ruff + basedpyright。クラウドなし）になっており、例であって既定ではない旨が明記されている。AWS を既定にしていない（確認方法: 自動テスト）

### AWS の集約と切り替え手順書
- [ ] AWS の記述が、「AWS を使う場合の例」として切り替え手順書の1か所に集約されている（確認方法: 自動テスト）
- [ ] 技術スタックの切り替えチェックリストが手順書にあり、書き換える対象のファイル・順序・確認コマンドを含む（確認方法: 自動テスト、人の確認）
- [ ] `.devcontainer/`、`.mcp.json.example`、`docs/harness-guide.md`、`docs/architecture.md`、`.claude/README.md` から AWS 前提が方針どおり除かれている（確認方法: 自動テスト）
- [ ] `.devcontainer/devcontainer.json` が JSONC として解釈でき、AWS 用の feature・マウント・環境変数・拡張を含まない（確認方法: エージェントの実機操作）

### 設計スキル
- [ ] 設計スキルから、既定の前提として読める TypeScript・npm の記述が除かれ、例は例として明示されている。U8 の担保テスト（`tests/procedures/test_skill_norm_alignment.py`）が通る（確認方法: 自動テスト、人の確認）

### pyproject.toml
- [ ] `pyproject.toml` の ruff `select`、basedpyright の include の扱い、name / description の扱いが承認した方針どおりで、正典の品質ゲートが全緑（確認方法: 自動テスト）

### .gitignore の例
- [ ] repository-structure スキルの `.gitignore` の例が、`.steering/` を Git で追跡する規範と矛盾しない（確認方法: 自動テスト）

### 正典と配布物
- [ ] 正典と配布物のどちらで直したかがファイルごとに design.md に記録され、配布物を実際に生成して内容を確認している。配布テストが通る（確認方法: エージェントの実機操作、自動テスト）
- [ ] 生成した配布物で、ローカル品質ゲートが全緑になる（確認方法: エージェントの実機操作）

### 申し送り・全体
- [ ] U6 の申し送り2点の扱いが記録されている（確認方法: 人の確認）
- [ ] 関連するテストが更新され、すべて通る。ローカル品質ゲートが全緑（確認方法: 自動テスト）
- [ ] G3 の要否を手順の基準で判定し、理由が記録されている（確認方法: 人の確認）

## 成功指標

- 派生プロジェクトが技術スタックを切り替えるとき、書き換える対象が手順書のチェックリストに列挙されたファイルに限られる
- 配布物の既定から AWS・npm の前提がなくなる（AWS の言及は切り替え手順書の例だけ）

## スコープ外

以下はこの作業では扱わない:

- U7 の対象（`docs/procedures/derived-project-rollout.md`、`docs/external-automation-policy.md`、`.github/workflows/` と参照するテスト）。derived-project-rollout.md の AWS への言及（223行目、Outfit-studio パイロット節）は記録だけする
- リリース、GitHub への書き込み（承認なし）
- 設計スキルのコード例を TypeScript 以外の言語へ書き換えること（例は例として残す）
- 古いブランチ `fix/setup-project-template-residue`

## 参照ドキュメント

- `AGENTS.md` - 技術スタック固有層、補足「技術スタックを変更するとき」
- `docs/procedures/add-feature.md` - パス判定・G3判定の基準
- `docs/procedures/template-distribution.md`、`distribution/template-manifest.json` - 配布の仕組み
- `docs/procedures/setup-project.md` - setup-project の例外（U6）
- `docs/harness-guide.md` - 利用者向けセットアップ手順
