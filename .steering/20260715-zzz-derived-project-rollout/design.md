# 設計書

## アーキテクチャ概要

派生プロジェクト展開を「候補を管理する台帳」と「選択された1件を安全に展開する手順」に分離する。台帳登録は自動展開を意味せず、人が対象を指定したときだけ個別リポジトリでIssue・steering・feature branchを開始する。outfit-studioは旧Claude専用世代から現行中立構成へ移行する最初のパイロットとして、ファイル境界と承認点を具体化する。

```text
platform-harness release v1.2.0
          │
          ▼
docs/derived-projects.md
  remote単位の候補台帳
  ├─ direct-sync
  ├─ migrate-then-sync
  ├─ decision-required
  └─ excluded
          │
          │ ユーザーが1件を指定
          ▼
docs/procedures/derived-project-rollout.md
  preflight → 計画承認 → 隔離 → 移行/同期
  → ローカル検証 → 人による対話型受入 → PR → 台帳更新
          │
          └─ 最初の適用計画: kanan4gh/outfit-studio
```

## コンポーネント設計

### 1. `docs/derived-projects.md`

**責務**:

- platform-harnessの展開候補をGitHub remote単位で一意に管理する。
- 現在の世代、展開方式、優先度、状態、人が判断すべき事項を可視化する。
- 同一remoteの運用コピー・一時clone・worktreeを別の同期先として数えない。
- 展開完了後の同期元release / commitと最終確認日を追跡する。

**台帳スキーマ**:

| 列 | 内容 |
|---|---|
| Remote | `OWNER/REPOSITORY`。一意キー |
| Repository URL | GitHub URL |
| Lineage evidence | `SOURCE`コメント、README、旧SDD構造等の根拠 |
| Harness generation | `current-neutral` / `legacy-platform-claude` / `legacy-sdd` / `distribution-asset` |
| Strategy | `direct-sync` / `migrate-then-sync` / `decision-required` / `excluded` |
| Priority | `P0` / `P1` / `P2` / `-` |
| State | 下記状態モデル |
| Last source | 未展開は`none`、履歴不明は`unknown (investigate)`、展開済みは`vX.Y.Z / <7〜40桁のcommit SHA>` |
| Last inspected | `YYYY-MM-DD` |
| Local caution | dirty / ahead / duplicate copy等。実行時に再確認する参考情報 |
| Decision / next action | 人の判断または次のオンデマンド操作 |

**状態モデル**:

```text
candidate
  ├─ user selects → approved → planned → in-progress → verified → synced
  ├─ unsafe / ongoing work → on-hold
  ├─ ownership unclear → decision-required
  └─ duplicate / superseded / distribution only → excluded
```

- 台帳更新だけで`candidate`から`approved`へ進めない。ユーザーの対象指定を必須とする。
- `synced`は固定的な完了ではない。新release発行時は`candidate`へ戻さず、`Last source`との差分がある状態として次回オンデマンド判断を待つ。
- `Local caution`は2026-07-15時点の観測であり、展開の安全判定には使わずpreflightで再取得する。
- `on-hold`は阻害要因をG0で解消して再preflightを記録した場合だけ`candidate`または`approved`へ戻す。`decision-required`は人の裁定を記録して`candidate`または`excluded`へ遷移する。

**初期分類**:

- P0: `project-uroboros-neo`（direct-sync）、`outfit-studio`（migrate-then-sync、パイロット）
- P1: `dev-tasks2-py`、`agentcore-work`（migrate-then-sync、既存作業の保護が必要）
- P2: `dev-tasks2`（継続利用確認後）
- decision-required: `project-ouroboros`、`platform-harness-engineering`
- excluded / separately managed: `platform-harness-for-codex`、`platform-harness-for-kiro`、`operated/outfit-studio`

### 2. `docs/procedures/derived-project-rollout.md`

**責務**:

- 台帳から人が指定した1リポジトリだけをオンデマンド展開する共通手順を定義する。
- platform-harness正典と派生固有層の境界を、コピー前にmanifestへ固定する。
- dirty worktree、ローカルahead、未マージPR、古いremote-tracking refがある状態での暗黙な上書きを防ぐ。
- 自動検証と人による承認・対話型受け入れの責任分界を定義する。

**展開単位**:

