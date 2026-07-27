# 設計書

## アーキテクチャ概要

終了時フックによる即時ブロックを廃止し、作業ライフサイクル、状態遷移、状態対応lint、PR前完了ゲートへ責務を分離する。状態は進捗の正本である`tasklist.md`に置き、意味判断はsteering手順、機械的更新は`steering_state.py`、整合性検証は`steering_lint.py`、PR前の完了要求は`local_quality_gate.py`が担う。

```text
ユーザーの作業
  └─ steering手順
       ├─ 新規作成 ─────────────────> active
       ├─ 明示的な中断 ─────────────> steering_state pause
       │                                └─ paused + 中断記録
       ├─ 再開 ─────────────────────> steering_state resume
       │                                └─ active + 再開記録
       └─ 実装・検証・振り返り完了 ─> steering_state complete
                                        └─ complete

検証
  ├─ steering_lint.py
  │    └─ 全履歴を通常プロファイルで単一走査
  └─ steering_lint.py --require-complete [対象]
       └─ 同じ走査で指定対象だけ完了規則を追加

PR前
  └─ local_quality_gate.py --steering [対象]
       └─ 完了プロファイルのsteering lintを1回起動
```

状態契約、遷移CLI、lint、ゲート、Stop不在は相互依存する。Stopだけを先に削除すると完了規律が弱くなり、状態だけを先に入れると旧C3と競合するため、1つのfeature PRで原子的に正典化する。

## 状態データ契約

### tasklistの状態ブロック

```markdown
## 作業状態

- **状態**: active
- **状態更新日時**: 2026-07-28T10:00:00+09:00
- **使用ハーネス**: Codex
```

- 状態値は`active / paused / complete`のみ
- 日時はタイムゾーン付きISO 8601
- 状態ブロックは1件だけ許可する
- 新規tasklistは`active`で作成する
- 状態なしの旧tasklistは、未完了ゼロなら`complete`相当として読む
- 状態なし・未完了ありは通常lintで分類要求を報告する
- `pause`は状態なし・未完了ありの旧tasklistも移行元として受け付け、状態と中断記録を同時追加できる

### 中断記録

```markdown
### 中断記録: 2026-07-28T18:00:00+09:00

- **使用ハーネス**: Codex
- **完了済みの範囲**: 状態対応lintまで
- **未コミット変更**: scriptsとtestsに変更あり
- **再開位置**: Stop不在テスト
- **中断理由**: ユーザーが作業中断を指示
```

`paused`の状態更新日時と一致する最新記録に必須5項目があることを検証する。過去の中断記録は履歴として保持するが、現在の状態判定には最新の対応記録だけを使う。

### 再開記録

```markdown
### 再開記録: 2026-07-29T09:00:00+09:00

- **使用ハーネス**: Codex
- **再開位置**: Stop不在テスト
- **再開理由**: ユーザーの再開指示
```

`complete → active`は最終品質ゲートまたはG3失敗後の修正にも利用するため、再開理由を必須とする。

## コンポーネント設計

### 1. `scripts/steering_state.py`

**責務**:

- 最新または明示された日付付きsteeringのtasklistを選択する
- 許可された遷移と前提条件を検証する
- 状態ブロック、中断記録、再開記録を定型更新する
- 全前提が成立した後に1回だけ書き込み、失敗時に部分更新を残さない

**遷移**:

| 操作 | 移行元 | 移行先 | 主な前提 |
|---|---|---|---|
| `pause` | `active`、状態なし・未完了の旧形式 | `paused` | 未完了あり、必須記録値あり |
| `resume` | `paused` | `active` | 有効な中断記録あり |
| `resume` | `complete` | `active` | 修正理由と再開位置あり |
| `complete` | `active` | `complete` | 未完了ゼロ、具体化済み振り返り、状態ブロック一意 |

**実装方針**:

- Python標準ライブラリだけを使う
- Markdown全体を自由解析せず、固定見出し・固定ラベル・正規表現を共有する
- project root外のtasklistを拒否する
- 日付接頭辞を持つディレクトリだけを対象にする
- 内容生成の判断はsteering手順が行い、CLIは値を引数で受け取る
- 状態解析と記録検証は`steering_lint.py`の純関数を再利用し、遷移とlintで契約を二重実装しない

### 2. `scripts/steering_lint.py`

**責務**:

- 全日付付きsteeringを単一走査する
- 各対象へ通常規則を1回だけ適用する
- 指定した完了対象へ追加の完了規則を適用する
- CLIの対象解決と決定論的な違反順序を保証する

**規則**:

| ID | 規則 |
|---|---|
| C1 | 必須ファイル（軽量パス例外を含む） |
| C2 | GitHub Issue URL |
| C3 | 状態と未完了タスクの整合性 |
| C4 | `complete`相当の振り返り |
| C5 | `paused`の中断記録 |
| G1 | 完了検査対象が`complete`相当 |

**C3 / C5 / G1の非重複**:

- `active`かつ未完了ありは通常lintで合格する
- `paused`かつ有効な記録と未完了ありは通常lintで合格する
- `paused`の記録不備はC5だけで報告する
- `active / paused`が完了対象ならG1だけで報告する
- `complete`かつ未完了ありはC3だけで報告し、状態値自体はG1を満たす
- 通常lintを別プロセスで先に実行せず、1回の`lint()`呼び出しへ`completion_target`を渡す

**CLI**:

```bash
python3 scripts/steering_lint.py [PROJECT_ROOT]
python3 scripts/steering_lint.py [PROJECT_ROOT] --require-complete
python3 scripts/steering_lint.py [PROJECT_ROOT] \
  --require-complete 20260728-steering-lifecycle-without-stop-hooks
```

存在しない対象、日付規約外、曖昧な対象、project root外はfail-closedにする。既存の軽量パス厳密判定、コードフェンス処理、worktree除外を回帰させない。

### 3. `scripts/local_quality_gate.py`

**責務**:

- `--steering [日付付き名]`を受け付ける
- 指定がなければ最新の日付付きsteeringを完了対象にする
- steering lintを`--require-complete`付きで1回だけ起動する
- pytest、ruff、basedpyright、metered automation lintの順序とfail-fastを維持する

通常作業中のlintは`steering_lint.py`を直接実行し、PR前の完了ゲートと分ける。

### 4. ハーネスアダプタ

**Claude Code**:

- `.claude/settings.json`の`Stop`登録を削除する
- `.claude/hooks/check_tasklist_complete.py`と専用テストを削除する
- `PostToolUse`の`remind_tasklist_update.py`は維持する
- READMEとsteeringスキルを、非強制リマインド＋共通状態遷移＋ローカルゲートの説明へ変更する

**Codex**:

- Stopだけを登録する`.codex/hooks.json`とStopスクリプトを削除する
- hooks trust、連続ブロックガード、Stop比較表をREADMEから削除する
- `.agents/skills/steering`へ明示的な状態操作を割り当てる

**Kiro**:

- `.kiro/agents/sdd.json`の`hooks.stop`とStopスクリプトを削除する
- IDE / CLIともStopなしとし、状態遷移・通常lint・完了lintを共通経路にする
- JSON agentのskill / resource / permission設定は維持する

**共通**:

- add-feature薄いアダプタから2回ゲートとStop前提を削除する
- フロントマター名・既存エントリポイント名は変更しない
- `tests/adapters/test_stop_hook_absence.py`で登録・実装の不在とPostToolUse維持を固定する

### 5. 中立手順とテンプレート

**steering**:

- `active / paused / complete`の意味を定義する
- 通常応答終了と意図的中断を分離する
- `pause / resume / complete`を状態操作として定義する
- モード3後に`complete`へ遷移する

**add-feature**:

- 承認待ちとStopフックの節を、承認待ちでも`active`を維持する契約へ変更する
- tasklistから最終品質ゲートフェーズを削除する
- ステップ7で`complete`へ遷移する
- ステップ8-Aは明示対象の最終ゲートを1回実行する
- ステップ8-Bは候補状態と受け入れ記録後状態にそれぞれ1回のゲートを実行する
- ゲート/G3失敗時は`resume`して影響する検証へ戻る

**harness acceptance**:

- Stop block fixtureを終了非ブロックfixtureへ変更する
- 自動検証できるStop不在・状態遷移・lintはpytestとCLIで確認する
- 対話型ではスキル読込、権限、通常終了、状態/lint経路を観察する
- 使い捨てclone内のfixtureを正式記録へ含めず、元リポジトリへ観察結果を転記する

**derived project rollout**:

- G3観点をUI・権限・終了非ブロック・状態/lintへ変更する
- manifestのAdd対象へ`steering_state.py`と状態遷移テストを追加する
- Stop専用スクリプト・状態ディレクトリを正典配布対象から外す
- 新しいadd-featureステップ8-Bの順序へ参照を更新する

**templates**:

- tasklistへ作業状態ブロックを追加する
- 最終品質ゲートチェックボックスを削除する
- 中断・再開・完了を手順管理へ移す
- acceptance recordへ「対象外」判定と終了非ブロック・状態/lint観点を追加する

### 6. 正典文書

- `AGENTS.md`: 状態、通常/完了lint、Stop不在、単一ゲート、併用時の共通状態遷移を汎用層へ反映する
- `CLAUDE.md`: Stopを削除しPostToolUseだけをClaude固有差分として説明する
- `docs/harness-guide.md`: 3ハーネス共通の状態遷移と終了非ブロックを利用者向けに説明する
- `docs/external-automation-policy.md`: 自動検証対象を「構造・形式・状態/lint判定」とし、削除済みStop判定への依存を残さない
- `docs/derived-projects.md`: 台帳の値は変えず、今回の正典機能を台帳更新として混在させない
- 空のプロダクト用テンプレート文書は変更しない

## データフロー

### 通常lint

```text
全日付付きsteeringを列挙
  → tasklistを各1回読む
  → 状態を解析（旧完了形式はcomplete相当）
  → C1〜C5を各1回評価
  → 結果を安定順で集約
```

### 完了lint

```text
完了対象を1件解決
  → 全日付付きsteeringを1回列挙
  → 各dirへC1〜C5を1回評価
  → 対象だけG1を追加評価
  → 結果を集約
```

### 最終品質ゲート

```text
実装・4段検証・振り返り・文書更新が完了
  → steering_state complete
  → local_quality_gate --steering [対象]
       → steering_lint --require-complete [対象]（1回）
       → 全緑
  → commit / G3 / PR
```

G3が必要な場合は、候補コミット前と受け入れ記録後でファイル状態が異なるため、それぞれの最終状態に対してゲートを1回ずつ実行する。これは同じ状態に対する自己参照の2回実行ではない。

## エラーハンドリング戦略

- 不明状態、重複状態ブロック、状態日時不正、記録欠落はlint違反にする
- 状態遷移CLIは全前提をメモリ上で検証し、違反時は非0終了してファイルを変更しない
- `complete`は未完了、振り返り見出し欠落、空の振り返り、プレースホルダー残存を拒否する
- 完了対象の不存在・規約外名はusage errorまたはG1違反としてfail-closedにする
- Stopフックのfail-open・連続ガード・揮発状態は実装ごと削除する
- metered automation lintの禁止シグネチャを手順本文へ否定例として再記載しない

## テスト戦略

### ユニットテスト

- 3状態と旧形式の解析
- 重複・不明・日時不正の状態ブロック
- C3 / C4 / C5 / G1の状態組み合わせと非重複
- paused履歴が別のcomplete対象を妨げないこと
- pause / resume / completeの正常・異常遷移と非変更保証
- 最新対象・明示対象・不正対象のCLI
- local quality gateが完了lintを1回だけ起動すること
- 既存の軽量パス・worktree除外・振り返り規則の回帰

