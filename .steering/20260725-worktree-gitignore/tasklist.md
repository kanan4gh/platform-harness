# タスクリスト

## 🚨 タスク完全完了の原則

**このファイルの全タスクが完了するまで作業を継続すること**

### フェーズとステップの対応

| フェーズ | 消化する add-feature ステップ |
|---|---|
| フェーズ1（実装） | ステップ5（実装ループ） |
| フェーズ2（4段検証） | ステップ6 |
| フェーズ3（振り返りとドキュメント更新） | ステップ7 |
| フェーズ4（最終品質ゲート） | ステップ8 |

**ステップ5の実装ループが消化するのは実装フェーズだけ**であり、フェーズ2〜4を先行して消化しない。

### 必須ルール
- **最終的に全てのタスクを`[x]`にすること**
- 未完了タスク（`[ ]`）を残したまま作業を終了しない

---

## フェーズ1: 作業ツリーの無視指定（実装フェーズ / add-feature ステップ5で消化）

- [x] `.gitignore` に `.claude/worktrees/` を追加（理由をコメントで添える）
- [x] `tests/lint/test_worktree_scan_exclusion.py` を新規作成
  - [x] `git check-ignore` で `.claude/worktrees/` 配下が無視されることを検証
  - [x] `.claude/` 直下の管理対象ファイルが無視されない（過剰無視でない）ことを検証
  - [x] 変異テストで実効性を確認（`.gitignore` から当該行を外すと落ちること）
  - 変異テスト結果: 当該行を外す → `test_nested_worktree_checkouts_are_ignored` が落ちる / `.claude/` 全体を無視する → `test_managed_claude_files_are_not_ignored` が落ちる。両方向とも実効性を確認

## フェーズ2: 4段検証（add-feature ステップ6で消化）

> 各段を実行し、その段の指摘対応まで終えた時点で該当行を `[x]` にする。
> **軽量パス適用のため段3は変更差分のセルフレビューに縮約し、段4はスキップできる**（スキップする場合は理由をその行に記録する）。

- [x] 段1: 静的検証（`uv run pytest` 192 passed / `uv run ruff check .` All checks passed / `uv run basedpyright` 0 errors）
- [x] 段2: 実挙動検証（作業ツリーが存在する状態の親リポジトリで、ruff の走査対象から作業ツリーが消えること・ゲートが全緑になることを観察）
  - 実条件: 親リポジトリに作業ツリーが**2つ**存在（`feature+lightweight-path-criteria` / `feature+worktree-gitignore`）。`.gitignore` だけを差し替えて前後比較した

  | 計測 | 修正前 | 修正後 |
  |---|---|---|
  | `git status --porcelain` の worktree 行 | 1 | 0 |
  | `ruff check . --show-files` の worktree 内ファイル | **46** | **0** |
  | metered automation lint | passed | passed |

  - 他ツールが影響を受けないことを実測: basedpyright 0 errors（`include` がルート相対の明示ディレクトリ）／ pytest 190 collected で worktree 内の収集なし（`testpaths = ["tests"]`。`grep worktrees` は `test_derived_project_rollout.py::test_procedure_protects_dirty_worktrees_and_target_history` というテスト名の一致であり収集経路の問題ではない）／ steering lint exit=0（ルート `.steering` の非再帰走査）／ metered automation lint は PR #39 で対応済みのため修正前から緑
  - **副次的な発見**: 計測開始時、ローカルの main が origin/main より1マージ分古く（`39d4d28`、PR #39 のマージ `27f082e` が未取得）、そのため main の policy に `.claude/worktrees` 除外が無く metered lint が22件の違反を報告していた。`git pull --ff-only` で最新化して解消。ruff の計測自体は PR #39 が `.gitignore` を変更していないため影響を受けない
- [x] 段3: 変更差分のセルフレビュー（軽量パスの縮約）
  - 差分は `.gitignore` の1エントリ（理由コメント付き）と新規テスト1ファイルのみ。既存の `.gitignore` の書式（コメント＋エントリ）を踏襲している
  - 指摘1件を自己修正: `git check-ignore --no-index` の意図が非自明かつ load-bearing だったため docstring で明示した。このフラグが無いと追跡済みファイルは常に「無視されない」と判定され、`.claude/` 全体を無視するような過剰除外を書いてもテストが通ってしまう（変異テストでこの経路が効くことを確認済み）
  - ruff の走査設定（`pyproject.toml` の `include`）には手を入れていない。`.gitignore` で解決できることを段2で実測済み（46件→0件）
  - `.claude/worktrees/` を無視しても `git worktree list` / `git worktree remove` は `.git/worktrees` のメタデータを見るため影響しない（本作業中も正常動作を確認）
- [x] ~~段4: スペック準拠検証~~（**軽量パスのためスキップ**）
  - 理由: 適用基準4項目をすべて満たす軽量パスであり、add-feature 手順ステップ6の縮約規定によりスキップできる。design.md が無く、requirements.md の「実装対象の機能」3項目と受け入れ条件は段1・段2で直接検証済み（`.gitignore` への追加＝受け入れ条件1、テスト2件＝受け入れ条件2、ruff 46→0件と他ツール無影響＝受け入れ条件3）。スペックと実装の乖離を独立検証する余地が小さいと判断した

## フェーズ3: 振り返りとドキュメント更新（add-feature ステップ7で消化）