1回の展開は`1 platform-harness release × 1 GitHub remote × 1 feature branch × 1 PR`とする。複数派生リポジトリを1つのIssue・PR・作業セッションへ束ねない。

**実行主体と権限の引き渡し**:

```text
移行前の通常作業
  対象の旧ハーネス → 旧ハーネスが依存するAIエージェント

ブートストラップ移行
  ユーザーのG0 / G1承認
    → platform-harnessの展開手順を一時的な実行根拠とする外部AIエージェント
    → 旧CLAUDE.md等からプロジェクト固有制約を抽出して遵守

移行後の通常作業
  対象の新AGENTS.md → Claude / Codex / Kiro各アダプタ
```

- 旧ハーネスに現在のAIエージェント用アダプタがない場合、そのエージェントは旧ハーネスを実行したことにしない。ユーザー承認済みの本展開手順を根拠とする`bootstrap executor`としてだけ動作する。
- bootstrap executorは旧ハーネスのプロダクト固有規則、技術スタック、テスト、Git運用を制約として読むが、Claude固有のツール呼び出し方法を模倣しない。
- `AGENTS.md`と対象エージェント用アダプタが導入・レビューされた時点を`authority handoff`とし、それ以降は対象リポジトリの新しい正典に従う。
- Claude Codeをbootstrap executorとして選ぶこともできるが必須ではない。どの実行者でも有料headless modeは使用せず、最終の各ハーネス受け入れは人が対話的に行う。

**承認ゲート**:

| ゲート | 人の判断 | エージェントが準備するもの |
|---|---|---|
| G0 対象選択・阻害要因裁定 | 対象remoteを指定し、競合PR等の処遇を裁定 | 候補・状態・競合範囲・再preflight結果 |
| G1 計画承認 | requirements / design / tasklistを承認 | 差分調査、manifest、検証計画 |
| G2 競合裁定 | 既存固有設定を保持・置換・統合のどれにするか | ファイル単位の3-way比較案 |
| G3 対話型受入 | Claude / Codex / KiroのUI・権限・Stopを人が操作 | 無課金の実機手順と記録テンプレート |
| G4 マージ | PRをレビューしてマージ | ローカル品質ゲート、差分、受入証跡 |

通常のSDD承認ゲートを増殖させない。G2は計画で裁定できなかった実競合がある場合だけ停止し、競合がなければG1の承認内容で自動継続する。

**preflight記録**:

```markdown
## 展開preflight
- 対象remote: OWNER/REPOSITORY
- default branch / OID: main / SHA
- remote確認日時・方法: YYYY-MM-DD / fetch済みremote-tracking ref等
- archive / template状態: ...
- local checkout: path（参考。同期先の一意キーではない）
- dirty / ahead / behind: ...
- active Issue / PR / branch: ...
- 同期元: platform-harness vX.Y.Z / SHA
- 作業隔離: worktreeまたはclean cloneのpath
```

**同期manifest**:

```markdown
## 同期manifest
### Preserve（派生固有のまま保持）
- path — 保持理由
### Replace from canonical（正典で置換）
- path — source release内のpath
### Add from canonical（正典から新規導入）
- path — source release内のpath
### Merge manually（人の裁定が必要）
- path — 競合点と選択肢
### Exclude（同期・コミット対象外）
- path — cache / runtime state / duplicate copy等
```

### 3. outfit-studioパイロット

**現状**:

- GitHub remoteは`kanan4gh/outfit-studio`、default branchは`main`。
- `CLAUDE.md`汎用層は`SOURCE: github.com/kanan4gh/platform-harness`、`UPDATED: 2026-05-27`。
- trackedなClaude Code資産はあるが、`AGENTS.md`、`docs/procedures/`、`.agents/`、`.codex/`、`.kiro/`、共通ローカル品質ゲートはない。
- 通常checkoutはremote mainと同期しているが、`.claude/hooks/`、`.coverage`、`.devcontainer/devcontainer-lock.json`、`.playwright-mcp/`が未追跡である。
- open PR #22がハーネス正典と重なるファイルを変更しているため、G0で処遇を裁定して再preflightを完了するまで`on-hold`である。G2は引継ぎ後のファイル単位統合だけを扱う。
- `/aiwork/operated/outfit-studio`は同一remoteの運用コピーであり、preflight参照・編集・同期の対象から除外する。

