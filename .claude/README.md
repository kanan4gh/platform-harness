# .claude/ ディレクトリ ガイド

このディレクトリはClaude Codeのカスタマイズファイル一式です。ハーネスエンジニア（Claude Code環境の設定・拡張を行う人）向けのリファレンスです。

## ディレクトリ構成

```
.claude/
├── README.md              # このファイル
├── settings.json          # Claude Code設定（パーミッション等）
├── commands/              # スラッシュコマンド（/コマンド名で呼び出す）
│   ├── setup-project.md   # /setup-project
│   ├── add-feature.md     # /add-feature
│   └── review-docs.md     # /review-docs
├── agents/                # サブエージェント定義
│   ├── doc-reviewer.md
│   └── implementation-validator.md
└── skills/                # スキル定義（Skill()で呼び出す）
    ├── steering/
    ├── prd-writing/
    ├── functional-design/
    ├── architecture-design/
    ├── repository-structure/
    ├── development-guidelines/
    └── glossary-creation/
```

---

## settings.json

```json
{
  "defaultMode": "bypassPermissions",
  "permissions": {
    "allow": [
      "Skill(prd-writing)",
      "Skill(functional-design)",
      "Skill(architecture-design)",
      "Skill(repository-structure)",
      "Skill(development-guidelines)",
      "Skill(glossary-creation)"
    ]
  }
}
```

### 設定の意味

| 項目 | 値 | 説明 |
|------|----|------|
| `defaultMode` | `bypassPermissions` | Claudeがツールを実行する際のパーミッション確認をスキップ。ドキュメント作成スキルの連続実行をスムーズにするため |
| `permissions.allow` | スキル6つ | 上記6つのスキルは確認なしに自動実行される |

### settings.local.json について

個人環境のパーミッション設定（例: `gh issue *` の許可）は `settings.local.json` に記述します。このファイルは `.gitignore` で除外されているため、リポジトリにはコミットされません。

---

## コマンド（commands/）

スラッシュコマンドは `claude` セッション内で `/コマンド名` として呼び出します。

### `/setup-project`

**用途**: プロジェクト開始時に `docs/` 以下の6つの永続ドキュメントを対話的に作成する。

**実行タイミング**: このテンプレートから新しいリポジトリを作成した直後。

**動作フロー**:
1. `docs/ideas/` 内のファイルを読み込み、インプットとして利用
2. `prd-writing` スキルで `docs/product-requirements.md` を作成（ユーザー承認待ち）
3. 以降、`functional-design` → `architecture-design` → `repository-structure` → `development-guidelines` → `glossary-creation` の順に自動実行

**カスタマイズ方法**: `commands/setup-project.md` の「ステップ」を編集することで、作成するドキュメントの順序・内容を変更できます。

---

### `/add-feature <機能名>`

**用途**: 新機能を完全自動で実装する（ステアリングファイル作成 → 実装ループ → 検証 → 振り返り）。

**実行例**:
```
/add-feature ユーザー認証
```

**動作フロー**:
1. `.steering/YYYYMMDD-機能名/` ディレクトリを作成
2. `steering` スキル（計画モード）でステアリングファイル3点を生成
3. `tasklist.md` の全タスクが完了するまで実装ループを自動実行
4. `implementation-validator` エージェントで品質検証
5. テスト・lint・型チェックを実行
6. `steering` スキル（振り返りモード）で振り返りを記録

**重要な設計思想**: このコマンドはユーザーの介入なしに最初から最後まで自動実行するよう設計されています。`tasklist.md` の全タスク完了が完了条件です。

**カスタマイズ方法**: ステップ7「自動テストの実行」のコマンドを、プロジェクトのテストコマンドに合わせて変更してください（デフォルトは `npm test`）。

---

### `/review-docs <ドキュメントパス>`

**用途**: 特定のドキュメントの品質を詳細レビューする。

**実行例**:
```
/review-docs docs/product-requirements.md
```

**動作フロー**:
1. `doc-reviewer` エージェントを起動
2. 完全性・明確性・一貫性・実装可能性・測定可能性の5観点で評価
3. スコアと改善提案をレポートとして出力

---

## エージェント（agents/）

