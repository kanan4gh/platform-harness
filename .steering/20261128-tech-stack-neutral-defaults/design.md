# 設計書

## アーキテクチャ概要

既定の技術スタックを中立にし、技術スタックに依存する記述を「記入欄（AGENTS.md）」「切り替えの手順書（1か所）」「例と明示した記述（設計スキル）」の3種に整理する。

```
AGENTS.md 技術スタック固有層
  ├─ ハーネスが使う道具（固定。uv・pytest・ruff・basedpyright・品質ゲート）
  └─ プロダクトの技術スタック（記入欄 + 例1つ: Python + uv + pytest + ruff + basedpyright、クラウドなし）
        │ 書き換えるとき
        ▼
docs/procedures/tech-stack-switch.md（新設）
  ├─ 切り替えチェックリスト（対象ファイル・順序・確認コマンド）
  └─ 付録: AWS を使う場合の例（devcontainer・postCreate・MCP・主要コマンド・AGENTS.md 記入例）
```

**中心となる区別**: ハーネス自身（`scripts/`、`tests/`、`.claude/hooks/` 等）は、プロダクトの技術スタックにかかわらず Python + uv で動く。そのため `pyproject.toml`・uv・ruff・basedpyright・ローカル品質ゲートは「プロダクトの選択」ではなく「ハーネスの道具」として常に残る。TypeScript のプロダクトでも、これらは削除しない。この区別を AGENTS.md と手順書に明記し、「中立」と「ハーネスの道具まで外す」を混同しないようにする。

## 0. 先に調べたこと（配布の仕組み）

`scripts/build_template_distribution.py` は、release tag の blob から `distribution/template-manifest.json` の `include_paths`（exact allowlist）だけを取り出し、`transformations`（`replace_exact_once` / `truncate_at_marker`）を適用して配布物を作る。現在の変換対象は `.gitignore`・`AGENTS.md`・`CLAUDE.md`・`README.md`・`docs/harness-guide.md`・`docs/procedures/derived-project-rollout.md` の6ファイルで、いずれも「正典だけにある参照」（派生台帳、`docs/ideas/`、正典の README、正典の `.steering/` 無視）を消すための変換である。

| ファイル | 配布の扱い（現状） | 今回の修正場所 | 理由 |
|---|---|---|---|
| `AGENTS.md` | 変換あり（派生台帳の行、ideas へのリンク） | **正典** | 中立な記入欄 + 例は、正典（ハーネス自身の開発）にもそのまま当てはまる。例の構成が正典の実際の構成と一致するため、正典と配布物で求める内容が同じ |
| `docs/harness-guide.md` | 変換あり（冒頭の正典/配布の説明） | **正典** | AWS 前提は正典にとっても誤り（正典は AWS を使わない）。既存の変換の対象文字列には触れない |
| `docs/architecture.md` | 変換なし | **正典** | 正典の docs はテンプレートのひな形そのもの |
| `.claude/README.md` | 変換なし | **正典** | 1行の説明文 |
| `.devcontainer/devcontainer.json`・`postCreate.sh` | 変換なし | **正典** | 正典の開発も AWS を使わない。AWS 用は手順書の例へ移す |
| `.mcp.json.example` | 変換なし | **正典** | サンプル。AWS 用は手順書の例へ移す |
| `pyproject.toml` | 変換なし | **正典**（`select` の追加と違反修正） | 正典と配布物で同じ lint 設定が要る（配布物にもハーネスの Python ファイルが入り、同じ品質ゲートを通す必要がある）。下の「4」を参照 |
| `uv.lock` | 変換なし | 変更しない | 依存を変えない |
| 設計スキル（`.claude/skills/*`） | 変換なし | **正典** | 例の明示は正典にも当てはまる |
| `.gitignore` | 変換あり（`.steering/*` の無視を削除） | 変更しない | 既存の変換で、配布物は `.steering/` を追跡する。規範の明文化は AGENTS.md（正典）で行う |
| 新規 `docs/procedures/tech-stack-switch.md` | — | **正典**（manifest の `include_paths` へ追加） | 派生プロジェクトが使う手順書のため配布する |
| 新規 `tests/procedures/test_tech_stack_neutrality.py` | — | **正典のみ**（`include_paths` に入れない） | 既定の中立性を守る検査であり、派生プロジェクトが技術スタックを切り替えた後は成り立たない。U8 の `test_skill_norm_alignment.py` と同じ扱い（配布しない） |

