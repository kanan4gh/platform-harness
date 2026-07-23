# 要求内容

## 概要

outfit-studioの台帳更新作業について、完了実態と一致していない受け入れ条件のチェック状態を補正する。

- **関連Issue**: https://github.com/kanan4gh/platform-harness/issues/22
- **使用ハーネス**: Codex

## 背景

PR #21でoutfit-studioのplatform-harness v1.3.0移行完了を派生プロジェクト台帳へ反映した。対応するtasklistには受け入れ条件6/6の充足、品質ゲート成功、PR作成が完了証拠とともに記録されている。一方、同作業の`requirements.md`では受け入れ条件6項目が`[ ]`のまま残っており、完了実態と記録が一致していない。

## ユースケースの軸

プロジェクト管理者が過去のsteeringを参照したとき、受け入れ条件のチェック状態から作業の完了実態を誤解なく確認できる。

## 実装対象の機能

### 1. 受け入れ条件の記録補正

- `.steering/20260715-zzzz-record-outfit-v1-3-0-rollout/requirements.md`の受け入れ条件6項目を`[x]`へ変更する。
- tasklist、完了証拠、マージ済みPR #21とrequirementsの記録を整合させる。

## 受け入れ条件

### 受け入れ条件の記録補正

- [ ] 対象の受け入れ条件6項目がすべて`[x]`になっている。
- [ ] 対象6項目の文言と、それ以外の過去steering記録が変更されていない。
- [ ] 今回のsteering記録を除き、変更対象が元の`requirements.md`だけに限定されている。
- [ ] steering lintと単一ローカル品質ゲートが成功する。
- [ ] Issue #22を参照するフィーチャーブランチのPRが作成される。

## 成功指標

- 過去steeringの受け入れ条件、tasklist、完了証拠の完了状態が一致する。
- 補正によるプロダクトコード・台帳・既存テストへの変更が0件である。

## スコープ外

以下はこのフェーズでは実装しない:

- `docs/derived-projects.md`の再変更
- outfit-studioリポジトリへの変更
- PR #21の実装内容や完了証拠の再評価
- 新しいリリースの作成

## 参照ドキュメント

- `.steering/20260715-zzzz-record-outfit-v1-3-0-rollout/requirements.md`
- `.steering/20260715-zzzz-record-outfit-v1-3-0-rollout/tasklist.md`
- https://github.com/kanan4gh/platform-harness/pull/21
