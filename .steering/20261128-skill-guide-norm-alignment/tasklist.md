# タスクリスト

## 作業状態

- **状態**: complete
- **状態更新日時**: 2026-11-28T06:20:06+09:00
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
  - important(検査器の取りこぼし): (1) push / pull_request 以外の自動起動(`schedule`・`pull_request_target` 等)を見逃す → `on:` のイベントは `workflow_dispatch` 以外をすべて違反とする許可リスト方式に変えた (2) `"on":`、`on: # コメント`、`push:` の後に値を続ける書き方を見逃す → 対応した (3) `git checkout -b feature/x develop` 等の git コマンドの develop を見逃す → 規則を追加した。いずれも陽性例を追加した
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

- [x] 永続ドキュメントの更新要否を判断し、必要な更新とレビューを完了(不要: `docs/` の永続ドキュメントに Git Flow・develop・「優先度」・旧識別子の記述はなく、スキルの例の変更は基本設計に影響しない。テストファイルの一覧を持つ文書もない)
- [x] README類の更新要否を判断し、必要なら更新(不要: README.md・.claude/README.md・.codex/README.md・.kiro/README.md に該当する記述がない)
- [x] 実装後の振り返りを記録
- [x] 全テスト通過、lintエラーなし、リリース判断を記録(pytest 432 passed、ruff・basedpyright 問題なし。リリース判断は振り返りに記載)

> 上の全チェック完了後、`python3 scripts/steering_state.py finish --harness "Claude Code"`で状態を遷移する。その後、add-featureステップ8で最終品質ゲートを1回実行する。ゲート失敗時は`resume`で`active`へ戻し、修正・再検証・振り返り更新・状態遷移をやり直す。

---

## 実装後の振り返り

### 実装完了日

2026-11-28

### 計画と実績の差分

**計画と異なった点**:

- prd-writing の3行を本作業で直した。計画の初版では U6 への引き渡しとしていたが、U6(#69)がマージ済みであり、承認時の指示で範囲に含めた。テストの prd-writing 免除も不要になった
- 担保テストは、承認時の指示で 4-B を絞った(develop はブランチの文脈だけ、`priority` の単独の語は検査しない、免除なし、旧ファイルで失敗することを確認)
- 段3の指摘で検査器を強化した: CI のトリガーを、push / pull_request の禁止リストから `workflow_dispatch` だけの許可リストに変えた。git コマンド中の develop を加え、入れ子のフェンスを扱えるようにした

**新たに必要になったタスク**:

- 段3の指摘対応(検査器の強化、SKILL.md の新規作成時の AGENTS.md 優先、glossary 例の判断基準と `#優先度` のリンク先、PR テンプレートの品質ゲート項目、lint-staged の例の不具合)
- 段4の指摘対応(design.md の古い記述の修正、調査の見落とし S12 の記録)

**技術的理由でスキップしたタスク**:

- 該当なし

### 学んだこと

**技術的な学び**:

- Python の正規表現の `\w` は日本語の文字を含む。日本語の文中で英単語の境界を取るには、`(?<![A-Za-z0-9_-])` のように ASCII に限った境界が要る(`(?![\w-])` では「developから」を取りこぼす)
- 禁止語の検査では、禁止リスト(push / pull_request)より許可リスト(`workflow_dispatch` だけ)の方が漏れにくい。規範が「これだけ許す」と書いているときは、検査も許可リストにそろえる
- スキルのガイドは、例の中に別のコードブロックを入れ子にする(```markdown の中の ```typescript)。CommonMark どおりのフェンス判定だと開閉が反転するため、文書の実態に合わせた判定が要る
- 検査器の有効性は、陽性例と陰性例だけでなく、旧い実物(main の旧ファイル)に当てて「旧い記述だけで失敗する」ことでも確かめられる

**プロセス上の改善点**:

- 計画時の調査は grep の語を「優先度」と「Git Flow / CI」に寄せたため、コマンド(`review-docs.md`)の「優先度: 高/中/低」を見落とした。独立コンテキストの段4が拾った。用語の調査では、語そのもの(「優先度」)を全指示面で grep する方が漏れにくい
- 改名(優先度 → 重要度)は語の置換で終わらず、例の内部の整合(値の定義と判断基準、リンク先の項目)まで崩れることがある。段3の独立レビューが有効だった

### 次回への改善提案

- 別 Issue の候補(本作業では直さず記録した):
  - S7 / R2: 派生プロジェクトで `.steering/` を git 管理するかを規範側で明文化する。そのうえで、repository-structure テンプレートの `.gitignore` 例を直す
  - S12: `.claude/commands/review-docs.md` の「優先度: 高/中/低」を、スキルの「指摘の区分」にそろえる。担保テストの対象を `.claude/commands/` へ広げるかも、あわせて決める
  - R1: add-feature のパス判定基準3「対象文書」に、`.claude/skills/` の設計スキル(作成ガイド)が含まれるかを明記する

### リリース判断

| 観点 | 評価 |
|---|---|
| ユーザー価値のあるまとまりか | Yes(派生プロジェクトが設計スキルの例をそのまま使っても、規範と食い違わない) |
| 未解決の重大バグ | なし |
| 適切なバージョン種別 | MINOR(配布物のスキル本文と担保テストの変更。破壊的変更なし) |

**提案**:

単独ではリリースしない。上位計画 B-2 のフェーズ3(U6・U8)の完了後に、未リリースの #66〜#69 と合わせて MINOR としてまとめてリリースすることを提案する。リリースの判断は石原さんに委ねる。