**結論**: 今回は変換規則を1つも追加しない。正典と配布物で求める内容が違うのは `pyproject.toml` の `name` / `description` だけで、これはチェックリストで扱う（下の「4」）。変換規則は文字列の完全一致に依存し、正典を直すたびに壊れやすいため、増やさない方針をとる。

## 1. AWS 前提の集約（#54 項目1）

### 1-A. AGENTS.md 技術スタック固有層

| 選択肢 | 内容 | 評価 |
|---|---|---|
| **A1（推奨）** | 正典の AGENTS.md 自体を「ハーネスの道具（固定）」+「プロダクトの技術スタック（記入欄 + 例1つ）」にする。例は Python + uv + pytest + ruff + basedpyright（クラウドなし）で「例であって既定ではない」と明記 | 正典と配布物が同じ内容で済む。例が正典の実際の構成と一致する |
| A2 | 正典は記入済みのまま、変換規則で配布物だけ記入欄にする | 大きなブロックの完全一致変換になり壊れやすい。正典側も AWS 前提を持つ理由がない |

主要コマンドは「ハーネスの必須コマンド（品質ゲート・steering lint・外部有料自動化 lint）」と「プロダクトの確認コマンド（記入欄）」に分ける。`cdk` / `sam` / `aws sts` は手順書の AWS の例へ移す。

### 1-B. AWS の記述の集約先

| 選択肢 | 内容 | 評価 |
|---|---|---|
| **B1（推奨）** | 手順書 `docs/procedures/tech-stack-switch.md` を新設し、切り替えチェックリスト + 付録「AWS を使う場合の例」を置く | 依頼書の「切り替えの手順書の1か所」に一致。手順書群の一覧（AGENTS.md）へ追加する |
| B2 | `docs/harness-guide.md` に節を足す | ガイドは利用者向け概説で、手順の正ではない（AGENTS.md の「手順の正は `docs/procedures/`」に反する） |

### 1-C. `.devcontainer/` の AWS 設定

| 選択肢 | 内容 | 評価 |
|---|---|---|
| **C1（推奨）** | 既定から AWS 部分（aws-cli feature、`~/.aws` マウント、AWS 環境変数、AWS Toolkit 拡張、postCreate の CDK・SAM）を外す。AWS 用の差分は手順書の AWS の例に、追加する JSON 断片として置く | AWS の記述が1か所に集まる |
| C2 | `.devcontainer/aws/devcontainer.json` を別ファイルで置く | 2か所目の AWS 記述になり、手順書と二重管理になる。VS Code が構成の選択を求めるようになる |

C1 で残すもの: Python 3.12 イメージ、Claude Code feature、node feature（Claude Code feature と `npx` 系 MCP サーバーが使う）、docker-in-docker と Docker 拡張（コンテナを使う開発全般で使い、AWS 専用ではない）、GitHub CLI、Python・TOML 拡張。コンテナ名 `claude-aws-devcontainer-starter` は `sdd-devcontainer-starter` にする。postCreate は uv・ruff・basedpyright（ハーネスの道具）だけを入れる。

### 1-D. `.mcp.json.example`

AWS の2サーバー（`aws-mcp`、`awslabs.aws-iac-mcp-server`）を手順書の AWS の例へ移す。サンプルの「プロジェクト固有層（AWS、DB 等）」の説明を「（クラウド、DB 等）」にする。残る DB・ドキュメントの例はコメントアウトのまま（既定で有効なサーバーは0）。

### 1-E. その他

- `docs/harness-guide.md`: 冒頭・ツール表・前提条件・手順2・4から AWS を外し、切り替え手順書への参照を置く
- `docs/architecture.md`: 見出し「AWSアーキテクチャ」を「インフラ構成」にし、コメントを「クラウド・実行環境の構成を記述（使わない場合は削除）」にする
- `.claude/README.md` 209行: 「AWSアーキテクチャ」→「インフラ構成」

