---
name: steering
description: 作業指示毎の作業計画、タスクリストをドキュメントに記録するためのスキル。ユーザーからの指示をトリガーとした作業計画時、実装時、検証時に読み込む。
allowed-tools: Read, Write, Edit
---

# Steering スキル

**手順の正は `docs/procedures/steering.md`(ハーネス中立の手順書)にある。必ず読み込み、記載のモード(1: 作業計画 / 2: 実装 / 3: 振り返り)に従うこと。** テンプレートは `docs/procedures/templates/` にある。

## Claude Code 固有の注記

- 手順書の「規律の担保」は、このプロジェクトでは以下のフックが実装する(`.claude/hooks/`):
  - **Stopフック**: 最新ステアリングディレクトリのtasklist.mdに `[ ]` が残っていると、セッション終了がブロックされる
  - **PostToolUseフック**: 実装ファイルの編集が続いてtasklist.mdが更新されないと、リマインドが注入される
- 手順書の「ハーネス内部のタスク管理機能」はTodoWriteを指す(補助であり、正はtasklist.md)
- tasklist.mdの更新はEditツールでリアルタイムに行う
