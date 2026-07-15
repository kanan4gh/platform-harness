# 要求内容

## 概要

platform-harnessの派生プロジェクトをremote単位で一意に管理する展開候補台帳を作り、`outfit-studio`を最初の旧世代プロジェクトとして、現行のハーネス中立コアと3ハーネス構成へ安全に移行するオンデマンド展開スキームを定義する。

- **関連Issue**: https://github.com/kanan4gh/platform-harness/issues/18
- **使用ハーネス**: Codex
- **基準release**: platform-harness `v1.2.0`

## 背景

platform-harnessから作成されたプロジェクトには、現在の`AGENTS.md`・`docs/procedures/`・Claude Code / Codex / Kiroアダプタ構成へ追随済みのものと、`CLAUDE.md`へ正典を内包した旧Claude専用世代のものが混在している。さらに、同じGitHub remoteを指す開発用コピーと運用コピー、旧実験リポジトリ、配布テンプレートがローカルに共存しているため、ディレクトリ単位の単純な一覧では同期先を重複計上する。

2026-07-15の棚卸しでは、`project-uroboros-neo`は現行構成へ直接同期可能である。一方、`outfit-studio`、`agentcore-work`はplatform-harness由来の旧Claude専用構成、`dev-tasks2-py`と`dev-tasks2`はその前身にあたる旧SDD構成であり、差分同期前に中立構成への移行が必要である。

同日の机上preflightで、outfit-studioにはハーネス正典と重なるopen PR #22が存在することを確認した。G0でこのPRをマージ・破棄・新移行へ引継ぎのいずれにするか裁定し、再preflightを完了するまでoutfit-studioは`on-hold`とする。引継ぎ後のファイル単位統合だけをG2で扱う。

ユーザー判断として、`/Users/akiraishihara/aiwork/operated/outfit-studio`は運用コピーなので展開候補から除外する。同期先はGitHub remote `kanan4gh/outfit-studio`として1件だけ数える。最初にoutfit-studio向けの展開スキームを確立し、他候補への実展開はユーザーが指定した時点でオンデマンド実行する。

## ユースケースの軸

ハーネス保守者が、展開候補台帳から対象プロジェクトを選び、リリース済みplatform-harness正典を派生固有差分と未コミット作業を壊さずにオンデマンド展開できる。

## 代表シナリオ

### シナリオ1: 現行構成の派生プロジェクトへ差分同期する

`project-uroboros-neo`のように`AGENTS.md`、`docs/procedures/`、`.agents/`、`.claude/`、`.codex/`、`.kiro/`、ローカル品質ゲートが既にある場合、同期元releaseと変更ファイルを記録し、正典差分だけを取り込む。プロダクト固有層・技術スタック固有層は上書きしない。

### シナリオ2: outfit-studioを旧Claude専用構成から移行する

`outfit-studio`は`CLAUDE.md`の汎用層に`SOURCE: github.com/kanan4gh/platform-harness`、`UPDATED: 2026-05-27`を持つが、現行の`AGENTS.md`と中立手順書がない。アプリケーションコード、プロダクト固有層、FastAPI等の技術スタック固有層を保持しながら、汎用正典を`AGENTS.md`へ移し、Claude / Codex / Kiroアダプタを現行releaseから導入する。

現在の通常checkoutには`.claude/hooks/`、`.coverage`、`.playwright-mcp/`等の未追跡ファイルがあるため、その作業ツリーを清掃・上書きして開始しない。remoteの最新mainを基準に隔離したworktreeまたは新しいclean cloneでfeature branchを作り、未追跡資産は所有者確認後に必要なものだけ移送する。

### シナリオ3: 台帳からオンデマンド展開する

`dev-tasks2-py`等は台帳に候補として残すが、候補登録だけで自動的にIssue、branch、PRを作らない。ユーザーが対象を指定した時点で最新releaseと対象の状態を再棚卸しし、対象リポジトリ内で個別Issue・steering・feature branchを作成して展開する。

