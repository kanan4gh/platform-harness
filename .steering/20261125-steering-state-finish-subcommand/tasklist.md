# タスクリスト

## 作業状態

- **状態**: complete
- **状態更新日時**: 2026-11-25T07:17:07+09:00
- **使用ハーネス**: Claude Code

## 作業履歴

_記録なし_

## タスク管理の原則

- `active`: 作業系列が継続中。未完了を許容する
- `paused`: 意図的な中断。有効な中断記録がある場合に未完了を許容する
- `complete`: 全タスクと振り返りが完了。未完了を許容しない
- 完了・技術的スキップは実態に合わせて即時記録する
- 「今日はここまで」はスキップではなく`scripts/steering_state.py pause`で記録する
- 最終品質ゲート、コミット、G3受け入れ記録、push、PRはチェックボックスにしない

---

## フェーズ1: CLI改名（実装フェーズ / ステップ5）

- [x] `scripts/steering_state.py` に `finish` を追加し、旧名をhelp非表示の互換エイリアスにする(出力は `finish` に正規化、`complete_text`→`finish_text`、pauseの案内文言を更新)
- [x] `tests/lint/test_steering_state.py` を更新し、`finish`・旧名の同一挙動と `--help` の非表示を検証するテストを追加する

## フェーズ2: 参照更新（実装フェーズ / ステップ5）

- [x] 手順書(`add-feature.md` / `steering.md` / `harness-acceptance.md`)のコマンド例・操作名を `finish` にする
- [x] テンプレート(`templates/tasklist.md` / `templates/harness-acceptance-record.md`)を更新する
- [x] アダプタ(`.claude/commands/add-feature.md` / `.claude/README.md` / 3つの steering SKILL.md / `.codex/README.md` / `.kiro/README.md`)と `CLAUDE.md` を更新する
- [x] `docs/procedures/steering.md` にworktree隔離ガードの注意書き(1〜2行)を追加する
- [x] `tests/procedures/test_add_feature_ordering.py` と `tests/adapters/test_harness_acceptance.py` の期待値を更新する
- [x] grepで旧コマンド参照の残存がないことを確認する

## フェーズ3: 再発防止テスト（実装フェーズ / ステップ5）

- [x] コマンド例の禁止語を検査するテスト `tests/procedures/test_guard_forbidden_words.py` を追加する(禁止語リスト管理・部分一致と状態値の除外・検査器の陽性/陰性例)

## フェーズ4: 4段検証（ステップ6）

