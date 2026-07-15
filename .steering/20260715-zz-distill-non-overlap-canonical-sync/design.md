# 設計書

## アーキテクチャ概要

環流PRの非重複を文章上の注意事項だけでなく、標準ライブラリ製のローカルCLIで決定論的に検査する。`distill`手順が候補の棚卸し・PR分割・正典同期を定義し、CLIが予定集合とGit実差分の積集合を同じ判定規則で評価し、テストが手順と実装の契約を固定する。

```text
distillレポート
  ├─ 環流候補
  └─ 環流PR計画（安定識別子・予定変更ファイル・branch）
             │
             ├─ 計画時: --set NAME=PATH
             │
             └─ 実装後: --base BASE --ref NAME=GIT_REF
                         │
                         ▼
             check_pr_file_overlap.py
              ├─ 入力集合を正規化
              ├─ 全組合せの積集合を計算
              └─ PASS / 重複パス付きFAIL
                         │
                         ▼
       統合・再分割・共通前提の先行正典化
                         │
                         ▼
       platform-harness PR → release → 派生側同期
```

## コンポーネント設計

### 1. `docs/procedures/distill.md`

**責務**:

- 環流候補をPR単位へまとめる前の予定集合検査を定義する。
- 実装後、baseとの差分から得た実集合をPR作成前に再検査する。
- 重複時の解消方法と、PR番号・マージ順へ依存しない完了条件を定義する。
- platform-harnessで中立化・リリースした正典を派生プロジェクトへ同期する順序と記録項目を定義する。

**実装の要点**:

- 蒸留レポート形式へ「環流PR計画」を追加し、各計画に安定識別子、Issue URL、branch、候補、予定変更ファイルを持たせる。
- PR番号は計画入力に使わず、全PR作成後に実在番号を追記する。
- 全PR組合せの積集合が空の場合だけ合格とする。重複がある状態でマージ順を固定する案は不合格のまま扱う。
- 重複時は、同じ責務の候補を統合する、責務単位で再分割する、共通前提だけを先に正典化して残りを再計画する、のいずれかを記録する。
- activeな環流PRが1件だけの場合も、他のactiveな環流branchがないことを棚卸し記録へ残す。比較対象を省略しただけのPASSにしない。
- 同期記録には同期元release tagまたはcommit、同期対象、派生固有差分、派生側の検証結果を必須化する。

### 2. `scripts/check_pr_file_overlap.py`

**責務**:

- 名前付きファイル集合の全組合せを比較し、重複パスを安定順で報告する。
- 計画時の明示パス集合と、実装後のGit branch差分集合を同じ内部表現へ変換する。
- 外部サービスやshellを使わず、ローカルで再現可能な終了コードを返す。

**CLI設計**:

予定集合モード:

```bash
python3 scripts/check_pr_file_overlap.py \
  --set issue-a=AGENTS.md \
  --set issue-a=docs/harness-guide.md \
  --set issue-b=docs/procedures/distill.md
```

実集合モード:

```bash
python3 scripts/check_pr_file_overlap.py \
  --base origin/main \
  --ref issue-a=feature/a \
  --ref issue-b=feature/b
```

| 引数 | 規則 |
|---|---|
| `--set NAME=PATH` | 同じNAMEを複数回指定して予定ファイル集合を構成する |
| `--ref NAME=GIT_REF` | NAMEごとに`git diff --name-only BASE...GIT_REF --`を実行して実集合を得る |
| `--base GIT_REF` | `--ref`モードで必須。比較の共通base |
| モード | `--set`と`--ref`は相互排他。各モードで2つ以上の名前付き集合を必須とする |

**終了コード**:

| 終了コード | 意味 |
|---|---|
| `0` | 全組合せの積集合が空 |
| `1` | 1組以上に重複があり、重複した組とパスを表示 |
| `2` | 引数不正、集合不足、Git ref不正、Git差分取得失敗 |

**判定アルゴリズム**:

1. `NAME=VALUE`を最初の`=`で分割し、空のNAME / VALUEと`-`で始まるGit refを拒否する。
2. パスをリポジトリルート相対のPOSIX表記へ限定する。空白を除去し、先頭`./`、絶対パス、親参照、末尾`/`、連続`//`、バックスラッシュを拒否する。同一パスを除き、名前・パスを辞書順に正規化する。文字大小は区別する。
3. `itertools.combinations`で全候補ペアを作る。
4. 各ペアの集合積を辞書順で計算する。
5. 重複が1件でもあれば全重複を表示して`1`、なければ比較した集合数・ペア数とともに`0`を返す。
6. Gitは`subprocess.run`へ引数配列で渡し、`shell=False`、ネットワーク処理なしとする。

### 3. 回帰テスト

**責務**:

- CLIの集合構築、全ペア比較、安定出力、終了コード、Git差分取得、異常系を検証する。
- `distill`手順から予定・実集合の2段検査、空集合条件、重複解消、PR番号禁止、正典同期順序が欠落しないことを検証する。

**追加ファイル**:

- `tests/scripts/test_check_pr_file_overlap.py`
- `tests/procedures/test_distill_procedure.py`

## データフロー

### 溜まった環流候補をPRへ分割する

```text
1. distillが候補ごとの変更対象ファイルを抽出する
2. 保守者がIssue URLとbranch名を安定識別子として環流PR計画へまとめる
3. --setモードで全予定集合を比較する
4. 重複があれば計画を統合・再分割し、空集合になるまで再実行する
5. 空集合になった計画だけをfeature branchで実装する
```