## 実装対象

### 1. 展開候補台帳

`docs/derived-projects.md`を作成し、GitHub remote単位で次を記録する。

- リポジトリ名とremote URL
- platform-harnessとの系譜を示す根拠
- 現在のハーネス世代
- 展開方式（直接同期 / 移行後同期 / 要判断 / 除外）
- 優先度と展開状態
- ローカル作業ツリー上の注意事項
- 最終確認日と、実展開時に再確認すべき情報

初期候補は次のとおりとする。

| remote | 初期分類 | 初期方針 |
|---|---|---|
| `kanan4gh/project-uroboros-neo` | 直接同期 | v1.2.0差分をオンデマンド同期 |
| `kanan4gh/outfit-studio` | 移行後同期 | 最初の展開スキーム対象 |
| `kanan4gh/dev-tasks2-py` | 移行後同期 | local ahead / dirtyを解消してから展開 |
| `kanan4gh/agentcore-work` | 移行後同期 | 執筆中の未コミット変更が落ち着いてから展開 |
| `kanan4gh/dev-tasks2` | 移行後同期 | 継続利用の有無を確認後に展開 |
| `kanan4gh/project-ouroboros` | 要判断 | neoで置換済みなら同期せずarchive候補 |
| `kanan4gh/platform-harness-engineering` | 要判断 | 現行platform-harnessへ統合済みならarchive候補 |
| `kanan4gh/platform-harness-for-codex` / `for-kiro` | 除外または別管理 | 派生製品でなく配布・実験資産として扱う |
| `operated/outfit-studio` | 除外 | 同一remoteの運用コピーであり重複計上しない |

### 2. オンデマンド展開手順

`docs/procedures/derived-project-rollout.md`を作成し、次の共通フローを定義する。

1. ユーザーが台帳から対象を指定する
2. 対象remote、default branch、archive状態、最新commit、dirty worktree、未マージ作業を再棚卸しする
3. 対象リポジトリで同期用Issue・steering・feature branchを作成する
4. 同期元platform-harness release tagとcommitを固定する
5. 中立コア、各ハーネスアダプタ、派生固有層をファイル単位で分類する
6. 旧ハーネスに現在の実行エージェント用アダプタがない場合、ユーザー承認済みの展開計画を根拠として外部エージェントがブートストラップ移行する
7. cleanな隔離作業ツリーで移行または差分同期する
8. 新しい`AGENTS.md`と各アダプタの導入後、対象リポジトリの新しい正典へ実行権限を引き渡す
9. 対象固有テスト、ローカル品質ゲート、必要な対話型受け入れを実行する
10. 同期元、同期対象、保持した固有差分、検証結果をtasklistへ記録してPRを作成する
11. 台帳の状態を更新する

展開はGitHub Actions自動run、GitHub APIを必要とする自動同期、有料LLM headless modeへ依存させない。

### 3. outfit-studioパイロット設計

オンデマンド展開手順へoutfit-studio固有の事前マッピングを含める。

- **保持**: アプリケーションコード、プロダクト固有ドキュメント、プロダクト固有層、FastAPI / uvicorn / Playwright等の技術スタック固有設定、対象固有テスト
- **中立コアへ置換・導入**: `AGENTS.md`汎用層、`docs/procedures/`、`docs/procedures/templates/`、ステアリングlint、ローカル品質ゲート、有料自動化lint
- **薄いアダプタへ移行**: `CLAUDE.md`と`.claude/`、`.agents/skills/`と`.codex/`、`.kiro/`
- **個別判断**: 既存`.claude/settings.json`権限、MCP、hooks、devcontainer、Python検証コマンド
- **除外**: `operated/outfit-studio`への直接編集、キャッシュ、coverage成果物、セッション状態

このIssueではoutfit-studio本体を変更せず、展開スキームと事前マッピングまでをplatform-harnessの正典として作成する。実展開はoutfit-studio側の独立Issueで行う。