- [x] 段1: `uv run pytest` / `uv run ruff check` / `uv run basedpyright`
- [x] 段2: 実挙動検証(一時プロジェクトで `finish` と旧名の遷移・終了コード・`--help` を観察)
- [x] 段3: コードレビューと指摘対応(`/code-review` 6件中5件対応: `-OO`実行時のdescription取得のIndexError修正 / 新テストを`distribution/template-manifest.json`の配布対象へ追加 / `steering_lint.py`のC3案内文を「resumeでactiveへ戻してからfinish」に修正(既存不具合だが旧コマンドへ誘導するため本件の参照更新に含めた) / 検査対象にREADME.md・docs/*.md・.steering/example/*.mdを追加 / フェンス判定を同種・同長以上の記号列で閉じる方式に修正。不正サブコマンド時のargparseエラーに旧名が出る件はdesign.md記載の既知残差として見送り)
- [x] 段4: スペック準拠検証と指摘対応(implementation-validator: 準拠・指摘なし。doc-reviewer: steering.mdの注意書きに`--require-complete`は対象外である旨と禁止理由、完了節にサブコマンド名と状態値の対応、モード3の表現を修正。harness-acceptance表の状態値併記・add-feature.md再遷移の言及は任意指摘のため見送り(状態値として既に正しい))

## フェーズ5: 振り返りとドキュメント更新（ステップ7）

- [x] 永続ドキュメントの更新要否を判断し、必要な更新とレビューを完了(不要: `docs/*.md` の永続ドキュメントに steering_state のサブコマンドへの言及なし。手順書・テンプレートの更新はステップ5で実施し段3・段4のレビュー済み)
- [x] README類の更新要否を判断し、必要なら更新(アダプタREADME 3件はステップ5で更新済み。ルート README.md は該当記述なしのため不要)
- [x] 実装後の振り返りを記録
- [x] 全テスト通過、lintエラーなし、リリース判断を記録(pytest 316件通過 / ruff・basedpyright エラー0)

> 上の全チェック完了後、`python3 scripts/steering_state.py finish --harness "Claude Code"`で`complete`へ遷移する。その後、add-featureステップ8で最終品質ゲートを1回実行する。

---

## 実装後の振り返り

### 実装完了日

2026-11-25

### 計画と実績の差分

**計画と異なった点**:

- 段3のコードレビューを受け、計画外の2ファイル(`scripts/steering_lint.py` のC3案内文、`distribution/template-manifest.json` の配布対象)を変更した。どちらも本件の目的(旧コマンドへの誘導をなくし、派生プロジェクトでも再混入を防ぐ)の範囲内。詳細は design.md「段3レビュー後の追加変更」
- doc-reviewer の指摘で、`steering.md` の注意書きに「`--require-complete` は対象外」と禁止理由を明記し、完了節にサブコマンド名と状態値の対応を1文追加した

**新たに必要になったタスク**:

- 上記の段3・段4指摘対応(各段の行に記録済み)

**技術的理由でスキップしたタスク**:

- 該当なし

### 学んだこと

**技術的な学び**:

- argparse の `aliases=` は `--help` に別名を表示する。非公開の別名は「help= なしの別サブパーサ + `add_subparsers(metavar=...)`」で実現できる。ただし不正サブコマンド時のエラーの選択肢一覧には別名が残る(既知残差)
- `ArgumentParser(description=__doc__)` で docstring に経緯を書くと、その内容がヘルプへ漏れる。今回は旧名がヘルプに出たため、1行目だけを使う形に直した
- 禁止語の検査は「コマンド起動を含むコード片の中の単独の語」に絞ると、状態値(地の文・状態だけのコードスパン)や部分一致の語を誤検出しない。テストは旧版の文書に対して12件の違反を検出した

**プロセス上の改善点**:

- 新しいテストを追加しても、`distribution/template-manifest.json` への登録漏れを検出する機構がない(今回は段3のコードレビューで発見した)。手順書の不備として記録する(本件では直さない)
- `.claude/commands/add-feature.md` のステップ0は EnterWorktree の使用を推奨している。しかし今回の不具合は worktree 隔離の中でだけ起きる。`finish` への改名で既知の語は回避したが、ガードの判定基準は Claude Code 本体側にあり、未知の禁止語が残る可能性がある(引用符内の語の扱いは未確認)。手順書の不備候補として記録する
- add-feature 手順は「Issue を同じリポジトリに作り、`Closes #番号` で閉じる」前提になっている。今回のように別リポジトリの Issue(neo#59)が起点の作業や、GitHub への書き込みに承認が必要な運用のときの扱いが書かれていない。今回は requirements に neo#59 の URL を記録し、コミットは `Refs` で参照した。手順書の不備として記録する
- ステップ3・4の Explore / Plan 委譲は、範囲が依頼書で列挙済みだったため使わず、メインで grep 調査した。網羅の漏れ(lint の案内文・manifest)は段3のレビューで補えた

### 次回への改善提案

- 配布 manifest と `tests/` の整合を検査するテスト(すべてのテストが include_paths か除外リストのどちらかにあること)を追加する(別 Issue 候補)
- ガードの拒否語が新たに判明したら、`tests/procedures/test_guard_forbidden_words.py` の `FORBIDDEN_COMMAND_WORDS` に追加する

### リリース判断

| 観点 | 評価 |
|---|---|
| ユーザー価値のあるまとまりか | Yes(worktree 隔離セッションで完了遷移が止まる不具合の解消) |
| 未解決の重大バグ | なし |
| 適切なバージョン種別 | PATCH(後方互換の別名を残した不具合修正) |

**提案**:

B-2 計画では U1 の後に続くユニットがあるため、リリースは上位の判断に委ねる。単独でリリースするなら PATCH が適切。
