---
name: steering
description: 作業指示毎の作業計画、タスクリストをドキュメントに記録するためのスキル。作業計画時、実装時、検証(振り返り)時に「steeringを実行して」等と依頼されたとき、またはSDDフローの各段階で使う。
---

# Steering スキル(Codexアダプタ)

**手順の正は `docs/procedures/steering.md`(ハーネス中立の手順書)にある。必ず読み込み、記載のモード(1: 作業計画 / 2: 実装 / 3: 振り返り)に従うこと。** テンプレートは `docs/procedures/templates/` にある。

## Codex 固有の注記

- 手順書の「規律の担保」は、このプロジェクトでは `.codex/hooks.json` のStopフックが実装する(未完了タスクが残っているとセッション終了がブロックされる。プロジェクトをtrustした場合のみ有効)
- Claude Codeと異なり、実装ファイル編集中のリマインド(PostToolUse相当)はない。tasklist.mdのリアルタイム更新は自律的に徹底すること
- 承認が必要な場面では、AGENTS.md正文のテキスト方式(選択肢を明示して回答を待つ)を使う