**隔離戦略**:

1. 通常checkoutの未追跡ファイルを削除・stash・自動コピーしない。
2. G0でopen PR #22をマージ・破棄・新移行へ引継ぎのいずれにするか裁定し、再preflightを完了する。
3. outfit-studio側で独立Issueを作成する。
4. 確認したmain OIDから`feature/sync-platform-harness-v1-2-0`を隔離worktreeまたはclean cloneに作る。
5. Issue URLを含む`.steering/[date]-sync-platform-harness-v1-2-0/`を作る。
6. 通常checkoutの未追跡資産が必要かはG2で所有者が判断し、必要なものだけ内容を確認して移送する。

**初期manifest案**:

| 分類 | 対象 |
|---|---|
| Preserve | `src/`、`tests/conftest.py`、`tests/integration/`、`tests/unit/`、6つの製品docs、CLAUDE.mdのプロダクト固有層・技術スタック固有層section |
| Replace | CLAUDE.mdの汎用層・補足section、`.claude/commands/{add-feature,review-docs,setup-project}.md`、`.claude/skills/steering/`と旧steering templates |
| Add | `AGENTS.md`、中立`docs/procedures/`とtemplates、`.agents/skills/`、state subpathを除く`.codex/`・`.kiro/`、3つの決定論的lint/gate script、対象に存在しない対応テストpath |
| Merge manually | CLAUDE.mdのプロジェクトメモリsection、`.claude/settings.json`、`.claude/README.md`、`.claude/agents/`、steering以外の既存`.claude/skills/`、`.claude/hooks/*.py`、`docs/ideas/harness-engineering.md`、`.gitignore`、`pyproject.toml`、`uv.lock`、`.devcontainer/devcontainer.json`、`.devcontainer/postCreate.sh`、`.mcp.json.example` |
| Exclude | `.coverage`、`.playwright-mcp/`、3ハーネスの`hooks/state/`、`**/__pycache__/`、`.devcontainer/devcontainer-lock.json` |

各具体pathまたは明示したsectionはちょうど1分類へ割り当て、親directoryと例外subpathを別分類で重複させない。

**移行順序**:

```text
1. outfit固有層をCLAUDE.mdから抽出してAGENTS.md 3層へ配置
2. neutral docs/proceduresとtemplatesを導入
3. Claude資産を薄いadapterへ更新し、既存権限・hooksを個別統合
4. Codex adapterを導入
5. Kiro adapterを導入
6. steering / paid-automation / adapter構造テストとlocal quality gateを導入
7. outfit固有テストを含む全静的検証
8. Claude / Codex / Kiroの対話型実機受け入れ
9. PR作成、台帳更新
```

**outfit固有の注意**:

- platform-harnessのAWS向けdevcontainerや空の永続docsを盲目的に上書きしない。
- `pyproject.toml`はoutfitの依存関係とテスト対象を正とし、品質ゲートに必要なdev依存だけを統合する。
- 既存テスト中のCodexサービスはCodex CLIアダプタとは別概念として扱い、名前の一致だけで置換しない。
- 対話型受け入れは利用許可済みの各IDE / CLIで人が実施し、従量課金型headless modeを使わない。

## データフロー

### 候補登録

```text
local / GitHub棚卸し
  → remoteで重複除去
  → lineage / generationを判定
  → strategy / priority / stateを記録
  → ユーザーの対象指定を待つ
```

### オンデマンド展開

```text
ユーザー指定
  → preflight再取得
  → 派生側Issue / steering / branch
  → release固定
  → manifest承認
  → clean隔離環境で移行
  → local quality gate
  → 人による対話型受入
  → PR / merge
  → 台帳のLast source / State更新
```

## エラーハンドリング戦略

### preflightで停止する条件

- 対象remote、default branch、同期元release / commitを一意に確定できない。
- remote-tracking refの鮮度を確認できず、利用可能なローカルrefの限界を記録しても安全なbaseを選べない。
- dirty / aheadな唯一のcheckoutしかなく、clean worktree / cloneを準備できない。
- activeな移行PRまたは同じ正典ファイルを変更するfeature branchがある。
- 派生固有層と正典の境界をG1 / G2で裁定できない。

