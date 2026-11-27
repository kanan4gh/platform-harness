# タスクリスト

## 作業状態

- **状態**: active
- **状態更新日時**: 2026-11-28T06:20:00+09:00
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

チェックボックスは、消化するステップごとに排他的に分割する。ステップ5の実装ループが消化するのは実装フェーズだけである。

| フェーズ | 消化するステップ |
|---|---|
| 実装フェーズ（フェーズ1〜4） | ステップ5 |
| 4段検証 | ステップ6 |
| 振り返りとドキュメント更新 | ステップ7 |
| `complete`遷移・最終品質ゲート・PR | ステップ7終端・ステップ8（手順管理） |

技術的理由でタスクが不要になった場合だけ、取り消し線と具体的理由を付けて完了扱いにする。時間や難易度を理由に使わない。

---

## フェーズ1: ブランチ戦略・CI を規範に合わせる（実装フェーズ / ステップ5）

- [x] `development-guidelines/guides/process.md` の Git運用ルールを、承認した方針(1-1)で feature ブランチ + PR → main を既定に書き換え、AGENTS.md 優先の1文を置く
- [x] `guides/process.md` の「自動化の推進」を、ローカル品質ゲート必須・GitHub Actions 任意(`workflow_dispatch` のみ、成功を完了条件にしない)に書き換え、チェックリストを改める
- [x] `development-guidelines/template.md` のブランチ戦略・PR 作成前チェック・レビュープロセスを改める
- [x] `development-guidelines/SKILL.md` の本文(優先順位・クイックリファレンス・使用シーン・チェックリスト)を改める。frontmatter は変えない

## フェーズ2: 「優先度」の二重の意味を解消する（実装フェーズ / ステップ5）

- [x] development-guidelines(`template.md`・`guides/process.md`・`guides/implementation.md`)のタスク属性の語と識別子を、承認した語にそろえ、レビュー指摘の「優先度の明示」を「指摘の区分の明示」に改める
- [x] `functional-design/guide.md` のタスク属性の語・型名・フィールド・推定器・UI 例・JSON 例をそろえる(P0 の記述は残す)
- [x] `architecture-design/guide.md` の例をそろえる
- [x] `glossary-creation/guide.md` の用語例を改め、優先度(P0〜P2)との区別を加える。ステアリングファイルの例を「履歴として保持」に改める(S6)
- [x] `prd-writing/SKILL.md` のタスク属性の3行(166・172・271行)をそろえる
- [x] 設計スキルに旧語(`priority` / `Priority` / 「優先度(高/中/低)」)が残っていないことを grep で確認する

## フェーズ3: 機械的な担保（実装フェーズ / ステップ5）

- [x] 承認した方針(4-B を絞った案)で `tests/procedures/test_skill_norm_alignment.py` を追加する(陽性例・陰性例。陰性例に `development-guidelines.md` を含む行を入れる)

## フェーズ4: 調査結果の確定（実装フェーズ / ステップ5）

- [x] design.md の調査一覧(S1〜S11)と記録事項(R1〜R3)を、実装結果に合わせて確定する(直した範囲・別 Issue・引き渡しの区分)

## フェーズ5: 4段検証（ステップ6）

- [x] 段1: 静的検証
  - [x] `uv run pytest`(418 passed)
  - [x] `uv run ruff check`(All checks passed)
  - [x] `uv run basedpyright`(0 errors, 0 warnings)
  - [x] `git diff main --name-only` で U5・U6 の対象を含まないこと、`SKILL.md` の frontmatter に差分がないことを確認(変更はスキル8ファイル・テスト1・ステアリング3。SKILL.md の差分は30行目以降だけ)
