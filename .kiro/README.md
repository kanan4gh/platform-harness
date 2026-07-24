# Kiroアダプタガイド

`.kiro/`は、ハーネス中立のSDDコアをKiro IDE / Kiro CLIから使うための薄いアダプタです。プロセスの正典は`AGENTS.md`、手順の正は`docs/procedures/`にあり、ここにはKiro固有の呼び出し、サブエージェント、フック設定だけを置きます。

## 構成

```text
.kiro/
├── README.md
├── skills/                         # 中立手順へのラッパ5件
├── agents/
│   ├── doc-reviewer.md             # IDE用の独立文書レビュー
│   ├── implementation-validator.md # IDE用の独立実装検証
│   └── sdd.json                    # CLI用SDDエージェント
└── hooks/
    └── check_tasklist_complete.py  # CLI Stopフック
```

Kiroはワークスペースルートの`AGENTS.md`を読み込みます。`.kiro/skills/`はIDE / CLIの両方で発見され、依頼とdescriptionの一致または`/skill-name`で有効になります。

## 対応条件

- Kiro IDEはworkspace skillsとworkspace agentsをサポートする安定版を使用する
- Kiro CLIは2.7.0以降を使用する
- CLI設定`chat.disableInheritingDefaultResources=false`（既定値）を使用する
- workspaceをtrustし、ルート`AGENTS.md`と`.kiro/skills/`を読み込める状態にする

製品の更新で表示や設定名が変わる可能性があるため、版番号だけでなく上記設定との組で確認してください。

## Kiro IDE

1. リポジトリを開き、workspace trustを確認する
2. Agent Steering & Skillsで5つのworkspace skillを確認する
3. 新規チャットで例として`/steering`を選択する
4. Agent selectorで`doc-reviewer`と`implementation-validator`を確認する

Kiro IDEのStop triggerはblockできず、command actionのstdoutもStopでは継続判断に使えません。そのためIDE Stop Hookは配布しません。IDEではtasklist.mdを完了直後に更新し、ローカル品質ゲートを最終ゲートとします。

## Kiro CLI

Kiro CLI 2.7.0以降ではカスタムエージェントも`AGENTS.md`、workspace skills、steeringを既定継承します。`sdd.json`はこれらをresourcesへ重複登録しません。

既定継承を無効化している場合は次で戻します。

```bash
kiro-cli settings --workspace chat.disableInheritingDefaultResources false
```

agentを検証して起動します。

```bash
kiro-cli --version
kiro-cli agent validate --path .kiro/agents/sdd.json
kiro-cli --agent sdd
```

起動後に`/context`を実行し、`Active agent context: sdd`、`AGENTS.md`、5つのworkspace skillが各1回だけ表示されることを確認します。

`sdd.json`はread / write / shell / subagentを利用可能にしますが、事前許可するのはreadだけです。write / shellはKiroの確認対象のままです。Stopフックは最新tasklist.mdが着手済み(完了タスク1件以上)で未完了タスクを残していればblock decisionを返し(完了ゼロの未着手tasklistは承認ゲート/作業前とみなしfail-open)、同一内容を3回ブロックした後は無限ループ防止のためfail-openします。

## 実機受入チェックリスト

共通方針、証跡様式、LLM headless modeを使わない規則は`docs/procedures/harness-acceptance.md`を参照してください。以下はKiro固有の補足です。

対象タグまたはcommitを`/private/tmp`等へcloneした隔離環境で実施します。Kiroへ受入対象機能のsteering作成を依頼せず、確認専用の最小steeringを人が作成します。

Stop確認用ディレクトリは`.steering/YYYYMMDD-zz-kiro-stop-smoke/`とし、既存ディレクトリより辞書順で後になることを確認します。

`requirements.md`:

```markdown
# 要求内容
- **関連Issue**: https://github.com/OWNER/REPO/issues/1
- **使用ハーネス**: Kiro CLI
```

`design.md`:

```markdown
# 設計書
Stopフックとlintの実機確認だけを行い、製品ファイルは変更しない。
```

`tasklist.md`(形の正は`docs/procedures/harness-acceptance.md`の「Stop確認用sentinel tasklistの形」):

