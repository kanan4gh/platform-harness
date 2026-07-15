---
name: add-feature
description: 新機能・バグ修正・既存機能変更をスペック駆動開発（SDD）フローで実装する。「add-featureを実行して」「新機能を追加して」「機能を実装して」と依頼されたときに使う。文書編集だけの依頼には使わない。
---

# 新機能追加（Kiroアダプタ）

**手順の正は `docs/procedures/add-feature.md` にある。必ず全文を読み、ステップ0〜8と完了条件に従うこと。**

## Kiro固有の割当

- ステップ4の計画は`.kiro/skills/steering/SKILL.md`から中立なsteering手順へ接続する
- ステップ4.5は唯一の承認ゲートである。計画要点と選択肢（承認して実装開始／修正を指示する／中止する）を示し、回答を待つ
- 承認後はtasklist.mdをリアルタイム更新しながらステップ5〜8を継続する
- 段4の独立検証は`.kiro/agents/implementation-validator.md`、docs変更時のレビューは`.kiro/agents/doc-reviewer.md`をサブエージェントとして使う。利用できない場合は独立した別コンテキストへ同じ手順を委譲する
- Kiro CLIでは`kiro-cli --agent sdd`を使うとStopフックが有効になる。IDEとの差分は`.kiro/README.md`を参照する
- 作業ツリー分離の専用機構を前提にせず、中立手順どおりフィーチャーブランチでmainから隔離する
