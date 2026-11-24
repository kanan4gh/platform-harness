# 要求内容

## 概要

`scripts/steering_state.py` の完了サブコマンドを `finish` に改名し(`pause / resume / finish`)、旧名は互換用の非公開エイリアスとして残す。手順書・アダプタ・テンプレートのコマンド例を `finish` に統一し、コマンド例へ禁止語が再混入しないことをテストで担保する。

- **関連Issue**: https://github.com/kanan4gh/project-uroboros-neo/issues/59
- **使用ハーネス**: Claude Code
- **軽量パス**: 非適用

## パス判定

- [x] 1. 既存パターンの踏襲のみで、新しいアーキテクチャ要素・新規依存を導入しない
- [ ] 2. 変更対象が3ファイル以下(テスト除く)
- [ ] 3. 対象文書の更新が不要
- [x] 4. データ形式・API契約の破壊的変更がない

**判定理由**:

- 基準1: 満たす。argparseのサブパーサ追加とテスト追加のみで、新しい依存・層は導入しない。
- 基準2: 満たさない。テストを除いて `scripts/steering_state.py`、`docs/procedures/` の手順書3件とテンプレート2件、`.claude/` `.codex/` `.kiro/` `.agents/` のアダプタ7件、`CLAUDE.md` の計14ファイルを変更する。
- 基準3: 満たさない。手順書・テンプレート・アダプタ規範記述のコマンド例を書き換え、`docs/procedures/steering.md` にworktree隔離ガードの注意書き(手順上の注意そのもの)を追加する。記録例外の「一覧・台帳の値の更新」にはあたらない。
- 基準4: 満たす。旧サブコマンドは同一挙動・同一終了コードのエイリアスとして残し、tasklistの状態値 `complete` も変更しないため、CLI契約・データ形式とも後方互換である。

## G3受け入れ判定

- **不要**。変更するアダプタ(`.claude/commands/add-feature.md`、`.claude/skills/steering/SKILL.md`、`.kiro/skills/steering/SKILL.md`、`.agents/skills/steering/SKILL.md`、各README、`CLAUDE.md`)はいずれも**本文の手順記述のみ**で、frontmatter・ファイル名・配置・権限設定(`.claude/settings.json`)・フック定義は変更しない(add-feature手順ステップ4の「アダプタ本文の手順記述だけを書き換えた変更」に該当)。

## 背景

派生プロジェクト task3 のR2で、worktree隔離セッション内の `steering_state.py` 完了コマンドがClaude Code本体のworktree隔離ガードに拒否され、手順が約9分半停止した。実験により、ガードは引数がちょうど単語 complete のとき(単独の語)に拒否し、`--require-complete`・completed・completion のように部分的に含む語は許可されることが判明している(neo#59 本文とコメント、D3実験 2026-11-25)。

## ユースケースの軸

worktree隔離されたClaude Codeセッションでも、エージェントが手順書どおりに `steering_state.py finish` を実行してステアリングを完了状態へ遷移できる。

## 実装対象の機能

### 1. サブコマンドの改名

- `steering_state.py finish --harness ...` を完了遷移の正式名とする
- 旧名は互換エイリアスとして残し、挙動・終了コード・出力を `finish` と同一にする(出力のコマンド名は `finish` に正規化)
- `--help` には `finish` だけを表示する(エイリアスは表示しない)

### 2. 参照の更新

- 手順書・テンプレート・アダプタ・`CLAUDE.md` のコマンド例と操作名を `finish` に統一する
- tasklist内の状態値 `complete`、`steering_lint.py --require-complete` は変更しない
- `docs/procedures/steering.md` に、worktree隔離セッションでは単独の語 complete を引数に含むコマンド(状態値の検索等)が拒否される旨を1〜2行で注記する

### 3. 再発防止テスト

- 手順書・アダプタのコマンド例(コードスパン・コードブロック内のコマンド行)に禁止語リストの語が単独の語として現れないことを検査する
- 状態値としての使用、`--require-complete` 等の部分一致は除外する

## 受け入れ条件

- [ ] `python3 scripts/steering_state.py finish --harness "Claude Code"` が従来の完了コマンドと同じ挙動・同じ終了コードで動く
- [ ] 旧名エイリアスも同じく動く
- [ ] `--help` 出力と手順書・アダプタ・テンプレートには `finish` だけが書かれている
- [ ] 既存ステアリングの tasklist.md(状態値 complete)がそのまま検査を通る
- [ ] 関連テストが更新され、再発防止テストが追加され、すべて通る
- [ ] ローカル品質ゲートが全緑
- [ ] G3の要否を手順の基準で判定し、理由を記録している(上記「G3受け入れ判定」)

## スコープ外

- `steering_lint.py --require-complete` の改名(部分一致は許可されることを確認済み)
- tasklistの状態値 `complete` の改名
- 他サブコマンドの追加、リリース、neo#59 の他項目(verify不在、画面確認と無停止)
- ブランチ `fix/setup-project-template-residue` への干渉

## 参照ドキュメント

- `docs/procedures/add-feature.md` / `docs/procedures/steering.md`
- neo#59: https://github.com/kanan4gh/project-uroboros-neo/issues/59
