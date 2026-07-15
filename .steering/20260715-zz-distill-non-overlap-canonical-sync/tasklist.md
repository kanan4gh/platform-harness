# タスクリスト

## 🚨 タスク完全完了の原則

**このファイルの全タスクが完了するまで作業を継続すること**

- 全タスクを`[x]`にし、完了・スキップは実態に合わせて即時記録する
- 大きすぎるタスクはルールAで分割する
- 技術的理由で不要になったタスクだけ、理由を明記してルールBでスキップする

## フェーズ1: 非重複チェッカーのテスト設計

- [x] `tests/scripts/test_check_pr_file_overlap.py`を追加する
  - [x] 予定集合が非重複の場合にexit 0と安定したPASS出力になるテストを追加する
  - [x] 複数ペアの重複パスをすべて安定順で表示してexit 1になるテストを追加する
  - [x] 同一NAMEの予定パス追加・重複除去・辞書順正規化を検証する
  - [x] 集合不足、形式不正、空値、モード混在がexit 2になるテストを追加する
  - [x] Git実集合取得とbase/refの引数配列を検証する
  - [x] Git失敗、空集合、不正refがfail-closedでexit 2になるテストを追加する
  - [x] subprocessが`shell=False`かつネットワーク処理なしで呼ばれることを検証する

## フェーズ2: 非重複チェッカーの実装

- [x] `scripts/check_pr_file_overlap.py`を追加する
  - [x] `--set NAME=PATH`による予定集合モードを実装する
  - [x] `--base`と`--ref NAME=GIT_REF`によるGit実集合モードを実装する
  - [x] 入力検証、パス正規化、全ペア積集合判定を実装する
  - [x] exit 0 / 1 / 2とstdout / stderrの契約を実装する
  - [x] Gitを引数配列・`shell=False`で実行し、不正refとGit失敗を拒否する
- [x] チェッカー単体テストを実行し、失敗を修正する（16件合格）

## フェーズ3: distill手順の更新

- [x] `docs/procedures/distill.md`へ環流PR計画の記録形式を追加する
  - [x] Issue URL、branch、候補、予定変更ファイルを安定識別子とともに定義する
  - [x] activeな環流Issue / branchの棚卸し規則を定義する
- [x] 予定集合と実集合の2段非重複検査を追加する
  - [x] 全組合せの積集合が空の場合だけ合格とする
  - [x] 重複時の統合・再分割・共通前提の先行正典化を定義する
  - [x] スタックPRやマージ順固定を代替策として認めない
- [x] PR番号と独立性の規則を既存注記へ統合する
  - [x] PR番号の事前予測を禁止する
  - [x] 全PR作成後に実在番号で相互参照を追記する
  - [x] 単独検証・レビュー・ロールバックと任意順マージを完了条件にする
- [x] platform-harness正典から派生プロジェクトへの同期ルートを追加する
  - [x] 中立化、PRマージ、release、派生同期の順序を定義する
  - [x] 同期元tag / commit、同期対象、派生固有差分、検証結果の記録を定義する
  - [x] 中立化が再利用可能なテンプレート化を兼ねる原則を記載する
  - [x] 派生側ローカル品質ゲートと必要な対話型受け入れを定義する

## フェーズ4: 手順の構造テスト

- [x] `tests/procedures/test_distill_procedure.py`を追加する
  - [x] 環流PR計画と予定・実集合の2段検査を固定する
  - [x] 空集合のみ合格と3つの重複解消方法を固定する
  - [x] PR番号予測禁止、安定識別子、実在番号追記、任意順マージを固定する
  - [x] 正典同期順序、同期記録、中立化原則、派生側検証を固定する
  - [x] GitHub Actions、GitHub API、LLM headless modeを必須経路にしない境界を固定する
- [x] 手順構造テストを実行し、失敗を修正する（対象22件合格、ruff合格）

## フェーズ5: 実データによる受け入れ確認

- [x] ~~Issue #15の予定変更ファイル集合をチェッカーへ入力して結果を記録する~~（比較対象となるactive環流branchが0件であり、チェッカーは設計どおり2集合未満を検査不能として拒否するため、単独集合の疑似PASSは作らない）
- [x] 他のactive環流Issue / branchを棚卸しする
  - [x] ~~比較対象がある場合は全予定集合の非重複を確認する~~（active環流branchが0件のため不要）
  - [x] 比較対象がない場合はactiveな環流branchなしの証跡を記録する（`git branch --no-merged main`および`git branch -r --no-merged origin/main`の出力が空）
- [x] 実装後のfeature branchについて共通baseから実変更集合を取得する
  - [x] ~~他のactive環流branchとの全組合せが非重複であることを確認する~~（Issue #15以外のactive環流branchが0件。手順どおりCLIで疑似PASSを作らず「比較対象なし（PASSではない）」として完了）
- [x] 検証中のGitHub Actions自動runが0件であることを記録する
- [x] 検証中の有料LLM headless mode起動が0件であることを記録する

### 受け入れ記録

