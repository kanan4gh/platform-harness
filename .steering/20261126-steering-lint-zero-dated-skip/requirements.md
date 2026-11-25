# 要求内容

## 概要

`scripts/steering_lint.py --require-complete`(対象が既定の latest)で、日付付きのステアリングが0件のときは、エラー(終了コード2)にせず、完了検査(G1)をスキップしてその旨を標準出力に表示する。通常規則の検査はこれまでどおり実行する。これにより、配布直後・setup-project 直後の状態でも、必須のローカル品質ゲートが通るようにする。

- **関連Issue**: https://github.com/kanan4gh/project-uroboros-neo/issues/56
- **使用ハーネス**: Claude Code
- **軽量パス**: 非適用

## パス判定

- [x] 1. 既存パターンの踏襲のみで、新しいアーキテクチャ要素・新規依存を導入しない
- [x] 2. 変更対象が3ファイル以下(テスト除く)
- [ ] 3. 対象文書の更新が不要
- [x] 4. データ形式・API契約の破壊的変更がない

**判定理由**:

- 基準1: 満たす。既存関数 `resolve_completion_target` の戻り値と `main` の分岐を変えるだけで、新しい依存・層は導入しない。
- 基準2: 満たす。テストとステアリングを除く変更対象は `scripts/steering_lint.py` と `docs/procedures/steering.md` の2ファイル。
- 基準3: 満たさない。`docs/procedures/steering.md`(手順書)の完了検査の説明に、0件のときの挙動と、その場合のPR本文の扱い(手順そのもの)を追加する。記録例外の「一覧・台帳の値の更新」にはあたらない。
- 基準4: 満たす。従来は終了コード2(エラー)だった状態だけを、終了コード0(スキップを表示)に緩める。日付付きのステアリングが1件以上あるときと、明示した対象の解決は従来どおりで、tasklistの形式も変えない。

**結論**: 通常パス(基準3を満たさないため)。

## G3受け入れ判定

- **不要**。変更するのはスクリプト(`scripts/steering_lint.py`)、テスト、手順書の本文(`docs/procedures/steering.md`)だけで、スキル・エージェント・コマンドの定義メタデータ(frontmatter・ファイル名・配置)、権限設定、フック定義・登録、ハーネス設定ファイルは変更しない(add-feature手順ステップ4の「不要」に該当)。

## 背景

派生プロジェクト task3 の R1(setup-project の直後)で、必須の品質ゲート(`uv run python3 scripts/local_quality_gate.py`)が、steering lint(`--require-complete`)で終了コード2となって止まった。原因は `resolve_completion_target` が、対象が latest で日付付きのディレクトリが0件のとき `ValueError("完了検査対象のステアリングがありません")` を出し、`main` がこれを終了コード2にすることである。品質ゲートは steering lint を `--require-complete` 付きで固定して呼ぶため、配布直後・setup-project 直後の状態では必ず失敗する。R2(add-feature の後)では日付付きのステアリングがあるため全緑で通ることを確認済み(neo#56 の追記)。

## ユースケースの軸

配布テンプレートから作った直後、または setup-project の直後(まだ add-feature を一度も行っていない)の派生プロジェクトで、エージェントと利用者が、必須のローカル品質ゲートを全緑で通し、スキップが起きたことを出力から読み取れる。

## 実装対象の機能

### 1. 完了検査の挙動の変更(`scripts/steering_lint.py`)

- `--require-complete`(対象が既定の latest)で、日付付きのステアリングが0件のとき: エラーにせず、完了検査(G1)をスキップする。通常規則の検査はこれまでどおり実行する
- スキップしたことを、必ず標準出力に表示する(`steering lint: 完了検査をスキップしました（日付付きのステアリングが0件）`)
- 明示した対象(名前・パス)が見つからない場合は、従来どおり終了コード2
- 日付付きのステアリングが1件以上あるときは、従来どおり、最新のものが完了していなければ失敗する

### 2. テストの追加(`tests/lint/test_steering_lint.py`、`tests/scripts/test_local_quality_gate.py`)

- 0件(`.steering/example/` だけ)で `--require-complete` が終了コード0になり、スキップの表示が出る
- 完了検査を要求しない通常プロファイルでは、スキップの表示が出ない
- 0件で明示した対象を指定すると、終了コード2のまま
- ローカル品質ゲートが、0件の状態で steering lint を通す(実物の steering lint を呼ぶ)

### 3. 手順書の更新(`docs/procedures/steering.md`)

- 完了検査の説明に、0件の状態ではスキップされ表示されることと、その場合のPRの扱い(PR本文に、ステアリングがなく完了検査の対象がない旨を書く)を1〜3行で書く

## 受け入れ条件

- [ ] 日付付きのステアリングが0件で、`steering_lint.py --require-complete` が終了コード0で、スキップの表示が出る
- [ ] 明示した対象が見つからないときは、従来どおり終了コード2
- [ ] 日付付きのステアリングが1件以上あるとき、最新のものが未完了なら、従来どおり失敗する
- [ ] ローカル品質ゲートが、日付付きのステアリングが0件の状態で、全緑で通る(テストで確認し、一時プロジェクトで実際にゲートを実行して観察する)
- [ ] 関連するテストが追加され、すべて通る。ローカル品質ゲートが全緑
- [ ] `docs/procedures/steering.md` に、0件のときの挙動とPRの扱いが書かれている
- [ ] G3の要否を手順の基準で判定し、理由を記録している(上記「G3受け入れ判定」)

## スコープ外

- `docs/procedures/add-feature.md` など、add-feature 関連の手順書の編集(U3 の範囲)
- setup-project 手順の変更、PRテンプレートの変更(design.md の代替案を参照)
- `steering_lint.py` の他の検査規則、`local_quality_gate.py` のコマンド構成の変更
- リリース、neo#56 以外の Issue の内容
- ブランチ `fix/setup-project-template-residue` への干渉

## 参照ドキュメント

- `docs/procedures/add-feature.md` / `docs/procedures/steering.md`
- neo#56: https://github.com/kanan4gh/project-uroboros-neo/issues/56