- [x] `docs/` 永続ドキュメントの更新要否を判断し、必要なら更新
  - 判断: **更新不要**。パス判定の基準3で確認したとおり、`docs/repository-structure.md` は `.claude/` をツリー内の1行で記すのみでサブディレクトリを列挙していない。`docs/external-automation-policy.md` の除外リストは metered automation lint 固有のもので、`.gitignore` を見る ruff には無関係。他の永続ドキュメントも `.gitignore` の内容を記述していない
  - このステップでは `docs/` を更新していないため、ステップ7内の review-docs レビューは対象なし
- [x] 実装後の振り返りを記録（このファイルの下部）

## フェーズ4: 最終品質ゲート（add-feature ステップ8で消化）

- [x] 最終品質ゲートを全体で1回パス（実行後に確認）: `uv run python3 scripts/local_quality_gate.py`

> **最終品質ゲートはこのファイルで最後のチェックボックスであり、1行だけ置く。** これ以降にチェックボックスを追加しない。
>
> ゲートは**2回実行が前提**: 1回目でゲート本体の健全性を確認 → この行を `[x]` にする → 2回目で全緑を最終確認する。
>
> **コミット・PR作成・G3受け入れ記録はチェックボックスにしない。** 実行管理は add-feature 手順に委ねる。

---

## 実装後の振り返り

### 実装完了日

2026-07-25

### 計画と実績の差分

**計画と異なった点**:
- 計画では ruff の走査対象が23件と見積もったが、実測時には作業ツリーが2つあったため**46件**だった。修正後は0件で結論は変わらない
- 計測中に、**ローカルの main が origin/main より1マージ分古い**ことが判明した（`39d4d28`、PR #39 のマージ `27f082e` が未取得）。そのため main の policy に `.claude/worktrees` 除外が無く、metered lint が22件の違反を報告していた。`git pull --ff-only` で解消。作業ツリーは `EnterWorktree` が origin/main から作るため、**ローカル main が古くても作業ツリーは最新**という状態が起こりうる

**新たに必要になったタスク**:
- なし。変更は計画どおり `.gitignore` 1ファイル＋テスト1ファイルに収まった

### 学んだこと

**技術的な学び**:
- **`git check-ignore` の `--no-index` が load-bearing**。これが無いと追跡済みファイルは常に「無視されない」と判定されるため、`.claude/` 全体を無視するような過剰除外を書いてもテストが通ってしまう。ignore ルールそのものを検証したいときは index を参照させない
- ruff は `include` で `*.py` のように階層非依存のパターンを使っていても、**除外は `.gitignore` に完全依存**する。ツールごとに走査範囲の決まり方が違う（ruff=`.gitignore`、basedpyright=`include` のルート相対明示、pytest=`testpaths`、自作lint=policy）ため、「作業ツリーを走査しない」保証は**ツールごとに別経路で確認する必要がある**
- 入れ子の checkout を無視しても `git worktree list` / `remove` は `.git/worktrees` のメタデータを見るため影響しない

**プロセス上の改善点**:
- **改訂後の基準3で軽量パスに乗った最初の実例**になった。design.md の作成とサブエージェント3体の起動が不要になり、Issue #38 と同規模の変更が実際に軽く回った。パス判定の4項目を計画時に提示したことで、判定根拠もその場で確認できた
- 段2で「他ツールが影響を受けないこと」を**推論ではなく実測**したことで、ローカル main の陳腐化という別の問題も検出できた。前回までは同種の主張をレビュアーの報告のまま受け取っていた

### 次回への改善提案

- 親リポジトリを対象にした計測を行う前に `git -C <main> log --oneline -1` で HEAD を確認する。作業ツリーは origin から作られるため、ローカル main との乖離に気づきにくい
- 「Xを走査しない」という保証を作るときは、**保証したいツールごとに走査範囲の決定機構を確認する**（設定ファイル / `.gitignore` / 明示パス）。1つのツールで塞いでも他が残る（本Issueは PR #39 の metered lint 対応が ruff に及んでいなかったケース）
- テストで外部コマンドを使うときは、**非自明なフラグの意図を docstring に残す**。`--no-index` は消されても表面上テストが通り続けるため、意図が失われると静かに無効化される

### リリース判断

> Claude が評価・提案し、プロジェクトオーナーが最終決定する。

**前提条件の確認**:
- 全テスト通過: はい（`uv run pytest` 192 passed）
- リントエラーなし: はい（`uv run ruff check .` All checks passed / `uv run basedpyright` 0 errors）
- リリースノートに記載すべき変更内容が整理されている: はい（作業ツリーを ruff の走査対象から外す。PR #39 の metered lint 対応と対になる修正）

**評価**:

| 観点 | 評価 |
|---|---|
| 今回の変更はユーザーにとって価値のあるまとまりか | Yes（PR #40 と合わせて「作業ツリーがゲート結果に影響しない」が完結する） |
| 未解決の重大バグはないか | なし |
| 適切なバージョン種別 | PATCH（単体） |

**提案**:
**PR #40 と合わせて `v1.5.0` としてリリース**することを提案する。本PR単体では PATCH 相当（ゲートの偽陽性修正）だが、PR #40 が軽量パス基準というワークフローの適用基準そのものを変える MINOR 相当の変更であり、2件をまとめると MINOR が妥当。ユーザーと「リリースは ruff 対策後にまとめる」方針で合意済み。

なお PR 作成は GitHub の Pull Requests が major outage 中（インシデント: critical）のため保留しており、復旧後に #40・#41 の2件をまとめて作成する。
