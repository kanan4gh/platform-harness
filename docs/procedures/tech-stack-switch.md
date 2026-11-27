# 技術スタックの切り替え手順

派生プロジェクトが、テンプレートの既定（中立な記入欄と例）から、自分のプロダクトの技術スタックへ切り替えるための手順書である。ハーネス中立の正であり、どのハーネスでも同じ手順で行う。

## 前提: ハーネスの道具とプロダクトの技術スタック

テンプレートには、性質の違う2種類の技術スタックがある。切り替えるのは後者だけである。

| 種類 | 内容 | 切り替え |
|---|---|---|
| **ハーネスの道具** | ハーネス自身（`scripts/`、`tests/`、`.claude/hooks/` 等）を動かす Python 3.12・uv・pytest・ruff・basedpyright と、ローカル品質ゲート（`scripts/local_quality_gate.py`） | **しない**。プロダクトが Python 以外でも残す。`pyproject.toml` の dev 依存・`uv.lock`・`scripts/` を削除しない |
| **プロダクトの技術スタック** | プロダクトの言語・フレームワーク・インフラ（クラウド等）・テストとリントの道具 | AGENTS.md の技術スタック固有層の記入欄を書き換え、下のチェックリストに従って関連ファイルを直す |

テンプレートの既定は、特定のクラウドに結びつけない。AGENTS.md の例（Python + uv + pytest + ruff + basedpyright、クラウドなし）は記入の例であり、既定ではない。

## いつ行うか（順序）

1. **setup-project で `docs/architecture.md` を承認する**。技術スタックはここで決まる。setup-project の作業中は、AGENTS.md の技術スタック固有層を記入欄のまま残してよい。setup-project の品質ゲートは、ハーネスの道具だけで動く
2. **setup-project の PR をマージした後、切り替えを1つの作業として行う**。add-feature 手順で行う（GitHub Issue とステアリングを作る）。setup-project のブランチには混ぜない
3. 承認した `docs/architecture.md` の技術スタックと、AGENTS.md の技術スタック固有層を一致させる。以後、architecture.md で技術スタックを変えたときも、同じチェックリストで AGENTS.md を更新する

技術スタックが AGENTS.md の「記入の例」と同じ（Python + uv、クラウドなし、ハーネスの道具のほかに追加する道具なし）なら、記入欄に記入の例を写し、チェックリストの1と2と最後の確認だけを行えばよい。3〜6は、追加する設定・道具がないため不要である。

## 切り替えチェックリスト

上から順に行う。各項目の確認コマンドを実行してから次へ進む。

| 順 | 対象ファイル | 変える内容 | 確認コマンド |
|---|---|---|---|
| 1 | `AGENTS.md`（技術スタック固有層） | 「プロダクトの技術スタック」の記入欄と「プロダクトの確認コマンド」を書き換える。「ハーネスの道具」と「ハーネスの必須コマンド」は変えない | `grep -n '\[記入' AGENTS.md` が何も出さない（記入欄が残っていない）こと、`uv run pytest tests/procedures`（文書一覧等の整合）。プロダクトの確認コマンド自体は、順3の後に通る |
| 2 | `pyproject.toml` | `[project]` の `name` / `description` をプロダクトに合わせる。Python のアプリなら、アプリのコードのディレクトリ（例: `src`）を `[tool.basedpyright]` の `include` へ足す（ruff は `*.py` ですべての Python ファイルを対象にするため追加は要らない）。Python 以外のアプリなら、アプリのコードは各言語の道具で検査し、ここへは足さない | `uv lock` の後、`uv run ruff check .` と `uv run basedpyright` |
| 3 | プロダクトの設定ファイル | プロダクトの依存定義・リンター・テストの設定を足す（例: `package.json`、`tsconfig.json`） | AGENTS.md に書いたプロダクトの確認コマンド |
| 4 | `.devcontainer/devcontainer.json`・`.devcontainer/postCreate.sh` | プロダクトの言語・インフラに必要な feature・マウント・環境変数・拡張・インストールを足す。uv・ruff・basedpyright の導入（ハーネスの道具）は残す | コンテナを再構築し、`uv --version`、プロダクトの道具の `--version` |
| 5 | `.mcp.json.example`（使うなら `.mcp.json`） | プロダクトの技術スタックに合う MCP サーバーの例を足す。MCP を有効にしないなら、`.mcp.json.example` の更新だけで足りる（サンプルのため G3 不要）。有効にする場合は `.mcp.json` を作る。ハーネス設定での有効化・許可を変えると G3 の対象になる（add-feature 手順のステップ4） | 有効にした場合だけ、使用中ハーネスの手順で再起動し、サーバーが認識されることを確認 |
| 6 | `docs/harness-guide.md` | 「前提条件」と「含まれるツール」の表に、プロダクトの道具を足す | 目視 |
| 7 | 全体 | ローカル品質ゲートを実行する | `uv run python3 scripts/local_quality_gate.py --steering [ステアリング名]` |

