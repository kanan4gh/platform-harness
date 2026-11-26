---
name: setup-project
description: プロジェクト初期化。6つの永続ドキュメント(docs/)を対話的に作成する。「setup-projectを実行して」と依頼されたとき、テンプレート複製直後の初回セットアップで使う。
---

# 初回プロジェクトセットアップ(Codexアダプタ)

**手順の正は `docs/procedures/setup-project.md`(ハーネス中立の手順書)にある。必ず全文を読み込み、手順書の全体(作業単位(ブランチ・コミット・PR)、ステップ0〜7、承認ゲート、承認済みドキュメントの訂正)に従うこと。**

## Codex 固有の注記

- 承認ゲートと承認済みドキュメントの訂正の確認はテキスト方式(手順書の選択肢を明示して回答を待つ)。push・PR作成の前の確認も同じ
- 各ステップの「作成ガイド」は、現時点では `.claude/skills/[ガイド名]/`(prd-writing / functional-design / architecture-design / repository-structure / development-guidelines / glossary-creation)配下にある。置き場所だけがClaude側にあり、内容はハーネス中立なので、SKILL.md・guide.md・template.md をそのまま読み込んで使う
