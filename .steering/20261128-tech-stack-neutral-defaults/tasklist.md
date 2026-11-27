# タスクリスト

## 作業状態

- **状態**: complete
- **状態更新日時**: 2026-11-28T07:16:53+09:00
- **使用ハーネス**: Claude Code

## 作業履歴

_記録なし_

## タスク管理の原則

- `active`: 作業系列が継続中。未完了を許容する
- `paused`: 意図的な中断。有効な中断記録がある場合に未完了を許容する
- `complete`: 全タスクと振り返りが完了。未完了を許容しない
- 完了・技術的スキップは実態に合わせて即時記録する
- 「今日はここまで」はスキップではなく`scripts/steering_state.py pause`で記録する
- 最終品質ゲート、コミット、G3受け入れ記録、push、PRはチェックボックスにしない

### フェーズとadd-featureステップ

| フェーズ | 消化するステップ |
|---|---|
| 実装フェーズ（フェーズ1〜4） | ステップ5 |
| 4段検証 | ステップ6 |
| 振り返りとドキュメント更新 | ステップ7 |
| `complete`遷移・最終品質ゲート・PR | ステップ7終端・ステップ8（手順管理） |

---

## フェーズ1: lint の既定（実装フェーズ / ステップ5）

- [x] `pyproject.toml` に ruff の `select = ["E", "F", "I"]` と、型検査の対象にアプリのコードを足す旨のコメントを追加
- [x] I001 を `ruff check --fix` で自動修正し、差分が import の並びだけであることを確認（`git diff` で import 行と空行以外の変更が0行）
  - 計画との差: U7 の対象（`.github/workflows/`、`derived-project-rollout.md`）を参照するテスト4ファイル（`tests/automation/test_workflow_structure.py`、`tests/procedures/test_derived_project_rollout.py`、`tests/procedures/test_add_feature_ordering.py`、`tests/distribution/test_template_distribution.py`）は、依頼書の「参照するテストを編集しない」に従って修正を戻した。代わりに `per-file-ignores` で、その4ファイルの該当ルール（3ファイルは I001、test_add_feature_ordering.py は E501）だけを一時的に除外し、U7 マージ後に直して削除するよう申し送る
- [x] 自動修正の直後に、`tests/lint/test_steering_state.py` を含む全テスト（`uv run pytest`）が通ることを確認（承認時のユーザー指示）: 全432件と test_steering_state.py 26件が通過
- [x] E501 を手で直す（文字列は連結で同値を保つ）: 7ファイル10か所。フックの1行目の docstring は要約行と本文に分けた
- [x] `uv run ruff check .` が0件、`tests/lint/test_steering_state.py` を含む全テストが通ることを確認: ruff は All checks passed、pytest は432件、test_steering_state.py は26件が通過、basedpyright は0件

## フェーズ2: 技術スタック固有層と切り替え手順書（実装フェーズ / ステップ5）

- [x] `docs/procedures/tech-stack-switch.md` を新設（チェックリスト: 対象ファイル・順序・確認コマンド。付録: AWS を使う場合の例）
- [x] AGENTS.md 技術スタック固有層を「ハーネスの道具（固定）」+「記入欄 + 例1つ」へ書き換え
- [x] AGENTS.md の手順書一覧へ切り替え手順書を追加し、「技術スタックを変更するとき」から参照
- [x] AGENTS.md に `.steering/` を Git で追跡する旨を明文化
- [x] AGENTS.md の Issue・ステアリング規約から setup-project の例外を参照（U6 ①）
- [x] `distribution/template-manifest.json` の `include_paths` へ切り替え手順書を追加

## フェーズ3: AWS 前提の除去（実装フェーズ / ステップ5）

- [x] `.devcontainer/devcontainer.json` から AWS の feature・マウント・環境変数・拡張を外し、名前を変更
- [x] `.devcontainer/postCreate.sh` から CDK・SAM と AWS の確認を外す
- [x] `.mcp.json.example` から AWS の2サーバーを外す（手順書の例へ移したことを確認）
- [x] `docs/harness-guide.md` から AWS 前提を外し、手順の順序を整理（U6 ②: 手順5はプロダクト固有層のみ、setup-project の後に切り替え手順書）
- [x] `docs/architecture.md` の「AWSアーキテクチャ」を「インフラ構成」へ
- [x] `.claude/README.md` の「AWSアーキテクチャ」を「インフラ構成」へ

## フェーズ4: 設計スキルの中立化と担保テスト（実装フェーズ / ステップ5）