### 1-F. 切り替えチェックリスト（手順書の中身）

順序: (1) setup-project で `docs/architecture.md` を承認（技術スタックの決定）→ (2) add-feature で切り替え作業を行う（Issue + ステアリング。setup-project のブランチには混ぜない）→ (3) AGENTS.md 技術スタック固有層 → (4) `pyproject.toml`（name / description、アプリのコードを型検査の対象に追加）→ (5) `.devcontainer/` → (6) `.mcp.json.example` / `.mcp.json` → (7) `docs/harness-guide.md` の前提条件・ツール表 → (8) 確認コマンド。各項目に対象ファイル・変える内容・確認コマンドを置く。ハーネスの道具（pyproject.toml の dev 依存、品質ゲート、scripts/）は消さない旨を明記する。

## 2. 設計スキルの中立化（#54 項目2）

依頼書の「9ファイル」は、実物では12ファイル（glossary-creation・architecture-design・functional-design・repository-structure の各 template.md / guide.md の8ファイルと、development-guidelines の template.md・SKILL.md・guides/process.md・guides/implementation.md）に TypeScript・npm 系の記述があった。12ファイルすべてを対象にする。

| 選択肢 | 内容 | 評価 |
|---|---|---|
| **G1（推奨）** | コード例は TypeScript のまま残し、各ファイルの冒頭に「コード例は TypeScript で示す例。プロジェクトの技術スタックに置き換える」注記を置く。既定として読める記述（技術スタック表の Node/TS/npm の値、「採用ツール」としての ESLint・Prettier・Vitest、「TypeScriptで定義します」等）だけを、プレースホルダーまたは「例（TypeScriptの場合）」へ直す | 差分が小さく、U8 の修正（Git Flow 削除、「重要度」）を壊さない |
| G2 | コード例を Python 等へ書き換える | 差分が大きく、依頼書の範囲（例は例として残す）を超える |

主な修正点:
- architecture-design/template.md: 技術スタック表の値を `[言語・ランタイム]` 等のプレースホルダーへ
- architecture-design/guide.md: Node.js/TypeScript/npm の列挙を「例（TypeScript/Node.js の場合）」の見出しの下へ。バージョン固定の `package.json` 例を「ロックファイル」の一般原則 + 例に
- development-guidelines/guides/process.md: 「自動化項目と採用ツール」を「自動化項目（ツールは技術スタックに合わせて選ぶ。以下は TypeScript の場合の例）」へ。`package.json`・CI・Husky の例も例と明示（CI 例の `workflow_dispatch` は維持）
- development-guidelines/SKILL.md: 「TypeScript/JavaScript規約」→「言語別のコーディング規約（例は TypeScript）」
- functional-design/guide.md: 「データモデルは TypeScript のインターフェースで定義します」→「プロジェクトの言語の型定義（例: TypeScript の interface、Python の dataclass）で定義します」
- repository-structure/template.md: テスト命名等の拡張子を例と明示、`.gitignore` の例（下の「4」）、`.prettierignore, .eslintignore` 節を「ツールの除外設定（例: lint・フォーマッタ）」へ
- glossary-creation/guide.md: 「TypeScript」の用語例は例として残す（用語集の書き方の例であり既定ではない）。冒頭注記のみ

