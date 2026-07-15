# 派生プロジェクト展開候補台帳

platform-harnessのリリース済み正典を展開する候補を、ローカルディレクトリではなくGitHub remote単位で管理する。候補登録は自動展開を意味しない。実展開はユーザーが1件を指定したときだけ、対象リポジトリの独立Issue・steering・feature branch・PRとして開始する。

- **台帳確認日**: 2026-07-15
- **確認時のplatform-harness release**: `v1.2.0`
- **展開手順**: `docs/procedures/derived-project-rollout.md`

## 管理規則

### 一意性

- 一意キーは`OWNER/REPOSITORY`形式のGitHub remoteとする。
- 同じremoteを指す通常checkout、worktree、clean clone、運用コピーは別候補として登録しない。
- ローカルパスは一時的な参考情報であり、同期先の識別子に使わない。
- 実展開時にはGitHub上のdefault branch、archive / template状態、最新commitを再確認する。

### Harness generation

| 値 | 意味 |
|---|---|
| `current-neutral` | `AGENTS.md`、中立`docs/procedures/`、複数ハーネスアダプタを持つ現行世代 |
| `legacy-platform-claude` | platform-harness由来だが、正典を`CLAUDE.md`へ内包する旧Claude専用世代 |
| `legacy-sdd` | platform-harness以前の共通SDD原則・steeringを持つ旧世代 |
| `distribution-asset` | 派生製品ではなく、ハーネス配布・実験を目的とする資産 |

### Strategy

| 値 | 意味 |
|---|---|
| `direct-sync` | 現行中立構成があり、release差分だけを同期できる |
| `migrate-then-sync` | 旧構成から中立コアとアダプタへ移行してからrelease差分を同期する |
| `decision-required` | 継続利用・統合・archive等の人による判断が先に必要 |
| `excluded` | 重複コピー、配布資産等で通常の派生プロジェクト展開対象にしない |

### State

```text
candidate
  ├─ user selects → approved → planned → in-progress → verified → synced
  ├─ unsafe / ongoing work → on-hold
  ├─ ownership unclear → decision-required
  └─ duplicate / superseded / distribution only → excluded
```

- 候補登録だけで展開を開始しない。`candidate`から`approved`へ進めるのは、ユーザーが対象remoteを明示した場合だけとする。
- `synced`は将来releaseへの追随完了を意味しない。`Last source`と最新releaseを比較し、次回の対象指定を待つ。
- `Local caution`は確認日時点の参考情報であり、展開可否は毎回のpreflightで再判定する。
- `on-hold`は阻害要因をG0で裁定・解消し、再preflightの証拠を記録した場合だけ`candidate`または`approved`へ戻す。`decision-required`は人の裁定を記録して`candidate`または`excluded`へ遷移する。
- `Last source`は未展開を`none`、履歴を確定できない場合を`unknown (investigate)`、展開済みを`vX.Y.Z / <7〜40桁のcommit SHA>`で表す。

## 展開候補