### 既存PRがある状態で新しい環流PRを追加する

```text
1. activeな環流Issue / branchを棚卸しする
2. 既存branchの実集合と新候補の予定集合を計画表へ記録する
3. 予定集合として比較し、重複があれば新PRを作らず解消する
4. 実装後、全branchを共通baseに対する--refモードで再比較する
5. 実集合も空の場合だけPRを作成する
```

### platform-harnessから派生プロジェクトへ同期する

```text
1. 派生側の振り返りをdistillで環流候補にする
2. platform-harnessで固有値を除去し、中立コアまたは適切なアダプタへ配置する
3. platform-harnessのローカル品質ゲートを通し、PRをマージしてreleaseを作る
4. 派生側で同期元tag / commit、対象、残す固有差分を記録して同期する
5. 派生側のローカル品質ゲートと必要な対話型受け入れを実行する
```

## エラーハンドリング戦略

### 入力エラー

- `NAME=VALUE`形式不正、集合数不足、相互排他違反はusageと具体的理由をstderrへ出して`2`終了する。
- 同じNAMEの`--set`はファイル追加として集約し、同一パスは1件へ正規化する。
- 同じNAMEの`--ref`重複、`--set`と`--ref`の混在、空集合は曖昧なため拒否する。

### Gitエラー

- 存在しないbase / ref、Git管理外、`git diff`非0終了はfail-closedで`2`とし、非重複合格へ変換しない。
- Git stderr本文は表示せず、対象NAME、ref、exit codeだけの固定診断へ要約する。

### 重複検出

- 重複は実行異常ではなく検査不合格として`1`を返す。
- 全ペアを最後まで検査し、最初の1件だけで停止せず、解消に必要なパスをまとめて表示する。

## テスト戦略

### ユニットテスト

- 予定集合の非重複合格、2組以上の重複、同一パス正規化、安定ソートを検証する。
- 引数形式不正、集合不足、モード混在、NAME重複、空refを検証する。
- Git runnerを差し替え、base / refごとの実集合取得、Git失敗のfail-closed、`shell=False`を検証する。

### 統合テスト

- CLIの`--set`モードをsubprocessで実行し、exit `0` / `1` / `2`とstdout / stderrを確認する。
- 現行Issue #15の予定変更集合を、他のactive環流PR計画と比較する。比較対象がなければactive環流branchなしの棚卸し証跡を残す。
- 実装後に共通base `origin/main`とfeature branchの実変更集合を取得し、他のactive環流branchとの積集合が空であることを確認する。
- `uv run python3 scripts/local_quality_gate.py`で全既存検証を含めて合格させる。

### ドキュメント構造テスト

- 環流PR計画、予定集合と実集合の2段検査、空集合のみ合格、3つの重複解消方法を確認する。
- PR番号の事前予測禁止、Issue URL / branchの安定識別子、全PR作成後の実在番号追記を確認する。
- 正典同期順序、release tag / commit記録、中立化=テンプレート化、派生側検証を確認する。

## 依存ライブラリ

追加しない。Python標準ライブラリ（`argparse`、`itertools`、`subprocess`、`collections`）とローカルGitだけを使用する。

## ディレクトリ構造

```text
docs/procedures/
└── distill.md                         # 非重複検査・PR計画・正典同期手順を追加
scripts/
└── check_pr_file_overlap.py           # 予定集合 / Git実集合の決定論的検査CLI
tests/
├── procedures/
│   └── test_distill_procedure.py      # 手順の必須契約を検証
└── scripts/
    └── test_check_pr_file_overlap.py  # CLI・集合演算・Git異常を検証
```

## 実装の順序

1. 非重複チェッカーの集合モデル・CLI・終了コードをテスト駆動で実装する。
2. `distill.md`へ環流PR計画、予定・実集合検査、重複解消、PR識別規則を追加する。
3. `distill.md`へplatform-harness正典化と派生プロジェクト同期ルートを追加する。
4. 構造テストを追加し、手順とCLI例の整合を固定する。
5. 実データで予定集合・実集合検査を行い、4段検証とローカル品質ゲートを完了する。

## セキュリティ考慮事項

- Git refとパスをshell文字列へ連結せず、`subprocess.run`の引数配列で実行する。
- Git refが`-`で始まる入力を拒否し、オプション注入を防ぐ。
- GitHub認証、API、Actions、ネットワーク、LLM headless modeを検査経路に含めない。
- 診断には候補名・ref・変更パスだけを表示し、ファイル本文や環境変数を出力しない。

## パフォーマンス考慮事項

- 候補数を`n`、候補あたりの変更パス数を`m`とすると、比較は`O(n² × m)`。distillで扱う少数PRを前提とし、全ペア表示を優先する。
- Git差分は候補refごとに1回だけ取得し、ペアごとに再実行しない。

### 単独PRの扱い

- activeな環流計画またはbranchが1件だけの場合、CLIは2集合未満を検査不能として拒否する。
- 保守者はCLIによる疑似PASSを作らず、棚卸し日時・情報源・base/refのcommit OID・実変更ファイルを記録し、「比較対象なし（PASSではない）」として各段を完了する。
- Git renameは`--no-renames`で旧パスと新パスの双方を変更集合へ含める。`-z`のNUL区切りでパスを取得し、Git quoteに依存せずUnicodeファイル名を保持する。

## 将来の拡張性

- JSON出力、計画manifest入力、GitHub UI連携は将来追加できるが、今回の必須経路には含めない。
- 同期CLIの自動化は、正典・派生固有差分の競合解決モデルが確立した後の独立Issueとする。
