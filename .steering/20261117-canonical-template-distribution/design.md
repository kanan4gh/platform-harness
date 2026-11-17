# 設計書

## アーキテクチャ概要

正典repositoryのrelease tagが指すGit treeを入力とし、exact allowlist manifestで選択したblobだけを一時領域へ展開する。配布向けに必要な差分はmanifest内の前提条件付き変換として適用し、契約検証とprovenance metadataの付与後に空の出力directoryへ移す。

```text
platform-harness release tag
        |
        v
Git tree検証 ---- origin / tag / commit / mode / pathをfail-closed検査
        |
        v
exact allowlist manifest
        |
        +---- required / forbidden / transformation前提条件
        v
一時staging directory ---- provenance metadata付与・契約検証
        |
        v
生成済み配布物 ---- ローカル品質ゲート・決定性比較・Git追跡契約
        |
        v  (正典化PRマージ・Issue close・release後のみ)
platform-harness-template
```

## コンポーネント設計

### 1. 配布manifest

**責務**:

- 配布するfile setをexact pathで固定する。
- required path、canonical-only forbidden path/prefix、配布向け変換を宣言する。
- include集合・禁止集合・metadata予約path・変換対象の整合性を機械検証可能にする。

**実装の要点**:

- allowlistはソート済み・重複なしのPOSIX相対pathに限定する。
- 変換は`replace_exact_once`またはmarker固定の切り詰めに限定し、前提不一致で失敗する。
- `.gitignore`のcanonical steering除外を生成物だけから除去する。
- 正典側でのみ存在する文書への参照は公開URLまたは配布向け説明へ変換する。

### 2. 配布生成CLI

**責務**:

- release tagとoriginを検証し、Git object databaseから対象blobを読む。
- manifest変換、provenance生成、出力契約検証、決定的な書き出しを行う。
- 不完全な成果物や既存出力の上書きを防ぐ。

**実装の要点**:

- branch名や相対refを受け付けず、`refs/tags/<tag>^{commit}`だけを解決する。
- working treeをsourceにせず、tagのtree entriesとblobを読む。
- 通常fileと実行可能fileだけを許可し、symlink・submodule・未知modeを拒否する。
- 一時directoryで完成・検証してから空の出力directoryへ移す。
- source repository/tag/commit、publisher repository/revision、manifest schema versionをmetadataへ記録する。

### 3. 契約テスト

**責務**:

- manifestとbuilderの正常系・異常系を固定する。
- 実manifestがcanonical-only資産を漏らさないことを検証する。
- 2回生成の一致と、利用者steeringの通常Git追跡を観察する。
- 公開手順の危険な順序が逆転しないことを構造契約で固定する。

**実装の要点**:

- 「`docs/ideas/`という概念説明」と「配布されない具体的ローカルfileへの参照」を区別し、過剰検出しない。
- output既存内容、origin不一致、非tag ref、欠落path、変換前提不一致、unsafe path、symlink、未対応modeを異常系に含める。

### 4. 正典・配布案内と公開手順

**責務**:

- `platform-harness`と`platform-harness-template`の役割を利用者・保守者へ明示する。
- 初回公開、継続更新、rollbackを人が開始する安全なローカル手順として定義する。

**実装の要点**:

- 正典化PRのマージ、Issue close、release/tag作成を外部変更の前提にする。
- 新templateの検証・有効化後に旧template設定を解除する。
- force-push、tag差し替え、生成物への直接修正を禁止する。
- 実際のrepository作成・settings変更は本PR中に実行しない。

## データフロー

### 配布生成

1. source checkoutのoriginと指定tagを検証し、完全commit OIDを解決する。
2. tag treeを列挙し、manifestのinclude pathとGit modeを検証する。
3. blobを一時stagingへ展開し、前提条件付き変換を順に適用する。
4. provenance metadataを生成する。
5. required/forbidden/file set/steering構成を検証する。
6. 空の出力directoryへ完成物を移す。

### 初回公開

1. 正典化PRのマージ、Issue close、release/tagを確認する。
2. clean cloneから2回生成・比較し、生成物内品質ゲートとGit追跡契約を確認する。
3. 空の`platform-harness-template`を作成し、検証済み成果物を初回pushする。
4. GitHub上のtreeとlocal成果物を照合する。
5. 新repositoryのtemplate設定を有効化する。
6. 利用可能性を確認してから正典repositoryのtemplate設定を解除する。

## エラーハンドリング戦略

- manifest、tag、origin、Git entry、変換、出力契約の不一致は`DistributionError`で停止する。
- 既存内容を持つoutputは変更せず拒否する。
- 生成中の失敗は一時stagingだけを破棄し、部分成果物を公開しない。
- GitHub側の初回公開失敗時は旧template設定を維持し、新repositoryを削除して隠蔽しない。

## テスト戦略

### ユニット・契約テスト

- manifest schema、path正規化、集合整合性、変換前提条件。
- tag/origin/tree entry/outputのfail-closed動作。
- provenance、実行bit、決定性、禁止資産、steering file set。
- 通常の`git add -A`による利用者steering追跡。
- 公開手順のマージ/release前禁止、settings変更順、rollback契約。

### 実挙動検証

- 現在の正典commitに一時tagを付けたclean local cloneから実manifestで2回生成する。
- file set、内容、実行bit、metadata、禁止path 0件を観察する。
- 生成物をGit repositoryとして初期化し、fixture steeringでローカル品質ゲートを実行する。
- 新規日付付きsteeringが通常の`git add -A`で追跡されることを観察する。

## 依存ライブラリ

新規外部依存は追加しない。Python標準ライブラリとGit CLIを使用する。

## ディレクトリ構造

```text
distribution/
└── template-manifest.json
scripts/
└── build_template_distribution.py
tests/
├── distribution/
│   └── test_template_distribution.py
└── procedures/
    └── test_template_distribution_procedure.py
docs/procedures/
└── template-distribution.md
```

既存の`README.md`、`docs/harness-guide.md`、`docs/procedures/setup-project.md`も更新する。

## 実装の順序

1. 既存ドラフトとIssue #64の要求を照合し、manifest契約を確定する。
2. builderの安全性・決定性・provenanceを完成させる。
3. 正常系・異常系・実manifest・Git追跡の契約テストを完成させる。
4. README、harness guide、setup案内、公開手順を一貫させる。
5. 4段検証、振り返り、明示steering付き最終品質ゲートを実施する。
6. commit・push・PRを作成する。外部repository公開はマージ・release後の手順に残す。

## セキュリティ考慮事項

- allowlist、正規化path、Git mode、origin、tagをfail-closed検証し、path traversalと意図しないfile混入を防ぐ。
- dirty working treeや差し替え可能なbranchをsourceにしない。
- 出力先の非空directoryを上書きしない。
- GitHub settingsは対象repositoryと現在値を取得し直してから変更する。

## パフォーマンス考慮事項

配布対象は小規模なtext/script集合である。正確性と決定性を優先し、全対象blobとdigestを毎回検証する。

## 将来の拡張性

manifest schema versionを持たせ、将来の変換種別は既存schemaが未知値を拒否する前提で明示的に追加する。ハーネス別配布repositoryへの分割は本変更に含めない。