| Remote | Repository URL | Lineage evidence | Harness generation | Strategy | Priority | State | Last source | Last inspected | Local caution | Decision / next action |
|---|---|---|---|---|---|---|---|---|---|---|
| `kanan4gh/project-uroboros-neo` | https://github.com/kanan4gh/project-uroboros-neo | READMEにplatform-harness template由来を明記。`AGENTS.md`と3ハーネス資産あり | `current-neutral` | `direct-sync` | P0 | `candidate` | `none` | 2026-07-15 | local mainはremoteと同期、clean | ユーザー指定時に`v1.2.0`差分を直接同期 |
| `kanan4gh/outfit-studio` | https://github.com/kanan4gh/outfit-studio | `CLAUDE.md`に`SOURCE: github.com/kanan4gh/platform-harness`、`UPDATED: 2026-05-27` | `legacy-platform-claude` | `migrate-then-sync` | P0 | `on-hold` | `none` | 2026-07-15 | 通常checkoutに未追跡hooks・coverage・Playwright等あり。ハーネス正典と重なるopen PR #22あり | G0でPR #22のマージ・破棄・新移行への引継ぎを裁定し、再preflight後に個別Issueを開始 |
| `kanan4gh/dev-tasks2-py` | https://github.com/kanan4gh/dev-tasks2-py | `CLAUDE.md`に旧SDD原則とsteering。正典sourceは旧`claude-guidelines`構想 | `legacy-sdd` | `migrate-then-sync` | P1 | `on-hold` | `none` | 2026-07-15 | local mainがremoteより3 commits ahead、tracked / untracked変更あり | 既存作業の所有者判断と保全後にオンデマンド移行 |
| `kanan4gh/agentcore-work` | https://github.com/kanan4gh/agentcore-work | `CLAUDE.md`にplatform-harness SOURCE、READMEにharnessed by platform-harness | `legacy-platform-claude` | `migrate-then-sync` | P1 | `on-hold` | `none` | 2026-07-15 | 執筆中のtracked / untracked変更あり | 執筆作業が安全な区切りに達した後に移行 |
| `kanan4gh/dev-tasks2` | https://github.com/kanan4gh/dev-tasks2 | 旧SDD原則とsteeringを持つTypeScript版 | `legacy-sdd` | `migrate-then-sync` | P2 | `decision-required` | `none` | 2026-07-15 | 同一remoteのローカルコピーが複数ある | 継続利用するremote / checkoutを決めてから移行 |
| `kanan4gh/project-ouroboros` | https://github.com/kanan4gh/project-ouroboros | 旧platform-harness SOURCEを持つ実験プロジェクト | `legacy-platform-claude` | `decision-required` | - | `decision-required` | `none` | 2026-07-15 | localはfeature branch上 | `project-uroboros-neo`で置換済みか判断。置換済みなら同期しない |
| `kanan4gh/platform-harness-engineering` | https://github.com/kanan4gh/platform-harness-engineering | platform-harness派生のハーネス開発作業場とREADMEに明記 | `legacy-platform-claude` | `decision-required` | - | `decision-required` | `none` | 2026-07-15 | local mainにtasklist変更あり | 現行platform-harnessへ統合済みならarchiveを別Issueで判断 |
| `kanan4gh/platform-harness-for-codex` | https://github.com/kanan4gh/platform-harness-for-codex | ハーネス配布・実験用remote | `distribution-asset` | `excluded` | - | `excluded` | `none` | 2026-07-15 | 派生製品として数えない | 配布資産として別管理 |
| `kanan4gh/platform-harness-for-kiro` | https://github.com/kanan4gh/platform-harness-for-kiro | Kiroユーザー向けtemplate remote | `distribution-asset` | `excluded` | - | `excluded` | `none` | 2026-07-15 | 派生製品として数えない | 配布資産として別管理 |

## 重複ローカルコピーの除外

| Local path | 対応remote | 扱い |
|---|---|---|
| `/Users/akiraishihara/aiwork/operated/outfit-studio` | `kanan4gh/outfit-studio` | 運用コピー。候補を増やさず、preflight・編集・同期対象から除外 |
| `/Users/akiraishihara/aiwork/Claude-code-book/dev-tasks2` | `kanan4gh/dev-tasks2` | 同一remoteの別コピー。実展開時に正とするcheckoutを人が選ぶ |
| `/Users/akiraishihara/aiwork/temp/dev-tasks2` | `kanan4gh/dev-tasks2` | 一時コピー。同期先として数えない |

## オンデマンド運用

1. ユーザーがこの台帳からremoteを1件指定する。
2. 実行エージェントは候補行を出発点にするが、GitHub metadataとローカル状態を再取得する。
3. 対象リポジトリに独立Issue・steering・feature branchを作成し、同期元release / commitを固定する。
4. `docs/procedures/derived-project-rollout.md`に従って、差分同期または移行後同期を行う。
5. PRマージ後、`State`、`Last source`、`Last inspected`、`Decision / next action`を更新する。

候補登録、platform-harness release作成、他候補の同期完了をトリガーにした自動展開は行わない。複数remoteへの一括Issue・一括branch・一括PRも作らない。