- **active環流branch棚卸し**: 2026-07-15、ローカルbranch・remote-tracking branchともにmain未マージはIssue #15の作業branch以外0件。作業branchはmainと同一commitから開始しており、実装前棚卸し時点では未コミット差分のみ。
- **予定集合**: `docs/procedures/distill.md`、`scripts/check_pr_file_overlap.py`、`tests/procedures/test_distill_procedure.py`、`tests/scripts/test_check_pr_file_overlap.py`。ステアリング3ファイルは履歴としてforce-addする。
- **外部有料自動化**: GitHub Actions自動run 0件、有料LLM headless mode起動 0件。検証はローカルコマンドと対話型Codexだけで実施。
- **実集合**: 2026-07-15、情報源はローカルrefと既存remote-tracking ref。base `main` / `origin/main` = `5ed97c1781c4debaa4f6b94e5552bd647fabd5f0`、Issue #15 branch = `484bf350b396dad6c0174378397cb23a727d2360`。`git branch --no-merged main`はIssue #15 branchのみ、`git branch -r --no-merged origin/main`は空。実変更7ファイル、比較対象なし（PASSではない）。ネットワークfetchは必須経路にせず、ローカルの`origin/main`が作業開始baseと一致することを確認。

## フェーズ6: 4段検証

- [x] 独立レビューの指摘を修正する
  - [x] 単独PR時は棚卸し証跡で「比較対象なし（PASSではない）」として完了する規則を追加する
  - [x] canonicalなリポジトリ相対POSIXパスだけを受け付け、renameの旧新パスを含める
  - [x] Git stderr本文を出力せず固定診断へ変更する
  - [x] 未設計だった公開`--root`引数を削除する
  - [x] `--set` / `--ref`混在、空ref、非正規パスの回帰テストを追加する
  - [x] active refの鮮度・OID記録と派生側同期記録テンプレートを追加する
  - [x] Git実集合をNUL区切りで取得し、UnicodeパスがGit quoteで拒否される不具合を修正する

- [x] 段1・静的検証を完了する
  - [x] `uv run pytest`を実行する（129件合格）
  - [x] `uv run ruff check .`を実行する
  - [x] `uv run basedpyright`を実行する（0 errors）
  - [x] ~~`python3 scripts/steering_lint.py`を実行する~~（macOS標準Python 3.9.6はプロジェクト要件Python 3.12の型構文を解釈できないため、`uv run`経路へ置換）
  - [x] `uv run python3 scripts/local_quality_gate.py`を実行する（内部の`uv run python3 scripts/steering_lint.py`を含む最終再実行で確認）
- [x] 段2・CLIの予定集合モードと実集合モードを実行し、出力とexit codeを観察する（予定集合exit 0 / 1 / 2、実GitのUnicodeパスでexit 0、重複履歴refsでexit 1）
- [x] 段3・変更差分のコードレビューを実施し、正当な指摘を修正する（stderr、単独PR、canonical path、ref鮮度、Unicode path等を修正）
- [x] 段4・ステアリングと実装のスペック準拠検証を独立した文脈で実施する（最終判定: 準拠）
- [x] `docs/procedures/distill.md`のドキュメントレビューを独立した文脈で実施する（最終評価4.8/5、承認可）

## フェーズ7: 完了処理

- [x] requirements.mdの受け入れ条件がすべて満たされたことを確認する
- [x] 実装後の振り返りを本ファイルへ記録する
- [x] Issue #15を参照するConventional Commitを作成する（`484bf35`）
- [x] feature branchをpushしてPRを作成する（PR #17）
- [x] PR URLと検証結果をユーザーへ報告する（最終応答で報告）

---

## 実装後の振り返り

### 実装完了日

2026-07-15

### 計画と実績の差分

- **計画と異なった点**: 独立レビューを受け、単独PRの完了規則、canonical path検証、renameの旧新パス取得、ref鮮度記録、Git stderr固定診断、Unicodeパス用NUL区切りを設計・実装へ追加した。
- **新たに必要になったタスク**: Git既定quoteによる非ASCIIパス拒否を実Gitで発見し、`git diff -z`とUnicode回帰テストを追加した。
- **技術的理由でスキップしたタスク**: Issue #15以外のactive環流branchが0件だったため、2集合を要求するチェッカーで単独集合の疑似PASSを作らず、OIDと棚卸し証跡を残して「比較対象なし（PASSではない）」とした。

### 学んだこと

- **技術的な学び**: Gitの機械可読なパス取得では表示用quoteを避け、NUL区切りを使う必要がある。`--no-renames`との併用でrenameの旧新双方を保守的な重複集合へ含められる。
- **プロセス上の改善点**: 非重複検査は2件以上の集合でのみ成立する。単独PRではPASSを捏造せず、情報源・日時・OID・比較対象なしを監査証跡として残す方が再現可能である。

### 次回への改善提案

- ファイル集合を扱う将来のローカル検査でも、Unicode・rename・単独集合・stale refを初期テスト行列へ含める。

### リリース判断

**前提条件の確認**:

- [x] 全テスト通過
- [x] リントエラーなし
- [x] リリースノートに記載すべき変更内容が整理されている

| 観点 | 評価 |
|---|---|
| 今回の変更はユーザーにとって価値のあるまとまりか | Yes |
| 未解決の重大バグはないか | なし |
| 適切なバージョン種別 | MINOR |

**提案**: PR #17マージ後、環流PR計画という新しい利用者向け機能追加としてv1.2.0を提案する。
