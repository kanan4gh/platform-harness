# タスクリスト

## 作業状態

- **状態**: active
- **状態更新日時**: 2026-11-28T07:20:00+09:00
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

- [ ] 永続ドキュメントの更新要否を判断し、必要な更新とレビューを完了
- [ ] README類の更新要否を判断し、必要なら更新
- [ ] 実装後の振り返りを記録
- [ ] 全テスト通過、lintエラーなし、リリース判断を記録

> 上の全チェック完了後、`python3 scripts/steering_state.py finish --harness "Claude Code"`で状態を遷移する。その後、add-featureステップ8で最終品質ゲートを1回実行する。

---

## 実装後の振り返り

### 実装完了日

{YYYY-MM-DD}

### 計画と実績の差分

**計画と異なった点**:

- {差分と理由}

**新たに必要になったタスク**:

- {追加タスクと理由}

**技術的理由でスキップしたタスク**:

- {該当なし、またはタスク名・理由・代替}

### 学んだこと

**技術的な学び**:

- {技術的知見}

**プロセス上の改善点**:

- {プロセス上の知見}

### 次回への改善提案

- {改善提案}

### リリース判断

| 観点 | 評価 |
|---|---|
| ユーザー価値のあるまとまりか | {Yes / No / 保留} |
| 未解決の重大バグ | {なし / あり: 内容} |
| 適切なバージョン種別 | {MAJOR / MINOR / PATCH / リリース不要} |

**提案**:

{リリース提案と理由}