### 4. 構造検証

- 台帳に分類・状態・一意remote・確認日があることを構造テストで固定する。
- 手順に同期元release固定、dirty worktree保護、固有差分保持、ローカル品質ゲート、対話型受け入れ、オンデマンド境界があることを固定する。
- outfit-studio固有マッピングと`operated/`除外が欠落しないことを固定する。

## 受け入れ条件

### 展開候補台帳

- [x] 候補をローカルディレクトリではなくGitHub remote単位で一意に管理している。
- [x] 直接同期、移行後同期、要判断、除外の分類が定義されている。
- [x] outfit-studio、project-uroboros-neo、dev-tasks2-py、agentcore-work等の初期候補が記録されている。
- [x] `operated/outfit-studio`が重複した同期先から除外されている。
- [x] 台帳登録だけでは自動展開しないオンデマンド状態管理が定義されている。

### オンデマンド展開手順

- [x] 同期元release tag / commitを展開開始時に固定する。
- [x] remote、default branch、archive状態、dirty worktree、未マージ作業を再確認する。
- [x] 派生側でIssue・steering・feature branchを作成する。
- [x] 旧ハーネスの通常実行者と、移行時のブートストラップ実行者の権限根拠が区別されている。
- [x] 移行後に対象リポジトリの新しい`AGENTS.md`とアダプタへ実行権限を引き渡す。
- [x] プロダクト固有層・技術スタック固有層・ハーネス固有差分を保持する。
- [x] cleanな隔離作業ツリーを使用し、既存の未コミット・未追跡ファイルを破壊しない。
- [x] 対象固有テスト、ローカル品質ゲート、必要な対話型受け入れを実行する。
- [x] GitHub Actions自動runと有料LLM headless modeの起動を0件に保つ。
- [x] 完了後に台帳の状態と同期元を更新する。

### outfit-studio展開スキーム

- [x] 2026-05-27世代のClaude専用構成から現行中立構成へ移行する境界が明確である。
- [x] 保持・置換・導入・個別判断・除外のファイル分類がある。
- [x] 通常checkoutの未追跡資産を破壊せず、clean worktree / cloneを使う規則がある。
- [x] `operated/outfit-studio`を編集対象にしない。
- [x] 実展開をoutfit-studio側の独立Issueへ分離している。
- [x] open PR #22の処遇をG0で裁定し、再preflightを完了するまで`on-hold`とする。
- [x] manifestの各具体pathまたはsectionが重複なく1分類へ割り当てられている。

### 検証

- [x] 台帳と手順の必須契約を構造テストで検証できる。
- [x] `uv run python3 scripts/local_quality_gate.py`が合格する。
- [x] 検証中のGitHub Actions自動runと有料LLM headless mode起動が0件である。

## 成功指標

- 同じremoteを指すローカルコピーの重複登録を0件にする。
- 展開開始前に対象のdirty状態と同期元releaseを100%記録する。
- outfit-studio以外への無指示の自動展開を0件にする。
- 各展開PRで派生固有差分、品質ゲート、対話型受け入れの証跡を追跡できる。

## スコープ外

以下はこのフェーズでは実装しない。

- outfit-studio、project-uroboros-neo、dev-tasks2-py等の派生リポジトリ本体への変更
- 複数リポジトリへの一括自動同期CLI
- GitHub Actionsによる自動展開
- GitHub APIへ依存する必須同期処理
- 有料LLM headless modeを使った受け入れ
- 運用コピー`operated/outfit-studio`への変更
- 旧リポジトリのarchive実行

## 参照ドキュメント

- `docs/procedures/distill.md` - 正典化・release・派生同期の順序
- `docs/harness-guide.md` - 現行の中立コアと3ハーネス構成
- `docs/procedures/steering.md` - 派生側の計画・記録規則
- `docs/procedures/harness-acceptance.md` - 対話型実機受け入れ
- `AGENTS.md` - 正典とプロダクト固有層・技術スタック固有層の境界
