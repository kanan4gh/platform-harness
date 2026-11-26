---
name: setup-project
description: テンプレート複製直後に6つの永続ドキュメントを対話的に作成してプロジェクトを初期化する。「setup-projectを実行して」と依頼されたときに使う。
---

# 初回プロジェクトセットアップ（Kiroアダプタ）

**手順の正は `docs/procedures/setup-project.md` にある。必ず全文を読み、手順書の全体（作業単位（ブランチ・コミット・PR）、ステップ0〜7、文書ごとの承認ゲート、承認済みドキュメントの訂正）に従うこと。**

## Kiro固有の割当

- 各文書の作成後、選択肢（承認して次へ／修正を指示する／スキップ）を明示して回答を待つ。承認済みドキュメントの訂正と、push・PR作成の前の確認も、選択肢を明示して回答を待つ
- 作成ガイドは現時点では`.claude/skills/`配下のprd-writing / functional-design / architecture-design / repository-structure / development-guidelines / glossary-creationにある。内容は中立なので、各SKILL.md・guide.md・template.mdを読んで使用する
- ルート`AGENTS.md`のプロダクト固有層と技術スタック固有層を前提に文書を具体化する