- [x] architecture-design（template.md・guide.md）
- [x] development-guidelines（SKILL.md・template.md・guides/process.md・guides/implementation.md）
- [x] functional-design（template.md・guide.md）
- [x] glossary-creation（template.md・guide.md）
- [x] repository-structure（template.md・guide.md。`.gitignore` の例を含む）
- [x] `tests/procedures/test_tech_stack_neutrality.py` を追加（正典のみ。配布しない）
  - 検出力の確認: 同じテストを main（6ea10aa）のスナップショットで実行すると28件が失敗する（AGENTS.md 固有層・AWS の語7ファイル・devcontainer・postCreate・手順書・ruff select・TS 注記10ファイル・技術スタック表・採用ツール・`.gitignore` の例）

## フェーズ5: 4段検証（ステップ6）

- [x] 段1: 静的検証
  - [x] `uv run pytest`（566件通過）
  - [x] `uv run ruff check .`（All checks passed）
  - [x] `uv run basedpyright`（0 errors）
- [x] 段2: 実挙動検証
  - [x] フック `.claude/hooks/remind_tasklist_update.py` を settings.json と同じ `python3` 起動で実行し、使い捨ての `CLAUDE_PROJECT_DIR` で観察（承認時のユーザー指示）: ①5回目の実装ファイル編集でリマインドが出る ②`.steering/` 配下の編集でカウントが0に戻る ③未完了ステアリングがなければ何も出さない ④終了コード0。このセッションの実際の注入の有無も記録
    - 結果（`python3` = Python 3.12.12）: ①edit1〜4 は count 1〜4 で出力なし、edit5 で additionalContext のリマインドが出て count が0に戻った ②count 2 の状態で `.steering/` 配下を編集すると0に戻り、出力なし ③未完了ステアリングがない場合、6回編集しても状態ファイルも出力もない ④終了コードはすべて0
    - 発見（既存の不具合。main 6ea10aa でも同じ。直さずに記録）: macOS 標準の `/usr/bin/python3`（3.9.6）では、import 時に `def check(...) -> dict[str, Any] | None` が TypeError になり、終了コード1になる。`main()` の try より前で起きるため fail-open にならない。settings.json の `python3` が PATH 上の 3.9 を指す環境では、編集のたびにフックのエラーになる（devcontainer は 3.12 のため影響なし）
    - 発見（既存の不具合。直さずに記録）: このセッションの実際の Edit/Write では、リマインドは注入されなかった。状態ファイルは worktree ではなく起動元の `platform-harness/.claude/hooks/state/edit_count.json`（count 0）にあった。フックは起動元を基準に最新ステアリングを探すため、worktree にある今回のステアリングを見ない（起動元の最新 `20261128-skill-guide-norm-alignment` は完了済み）。worktree で add-feature を行うと、リマインドが働かない
  - [x] devcontainer.json を JSONC として解釈し、AWS の要素がないことを確認: features は claude-code・node・docker-in-docker・github-cli、mounts と containerEnv はなし、拡張に AWS なし。`bash -n postCreate.sh` 成功
    - 未確認: コンテナの実際の再構築（Dev Containers での Reopen in Container）。この環境から VS Code の Dev Containers を操作する手段がないため。人の確認に載せる
  - [x] 一時 clone・一時 tag で配布物を生成し、内容と配布物での品質ゲートを確認（結果は design.md の「配布物の生成と確認の結果」）
- [x] 段3: コードレビューと指摘対応（`/code-review medium 6ea10aa`、7件）
  - important 1（Codex アダプタの「主要コマンド」参照切れ）→ 段4の確認中に修正済み
  - important 2（AGENTS.md「初回セットアップ」の手順2が、setup-project の前に技術スタック固有層を書き換えさせる）→ 手順2をプロダクト固有層だけにし、setup-project の後に切り替えの手順を足した
  - pre_existing 3（Python 3.9 でフックが import 時に落ちる）・4（worktree ではフックが起動元のステアリングを見る）→ 段2で見つけた2件と同じ。フックのロジックの変更は G3 の対象になり U5 の範囲を超えるため、直さずに申し送る
  - nit 5（付録の AGENTS.md 記入例が記入欄の形と違う）→ 記入欄と同じ見出し・項目・bash フェンスにそろえ、担保テストに項目の一致の検査を追加
  - nit 6（一時除外の表が配布物にも入る）→ 配布物にも test_workflow_structure.py と test_add_feature_ordering.py が入り、表を消すと配布物の ruff が落ちるため、表は残す。U7 マージ後に削除する申し送りとする。なお、配布物にない除外対象は2ファイル（test_derived_project_rollout.py・test_template_distribution.py。manifest の forbidden_paths で確認。レビューの「3」は誤り）
  - nit 7（担保テストの語の範囲が狭い）→ `s3`・`dynamodb`・`amazon` を加え、devcontainer の検査を大文字小文字を区別しない形にした（配布対象で誤検出が0件であることを確認）。`/* */` コメントへの対応は、devcontainer.json が `//` だけを使うため見送り