サブエージェントは専用のコンテキストで動作するため、メインエージェントのコンテキストを消費しません。`/add-feature` や `/review-docs` コマンドから自動的に起動されます。

### `doc-reviewer`

- **モデル**: Claude Sonnet
- **用途**: `/review-docs` コマンドから呼び出され、ドキュメントを5観点（完全性・明確性・一貫性・実装可能性・測定可能性）で評価してレポートを作成する
- **ドキュメント種別対応**: PRD・機能設計書・アーキテクチャ設計書・リポジトリ構造定義書・開発ガイドライン・用語集それぞれに特化したチェック項目を持つ

### `implementation-validator`

- **モデル**: Claude Sonnet
- **用途**: `/add-feature` コマンドの実装後検証フェーズで呼び出される。スペック準拠・コード品質・テストカバレッジ・セキュリティ・パフォーマンスを検証する
- **自動実行ツール**: lint・型チェック・テスト・ビルドを実行し、結果をレポートに含める

---

## スキル（skills/）

スキルはClaude Codeの内部で `Skill('スキル名')` として呼び出されます。各スキルは `SKILL.md`（動作定義）とテンプレートファイルで構成されています。

### `steering` スキル

**最重要スキル**。スペック駆動開発の中核を担います。

**3つのモード**:

| モード | 呼び出しタイミング | 主な動作 |
|--------|-----------------|---------|
| 計画モード | `/add-feature` 開始時 | `.steering/` にrequirements.md・design.md・tasklist.mdを生成 |
| 実装モード | タスク実行中 | tasklist.mdをリアルタイムで更新（`[ ]`→`[x]`）し、進捗を追跡 |
| 振り返りモード | 全タスク完了後 | tasklist.mdの振り返りセクションに完了日・学びを記録 |

**テンプレートファイル** (`skills/steering/templates/`):
- `requirements.md` - ステアリング要求定義のひな形
- `design.md` - 実装設計のひな形
- `tasklist.md` - タスクリストのひな形

**設計上の重要原則**: tasklist.mdの全タスクが `[x]` になるまで作業を継続します。スキップは技術的な理由がある場合のみ許可されます。

---

### ドキュメント作成スキル（6種）

`/setup-project` コマンドから順番に呼び出され、`docs/` 以下の永続ドキュメントを作成します。各スキルは `SKILL.md`（手順）・`guide.md`（作成指針）・`template.md`（ひな形）で構成されています。

| スキル名 | 生成ファイル | 概要 |
|---------|------------|------|
| `prd-writing` | `docs/product-requirements.md` | ユーザーストーリー・受け入れ条件・成功指標を含むPRD |
| `functional-design` | `docs/functional-design.md` | 機能一覧・入出力・UIフロー |
| `architecture-design` | `docs/architecture.md` | システム構成・技術スタック・AWSアーキテクチャ・データ設計 |
| `repository-structure` | `docs/repository-structure.md` | ディレクトリ構造・命名規則・依存関係ルール |
| `development-guidelines` | `docs/development-guidelines.md` | ブランチ戦略・コーディング規約・テスト方針・デプロイ手順 |
| `glossary-creation` | `docs/glossary.md` | プロジェクト固有用語の定義・ユビキタス言語 |

---

## このテンプレートをカスタマイズする場合

### テストコマンドを変更する

`commands/add-feature.md` のステップ7を編集します:

```markdown
## ステップ7: 自動テストの実行

1. 以下のコマンドを順番に実行し...
  ```bash
  Bash('uv run pytest')       # ← Python/uvの場合
  Bash('uv run ruff check')
  Bash('uv run basedpyright')
  ```
```

### 新しいスキルを追加する

1. `skills/新スキル名/SKILL.md` を作成（スキルの動作定義）
2. 必要に応じて `skills/新スキル名/template.md` を追加
3. `settings.json` の `permissions.allow` に `"Skill(新スキル名)"` を追加
4. 呼び出し元コマンドやスキルから `Skill('新スキル名')` で参照

### パーミッションを追加する

`settings.json` に追記するか、個人設定なら `settings.local.json` に記述します:

```json
{
  "permissions": {
    "allow": [
      "Bash(uv *)",
      "Bash(gh *)"
    ]
  }
}
```
