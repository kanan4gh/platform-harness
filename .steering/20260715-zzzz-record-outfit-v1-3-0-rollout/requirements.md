# 要求定義

## 関連Issue

- https://github.com/kanan4gh/platform-harness/issues/20

## 使用ハーネス

- Codex

## 概要

outfit-studioのplatform-harness v1.3.0移行PR #26がG4でマージされた事実を、platform-harnessの派生プロジェクト台帳へ反映する。旧`on-hold` / `legacy-platform-claude` / `migrate-then-sync`状態を、実態に合わせて`synced` / `current-neutral` / `direct-sync`へ更新する。

## 背景

- outfit-studio PR #26は2026-07-15にmerge commit `ed6baaaeb5d57e8b5c07dcd64ce2464b64647587`でマージされた。
- outfit-studio Issue #25はPRマージによりクローズされた。
- 同期元はplatform-harness `v1.3.0 / bd2cd8c537fe257353e3efd19c1ea2407d6d6e66`である。
- 対象側では単一ローカル品質ゲート、独立レビュー、Claude Code / Codex / Kiroの対話型受け入れが合格し、GitHub Actions自動runと有料LLM headless mode起動は0件だった。
- `docs/procedures/derived-project-rollout.md`は、G4マージ後にplatform-harness側で別の台帳更新PRを作ることを要求している。

## 要求内容

1. `docs/derived-projects.md`のoutfit-studio行をマージ後の実態へ更新する。
2. Harness generationを`current-neutral`、Strategyを`direct-sync`、Stateを`synced`へ変更する。
3. Last sourceを`v1.3.0 / bd2cd8c`、Last inspectedを`2026-07-15`として記録する。
4. PR #22による旧阻害要因が解消され、PR #26で同期完了したことをDecision / next actionへ記録する。
5. 次回以降はユーザー指定時に新しいplatform-harness releaseとの差分だけを直接同期する状態とする。
6. 台帳以外の派生プロジェクト行とoutfit-studioリポジトリ本体を変更しない。

## 受け入れ条件

- [x] outfit-studio行のHarness generation / Strategy / State / Last sourceがマージ実態と一致する。
- [x] outfit-studioのremote行が引き続き1件だけである。
- [x] 他の派生候補行が変更されていない。
- [x] 台帳構造テストと単一ローカル品質ゲートが成功する。
- [x] GitHub Actions自動runと有料LLM headless mode起動が0件である。
- [x] Issue #20を参照する専用PRが作成される。

## スコープ外

- outfit-studio本体または運用コピーへの変更
- platform-harnessの新release作成
- 他の派生候補の同期開始・状態変更
- GitHub Actionsの手動実行
- LLM headless modeによる検証

## 参照

- https://github.com/kanan4gh/outfit-studio/pull/26
- https://github.com/kanan4gh/outfit-studio/issues/25
- https://github.com/kanan4gh/platform-harness/issues/18
- `docs/derived-projects.md`
- `docs/procedures/derived-project-rollout.md`
