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
- [ ] 実装後のfeature branchについて共通baseから実変更集合を取得する
  - [ ] 他のactive環流branchとの全組合せが非重複であることを確認する
- [x] 検証中のGitHub Actions自動runが0件であることを記録する
- [x] 検証中の有料LLM headless mode起動が0件であることを記録する

### 受け入れ記録

- **active環流branch棚卸し**: 2026-07-15、ローカルbranch・remote-tracking branchともにmain未マージはIssue #15の作業branch以外0件。作業branchはmainと同一commitから開始しており、実装前棚卸し時点では未コミット差分のみ。
- **予定集合**: `docs/procedures/distill.md`、`scripts/check_pr_file_overlap.py`、`tests/procedures/test_distill_procedure.py`、`tests/scripts/test_check_pr_file_overlap.py`。ステアリング3ファイルは履歴としてforce-addする。
- **外部有料自動化**: GitHub Actions自動run 0件、有料LLM headless mode起動 0件。検証はローカルコマンドと対話型Codexだけで実施。

## フェーズ6: 4段検証

- [x] 独立レビューの指摘を修正する
  - [x] 単独PR時は棚卸し証跡で「比較対象なし（PASSではない）」として完了する規則を追加する
  - [x] canonicalなリポジトリ相対POSIXパスだけを受け付け、renameの旧新パスを含める
  - [x] Git stderr本文を出力せず固定診断へ変更する
  - [x] 未設計だった公開`--root`引数を削除する
  - [x] `--set` / `--ref`混在、空ref、非正規パスの回帰テストを追加する
  - [x] active refの鮮度・OID記録と派生側同期記録テンプレートを追加する
  - [x] Git実集合をNUL区切りで取得し、UnicodeパスがGit quoteで拒否される不具合を修正する

- [ ] 段1・静的検証を完了する
  - [x] `uv run pytest`を実行する（129件合格）
  - [x] `uv run ruff check .`を実行する
  - [x] `uv run basedpyright`を実行する（0 errors）
  - [ ] `python3 scripts/steering_lint.py`を実行する
  - [ ] `uv run python3 scripts/local_quality_gate.py`を実行する
- [x] 段2・CLIの予定集合モードと実集合モードを実行し、出力とexit codeを観察する（予定集合exit 0 / 1 / 2、実GitのUnicodeパスでexit 0、重複履歴refsでexit 1）
- [x] 段3・変更差分のコードレビューを実施し、正当な指摘を修正する（stderr、単独PR、canonical path、ref鮮度、Unicode path等を修正）
- [x] 段4・ステアリングと実装のスペック準拠検証を独立した文脈で実施する（最終判定: 準拠）
- [x] `docs/procedures/distill.md`のドキュメントレビューを独立した文脈で実施する（最終評価4.8/5、承認可）

## フェーズ7: 完了処理

- [ ] requirements.mdの受け入れ条件がすべて満たされたことを確認する
- [ ] 実装後の振り返りを本ファイルへ記録する
- [ ] Issue #15を参照するConventional Commitを作成する
- [ ] feature branchをpushしてPRを作成する
- [ ] PR URLと検証結果をユーザーへ報告する

---

## 実装後の振り返り

### 実装完了日

{YYYY-MM-DD}

### 計画と実績の差分

- **計画と異なった点**: {実装後に記入}
- **新たに必要になったタスク**: {実装後に記入}
- **技術的理由でスキップしたタスク**: {該当時に理由と代替実装を記入}

### 学んだこと

- **技術的な学び**: {実装後に記入}
- **プロセス上の改善点**: {実装後に記入}

### 次回への改善提案

- {実装後に記入}

### リリース判断

**前提条件の確認**:

- [ ] 全テスト通過
- [ ] リントエラーなし
- [ ] リリースノートに記載すべき変更内容が整理されている

| 観点 | 評価 |
|---|---|
| 今回の変更はユーザーにとって価値のあるまとまりか | {Yes / No / 保留} |
| 未解決の重大バグはないか | {なし / あり: 内容} |
| 適切なバージョン種別 | {MAJOR / MINOR / PATCH / リリース不要} |

**提案**: {実装後に記入}
