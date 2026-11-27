# 設計

## 方針の全体像

スキルの側を規範(AGENTS.md・外部自動化ポリシー)に合わせる。規範の側に不備を見つけても直さず、本書「記録事項」に残す。スキルの frontmatter・ファイル名・配置は変えない(G3 不要を保つ)。

各項目は選択肢を示し、推奨案に「(推奨)」を付ける。ステップ4.5の承認で選択を確定する。

## 確定した方針(ステップ4.5、2026-11-28 06:11 承認)

| 項目 | 確定 |
|---|---|
| 1-1 Git Flow | 1-A(削除。AGENTS.md を先に改める旨の1文) |
| 1-2 CI | 案どおり(ローカル品質ゲート必須、Actions は任意・`workflow_dispatch` のみ) |
| 1-3 AGENTS.md 優先 | 1-3A(development-guidelines のみ) |
| 2 優先度 | 2-A(タスク属性 → 重要度 / importance)。**prd-writing の 166・172・271行も本作業で直す**(U6 #69 はマージ済みで、本ブランチの base に含まれる。承認時の指示) |
| 4 担保テスト | 4-B を次のとおり絞る(承認時の指示): ① develop はブランチとしての文脈(バッククォート、「develop ブランチ」、ツリー図、`develop から/へ/→` 等)に限り、語境界を付けて `development` / `development-guidelines` に一致させない。陰性例に `development-guidelines.md` を含む行を入れる ② `priority` の単独の語は検査せず、改名する識別子(`TaskPriority`・`PriorityEstimator`・`--priority`・「優先度(高/中/低)」)だけを対象にする ③ prd-writing の免除は設けない ④ 追加したテストが main の旧ファイルで失敗し、現在の全スキルでは誤検知なく通ることを確認する |

`guides/implementation.md` の変更理由は、優先度の改名だけである(Git Flow・CI の記述はない。663行の「CI」は判定の一元化の説明で、規範に反しない)。

以下の選択肢の表は、判断の記録として残す。

## 項目1: ブランチ戦略・CI(#58 項目1)

### 1-1. Git Flow の扱い

| 案 | 内容 | 利点 | 欠点 |
|---|---|---|---|
| **1-A(推奨)** | Git Flow の説明を削除する。既定は「feature/fix 等の作業ブランチ → PR → main」。「より複雑なブランチモデルが必要になったら、スキルのガイドで上書きせず、AGENTS.md(プロダクト固有層)の側を先に改める」と1文だけ書く | ガイドだけを読んだ AI が Git Flow を選ぶ余地がなくなり、矛盾の再発源を断てる。規範を変える経路(AGENTS.md)が明確 | Git Flow の解説が欲しい利用者は外部資料を参照する必要がある |
| 1-B | Git Flow を「大規模・複数リリースの並行運用時の選択肢」として短く残す(既定ではない、採用時は AGENTS.md を改める旨を付す) | 選択肢の知識がスキル内に残る | 「選択肢」として残すと、AI が規模を自己判断して採用しうる。AGENTS.md の基本フロー6 と食い違う運用を、スキルが半ば推奨する形になる |

推奨理由: AGENTS.md の基本フロー6 は「フィーチャーブランチから PR を作成し、main にマージ」を基本と定める。スキルの例は既定を示すものであり、規範にない運用を選択肢として残す理由が薄い。必要になった時点で規範側を変える方が、変更経路が一つで済む。

### 1-2. CI の扱い(案は1つ。承認で確定)

- `guides/process.md`「自動化の推進」を、次の構成に書き換える
  - **必須の品質確認はローカル品質ゲート**(プロジェクトの検証コマンドを1つのコマンドにまとめ、PR 前に実行する)。本プラットフォームの `scripts/local_quality_gate.py` を例として示す
  - **GitHub Actions は任意**。例の workflow は `on: workflow_dispatch` だけにし、push / pull_request では起動しない。成功を PR の完了条件にしない(外部自動化ポリシーへの参照を付す)
  - pre-commit フック(Husky 等)はローカルで動くため任意の補助として残す
  - 「導入効果」から「PR作成時に自動でCI実行され、マージ前に品質を担保」を削り、ローカル品質ゲートの効果に置き換える
- チェックリストの「CI/CDパイプラインが構築されている」を「ローカル品質ゲート(単一コマンド)が定義されている(CI は任意)」に置き換える(`SKILL.md`・`guides/process.md`)
- `template.md` の「レビュープロセス」の「自動テスト実行」を「ローカル品質ゲートの実行(全緑)」に、「作成前のチェック」に同ゲートの項目を加える

### 1-3. AGENTS.md 優先の明示

| 案 | 内容 |
|---|---|
| **1-3A(推奨)** | development-guidelines の `SKILL.md`「既存ドキュメントの優先順位」の先頭に「0. AGENTS.md と、それが参照する規範(外部自動化ポリシー等)」を置き、既存の開発ガイドラインもこれに従うこと、ガイドと食い違う場合は AGENTS.md を優先することを書く。`guides/process.md` の「Git運用ルール」冒頭にも同旨を1文置く |
| 1-3B | 1-3A に加え、prd-writing を除く設計スキル全部(architecture-design・functional-design・glossary-creation・repository-structure)の `SKILL.md` にも同じ優先順位を書く |

推奨理由: 矛盾が見つかったのは development-guidelines(ブランチ・CI)であり、他の設計スキルは規範と重なる領域が小さい。1-3B は一貫性が高いが、prd-writing(U6 の範囲)だけ欠ける不揃いが残る。1-3B を選ぶ場合、prd-writing への追加は U6 への引き渡し事項にする。

## 項目2: 「優先度」の二重の意味(#58 項目2)

### 実物の調査結果

| 意味 | 箇所 |
|---|---|
| 機能の優先順位(P0〜P2) | `prd-writing/SKILL.md`(139〜145, 249, 262, 319, 333行)・`prd-writing/template.md`(65, 76, 92行)、`functional-design/guide.md`(27行) |
| タスクの属性(high/medium/low) | `glossary-creation/guide.md`(36〜54, 122, 435行)、`architecture-design/guide.md`(70, 74行)、`development-guidelines/template.md`(161〜166行)・`guides/process.md`(114〜128行)・`guides/implementation.md`(46, 155, 167, 323行)、`functional-design/guide.md`(56, 63, 81〜90, 191〜195, 282〜305, 359〜367, 382〜400, 421〜422行)、`prd-writing/SKILL.md`(166, 172, 271行) |
| 第3の意味: レビュー指摘の重み([必須]/[推奨]/[提案]/[質問]) | `development-guidelines/template.md`(374行)・`guides/process.md`(288行)「優先度の明示」 |

### 選択肢

| 案 | 内容 | 利点 | 欠点 |
|---|---|---|---|
| **2-A(推奨)** | 「優先度」は機能の優先順位(P0〜P2)に固定する。タスクの属性は「**重要度**」(importance)に改める。型名・フィールド名・関数名・CLI オプションもそろえる(`TaskPriority`→`TaskImportance`、`priority`→`importance`、`estimatedPriority`→`estimatedImportance`、`PriorityEstimator`→`ImportanceEstimator`、`estimatePriority`→`estimateImportance`、`--priority`→`--importance`、「優先度自動推定」→「重要度自動推定」、ステアリング名の例 `add-priority-feature`→`add-importance-feature`)。値(high/medium/low・高/中/低)は変えない | task3 の決定と同じで、派生プロジェクトとの整合が取れる。P0〜P2 を使う prd-writing(U6 の範囲)を変えずに済む | prd-writing の 166・172・271行(タスクの属性の意味の「優先順位の自動推定」「--priority high」)が残る → U6 へ引き渡す |
| 2-B | タスクの属性を「優先度」のまま残し、機能の優先順位を「優先順位」「リリース優先度」等に改める | タスク管理の一般的な語感に近い | prd-writing の template・SKILL の多数の箇所(U6 の範囲)を変える必要があり、U8 で完結しない。task3 の決定とも逆になる |
| 2-C | 語は変えず、glossary-creation のガイドに「両義に注意」の注記だけを置く | 変更が最小 | 衝突そのものは残り、受け入れ条件を満たさない |

**第3の意味(レビュー指摘)**: 2-A・2-B のどちらでも、「優先度の明示」を「**指摘の区分の明示**」に改める([必須]/[推奨]/[提案]/[質問] はそのまま)。「重要度」にすると 2-A のタスク属性と衝突するため、別の語にする。

**glossary-creation の例**: 2-A では例の用語エントリを「重要度 (Importance)」にし、関連用語として「優先度(機能の優先順位 P0〜P2。PRD で使う)と区別する」旨を加える。用語集の作り方の例として、両義を避ける書き方そのものを示す。

**ずれ防止**: 置換は箇所ごとに行い、置換後に `priority` / `Priority` / 「優先度(高/中/低)」が編集対象のスキルに残っていないことを grep とテストで確認する。

## 項目3: 全スキルの調査結果(#58 の「未確認」)

調査範囲: `.claude/skills/`(設計スキル6種・steering・distill)、`.agents/skills/`(5種)、`.kiro/skills/`(5種)、`.claude/commands/`、`.claude/agents/`、`.kiro/agents/`、`.codex/`。観点: Git Flow / develop ブランチ、CI 必須・自動起動、PR を経ない運用・main への直接コミット、承認ゲートの迂回、非対話 LLM 実行、`.steering/` の扱い。

| # | 箇所 | 内容 | 規範 | 扱い |
|---|---|---|---|---|
| S1 | `development-guidelines/guides/process.md` 55〜81行 | 「ブランチ戦略(Git Flow採用)」、develop を統合先・CI 実施場所とする | AGENTS.md 基本フロー6 | **本作業で直す**(項目1-1) |
| S2 | 同 366〜384, 412〜415行 | CI 例が `on: [push, pull_request]`、「PR作成時に自動でCI実行され、マージ前に品質を担保」 | 外部自動化ポリシー(Actions は任意、`workflow_dispatch` のみ、成功を完了条件にしない) | **本作業で直す**(項目1-2) |
| S3 | 同 429行、`SKILL.md` 69, 103, 108行 | チェックリスト「CI/CDパイプラインが構築されている」「ブランチ戦略(Git Flow推奨)」、クイックリファレンス「Git Flow ブランチ戦略」 | 同上 | **本作業で直す** |
| S4 | `development-guidelines/template.md` 119〜137, 202〜207行 | ブランチ種別に develop、フローが main←develop←feature。レビュープロセスに「自動テスト実行」 | 同上 | **本作業で直す** |
| S5 | `development-guidelines/SKILL.md` 94〜96行 | 「リリース準備時: main へのマージ方針」(Git Flow の develop→main を前提) | AGENTS.md 基本フロー6・7 | **本作業で直す**(PR マージ後のリリースに改める) |
| S6 | `glossary-creation/guide.md` 102〜126行 | ステアリングファイルを「一時的なドキュメント」「タスク完了後1-2週間で削除」「削除またはアーカイブする」と例示 | AGENTS.md「作業単位のドキュメント: 履歴として保持」、distill が振り返りを横断収集する | **本作業で直す**(例を「履歴として保持」に改める。小さく、規範が明確) |
| S7 | `repository-structure/template.md` 290〜305行 | `.gitignore` と `.prettierignore`/`.eslintignore` に `.steering/`(「タスク管理用の一時ファイル」)を入れる例 | AGENTS.md「履歴として保持」。ただし本リポジトリ自身も `.gitignore` で `.steering/*` を除外し(テンプレート複製対象外にするため)、作業分は強制追加で記録している | **別 Issue**(規範側で、派生プロジェクトの `.steering/` を git 管理するかが明文化されていない。スキルだけを直すと規範を先取りする。記録事項 R2) |
| S8 | `prd-writing/SKILL.md` 166, 172, 271行 | 「優先順位の自動推定」「`--priority high`」(タスクの属性の意味) | 項目2 で決める用語 | **本作業で直す**(計画時は U6 への引き渡しとしたが、U6 #69 がマージ済みのため、承認時の指示で本作業に含めた) |
| S9 | 設計スキル全般の例 | 例の技術スタックが TypeScript・ESLint・Vitest・Jest | AGENTS.md の技術スタック固有層は「プロダクトごとに書き換える」層であり、例の言語は規範と矛盾しない | **対象外**(矛盾ではない。記録のみ) |
| S10 | `.claude/commands/`・`.claude/agents/`・`.agents/skills/`・`.kiro/skills/`・`.kiro/agents/`・`.codex/` | 手順書を参照する薄いラッパ。承認ゲート・ブランチ・PR・非対話 LLM の記述は手順書と一致 | — | **矛盾なし**(setup-project 関連は U6 が編集中のため、本調査では grep での確認にとどめた) |
| S11 | `steering`・`distill` スキル | 手順書を参照する薄いラッパ | — | **矛盾なし** |

## 項目4: 整合性の機械的な担保(#58 の提案)

| 案 | 内容 | 誤検知と保守 |
|---|---|---|
| 4-A | `tests/procedures/test_skill_norm_alignment.py` を追加し、ブランチ・CI だけを検査する: (a) `Git ?Flow(採用|推奨)` の表現、(b) 単独の語 `develop`(ブランチ名として。`development` 等の部分一致は除外)、(c) コードブロック内の workflow の `on:` に `push` / `pull_request` が現れる、(d) development-guidelines の `SKILL.md` に AGENTS.md 優先の記述があること | 対象語は狭く、日本語の本文で誤検知しにくい。`test_guard_forbidden_words.py` と同じく、陽性例・陰性例で検査器を検証する |
| **4-B(推奨)** | 4-A に加え、(e) タスク属性の旧語(英字の `priority` / `Priority` 識別子、「優先度(高/中/低)」)が設計スキルに残っていないことを検査する。prd-writing は U6 の範囲のため、理由(U6 への引き渡し)付きのファイル単位の除外にする | 英字識別子の検査は誤検知が小さい。除外はファイル単位で理由を書き、U6 で prd-writing が直ったら除外を外す(記録事項 R3 に明記) |
| 4-C | テストを追加せず、方針と理由を記録して別 Issue にする | — |

推奨理由: いずれも語の一覧と正規表現だけの小さな検査で、既存テストと同型に実装できる。用語の決定(項目2)は再混入しやすい(例を追加する人が `priority` と書きやすい)ため、4-B で併せて固定する価値がある。検査対象は `.claude/skills/`・`.agents/skills/`・`.kiro/skills/` の Markdown。

検査は「既定として書かれているか」の意味までは判定しない(例: 「Git Flow は採用しない」と書くと (a) に当たらないが、「Git Flow 採用」と否定文で書くと当たる)。そのため、禁止表現は既定を宣言する言い回し(「採用」「推奨」)に限定し、ガイド側で否定の説明が要る場合は別の言い回しを使う。

## 変更対象ファイル(推奨案を選んだ場合)

| ファイル | 変更 |
|---|---|
| `.claude/skills/development-guidelines/SKILL.md` | 本文のみ: 優先順位に AGENTS.md を追加、クイックリファレンス・使用シーン・チェックリストの Git Flow / CI 記述を改める |
| `.claude/skills/development-guidelines/guides/process.md` | Git運用ルール、コミット例(重要度)、レビュー指摘の区分、自動化の推進(ローカル品質ゲート・任意の Actions)、チェックリスト |
| `.claude/skills/development-guidelines/template.md` | ブランチ戦略、コミット例(重要度)、PR 作成前チェック・レビュープロセス、指摘の区分 |
| `.claude/skills/development-guidelines/guides/implementation.md` | 例のフィールド `priority` → `importance` |
| `.claude/skills/functional-design/guide.md` | タスク属性の型名・フィールド・推定器・UI 表・JSON 例を重要度へ(27行の P0 はそのまま) |
| `.claude/skills/architecture-design/guide.md` | 例の推定処理を重要度へ |
| `.claude/skills/glossary-creation/guide.md` | 用語例を「重要度」にし優先度との区別を追記、ステアリングファイルの例を「履歴として保持」へ、ディレクトリ例の名前 |
| `tests/procedures/test_skill_norm_alignment.py` | 新規(4-B) |

変更しない: `AGENTS.md`、`.claude/skills/prd-writing/`、setup-project 関連、`repository-structure/template.md`(S7 は別 Issue)、全 `SKILL.md` の frontmatter。

## 検証方針

- 段1: `uv run pytest` / `uv run ruff check` / `uv run basedpyright`。加えて、`git diff main --name-only` で U5・U6 の対象が含まれないこと、`git diff main -- '*SKILL.md'` で frontmatter に差分がないことを確認する
- 段2(スキル定義の実挙動): development-guidelines スキルと functional-design のガイドを読み込み、scratchpad に「開発ガイドラインの Git運用ルール節」と「機能設計のデータモデル節」を1回生成して、feature ブランチ + PR が既定・CI が任意・タスク属性が重要度で書かれることを観察する。検査器は違反を仕込んだ一時ファイルで陽性を確認する
- 段3: `Skill('code-review')`
- 段4: implementation-validator(並列)。`docs/` の永続ドキュメントは変更しないため doc-reviewer は不要

## 記録事項(直さずに記録する。別 Issue 候補)

- **R1(手順書の不備候補)**: add-feature ステップ4 のパス判定基準3「対象文書」の列挙(`CLAUDE.md` / `.claude/commands/` / `.agents/skills/` / `.kiro/skills/` 等)に、`.claude/skills/` の設計スキル(作成ガイド)が含まれるかが読み取れない。本作業は保守的に「含む」と判定した
- **R2(規範側の不明確)**: 派生プロジェクトで `.steering/` を git 管理するかが AGENTS.md に明文化されていない。AGENTS.md は「履歴として保持」とする一方、正典(本リポジトリ)の `.gitignore` は `.steering/*` を除外し(テンプレート複製対象外にするため)、作業分は `git add -f` で追跡している。配布物では無視の行が変換で消える(U2 の報告)。repository-structure テンプレートの `.gitignore` 例(S7)をどう直すかは、この明文化を待つ。**別 Issue の候補**
- ~~**R3(U6 への引き渡し)**~~: 解消。U6 #69 がマージ済みのため、prd-writing の3行は本作業で直した(S8)。テストに prd-writing の免除は設けていない

## 実装結果(ステップ5)

- 項目1: `guides/process.md` の Git Flow 節を「作業ブランチ + PR → main」に置き換え、冒頭に AGENTS.md 優先の1文、末尾に「複雑なモデルは AGENTS.md を先に改める」の1文を置いた。「自動化の推進」は、1. ローカル品質ゲート(必須)、2. CI(任意・`workflow_dispatch` のみ・成功を完了条件にしない)、3. pre-commit(任意)の順に再構成した。`template.md` のブランチ戦略から develop を除き、PR 作成前チェックとレビュープロセスをローカル品質ゲートに改めた。`SKILL.md` は本文だけを変更し(優先順位の 0 番に AGENTS.md、クイックリファレンス、リリース準備時、チェックリスト)、frontmatter は変えていない
- 項目2: 2-A のとおり改名した。`guides/implementation.md` は優先度の改名だけ(4箇所)。prd-writing は3行。glossary-creation の用語例は「重要度 (Importance)」にし、「区別する用語」として優先度(P0〜P2)を相互参照する形と、一語一義の注意を加えた
- 項目3: S6(ステアリングファイルの例)を「作業ごとに新規作成し、完了後も履歴として保持」に改め、例のディレクトリ名を `add-importance-feature` にした
- 項目4: `tests/procedures/test_skill_norm_alignment.py` を追加した(承認時の指示どおり絞った検査)。develop の語境界は ASCII の英数字・下線・ハイフンだけで判定する。Python の `\w` は日本語の文字を含むため、`(?![\w-])` では「developから」「developへ」を取りこぼすことが分かり、ASCII 限定の境界にした
