# platform-harness テンプレートガイド

スペック駆動開発（AIコーディングエージェント）＋ AWS開発のためのDevcontainerスターターテンプレートの使い方ガイドです。

## このテンプレートについて

以下をすぐに使える状態で提供します:

- **Devcontainer環境**: Claude Code・AWS CLI・CDK・SAM CLI・GitHub CLI がセットアップ済み
- **スペック駆動開発**: AGENTS.md(SDDプロセス正典)・ハーネスアダプタ(CLAUDE.md等)・docs/ ひな形・ステアリングファイル・カスタムスキル一式
- **AWS認証**: `~/.aws/` バインドマウントによる AWS Profile 認証

SDDプロセスの正典はハーネス中立の `AGENTS.md` にあり、各AIコーディングエージェント(ハーネス)固有の運用差分はアダプタが定義します(換装の構想と経緯は `docs/ideas/harness-swap.md` を参照)。

### ハーネスの選択

| ハーネス | アダプタ | 呼び出し方 |
|---------|---------|-----------|
| Claude Code | `CLAUDE.md` + `.claude/` | スラッシュコマンド(`/add-feature` 等)・スキル自動ロード |
| Codex CLI | `.codex/` + `.agents/skills/`(詳細は `.codex/README.md`) | チャットで「add-featureを実行して」等。初回にプロジェクトのtrustが必要 |

どちらのハーネスでも同じ正典・手順書・強制力(Stopフック+lint/CI)でSDDフローが回り、成果物(`.steering/`)は相互運用できます(併用規約は `AGENTS.md` を参照)。

## 前提条件

- [Docker](https://www.docker.com/) がインストールされていること
- [VSCode](https://code.visualstudio.com/) + [Dev Containers 拡張](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) がインストールされていること
- AWS Profile が `~/.aws/` に設定されていること（`aws configure` 等で設定済みであること）

## セットアップ手順

### 1. テンプレートからリポジトリを作成

GitHub の「Use this template」ボタンから新しいリポジトリを作成します。

### 2. AWS設定をカスタマイズ

`.devcontainer/devcontainer.json` を開き、以下を自分の環境に合わせて変更します:

```json
"containerEnv": {
  "AWS_PROFILE": "your-profile",      // ← 使用するAWS Profileに変更
  "AWS_REGION": "ap-northeast-1",     // ← 使用するリージョンに変更
  "AWS_DEFAULT_REGION": "ap-northeast-1"
}
```

### 3. devcontainerを開く

VSCode でリポジトリを開き、「Reopen in Container」を実行します。

postCreate.sh が自動実行され、以下がインストールされます:
- uv（Pythonパッケージマネージャー）
- ruff・basedpyright
- AWS CDK
- AWS SAM CLI

### 4. AWS接続を確認

```bash
aws sts get-caller-identity
```

### 5. AGENTS.md をカスタマイズ

`AGENTS.md` のプロダクト固有層・技術スタック固有層をプロダクトに合わせて書き換えます(ハーネス固有の運用を変える場合のみアダプタファイルも調整します)。

### 6. プロジェクトをセットアップ

AIコーディングエージェント(Claude Code等)で以下を実行します:

```
/setup-project
```

対話的に `docs/` 以下の6つのドキュメントを作成します。

## 含まれるツール

| ツール | 用途 |
|--------|------|
| AIコーディングエージェント(Claude Code等) | AI駆動開発 |
| AWS CLI | AWSリソース操作 |
| AWS CDK | IaC（インフラのコード化） |
| AWS SAM CLI | サーバーレス開発・デプロイ |
| GitHub CLI | PR・Issue管理 |
| uv | Pythonパッケージ管理 |
| ruff | Pythonリンター |
| basedpyright | Python型チェッカー |

## スペック駆動開発フロー

```
1. GitHub Issue を作成
2. /add-feature で機能実装（ステアリングファイル → 実装 → PR）
3. PR をマージ
4. gh release create でリリース
```

詳細は `AGENTS.md` を参照してください。

---

## 開発者（ハーネスエンジニア）向け

Claude Code環境のカスタマイズ・拡張を行う方は [`.claude/README.md`](.claude/README.md) を参照してください。

コマンド・エージェント・スキルの動作説明と、テストコマンドの変更方法やパーミッション設定のカスタマイズ方法を記載しています。