これらを「最新と思われる」「たぶん一時ファイル」等の推測で通過させない。状態を`on-hold`または`decision-required`として台帳へ記録し、ユーザー判断を待つ。

### 実装中の失敗

- 正典ファイルの単純コピーで対象固有テストが失敗した場合、対象固有設定を正典で上書きして解消しない。manifestを`Merge manually`へ戻して統合する。
- 1つのハーネスだけ受け入れ不能な場合、他ハーネスの合格で代替せず、能力差・代替ゲート・未確認理由を記録する。
- GitHub Actionsや有料headless modeを「早い代替」として起動しない。

## テスト戦略

### 構造テスト

`tests/procedures/test_derived_project_rollout.py`を追加し、次を固定する。

- 台帳のremote一意キー、4分類、状態、同期元、確認日、オンデマンド境界。
- 初期候補と`operated/outfit-studio`除外。
- 手順のrelease固定、preflight、manifest 5分類、dirty worktree保護、1 remote / 1 PR原則。
- 旧ハーネスの通常実行者、bootstrap executorの権限根拠、authority handoff。
- outfit-studioの旧世代根拠、clean隔離戦略、保持 / 置換 / 追加 / 個別統合境界。
- ローカル品質ゲート、人による対話型受け入れ、GitHub Actions自動run / 有料headless mode 0件の境界。

### 実挙動検証

- 現在のローカル棚卸し結果から、同じoutfit-studio remoteを2件登録しないことを確認する。
- 手順をoutfit-studioの現況へ机上適用し、preflightと初期manifestを一意に作れることを確認する。
- このIssueでは派生リポジトリを変更しないことを`git status`で確認する。

## 依存ライブラリ

追加しない。Markdownと既存pytestによる構造検証だけを使用する。

## ディレクトリ構造

```text
docs/
├── derived-projects.md                       # remote単位の展開候補台帳
└── procedures/
    └── derived-project-rollout.md             # 共通手順+outfitパイロット
tests/
└── procedures/
    └── test_derived_project_rollout.py         # 台帳・手順の構造契約
.steering/
└── 20260715-zzz-derived-project-rollout/
    ├── requirements.md
    ├── design.md
    └── tasklist.md
```

## 実装の順序

1. `docs/derived-projects.md`へ初期候補・状態モデル・オンデマンド原則を記載する。
2. `docs/procedures/derived-project-rollout.md`へ共通preflight、manifest、承認ゲートを記載する。
3. 同手順へoutfit-studioの現況・初期manifest・隔離戦略を追加する。
4. 構造テストを追加して台帳と手順の契約を固定する。
5. outfit-studioへ机上適用し、派生リポジトリ無変更を確認する。
6. ローカル品質ゲート、独立ドキュメントレビュー、スペック準拠検証を実施する。
7. platform-harnessのPRを作成し、outfit-studio実展開は別Issueへ残す。

## セキュリティ考慮事項

- dirty / untrackedファイルを本文表示・自動コピーせず、パスと状態だけをpreflightへ記録する。
- `.claude/settings.local.json`、認証情報、MCP secret、AWS profile等のローカル設定を正典やPRへ取り込まない。
- remote URL、release tag、commit OIDを固定し、別リポジトリやstale refへの誤展開を防ぐ。
- hooksはtrust後にsandbox外で動く可能性があるため、対象ごとに人がレビューする。
- 有料LLM headless mode、GitHub Actions自動run、無承認の外部自動同期を使用しない。

## パフォーマンス考慮事項

- 全候補を毎回clone・検証せず、台帳棚卸しは軽量なmetadata確認に限定する。
- 重い差分調査と実機受け入れはユーザーが選んだ1件だけにオンデマンド実行する。
- 台帳のローカル状態は参考情報として古くなり得るため、実展開時のpreflightを省略しない。

## 将来の拡張性

- outfit-studioで確立したmanifestと承認ゲートを、`dev-tasks2-py`等へ再利用できる。
- 台帳を将来JSON/YAMLへ分離する場合も、remote一意キー・状態モデル・人の対象指定という契約を維持する。
- 半自動の差分レポート生成は追加可能だが、自動上書き・自動PR・自動マージは独立Issueで安全境界を設計する。
