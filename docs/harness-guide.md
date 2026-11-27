# platform-harness テンプレートガイド

スペック駆動開発（AIコーディングエージェント）のためのDevcontainerスターターテンプレートの使い方ガイドです。特定のクラウドや言語に結びつけず、プロダクトの技術スタックは利用者が決めて追加します。

## このテンプレートについて

以下をすぐに使える状態で提供します:

- **Devcontainer環境**: AIコーディングエージェント・GitHub CLI・ハーネスの道具（uv・ruff・basedpyright）を利用可能
- **スペック駆動開発**: AGENTS.md、Claude Code / Codex / Kiroアダプタ、docs/ひな形、ステアリング、スキル一式
- **ローカル品質ゲート**: GitHub ActionsやLLM headless modeへ依存せず、全員が同じ検証を1コマンド実行可能
- **技術スタックの切り替え手順**: プロダクトの言語・クラウド等を追加するチェックリスト（`docs/procedures/tech-stack-switch.md`）

本書の正典は [platform-harness](https://github.com/kanan4gh/platform-harness) で開発・リリースし、生成済み配布物だけを [platform-harness-template](https://github.com/kanan4gh/platform-harness-template) へ公開します。正典の構想・履歴・派生台帳は配布物へ含めません。

SDDプロセスの正典はハーネス中立の `AGENTS.md` にあり、各AIコーディングエージェント(ハーネス)固有の運用差分はアダプタが定義します(換装の構想と経緯は `docs/ideas/harness-swap.md` を参照)。

### ハーネスの選択

| ハーネス | アダプタ | 呼び出し方 |
|---------|---------|-----------|
| Claude Code | `CLAUDE.md` + `.claude/` | スラッシュコマンド(`/add-feature` 等)・スキル自動ロード |
| Codex CLI | `.codex/` + `.agents/skills/`(詳細は `.codex/README.md`) | チャットで「add-featureを実行して」等。初回にプロジェクトのtrustが必要 |
| Kiro IDE / CLI | `.kiro/`(詳細は `.kiro/README.md`) | IDEはskills / agents、CLIは`kiro-cli --agent sdd`を使用 |

3ハーネスは同じ正典・手順書・状態遷移CLI・通常／完了lintを共有し、`.steering/`成果物を相互運用できます。Stopフックは使わず、通常の応答終了を妨げません。

### 品質保証

PR前の必須入口は次です。

```bash
uv run python3 scripts/local_quality_gate.py
```

GitHub Actionsは`workflow_dispatch`だけの任意ミラーで、PRやpushでは自動起動しません。LLMのUI・権限・応答終了非ブロックは`docs/procedures/harness-acceptance.md`に従い、対話型IDE / CLIで確認します。標準受け入れに従量課金型headless modeを使いません。

## 前提条件

- [Docker](https://www.docker.com/) がインストールされていること
- [VSCode](https://code.visualstudio.com/) + [Dev Containers 拡張](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) がインストールされていること

## セットアップ手順

### 1. テンプレートからリポジトリを作成

[platform-harness-template](https://github.com/kanan4gh/platform-harness-template) の「Use this template」ボタンから新しいリポジトリを作成します。正典への変更提案や不具合報告は [platform-harness](https://github.com/kanan4gh/platform-harness) で行います。

### 2. devcontainerを開く

VSCode でリポジトリを開き、「Reopen in Container」を実行します。

postCreate.sh が自動実行され、以下がインストールされます:
- uv（Pythonパッケージマネージャー）
- ruff・basedpyright

### 3. AGENTS.md のプロダクト固有層をカスタマイズ

`AGENTS.md` のプロダクト固有層をプロダクトに合わせて書き換えます(ハーネス固有の運用を変える場合のみアダプタファイルも調整します)。技術スタック固有層の記入欄は、まだ書き換えません。技術スタックは次の setup-project で `docs/architecture.md` を承認したときに決まるためです(setup-project の品質ゲートは、記入欄のままでもハーネスの道具だけで動きます)。

### 4. プロジェクトをセットアップ

選択したAIコーディングエージェントでsetup-projectを実行します。呼び出し方は各アダプタを参照してください。

```
/setup-project
```

対話的に `docs/` 以下の6つのドキュメントを作成します。`feature/setup-project` ブランチ上で、承認したドキュメントごとにコミットし、最後にローカル品質ゲートを実行し、確認のうえpush・PR作成を行います(GitHub Issueとステアリングは作りません)。手順3のAGENTS.mdのカスタマイズを未コミットのまま実行した場合は、ブランチ作成の直後に独立のコミットになります。手順の正は `docs/procedures/setup-project.md` です。

### 5. 技術スタックを切り替える

setup-project のPRをマージした後、`docs/architecture.md` で決めた技術スタックに合わせて、`docs/procedures/tech-stack-switch.md` のチェックリストに従い、AGENTS.md の技術スタック固有層の記入欄と関連ファイル(`pyproject.toml`、`.devcontainer/`、`.mcp.json.example` 等)を書き換えます。add-feature で1つの作業(GitHub Issue とステアリング)として行います。クラウド等を使う場合の例も同じ手順書の付録にあります。

## 含まれるツール

| ツール | 用途 |
|--------|------|
| AIコーディングエージェント(Claude Code等) | AI駆動開発 |
| GitHub CLI | PR・Issue管理 |
| uv | Pythonパッケージ管理 |
| ruff | Pythonリンター |
| basedpyright | Python型チェッカー |

uv・ruff・basedpyright はハーネスの道具で、プロダクトの技術スタックにかかわらず使います。プロダクトの道具は、技術スタックを切り替えるときにこの表へ追加します。

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

各環境のカスタマイズは`.claude/README.md`、`.codex/README.md`、`.kiro/README.md`を参照してください。

コマンド・エージェント・スキルの動作説明と、テストコマンドの変更方法やパーミッション設定のカスタマイズ方法を記載しています。
