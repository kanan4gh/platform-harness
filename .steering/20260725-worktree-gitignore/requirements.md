# 要求内容

## 概要

`.claude/worktrees/` を `.gitignore` に追加し、ruff が入れ子の作業ツリーを走査してローカル品質ゲートが誤検出で落ちる問題を解消する。

- **関連Issue**: https://github.com/kanan4gh/platform-harness/issues/41
- **使用ハーネス**: Claude Code
- **軽量パス**: 適用
- **G3受け入れ**: 不要（`.gitignore` とテストのみの変更。アダプタ構成・権限・フックはいずれも不変）

## 軽量パス判定（適用時のみ記載。基準の正は add-feature 手順のステップ4）

- [x] 既存パターンの踏襲のみで、新しいアーキテクチャ要素・新規依存を導入しない
- [x] 変更対象が3ファイル以下(テスト除く)
- [x] `docs/` 永続ドキュメントの更新が不要
- [x] データ形式・API契約の破壊的変更がない

**判定理由**:

- 基準1: **満たす**。`.gitignore` への1行追加であり、既存の除外エントリと同じパターン。新しい仕組みも依存も導入しない
- 基準2: **満たす**。変更対象は `.gitignore` の1ファイル（テスト除く）
- 基準3: **満たす**。`docs/` 永続ドキュメント・`docs/procedures/`・`AGENTS.md` のいずれも更新不要。`docs/repository-structure.md` は `.claude/` をツリー内の1行で記すのみでサブディレクトリを列挙していないため、追随の必要がない。`docs/external-automation-policy.md` の除外リストは metered automation lint 固有のものであり、`.gitignore` を見る ruff には無関係
- 基準4: **満たす**。データ形式・API契約の変更なし

4項目すべてを満たすため軽量パスを適用する。設計判断が発生しないため design.md は作成しない。

## 背景

Issue #38 / PR #39 で metered automation lint の作業ツリー走査問題を解消したが、**同じ根本原因が ruff に残っている**（PR #39 の段3コードレビュー指摘2）。

`EnterWorktree` が作る作業ツリーはリポジトリ内の `.claude/worktrees/<名前>/` に置かれ、そこにリポジトリのcheckout全体が現れる。`.gitignore` に `.claude/worktrees/` が無いため、`git status` は `?? .claude/worktrees/` を出し、**`.gitignore` を尊重する ruff はこの配下を通常のプロジェクトファイルとして走査する**。

実測（作業ツリーが1つ存在する状態の親リポジトリ）:

```
$ uv run ruff check . --show-files | grep -c worktrees
23
```

ruff の設定 `include = ["*.py", ...]`（`pyproject.toml`）は `*.py` が階層を問わずマッチするため、除外は `.gitignore` に依存している。

### 影響

現状はたまたま緑である（作業ツリーの中身がクリーンなため）。しかし**lintエラーを含む作業中の作業ツリーが存在すると、親リポジトリのローカル品質ゲートが ruff (2/5) で落ちる**。Issue #38 と同型の偽陽性であり、無関係な作業ツリーの状態でゲートの結果が変わる。ゲートは最初の失敗で停止するため、後段の検査にも到達しない。

副次的に、`git add -A` で作業ツリーの gitlink を誤ってステージする事故も防げる。

## ユースケースの軸

**作業中・マージ待ちの作業ツリーが存在しても、親リポジトリのローカル品質ゲートがその内容に影響されない。**

## 実装対象の機能

### 1. `.claude/worktrees/` の無視指定

- `.gitignore` に `.claude/worktrees/` を追加する（理由をコメントで添える。既存エントリと同じ形式）
- これにより git が無視し、`.gitignore` を尊重する ruff も走査しなくなる

### 2. 無視が効いていることの決定論的テスト

- `git check-ignore` で、`.claude/worktrees/` 配下が実際に無視対象になることを検証する（`.gitignore` の文字列一致ではなく、**git のignore解決という実際の機構**で確認する。ruff が消費するのはこの解決結果であるため）
- **過剰無視でないこと**を同時に検証する（`.claude/commands/` 等、`.claude/` 直下の管理対象ファイルは無視されない）

### 3. 他ツールへの影響がないことの確認

- basedpyright（`include` がルート相対の明示ディレクトリ）、pytest（`testpaths = ["tests"]`）、steering lint（ルート `.steering` の非再帰走査）、metered automation lint（PR #39 で対応済み）が影響を受けないことを確認し、tasklist に記録する

## 受け入れ条件

### 無視指定

- [ ] `.gitignore` に `.claude/worktrees/` が追加されている
- [ ] 作業ツリーが存在する状態で `git status --porcelain` に `?? .claude/worktrees/` が現れない

### テスト

- [ ] `git check-ignore` で `.claude/worktrees/` 配下が無視されることを検証するテストがある
- [ ] `.claude/` 直下の管理対象ファイルが無視されない（過剰無視でない）ことを検証するテストがある
- [ ] `uv run pytest` が緑になる

### 実挙動

- [ ] 作業ツリーが存在する状態の親リポジトリで `uv run ruff check . --show-files` に作業ツリー内のファイルが現れない
- [ ] `uv run python3 scripts/local_quality_gate.py` が全5検査パスする

## 成功指標

- lintエラーを含む作業ツリーが存在しても、親リポジトリのゲート結果が変わらない
- `.gitignore` から当該エントリが失われた場合、テストが決定論的に検出する

## スコープ外

以下はこのフェーズでは実装しません:

- ruff の設定（`pyproject.toml` の `include`）の変更。`.gitignore` で解決できるため、走査設定には手を入れない
- `.claude/worktrees/` というパス規約のドキュメント化（PR #39 の段3レビュー指摘4。`EnterWorktree` の実装詳細であり、規約として文書化するかは別途判断する）
- metered automation lint の除外（PR #39 で対応済み）
- 他ハーネス（Codex / Kiro）が作業ツリーを作る場合の配置規約

## 参照ドキュメント

- `docs/harness-guide.md` - ローカル品質ゲートの位置づけ
- `docs/procedures/add-feature.md` - ステップ0（作業ツリー分離）・ステップ8-A手順6（後片付け）
- `.steering/20260724-worktree-lint-exclusion/tasklist.md` - 切り出し元の記録