担保: 新規テスト `tests/procedures/test_tech_stack_neutrality.py` で、(a) architecture-design/template.md の技術スタック表に具体の言語名を既定値として書かない、(b) ```` ```typescript ```` のコード例を持つ設計スキルのファイルに注記がある、(c) process.md が ESLint 等を「採用ツール」として書かない、を検査する。

## 3. pyproject.toml（#54 項目3）

実測（main 6ea10aa）: `ruff check --select E,F,I` で **30件**（I001 16件、E501 14件。task3 の18件より多いのは、配布物にない `scripts/build_template_distribution.py` や `tests/distribution/` 等も正典に含まれるため）。F は0件。

| 選択肢 | 内容 | 評価 |
|---|---|---|
| **(a)（推奨）** | `select = ["E", "F", "I"]` を明示し、正典のハーネスのファイルを直して違反を0にする（I001 は `ruff check --fix` の自動修正、E501 は手で改行） | 正典と配布物で同じ設定・同じ結果。ハーネスのファイルが派生プロジェクトの lint 既定に従うので、派生側で除外の保守が要らない |
| (b) | ハーネスのパスを `per-file-ignores` で除外 | 派生プロジェクトにも除外が残り、ハーネスのファイルだけ規約外になる。除外対象の一覧の保守が要る |
| (c) | 変換で配布物だけに `select` を入れる | 配布物にもハーネスの Python ファイルが入るため、(a) か (b) が結局必要。変換が増える |

I001 の自動修正は import の並びだけを変え、挙動を変えない。E501 は文字列の分割・改行で直す（テストの期待文字列は連結で同値を保つ）。

**name / description**: 正典は `platform-harness` のまま変えない（変換規則で書き換えると `uv.lock` の project 名とずれ、ロックの更新が要るため）。チェックリストに「name / description を書き換え、`uv lock` でロックを更新する」手順を置く。description は「スペック駆動開発ハーネスのプラットフォームテンプレート」のままで、テンプレート由来であることが分かる。

**basedpyright の include**: 既定には `src` を足さない（存在しないパスを含めると警告の原因になり、アプリのコードの置き場所はプロジェクトが決める）。pyproject.toml にコメントで「アプリのコードのディレクトリを足す」旨を書き、チェックリストに手順を置く。ruff の `include` も同様（`*.py` は既にすべての Python ファイルに一致するため、Python のアプリなら追加不要である旨を手順書に書く）。

## 4. .gitignore の例（#54 項目4、U8 の S7）

実物の確認: 正典の `.gitignore` は `.steering/*` を無視し `!.steering/example/` を残す（日付付きステアリングは `git add -f` で追跡）。配布物では manifest の変換でこの3行が消え、派生プロジェクトは通常の `git add -A` で `.steering/` を追跡する（`tests/distribution/` の `test_generated_project_tracks_new_steering_with_plain_git_add` が担保）。

規範側の明文化: AGENTS.md は「`.steering/` は作業ごとに新規作成し、履歴として保持」と書くが、Git で追跡するとは書いていない。スキルの例が「`.steering/`（タスク管理用の一時ファイル）」を除外するのと矛盾しても、規範の根拠が弱い。そこで **AGENTS.md の「作業単位のドキュメント」に「`.steering/` は履歴として Git で追跡する（.gitignore で無視しない）」を1行足す**（推奨）。正典は無視したうえで `git add -f` で追跡しており「追跡する」は正典でも成り立つが、「無視しない」は正典では成り立たない。そこで正典の例外は `.gitignore` のコメント（既存）に任せ、AGENTS.md には「Git で追跡し、履歴として保持する」とだけ書く（配布される AGENTS.md に正典固有の事情を書かない）。

スキルの修正: repository-structure/template.md の `.gitignore` の例から `.steering/` を除き、「`.steering/` は履歴として追跡するため除外しない」を注記する。`node_modules/` は「言語・ツールが生成する依存・ビルド成果物（例: Python なら `.venv/`、Node.js なら `node_modules/`）」へ。lint ツールの除外設定の例からも `.steering/` を除く必要はない（lint の対象外にするのは規範と矛盾しない）ため残す。

## 5. 申し送りの処理

### U6 ①: AGENTS.md から setup-project の例外を参照するか

**参照を足す（推奨）**。AGENTS.md の「IssueとステアリングはセットでGitHub Issueを先に作成し…」の直後に「（setup-project は例外。`docs/procedures/setup-project.md` の「作業単位」を参照）」を1文で足す。AGENTS.md だけを読んだエージェントが setup-project で Issue・ステアリングを作る誤りを防ぐため。このセッションは AGENTS.md を編集してよい唯一のセッションなので、ここで行う。

### U6 ②: harness-guide の手順順序

| 選択肢 | 内容 | 評価 |
|---|---|---|
| **H1（推奨）** | harness-guide の手順5を「プロダクト固有層だけを書き換える（技術スタック固有層は記入欄のまま）」にし、setup-project の後に「技術スタックが例と異なる場合は、切り替え手順書に従って add-feature で切り替える」手順を足す。setup-project.md は変えない | ハーネスの道具は Python で固定のため、setup-project の品質ゲートは技術スタックの決定前でも動く。切り替えは Issue・ステアリング付きの通常の作業単位になり、1対1の規約に合う |
| H2 | setup-project.md の architecture ステップに AGENTS.md 更新のコミットを組み込む | setup-project の作業単位（文書ごとのコミット）と各ハーネスのアダプタ（`.claude/commands/setup-project.md` 等）とテストの変更が要り、U5 の範囲が広がる |

### U8: `.gitignore` の例

上の「4」で処理する。

## テスト戦略

- 新規 `tests/procedures/test_tech_stack_neutrality.py`（正典のみ。配布しない）:
  - AGENTS.md 技術スタック固有層が AWS・CDK・SAM を含まず、「例」「既定ではない」を含む
  - AWS の語（`AWS`、`aws-cli`、`cdk`、`sam`）が、配布対象（manifest の `include_paths`）のうち切り替え手順書以外に出ない。ただし `docs/procedures/derived-project-rollout.md`（U7 の範囲。配布物では該当節が切り詰められる）は、配布の変換後の内容で判定するか除外として明記する
  - 切り替え手順書に、チェックリスト（対象ファイル・順序・確認コマンド）と「AWS を使う場合の例」がある
  - `.devcontainer/devcontainer.json` を JSONC として読み、AWS の feature・マウント・環境変数・拡張がない
  - 設計スキルの検査（上の「2」）
  - repository-structure の `.gitignore` の例が `.steering/` を除外しない
  - `pyproject.toml` の ruff `select` が E・F・I を含む
- 既存テスト: `tests/distribution/`（manifest の実ファイル整合）、`test_skill_norm_alignment.py`（U8）、`test_lightweight_path_criteria.py`（AGENTS.md の docs 一覧）が通ること
- 実挙動: 一時 clone に一時 tag を付けて配布物を生成し、AWS の語の残存、`.devcontainer` の内容、ローカル品質ゲート（fixture ステアリング付き）を観察する

## 変更対象ファイル

正典で直す:
- `AGENTS.md`（技術スタック固有層、手順書の一覧、`.steering/` の Git 追跡、setup-project 例外の参照）
- `docs/procedures/tech-stack-switch.md`（新規）
- `docs/harness-guide.md`、`docs/architecture.md`、`.claude/README.md`
- `.devcontainer/devcontainer.json`、`.devcontainer/postCreate.sh`、`.mcp.json.example`
- `pyproject.toml`、ruff 違反のある Python ファイル（scripts/・tests/・.claude/hooks/ の約25ファイル。import 順と改行のみ）
- 設計スキル12ファイル（`.claude/skills/{architecture-design,functional-design,glossary-creation,repository-structure}/{template,guide}.md`、`.claude/skills/development-guidelines/{SKILL.md,template.md,guides/process.md,guides/implementation.md}`）
- `distribution/template-manifest.json`（`include_paths` へ新規手順書を追加）
- `tests/procedures/test_tech_stack_neutrality.py`（新規、正典のみ）

変更しない（記録のみ）:
- `docs/procedures/derived-project-rollout.md` 223行「platform-harnessのAWS向けdevcontainer」（U7 の範囲。Outfit-studio パイロット節で、配布物では切り詰められる）
- `docs/derived-projects.md`（台帳。配布しない）、`docs/ideas/`（配布しない）

## 実装の順序

1. ruff の `select` 追加と違反修正（機械的変更を先に分離してコミット）
2. 切り替え手順書の新設（AWS の例の受け皿を先に作る）
3. AGENTS.md の書き換え
4. `.devcontainer/`・`.mcp.json.example`・harness-guide・architecture・`.claude/README.md`
5. 設計スキル12ファイル
6. manifest 更新、新規テスト
7. 配布物の生成と確認

## セキュリティ考慮事項

- `~/.aws` のマウントを既定から外すことで、AWS を使わない利用者のコンテナへ認証情報が入らなくなる（改善）
- GitHub への書き込みは承認なしに行わない

## 将来の拡張性

- 他クラウド（GCP 等）の例が必要になれば、切り替え手順書の付録に「〜を使う場合の例」を並べる