- [x] 段4: スペック準拠検証と指摘対応
  - implementation-validator: 重大な乖離なし。M1（G3 理由が「hooks は変更しない」と、docstring の改行と食い違う）→ requirements.md の G3 理由を修正。M2（design.md 3節に一時除外が未反映）→ 追記。M3（一時除外の表が配布物にも入る）→ 申し送りに残す。M4（除外ルールの記述が粗い）→ tasklist を修正
  - doc-reviewer: 2（順1の確認コマンドが記入の正しさを見ない）→ `grep -n '\[記入' AGENTS.md` を加え、開発環境の欄を `[記入。…]` にそろえ、担保テスト `test_every_fill_in_field_is_found_by_the_checklist_grep` を追加。3（段1の「検証コマンド」が2つの記入欄のどちらか不明）→ add-feature.md 段1と Claude / Codex アダプタに「ハーネスの必須コマンドと、記入があればプロダクトの確認コマンド」を明記。4（例と同じ構成の簡略パスが曖昧）→ 条件と、3〜6が不要な理由を明記。5（順の依存）→ プロダクトの設定ファイルを順3へ移す。6（MCP の確認）→ 有効化しないなら example の更新だけ・G3 不要と明記。9（付録の細部）→ v1.8.0 の言及を削除し、mounts・containerEnv にも「既存に加える」注記
  - doc-reviewer の見送り: 1（`.gitignore` との矛盾）は当たらない。配布物では manifest の変換で `.steering/*` の無視が消え、段2で実際に生成した配布物で確認済み。7（時期の言い方の差）は、AGENTS.md の手順4に時期を書いているため見送り。8（用語の揺れ）は低で、「記入の例」と「付録の例」を手順書で区別して書いたため、ほかは見送り。10（architecture-design スキルの節名）は、スキルに AWS の見出しがないことを grep で確認済み
  - 自分で見つけた不具合（段4の確認中）: `.agents/skills/add-feature/SKILL.md` が、AGENTS.md の改名前の見出し「主要コマンド」を参照していた → 「ハーネスの必須コマンド」と「プロダクトの確認コマンド」へ修正。ほかに参照がないことを grep で確認（本文の変更だけで、G3 不要の判定は変わらない）

## フェーズ6: 振り返りとドキュメント更新（ステップ7）

- [x] 永続ドキュメントの更新要否を判断し、必要な更新とレビューを完了: ステップ7で追加の docs/ の更新は不要（`docs/harness-guide.md`・`docs/architecture.md`・`docs/procedures/tech-stack-switch.md` は実装フェーズで更新し、段4の doc-reviewer でレビュー済み。ほかの docs/ はひな形で AWS・技術スタックの前提がないことを grep で確認）。ステップ7で docs/ を変更していないため、追加のレビューは不要
- [x] README類の更新要否を判断し、必要なら更新: `.claude/README.md` の「テストコマンドを変更する（他スタックへの複製時）」とステップ6のカスタマイズ方法が、段1のコマンドを他スタックのコマンドに置き換える前提だったため、「ハーネスの必須コマンドは残し、プロダクトの確認コマンドを AGENTS.md に書く」へ更新。`README.md`（正典）・`.codex/README.md`・`.kiro/README.md` は該当なし
- [x] 実装後の振り返りを記録
- [x] 全テスト通過、lintエラーなし、リリース判断を記録: pytest 567件、ruff 0件、basedpyright 0件（2026-11-28 07:16）。リリース判断は下の表

> 上の全チェック完了後、`python3 scripts/steering_state.py finish --harness "Claude Code"`で状態を遷移する。その後、add-featureステップ8で最終品質ゲートを1回実行する。

---

## 実装後の振り返り

### 実装完了日

2026-11-28

### 計画と実績の差分

**計画と異なった点**:

