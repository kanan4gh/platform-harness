# タスクリスト

## 作業状態

- **状態**: complete
- **状態更新日時**: 2026-11-17T13:56:00+09:00
- **使用ハーネス**: Codex

## 作業履歴

- 2026-11-17T13:18:02+09:00 Codex: 過去セッションから再開。Issue #64のworktreeと既存ドラフトを特定し、診断テスト27件中26件成功・1件過剰検出を確認した。計画承認前のためドラフト本体は未修正。
- 2026-11-17 Codex: 承認済み計画に基づく実装、段1〜3、初回の独立レビューを完了後、レビュー指摘を反映した地点でユーザー指定により一時中断した。
- 2026-11-17T13:33:53+09:00 Codex: 中断記録を正として再開。別セッションが再構成したsteeringを実装実績と照合し、完了済み進捗を復元した。

## タスク管理の原則

- `active`: 作業系列が継続中。未完了を許容する
- `paused`: 意図的な中断。有効な中断記録がある場合に未完了を許容する
- `complete`: 全タスクと振り返りが完了。未完了を許容しない
- 完了・技術的スキップは実態に合わせて即時記録する
- 最終品質ゲート、コミット、G3受け入れ記録、push、PRはチェックボックスにしない

---

## フェーズ1: 配布契約と生成CLI（実装フェーズ / ステップ5）

- [x] Issue #64と既存ドラフトを照合し、exact allowlist manifestのinclude/required/forbidden/transformationsを確定する
- [x] Git objectベース生成CLIのtag・origin・path・mode・output・provenance検証を完成させる
- [x] manifestと生成CLIの正常系・異常系・決定性・実行bitテストを完成させる
- [x] 正典専用文書への具体的参照だけを検査し、`docs/ideas/`一般概念を誤検出する既存テストを修正する

## フェーズ2: 配布物契約と実追跡（実装フェーズ / ステップ5）

- [x] 生成物のcanonical-only資産0件と`.steering/example/`限定を実manifestで固定する
- [x] 生成物で新規日付付きsteeringが通常の`git add -A`対象になる契約を固定する
- [x] 生成物内ローカル品質ゲートを実データで実行できるfixture・観察手順を確定する

## フェーズ3: 正典・配布案内と運用手順（実装フェーズ / ステップ5）

- [x] README、harness guide、setup手順の正典/配布境界を一貫させる
- [x] 初回公開・継続更新・rollback手順のpreflight、禁止境界、検証、settings変更順、証跡を完成させる
- [x] 手順構造テストでマージ/release前禁止、新旧template設定順、rollback、無課金検証境界を固定する

## フェーズ4: 4段検証（ステップ6）

- [x] 段1: 静的検証
  - [x] `uv run pytest`（226件成功。レビュー指摘反映分は増分再検証を実施）
  - [x] `uv run ruff check .`
  - [x] `uv run basedpyright`
  - [x] `python3 scripts/steering_lint.py`
  - [x] `python3 scripts/metered_automation_lint.py`
- [x] 段2: 実挙動検証
  - [x] clean local source tagから2回生成し、path・内容・実行bit・metadata・禁止path 0件を観察
  - [x] 生成物へ完了済みfixture steeringを追加し、ローカル品質ゲート成功（188件）を観察
  - [x] 新規日付付きsteeringが通常の`git add -A`でindexへ入ることを観察
- [x] 段3: コードレビューと指摘対応（source origin照合、metadata予約path拒否、除外文書参照変換を追加）
- [x] 段4: スペック準拠検証とドキュメントレビューの指摘対応（両独立レビュー合格、残課題なし）

## フェーズ5: 振り返りとドキュメント更新（ステップ7）

- [x] 永続ドキュメントの更新要否を判断し、`docs/harness-guide.md`・setup手順・新規配布手順の更新と独立レビューを完了
- [x] README類の更新要否を判断し、正典READMEと生成時の配布README変換を完了
- [x] 実装後の振り返りを記録
- [x] 段1全体検証とレビュー修正後の増分検証が成功し、lintエラーなし、リリース判断を記録

---

## 実装後の振り返り

### 実装完了日

2026-11-17

### 計画と実績の差分

**計画と異なった点**:

- PR #53の実証済み生成核に加え、source originとmanifest repositoryの照合、生成metadata予約pathの宣言拒否を正典公開用のprovenance強化として追加した。
- canonical-only文書を除外するだけでは配布物内に欠落参照が残るため、同一pathへ複数の完全一致変換をmanifest順で適用する機能を追加し、AGENTS・CLAUDE・派生展開手順の参照を上流URLへ変換した。
- 正典repositoryのREADMEをplatform-harness自身の説明へ改め、生成時にプロジェクト用README全体へfail-closed変換する構成にした。
- トークン利用制限による中断後、別セッションが再構成した同名steeringを本セッションの中断記録と照合し、実装をやり直さず進捗を復元した。

**新たに必要になったタスク**:

- 除外文書への具体的な相対参照だけを検出し、`docs/ideas/`という一般概念は許容する契約テストを追加した。
- 公式公開手順をそのまま実行できるよう、パラメータ定義、clean clone、detached tag、初回push、対象checkoutを明示したpreflightコマンドと順序テストを追加した。

**技術的理由でスキップしたタスク**:

- 該当なし。

### 学んだこと

**技術的な学び**:

- exact allowlistでfile setを閉じても、配布文書の参照閉包は別途検証が必要である。除外対象への参照は上流URLまたは配布向け文面へ明示変換すると、正典情報を配布せず自己完結性を保てる。
- provenance metadataを信頼可能にするには、tag/commitだけでなくsource origin、publisher clean HEAD、metadata予約pathを相互に検証する必要がある。
- 複数変換をmanifest順に逐次適用すると、source文書を正典向けに保ったまま配布向け差分を小さな完全一致契約として表現できる。

**プロセス上の改善点**:

- コード・スペック・ドキュメントを独立レビューに分けることで、実装契約の準拠とは別に、欠落参照やコマンド実行directoryの曖昧さを検出できた。
- 外部repository作成とsettings変更をマージ・release後の公式手順へ明確に分離すると、PRレビュー中の実証と本番公開の権限境界を維持できる。
- 中断時に再開位置と未コミット差分を残すことで、別セッションの再構成が入ってもfilesystemと実績を照合して安全に復元できる。

### 次回への改善提案

- 正典化PRのマージ後は、本手順に従ってMINOR releaseを作成し、`platform-harness-template`の初回公開・検証・settings切替を別の実行記録として残す。
- 将来manifestのinclude pathを更新する際は、file setだけでなくcanonical-only参照の閉包検査も同じレビュー単位で更新する。

### リリース判断

| 観点 | 評価 |
|---|---|
| ユーザー価値のあるまとまりか | Yes |
| 未解決の重大バグ | なし |
| 適切なバージョン種別 | MINOR |

**提案**:

正典開発ツリーと配布テンプレートの分離は新しい配布生成・運用能力を追加するためMINOR releaseを提案する。releaseと初回配布は本PRのマージ後に実施し、このPR中には外部template repositoryを変更しない。