### 構造テスト

- 3ハーネスにStop登録・実装が存在しない
- Claude CodeのPostToolUseリマインドが残る
- 手順・テンプレートに自己参照2回ゲートが残らない
- 派生展開manifestが状態遷移CLIを配布対象に含む
- アダプタが中立手順と状態遷移を参照する

### 実挙動検証

- 一時プロジェクトで`pause / resume / complete`を実行する
- `active / paused / complete / 旧形式`を通常lintと完了lintで観察する
- local quality gateのコマンド構成でsteering lint起動が1回であることを観察する
- clean cloneの3ハーネスで未完了`active`を読む依頼が通常終了することをG3で確認する

## 依存ライブラリ

新規依存は追加しない。Python標準ライブラリと既存のpytest基盤だけを使う。

## 変更対象

主な変更対象は次のとおり。実装時に全参照を検索し、Stop・2回ゲート・旧C3を現行契約として説明する箇所を同じ責務内で整合させる。

```text
scripts/
├── steering_lint.py
├── steering_state.py（新規）
└── local_quality_gate.py

tests/
├── lint/{test_steering_lint,test_steering_state,test_worktree_scan_exclusion}.py
├── scripts/test_local_quality_gate.py
├── adapters/{test_harness_acceptance,test_kiro_adapter,test_stop_hook_absence}.py
├── hooks/test_check_tasklist_complete*.py（削除）
└── procedures/{test_add_feature_ordering,test_derived_project_rollout}.py

.claude/
├── settings.json
├── hooks/check_tasklist_complete.py（削除）
├── hooks/remind_tasklist_update.py（維持）
└── README・skills・commands

.codex/
├── hooks.json（削除）
├── hooks/check_tasklist_complete.py（削除）
└── README

.agents/skills/
├── add-feature/SKILL.md
└── steering/SKILL.md

.kiro/
├── agents/sdd.json
├── hooks/check_tasklist_complete.py（削除）
└── README・skills

docs/
├── harness-guide.md
├── external-automation-policy.md
└── procedures/
    ├── steering.md
    ├── add-feature.md
    ├── harness-acceptance.md
    ├── derived-project-rollout.md
    ├── validate-implementation.md
    └── templates/{tasklist,harness-acceptance-record}.md

root/
├── AGENTS.md
├── CLAUDE.md
└── .gitignore
```

## 実装の順序

1. 状態解析・通常/完了lint・状態遷移CLIとテスト
2. local quality gateの明示対象・単一完了lint化
3. 3ハーネスのStop削除とStop不在構造テスト
4. 中立手順・テンプレート・正典文書・アダプタの更新
5. 派生展開手順とmanifestの整合
6. このtasklistを新状態契約へ移行してドッグフーディング
7. 静的検証、実挙動、独立レビュー、スペック準拠検証
8. 振り返り、`complete`遷移、候補ゲート、候補コミット、G3、受け入れ記録、最終ゲート、PR

## セキュリティ考慮事項

- 状態遷移CLIはリポジトリ内の明示対象だけを書き換える
- 外部通信、GitHub Actions、LLM起動を行わない
- subprocessを使う場合は引数配列・`shell=False`を維持する
- 揮発状態削除時に秘密情報やユーザー固有設定を読み取らない
- 禁止コマンドの具体的シグネチャは既存ポリシーへ一元化する

## パフォーマンス考慮事項

- `.steering/`は数百件までを想定し、各tasklistを1 lint実行につき1回だけ読む
- 完了プロファイルでも通常lintを別プロセスで再実行しない
- 状態遷移は対象tasklist 1件だけを読む

## 将来の拡張性

- `superseded`等の状態はユースケースが確定するまで追加しない
- 派生同期manifest検査CLIは別Issueへ分離する
- 正典release後、各派生プロジェクトはrelease tag / commitを固定し、排他的manifestで同期する