- [x] 段2: 実挙動検証(スキルを読み込んで節を1回生成し、成果物を観察。検査器を main の旧ファイルへ当てて、旧い記述の箇所だけで失敗し、`development-guidelines` を含む行が含まれないことを確認)
  - 検査器を main(262944e)の旧スキル30ファイルへ当てた(`git archive` で scratchpad に展開): 違反25件(git-flow-default 2、develop-branch 6、ci-auto-trigger 1、old-task-priority 16)。すべて旧い記述の箇所で、`development-guidelines` を含む行(11行。development-guidelines 自身の SKILL.md 4行と、他の5ファイルの6行と1行(.agents/.kiro の setup-project を含む))への誤検知は0件。旧 SKILL.md には AGENTS.md 優先の記述がないため、優先の検査も失敗する
  - 現在のブランチの全スキル(30ファイル)では、テストが誤検知なく通る(段1の pytest に含む)
  - スキルを読み込んで、架空の派生プロジェクト向けに「Git運用ルール」「PRプロセス」「CI(任意)」「データモデル」の節を1回生成した(scratchpad の `generated/sample-docs.md`)。作業ブランチ + PR → main、ローカル品質ゲート必須、CI は `workflow_dispatch` のみ、タスク属性は重要度(`TaskImportance`・`ImportanceEstimator`)、機能の優先度は P0 で書かれ、検査器の違反は0件。限界: 生成は著者と同じセッションで行った(独立の実行主体ではない)
  - 観察の途中で、functional-design のデータモデル例のコメント位置が改名でずれていたため直した(1行)
- [x] 段3: コードレビューと指摘対応
  - `/code-review medium main`(別コンテキスト): important 3、nit 5、pre_existing 1。すべて正当と判断して修正した
  - important(検査器の取りこぼし): (1) push / pull_request 以外の自動起動(`schedule`・`pull_request_target` 等)を見逃す → `on:` のイベントは `workflow_dispatch` 以外をすべて違反とする許可リスト方式に変えた (2) `"on":`、`on: # コメント`、`push: {…}` の書き方を見逃す → 対応した (3) `git checkout -b feature/x develop` 等の git コマンドの develop を見逃す → 規則を追加した。いずれも陽性例を追加した
  - nit: (4) 入れ子のフェンス(```markdown の中の ```typescript)で開閉が反転する → 情報文字列付きのフェンスを入れ子の開始とみなすスタックにし、陽性・陰性例を追加した (5) SKILL.md の AGENTS.md 優先が「既存がある場合」の条件の内側だけにある → 「新規作成時」の行にも書いた (6) glossary の重要度の例で、値の定義(影響)と判断基準(期限)が食い違う → 判断基準を緊急性と影響の両軸にそろえた (7) `#優先度` のリンク先がない → 例に「優先度 (Priority)」の項目を加え、相互参照にした (8) process.md の PR テンプレートに品質ゲートの項目がない → 加えた
  - pre_existing: (9) `.husky/pre-commit` の `npm run lint-staged` が未定義のスクリプト → `npx lint-staged` に直した(変更範囲内の例のため)
  - 再検証(増分): `uv run pytest`(432 passed)、ruff・basedpyright は問題なし。検査器を変えたため main の旧ファイルへの適用をやり直し、結果は同じ(違反25件、`development-guidelines` を含む行への誤検知0件。入れ子のフェンスを含む process.md の CI 例も引き続き検出)
- [x] 段4: スペック準拠検証と指摘対応
  - implementation-validator(別コンテキストのサブエージェント): 重大・中の指摘なし。受け入れ条件は実装側で全件充足
  - M1(`.claude/commands/review-docs.md` 53〜55行の「優先度: 高/中/低」、調査の見落とし): 承認範囲(スキル)外のアダプタのため、design.md に S12 として別 Issue で記録し、S10 の記述を補正した
  - M2(design.md の変更対象表・「変更しない」の行が承認後の確定方針と矛盾): 修正した
  - 軽微(functional-design の「高重要度/中重要度/低重要度」の語感): 「重要度が高い/中程度/低い」に改めた。テーブル罫線のずれは改名前からあるもので、対象外
  - doc-reviewer: `docs/` の永続ドキュメントを変更していないため不要

## フェーズ6: 振り返りとドキュメント更新（ステップ7）

- [ ] 永続ドキュメントの更新要否を判断し、必要な更新とレビューを完了
- [ ] README類の更新要否を判断し、必要なら更新
- [ ] 実装後の振り返りを記録
- [ ] 全テスト通過、lintエラーなし、リリース判断を記録

> 上の全チェック完了後、`python3 scripts/steering_state.py finish --harness "Claude Code"`で状態を遷移する。その後、add-featureステップ8で最終品質ゲートを1回実行する。ゲート失敗時は`resume`で`active`へ戻し、修正・再検証・振り返り更新・状態遷移をやり直す。

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