ローカル品質ゲートは `uv run pytest`・`uv run ruff check .`・`uv run basedpyright`・steering lint・外部有料自動化 lint を実行する。Python のアプリのテストを `tests/` に置けば、品質ゲートの pytest に含まれる。Python 以外の道具による検査（例: `npm test`）は品質ゲートに含まれないため、AGENTS.md の「プロダクトの確認コマンド」に書き、PR 前に品質ゲートとあわせて実行する。

## 付録: AWS を使う場合の例

AWS（CDK・SAM）を使うプロダクトの例である（付録の例。既定ではない）。使わない項目は省く。

### AGENTS.md の記入例

技術スタック固有層の2つの記入欄を、次のように書く（「ハーネスの道具（固定）」と「ハーネスの必須コマンド」はそのまま残す）。

````markdown
## プロダクトの技術スタック（記入欄）

- 開発環境: devcontainer
- 言語・ランタイム: Python 3.12（CDK は TypeScript または Python）
- パッケージマネージャー: uv（CDK を TypeScript で書く場合は npm も使う）
- フレームワーク・主要ライブラリ: AWS CDK
- インフラ(クラウド等): AWS（AWS SAM CLI によるサーバーレス、AWS Profile（`~/.aws/` マウント）で認証）
- テスト: pytest
- 型チェック: basedpyright
- リンター: ruff

## プロダクトの確認コマンド（記入欄）

```bash
cdk --version        # CDK 動作確認
sam --version        # SAM CLI 動作確認
aws sts get-caller-identity  # AWS認証確認
```
````

### `.devcontainer/devcontainer.json` に足すもの

```jsonc
{
  "features": {
    // 既存の feature に加える
    "ghcr.io/devcontainers/features/aws-cli:1": {}
  },

  // 既存の mounts があれば、その配列に加える
  "mounts": [
    "source=${localEnv:HOME}/.aws,target=/home/vscode/.aws,type=bind,consistency=cached"
  ],

  // 既存の containerEnv があれば、そのオブジェクトに加える
  "containerEnv": {
    "AWS_PROFILE": "your-profile",       // 使用するAWS Profileに変更
    "AWS_REGION": "ap-northeast-1",      // 使用するリージョンに変更
    "AWS_DEFAULT_REGION": "ap-northeast-1"
  },

  "customizations": {
    "vscode": {
      "extensions": [
        // 既存の拡張に加える
        "amazonwebservices.aws-toolkit-vscode"
      ]
    }
  }
}
```

前提条件: AWS Profile が `~/.aws/` に設定されていること（`aws configure` 等）。`~/.aws` が存在しないとマウントに失敗するため、AWS を使わない利用者の既定には含めない。

### `.devcontainer/postCreate.sh` に足すもの

```bash
# AWS CDK
npm install -g aws-cdk

# AWS SAM CLI
pip install aws-sam-cli

# バージョン確認
aws --version || true
cdk --version || true
sam --version || true
```

### `.mcp.json.example` に足すもの

```jsonc
{
  "mcpServers": {
    // aws-mcp: AWS サービスのドキュメント検索・API 呼び出し
    //   - CDK や SAM でインフラを書くとき
    //   - AWS サービスの仕様・料金を調べるとき
    //   AWS_REGION を実際に使うリージョンに変更すること
    "aws-mcp": {
      "command": "uvx",
      "args": [
        "mcp-proxy-for-aws@latest",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--metadata", "AWS_REGION=ap-northeast-1"
      ]
    },

    // awslabs.aws-iac-mcp-server: CDK / CloudFormation の検証・ドキュメント検索
    //   - CDK コードのレビュー・ベストプラクティス確認
    //   - CloudFormation テンプレートの lint / compliance チェック
    "awslabs.aws-iac-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-iac-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

### `docs/harness-guide.md` の表に足すもの

| ツール | 用途 |
|--------|------|
| AWS CLI | AWSリソース操作 |
| AWS CDK | IaC（インフラのコード化） |
| AWS SAM CLI | サーバーレス開発・デプロイ |

### `docs/architecture.md`

「インフラ構成」の節に、使用する AWS サービスと構成を書く。

### 確認コマンド

```bash
aws sts get-caller-identity  # AWS認証確認
cdk --version                # CDK 動作確認
sam --version                # SAM CLI 動作確認
```
