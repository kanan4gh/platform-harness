# platform-harness

スペック駆動開発（Claude Code）＋ AWS開発のためのDevcontainerスターターテンプレート。

## このテンプレートについて

以下をすぐに使える状態で提供します:

- **Devcontainer環境**: Claude Code・AWS CLI・CDK・SAM CLI・GitHub CLI がセットアップ済み
- **スペック駆動開発**: CLAUDE.md テンプレート・docs/ ひな形・ステアリングファイル・カスタムスキル一式
- **AWS認証**: `~/.aws/` バインドマウントによる AWS Profile 認証

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

### 5. CLAUDE.md をカスタマイズ

`CLAUDE.md` のプロダクト固有層・技術スタック固有層をプロダクトに合わせて書き換えます。

### 6. プロジェクトをセットアップ

Claude Code で以下を実行します:

```
/setup-project
```

対話的に `docs/` 以下の6つのドキュメントを作成します。

## 含まれるツール

| ツール | 用途 |
|--------|------|
| Claude Code | AI駆動開発 |
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

詳細は `CLAUDE.md` を参照してください。

---

## 開発者（ハーネスエンジニア）向け

Claude Code環境のカスタマイズ・拡張を行う方は [`.claude/README.md`](.claude/README.md) を参照してください。

コマンド・エージェント・スキルの動作説明と、テストコマンドの変更方法やパーミッション設定のカスタマイズ方法を記載しています。
