# タスクリスト

## 🚨 タスク完全完了の原則

**このファイルの全タスクが完了するまで作業を継続すること**

- 全タスクを`[x]`にし、完了・スキップは実態に合わせて即時記録する
- 大きすぎるタスクはルールAで分割する
- 技術的理由で不要になったタスクだけ、理由を明記してルールBでスキップする

## フェーズ1: 展開候補台帳

- [x] `docs/derived-projects.md`を作成する
  - [x] GitHub remoteを一意キーとする台帳スキーマを定義する
  - [x] harness generation、展開方式、優先度、状態モデルを定義する
  - [x] Last source、Last inspected、Local caution、次の判断を記録できるようにする
- [x] 初期候補をremote単位で登録する
  - [x] `project-uroboros-neo`をP0 direct-syncとして登録する
  - [x] `outfit-studio`をP0 migrate-then-syncパイロットとして登録する
  - [x] `dev-tasks2-py`、`agentcore-work`、`dev-tasks2`を移行候補として登録する
  - [x] `project-ouroboros`と`platform-harness-engineering`を要判断として登録する
  - [x] 配布・実験資産を派生製品と分離する
  - [x] `operated/outfit-studio`を同一remoteの運用コピーとして除外する
- [x] 台帳登録だけで展開を開始しないオンデマンド原則を記載する

## フェーズ2: 共通オンデマンド展開手順

- [x] `docs/procedures/derived-project-rollout.md`を作成する
  - [x] `1 release × 1 remote × 1 branch × 1 PR`の展開単位を定義する
  - [x] G0対象選択、G1計画承認、G2競合裁定、G3対話型受入、G4マージを定義する
- [x] preflight記録を定義する
  - [x] remote、default branch、OID、ref鮮度、archive / template状態を記録する
  - [x] dirty / ahead / behind、active Issue / PR / branchを記録する
  - [x] 同期元release / commitと隔離作業ツリーを固定する
- [x] 同期manifestを定義する
  - [x] Preserve、Replace、Add、Merge manually、Excludeの5分類を定義する
  - [x] 派生固有層を正典コピーで暗黙に上書きしない規則を定義する
- [x] 安全な実装・検証・完了手順を定義する
  - [x] 派生側Issue・steering・feature branchを必須化する
  - [x] 旧ハーネスの通常実行者とbootstrap executorを区別する
  - [x] ユーザー承認済み展開手順をbootstrap executorの権限根拠として定義する
  - [x] 新AGENTS.mdとアダプタへのauthority handoffを定義する
  - [x] clean worktree / cloneを使い、dirtyな既存checkoutを破壊しない
  - [x] 対象固有テスト、ローカル品質ゲート、対話型受け入れを定義する
  - [x] 同期記録、PR、台帳更新までを完了条件にする
  - [x] GitHub Actions自動runと有料LLM headless modeを必須経路から排除する

## フェーズ3: outfit-studioパイロットスキーム

- [x] outfit-studioの現況を手順へ記録する
  - [x] 2026-05-27世代のClaude専用構成である根拠を記載する
  - [x] 現行中立コア・Codex・Kiro資産が未導入であることを記載する
  - [x] 通常checkoutの未追跡資産と運用コピー除外を記載する
- [x] outfit-studioの隔離戦略を定義する
  - [x] remote mainからcleanなworktree / cloneと専用branchを作る
  - [x] 通常checkoutの未追跡ファイルを削除・stash・自動コピーしない
  - [x] outfit-studio側の独立Issueとsteeringを必須化する
- [x] outfit-studioの初期manifestを定義する
  - [x] アプリ本体・製品文書・技術スタック固有設定をPreserveへ分類する
  - [x] 旧CLAUDE汎用層・旧手順本体をReplaceへ分類する
  - [x] AGENTS・中立手順・Codex・Kiro・品質ゲートをAddへ分類する
  - [x] 権限・hooks・MCP・devcontainer・pyprojectをMerge manuallyへ分類する
  - [x] cache・runtime state・運用コピーをExcludeへ分類する
- [x] outfit-studioの移行順序と人による判断点を定義する
- [x] このIssueでoutfit-studio本体を変更しない境界を明記する

## フェーズ4: 構造テスト

- [x] `tests/procedures/test_derived_project_rollout.py`を追加する
  - [x] 台帳のremote一意キー、4分類、状態、同期元、確認日を固定する
  - [x] 初期候補、P0分類、`operated/outfit-studio`除外を固定する
  - [x] オンデマンド境界と人による対象選択を固定する
  - [x] preflight、manifest 5分類、dirty worktree保護を固定する
  - [x] bootstrap executorとauthority handoffの契約を固定する
  - [x] outfit-studioの現況、隔離戦略、ファイル分類を固定する
  - [x] ローカル品質ゲート、対話型受入、無課金境界を固定する
- [x] 構造テストを実行し、失敗を修正する（独立レビュー後に14件へ補強、ruff合格）

## フェーズ5: 机上受け入れ

