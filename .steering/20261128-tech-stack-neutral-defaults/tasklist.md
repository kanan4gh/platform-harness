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
  - 計画との差: U7 の対象（`.github/workflows/`、`derived-project-rollout.md`）を参照するテスト4ファイル（`tests/automation/test_workflow_structure.py`、`tests/procedures/test_derived_project_rollout.py`、`tests/procedures/test_add_feature_ordering.py`、`tests/distribution/test_template_distribution.py`）は、依頼書の「参照するテストを編集しない」に従って修正を戻した。代わりに `per-file-ignores` で、その4ファイルの該当ルールだけを一時的に除外し、U7 マージ後に直して削除するよう申し送る
- [x] 自動修正の直後に、`tests/lint/test_steering_state.py` を含む全テスト（`uv run pytest`）が通ることを確認（承認時のユーザー指示）: 全432件と test_steering_state.py 26件が通過
- [x] E501 を手で直す（文字列は連結で同値を保つ）: 7ファイル10か所。フックの1行目の docstring は要約行と本文に分けた
- [x] `uv run ruff check .` が0件、`tests/lint/test_steering_state.py` を含む全テストが通ることを確認: ruff は All checks passed、pytest は432件、test_steering_state.py は26件が通過、basedpyright は0件

## フェーズ2: 技術スタック固有層と切り替え手順書（実装フェーズ / ステップ5）

- [ ] `docs/procedures/tech-stack-switch.md` を新設（チェックリスト: 対象ファイル・順序・確認コマンド。付録: AWS を使う場合の例）
- [ ] AGENTS.md 技術スタック固有層を「ハーネスの道具（固定）」+「記入欄 + 例1つ」へ書き換え
- [ ] AGENTS.md の手順書一覧へ切り替え手順書を追加し、「技術スタックを変更するとき」から参照
- [ ] AGENTS.md に `.steering/` を Git で追跡する旨を明文化
- [ ] AGENTS.md の Issue・ステアリング規約から setup-project の例外を参照（U6 ①）
- [ ] `distribution/template-manifest.json` の `include_paths` へ切り替え手順書を追加

## フェーズ3: AWS 前提の除去（実装フェーズ / ステップ5）

- [ ] `.devcontainer/devcontainer.json` から AWS の feature・マウント・環境変数・拡張を外し、名前を変更
- [ ] `.devcontainer/postCreate.sh` から CDK・SAM と AWS の確認を外す
- [ ] `.mcp.json.example` から AWS の2サーバーを外す（手順書の例へ移したことを確認）
- [ ] `docs/harness-guide.md` から AWS 前提を外し、手順の順序を整理（U6 ②: 手順5はプロダクト固有層のみ、setup-project の後に切り替え手順書）
- [ ] `docs/architecture.md` の「AWSアーキテクチャ」を「インフラ構成」へ
- [ ] `.claude/README.md` の「AWSアーキテクチャ」を「インフラ構成」へ

## フェーズ4: 設計スキルの中立化と担保テスト（実装フェーズ / ステップ5）

- [ ] architecture-design（template.md・guide.md）
- [ ] development-guidelines（SKILL.md・template.md・guides/process.md・guides/implementation.md）
- [ ] functional-design（template.md・guide.md）
- [ ] glossary-creation（template.md・guide.md）
- [ ] repository-structure（template.md・guide.md。`.gitignore` の例を含む）
- [ ] `tests/procedures/test_tech_stack_neutrality.py` を追加（正典のみ。配布しない）

## フェーズ5: 4段検証（ステップ6）

- [ ] 段1: 静的検証
  - [ ] `uv run pytest`
  - [ ] `uv run ruff check .`
  - [ ] `uv run basedpyright`
- [ ] 段2: 実挙動検証
  - [ ] フック `.claude/hooks/remind_tasklist_update.py` を settings.json と同じ `python3` 起動で実行し、使い捨ての `CLAUDE_PROJECT_DIR` で観察（承認時のユーザー指示）: ①5回目の実装ファイル編集でリマインドが出る ②`.steering/` 配下の編集でカウントが0に戻る ③未完了ステアリングがなければ何も出さない ④終了コード0。このセッションの実際の注入の有無も記録
  - [ ] devcontainer.json を JSONC として解釈し、AWS の要素がないことを確認
  - [ ] 一時 clone・一時 tag で配布物を生成し、内容と配布物での品質ゲートを確認
- [ ] 段3: コードレビューと指摘対応
- [ ] 段4: スペック準拠検証と指摘対応

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
