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
| `kanan4gh/project-uroboros-neo` | https://github.com/kanan4gh/project-uroboros-neo | READMEにplatform-harness template由来を明記。`AGENTS.md`と3ハーネス資産あり | `current-neutral` | `direct-sync` | P0 | `synced` | `v1.6.1 / 6b13140` | 2026-08-29 | 正典側資産は未取り込み(`docs/derived-projects.md`・`tests/procedures/test_derived_project_rollout.py`・`docs/ideas/template-unification.md`)。neoは下流契約テスト`test_derived_project_rollout_downstream.py`を持つ。有料自動化ポリシーの文書名が異なる(正典`external-automation-policy.md` / neo`paid-automation-policy.md`)、`scripts/metered_automation_policy.json`の参照先も追随。neo固有文書(`harness-swap-design.md`・`docs/ideas/`3件)を保持。`.gitignore`はドッグフーディング履歴保持のため`.steering/*`を無視しない。`scripts/check_pr_file_overlap.py`はneo側だけ`except (OSError, UnicodeError)`で、正典未環流の改善のため温存する | neo PR #44 で`v1.6.1`をdirect-sync(main `02c7b0f`)。v1.3.0 / v1.5.1 / v1.6.0 / v1.6.1 の4回を実施済みだが、台帳更新は本行が初回(Issue #57)。次回はユーザー指定時に`v1.6.2`以降の差分をdirect-sync |
| `kanan4gh/outfit-studio` | https://github.com/kanan4gh/outfit-studio | PR #26で`AGENTS.md`とClaude Code / Codex / Kiroの3ハーネス構成へ移行済み | `current-neutral` | `direct-sync` | P0 | `synced` | `v1.4.0 / 2bd61f1` | 2026-07-24 | 通常checkoutの未追跡hooks・coverage・Playwright等は残存。次回もclean clone / worktreeを使用。steering_lintに outfit固有差分(LEGACY grandfather・PLACEHOLDER拡張)あり、direct-sync時は温存する | outfit-studio PR #34 で`v1.4.0`をdirect-sync(候補2〜6相当、固有差分温存)。PR #22は不要としてcloseし、PR #26で同期完了。次回はユーザー指定時に新しいplatform-harness releaseとの差分をdirect-sync |
| `kanan4gh/dev-tasks2-py` | https://github.com/kanan4gh/dev-tasks2-py | PR #27で`AGENTS.md`とClaude Code / Codex / Kiroの3ハーネス構成へ移行済み | `current-neutral` | `direct-sync` | P1 | `synced` | `v1.6.1 / 6b13140` | 2026-08-29 | steering_lintに派生固有差分(移行前18ステアリングのLEGACY grandfatherと契約テスト)あり、direct-sync時は温存する。台帳検査6件は正典側資産のため未取り込み。`.gitignore`は適応度計測のため`.steering/*`を無視しない。`pyproject.toml`は`[tool.ruff.lint] select`を明示(ruff既定のバージョン変動対策)。`.devcontainer/`はプロダクト固有(AWS CLI手動導入 + Obsidianマウント) | dev-tasks2-py PR #27 で`v1.6.1`をmigrate-then-sync(マージcommit `1d6074c`、authority handoff `e5ff9f6`)。G3はClaude Code / Codex / Kiro CLIの3実行面で合格、Kiro IDE面は本体未導入のため対象外。次回はユーザー指定時に新しいplatform-harness releaseとの差分をdirect-sync |
| `kanan4gh/agentcore-work-neo` | https://github.com/kanan4gh/agentcore-work-neo | READMEにplatform-harness template由来を明記。`AGENTS.md`と3ハーネス資産あり | `current-neutral` | `direct-sync` | P1 | `on-hold` | `v1.6.1 / 6b13140` | 2026-08-29 | 学習型プロジェクト(書籍の写経)。派生固有拡張として**学習パス**を実装済み(`scripts/steering_lint.py`に`LEARNING_PATTERN`・`has_learning_declaration()`・新規検査C6、`AGENTS.md`・`docs/procedures/`4件・`.claude/`2件)。正典へ未環流のため、direct-sync時は温存する。確認時点でfeature branchに滞在し写経途中の未追跡ファイルあり、ステアリング1件が`paused` | 進行中の学習作業があるため`on-hold`(Issue #59で登録)。展開はG0で章の区切りを待つか裁定し、clean clone / worktreeを用意する。学習パスを正典へ返すか別系統の正典とするかはproject-uroboros-neo側で検討中であり、台帳登録は環流先の決定を意味しない |
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