- pyproject.toml は (a)（違反0）を基本にしたが、U7 の対象を参照するテスト4ファイルを `per-file-ignores` で一時的に除外した（依頼書が U7 の参照テストの編集を禁じているため）。I001 の自動修正が、U7 の参照テストにも及ぶことを、実行後の差分で気づいた。計画時には、ruff 違反のファイルと U7 の範囲の重なりを確かめていなかった
- 設計スキルの対象は、依頼書の「9ファイル」に対して実物では12ファイルだった
- 配布物の生成は、計画ではフェーズ4のタスクだったが、段2の観察として1回だけ行った（実装フェーズで検証を先取りしないため）

**新たに必要になったタスク**:

- AGENTS.md の見出しの改名（「主要コマンド」→「ハーネスの必須コマンド」）に伴う、Codex アダプタ `.agents/skills/add-feature/SKILL.md` の参照の修正（段4の確認中に発見。code-review も同じ指摘）
- add-feature 段1の対象を「ハーネスの必須コマンド + プロダクトの確認コマンド」と明記（手順書と Claude / Codex アダプタ）
- AGENTS.md「初回セットアップ」の順序の修正（code-review の指摘）
- `.claude/README.md` の段1カスタマイズ説明の更新（ステップ7）

**技術的理由でスキップしたタスク**:

- 該当なし

### 学んだこと

**技術的な学び**:

- 「中立」の対象は、プロダクトの技術スタックだけである。ハーネスの道具（uv・pytest・ruff・basedpyright・品質ゲート）は、どの技術スタックでも残る。この2つを AGENTS.md で分けると、既定の例がハーネス自身の構成と一致し、正典と配布物で同じ内容にできた。変換規則を1つも足さずに済んだ
- 見出しの改名は、ほかのアダプタからの参照を壊す。AGENTS.md の見出しを変えるときは、`.agents/`・`.kiro/`・`.claude/` の全文を grep する
- フックは fail-open に見えて、import 時の例外（Python 3.9 の型注釈）は `main()` の try の外で起きるため、fail-open にならない。「出ないこと」では正常と区別できないため、出る条件を実際に起こして確かめる観察が要った（ユーザーの承認時の指示で追加）
- worktree 隔離のガードは、複合のシェルコマンドを拒否する。観察用の処理は scratchpad のスクリプトにまとめ、単純な1コマンドで起動した（ガードの対象である git の操作は、すべて worktree か scratchpad の使い捨ての clone に限った）

**プロセス上の改善点**:

- 並行作業がある場合は、一括の自動修正（`ruff --fix` 等）を実行する前に、対象ファイルが他の作業の範囲に入らないかを確かめる
- 日本語の文字列の完全一致による置換は、範囲の起点が複数あると広がりすぎる（AGENTS.md の `<!-- 他のリポジトリへの移植時` が3か所あった）。置換範囲は見出しを起点に決め、範囲の大きさを assert で確かめる

### 次回への改善提案

- 申し送り（別 Issue の候補）:
  1. フック `remind_tasklist_update.py` が Python 3.9 で import 時に落ちる（既存。`from __future__ import annotations` 等で直せる。フックの変更のため G3 が要る）
  2. worktree で作業すると、フックが起動元のステアリングを見てリマインドが働かない（既存。`CLAUDE_PROJECT_DIR` ではなく編集したファイルの位置から作業ツリーを求める等）
  3. U7 のマージ後に、U7 参照テスト4ファイルの ruff 違反を直し、`pyproject.toml` の一時除外の表を削除する（この表は配布物にも入る）
  4. `docs/procedures/derived-project-rollout.md` 223行の「platform-harnessのAWS向けdevcontainer」（U7 の範囲。Outfit-studio パイロット節で、配布物では切り詰められる）。本作業で既定が中立になったため、記述が古くなる
- 手順書の不備（直さずに記録）: add-feature 手順は「承認後は push・PR まで無停止」だが、上位の依頼書は GitHub への書き込みに個別の承認を求めた。両者の優先順位が手順書に書かれていない

### リリース判断

| 観点 | 評価 |
|---|---|
| ユーザー価値のあるまとまりか | Yes（配布テンプレートの既定から AWS・npm の前提がなくなり、切り替え手順が1か所にまとまる） |
| 未解決の重大バグ | なし（既存の不具合2件は申し送り。本作業の変更によるものではない） |
| 適切なバージョン種別 | MINOR（手順書の追加と既定の変更。データ形式・コマンドの破壊的変更なし） |

**提案**:

B-2 計画では、フェーズ4で U7 と並行して進めている。そのため、U5 と U7 の両方のマージ後に、まとめて MINOR リリースする（R1・R2 のやり直しの前提）。リリースは上位の判断に委ねる。
