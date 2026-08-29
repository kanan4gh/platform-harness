# 要求内容

## 概要

振り返り本文のコード表記（フェンス付きコードブロックとインラインコード）を、C4プレースホルダ検査の対象外にする。あわせて `steering_lint.py` と `steering_state.py` に重複している振り返りプレースホルダ抽出を共有関数へ集約する。

- **関連Issue**: https://github.com/kanan4gh/platform-harness/issues/55
- **使用ハーネス**: Claude Code
- **軽量パス**: 適用

## パス判定（**通常パス・軽量パスのどちらでも必ず記載する**。基準の正は add-feature 手順のステップ4）

- [x] 1. 既存パターンの踏襲のみで、新しいアーキテクチャ要素・新規依存を導入しない
- [x] 2. 変更対象が3ファイル以下(テスト除く)
- [x] 3. 対象文書の更新が不要
- [x] 4. データ形式・API契約の破壊的変更がない

**判定理由**:

- 基準1: 満たす。既存の `strip_code_fences()` と同じ「検査対象外の範囲を空白化してから正規表現をかける」パターンを踏襲する。標準ライブラリ以外の依存も新しい層も追加しない。
- 基準2: 満たす。変更対象は `scripts/steering_lint.py` と `scripts/steering_state.py` の2ファイル。`tests/lint/test_steering_lint.py` と `tests/lint/test_steering_state.py` は基準の除外対象。
- 基準3: 満たす。`docs/procedures/steering.md` と `docs/procedures/add-feature.md` は「未完了・振り返り欠落・プレースホルダーがあれば遷移は失敗する」と定めるのみで、その規定自体は変わらない。手順・テンプレート・永続ドキュメント・アダプタの規範記述はいずれも変更しない。記録例外は使用しない。
- 基準4: 満たす。CLIの引数、tasklistの状態形式、`TransitionError` とViolationのメッセージ契約は変えない。検査は緩む方向に動くが、テンプレート `docs/procedures/templates/tasklist.md` のプレースホルダは全てバッククォート外の裸記述であり、本検査が本来捕捉すべき真陽性の検出力は変わらない。

## G3受け入れの要否判定

- **判定**: 不要
- **理由**: 変更対象はハーネス中立スクリプトと回帰テストのみである。スキル・エージェント・コマンドの定義メタデータ、権限設定、フック定義・登録、ハーネス設定ファイルは変更しない。

## 背景

Issue #55 は、`PLACEHOLDER_PATTERN` が振り返り本文中のインラインコードに含まれる波括弧を未置換テンプレートと誤検出すると報告している。dev-tasks2-py への v1.6.1 展開（#52）で2件発生し、2件目は「誤検出を報告する文章を書くこと自体が誤検出を誘発する」再現になった。

着手時の実装確認で、Issueの記述より問題範囲が広いことが判明した。

- Issueは「`strip_code_fences()` はフェンスを除去するが、インラインコードは対象外」としているが、**C4のプレースホルダ検査は `strip_code_fences()` を一度も呼んでいない**（`scripts/steering_lint.py:292-297` が生テキストを partition してそのまま `findall` している）。実測でフェンス付きコードブロック内の `{"key": 1}` も検出された。
- 同じ抽出ロジックが `scripts/steering_state.py:218-226` にも重複しており、`steering_lint.py` 側だけを直すと `steering_state.py complete` の拒否（Issueが報告した実際の症状）が残る。

したがって修正は「インラインコードの除外」に加え、「C4へのフェンス除去の適用」と「両呼び出し箇所の共有関数への集約」を含む。

## ユースケースの軸

> ハーネス利用者が、振り返りにコード片を正確に引用したまま `complete` 遷移とローカル品質ゲートを通過できる。

## 実装対象の機能

### 1. 振り返りプレースホルダ抽出の共有関数化

- `steering_lint.py` に `find_retrospective_placeholders(text) -> list[str]` を追加する
- 振り返りセクションを取り出し、フェンス付きコードブロックとインラインコードを空白化してから `PLACEHOLDER_PATTERN` を適用する
- `check_retrospective()` と `steering_state.py` の `complete_text()` を、この関数の呼び出しへ置き換える

### 2. インラインコードの空白化

- `strip_inline_code(text)` を追加し、同一行内で同じ長さのバッククォート列に挟まれた範囲を同じ長さの空白へ置換する
- 閉じられていないバッククォートは置換せず、波括弧は従来どおり検出する（fail-closed）

## 受け入れ条件

### 振り返りプレースホルダ抽出の共有関数化

- [ ] `check_retrospective()` と `complete_text()` が同じ抽出関数を使い、判定が一致する
- [ ] 振り返りセクションが無い場合の既存の挙動（C4違反 / TransitionError）が変わらない
- [ ] `PLACEHOLDER_PATTERN` 自体の正規表現は変更しない

### インラインコードの空白化

- [ ] バッククォートで囲まれた波括弧は違反にならない
- [ ] バッククォートの外にある波括弧は従来どおり違反になる
- [ ] フェンス付きコードブロック内の波括弧は違反にならない
- [ ] 閉じられていないバッククォートの後ろの波括弧は違反になる
- [ ] `steering_state.py complete` が、コード表記を含む振り返りで成功する

## 成功指標

- Issue #55 の再現記述（`{parent}_{name}` を含む振り返り行）が、言い換えなしで `complete` 遷移とローカル品質ゲートを通過する
- 既存テストが1件も退行しない

## スコープ外

- `PLACEHOLDER_PATTERN` の文字クラスを絞る方向の変更（outfit-studio の派生固有差分が採った方式。`{parent}` のような英数字のみのプレースホルダには効かず、根本解決にならない）
- 振り返り以外（requirements.md / design.md 等）へのプレースホルダ検査の拡張
- 派生プロジェクトへの展開。本修正のリリース後に、別途 `docs/procedures/derived-project-rollout.md` に従って実施する

## 参照ドキュメント

- `docs/procedures/steering.md` - steering 手順（C4の位置づけ）
- `docs/procedures/add-feature.md` - ステップ7終端の `complete` 遷移
- `docs/procedures/templates/tasklist.md` - 振り返りテンプレート（真陽性の形）