- [x] 2026-07-15の棚卸し結果を台帳へ反映する（remote・branch・dirty/ahead状態を読み取りで再確認）
- [x] outfit-studioへ手順を机上適用し、preflight記録を一意に作れることを確認する（open PR #22との重複によりStop条件も確認）
- [x] outfit-studioの初期manifestが既存tracked資産を分類できることを確認する（ReplaceとMerge manuallyの境界をファイル単位へ具体化）
- [x] 同じoutfit-studio remoteが台帳に1件だけであることを確認する（台帳行1件）
- [x] `project-uroboros-neo`がdirect-sync対象に含まれることを確認する
- [x] outfit-studio、project-uroboros-neo、dev-tasks2-py等の派生リポジトリに変更がないことを確認する（再取得したstatusが事前観測と一致）
- [x] GitHub Actions自動runと有料LLM headless mode起動が0件であることを記録する

## フェーズ6: 4段検証

- [ ] 段1・静的検証を完了する
  - [x] `uv run pytest`を実行する（最終編集後143件合格）
  - [x] `uv run ruff check .`を実行する（合格）
  - [x] `uv run basedpyright`を実行する（0 errors / 0 warnings）
  - [ ] `uv run python3 scripts/local_quality_gate.py`を実行する
- [x] 段2・台帳と手順をoutfit-studio現況へ机上適用し、成果物を観察する（open PR #22との競合を検出し`on-hold`へ反映）
- [x] 段3・変更差分をレビューし、正当な指摘を修正する（G0順序、manifest排他性、状態遷移、テスト粒度を修正）
  - [x] 独立スペック検証の指摘に従い、全remote一意性・台帳必須列・preflight・manifest境界の構造テストを補強する（14件合格）
- [x] 段4・ステアリングと実装のスペック準拠検証を独立した文脈で実施する（重大・推奨指摘なし、準拠）
- [x] 台帳と展開手順のドキュメントレビューを独立した文脈で実施する（最終4.8/5、残存指摘を修正）

## フェーズ7: 完了処理

> 計画調整: steering lintはtasklistの完了状態自体を検証するため、commit・PR URLの記録後に全完了状態を固定し、PRマージ前の最終ローカル品質ゲートとして実行する。

- [ ] requirements.mdの受け入れ条件がすべて満たされたことを確認する
- [ ] 実装後の振り返りを本ファイルへ記録する
- [ ] Issue #18を参照するConventional Commitを作成する
- [ ] feature branchをpushしてPRを作成する
- [ ] PR URLと検証結果をユーザーへ報告する

---

## 机上受け入れ記録（2026-07-15）

### outfit-studio preflight

- 対象remote: `kanan4gh/outfit-studio`
- default branch / OID: `main` / `43c874f9316b9f8149e8dffcc06f903de0e4c500`
- remote確認日時・方法: 2026-07-15 / GitHub CLIによるrepository metadata・main commit照会。通常checkoutの`HEAD`と`origin/main`も同OID
- archive / template状態: `false` / `false`
- local checkout: `/Users/akiraishihara/aiwork/outfit-studio`（参考。一意キーではない）
- dirty / ahead / behind: tracked変更なし、ahead 0 / behind 0。`.claude/hooks/`、`.coverage`、`.devcontainer/devcontainer-lock.json`、`.playwright-mcp/`が未追跡
- active Issue / PR / branch: open Issue 0件。open PR #22 `chore/20260711-sync-harness`が存在し、`CLAUDE.md`、`.claude/`、`.gitignore`、`pyproject.toml`等を変更
- 同期元: platform-harness `v1.2.0` / `d61fcf947f7ffc6fe41da6095964d0a848153507`
- bootstrap executor: 実展開時のG1で決定（このIssueでは派生本体を変更しない）
- 作業隔離: 未作成。PR #22との競合がStop条件に該当するため、G0で処遇を裁定し再preflight後にclean worktree / cloneを用意する
- 判定: 一意なpreflight記録は作成可能。実展開は`on-hold`

### 初期manifestの机上適用

- Preserve: trackedの`src/`、`tests/conftest.py`、`tests/integration/`、`tests/unit/`、6つの製品docs、`CLAUDE.md`内の固有層section
- Replace from canonical: `CLAUDE.md`旧汎用層・補足section、`.claude/commands/{add-feature,review-docs,setup-project}.md`、`.claude/skills/steering/`
- Add from canonical: 現在存在しない`AGENTS.md`、中立`docs/procedures/`、`.agents/skills/`、state subpathを除く`.codex/`・`.kiro/`、品質ゲートscriptと対象に存在しない対応テストpath
- Merge manually: `CLAUDE.md`のプロジェクトメモリsection、`.claude/settings.json`、`.claude/README.md`、`.claude/agents/`、steering以外の既存`.claude/skills/`、`.claude/hooks/*.py`、`docs/ideas/harness-engineering.md`、`.gitignore`、`pyproject.toml`、`uv.lock`、`.devcontainer/devcontainer.json`、`.devcontainer/postCreate.sh`、`.mcp.json.example`
- Exclude: 未追跡の`.coverage`、`.playwright-mcp/`、3ハーネスの`hooks/state/`、`**/__pycache__/`、`.devcontainer/devcontainer-lock.json`
- 観察結果: 各具体path/sectionを重複なく5分類へ割り当て可能。PR #22の処遇はG0、引継ぎ後に重なるファイルはG2で3-way比較が必要

### 無変更・無課金記録

- 派生リポジトリへの書き込み: 0件（状態・tracked一覧・GitHub metadataの読み取りのみ）
- GitHub Actions自動run: 0件
- 有料LLM headless mode起動: 0件

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