```markdown
# タスクリスト
- [x] Stop smoke 着手マーカー（人が事前に付ける。Stop契約の「着手済み」条件を満たすため）
- [ ] Stop smoke sentinel（agentは完了・更新しない。最初のblock後に人が中断する）
```

着手マーカーは人が最初から`[x]`で置きます。完了ゼロの未着手tasklistは承認ゲート/作業前とみなしてfail-openするため、未完了行だけではblockを観察できません。

選択対象を確認します。

```bash
find .steering -mindepth 1 -maxdepth 1 -type d \
  -name '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-*' -print | sort | tail -1
```

### IDE

- Agent Steering & Skillsにsteering / add-feature / setup-project / review-docs / distillが表示される
- 新規チャットで`/steering`を選択でき、実際にSKILL.mdが読まれる
- Agent selectorにdoc-reviewer / implementation-validatorが表示される
- read / write / shellの承認UIを個別に観察する
- Stop block不可を能力差として記録し、ローカル品質ゲートが代替になることを確認する

### CLI

- agent validateがexit 0になる
- `/context`で5 skillsが各1回だけ表示される
- 指定ファイルが実際に読まれた証跡を確認する
- shellとwriteを別々に依頼し、承認画面で拒否する
- 未完了tasklistを残して応答を終了し、Stop blockによる自動継続を確認する。Kiro CLIの版によってはstdout reasonがUIに表示されず、モデルの継続だけが見える
- モデルがtasklist更新を試みた場合はwriteを拒否する。最初の自動継続を確認した時点で`Ctrl+C`で中断し、write再試行やルールBの誤用を誘発させない
- 発火が画面だけでは判別できない場合、`.kiro/hooks/state/stop_guard.json`の`consecutive_blocks`増加を補助証跡にする
- `uv run python3 scripts/steering_lint.py`が確認用tasklistをC3、exit 1として検出する

観察結果は配布文書へ固定せず、作業単位の受け入れ記録へ保存します。未観察項目は合格に含めず、合格・不合格・保留・対象外を分けます。

## スキル

| スキル | 用途 | 中立手順 |
|---|---|---|
| `steering` | 計画・実装・振り返り | `docs/procedures/steering.md` |
| `add-feature` | IssueからPRまでの機能実装 | `docs/procedures/add-feature.md` |
| `setup-project` | 永続ドキュメント作成 | `docs/procedures/setup-project.md` |
| `review-docs` | ドキュメント品質レビュー | `docs/procedures/review-docs.md` |
| `distill` | 振り返りの蒸留 | `docs/procedures/distill.md` |

## IDEとCLIの差分

| 項目 | Kiro IDE | Kiro CLI |
|---|---|---|
| `AGENTS.md` | 自動読込 | 自動読込 |
| workspace skills | `.kiro/skills/` | `.kiro/skills/` |
| カスタムエージェント | Markdown | JSON |
| Stop規律 | block不可。ローカルゲートで捕捉 | `sdd.json`がblockフックを登録 |
| 最終ゲート | ローカル品質ゲート | ローカル品質ゲート |

## 既知の差分

- PostToolUse相当のtasklistリマインドは配布しません。tasklist.mdを完了直後に更新してください
- 強制力が必要なCLI作業では`kiro-cli --agent sdd`を使ってください
- Kiro本体のインストールとアカウント認証はテンプレートの配布対象外です
- setup-project用の詳細ガイドは、中立配置へ移すまで暫定的に`.claude/skills/`を参照します

## トラブルシューティング

- スキルが見えない: workspace root、trust、製品更新、window reloadの順で確認する
- CLIでスキルが二重表示される: `sdd.json`のresourcesに既定資源を再登録していないか確認する
- CLIの`sdd`だけスキルが見えない: `chat.disableInheritingDefaultResources`を`false`にする
- CLI Stopフックが動かない: `kiro-cli --agent sdd`で起動したか、`python3`が利用可能か確認する
- Stopフックが無言で通る: 入力異常や状態破損ではfail-openするため、steering lintを直接実行して診断する

## 公式仕様

- https://kiro.dev/docs/steering/
- https://kiro.dev/docs/skills/
- https://kiro.dev/docs/custom-agents/
- https://kiro.dev/docs/hooks/
- https://kiro.dev/docs/cli/skills/
- https://kiro.dev/docs/cli/custom-agents/configuration-reference/
- https://kiro.dev/docs/cli/hooks/
