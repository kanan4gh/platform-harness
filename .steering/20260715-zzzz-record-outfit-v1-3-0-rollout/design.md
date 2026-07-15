# 実装設計

## アプローチ

`docs/derived-projects.md`の表をremote単位の状態機械として扱い、`kanan4gh/outfit-studio`の1行だけをG4マージ後の確定値へ遷移させる。新しい展開機能や自動同期は追加せず、既存の台帳スキーマと構造テストを利用する。

```text
legacy-platform-claude / migrate-then-sync / on-hold / none
                         │
                         │ PR #22裁定 → Issue #25 → PR #26 merge
                         ▼
current-neutral / direct-sync / synced / v1.3.0 / bd2cd8c
```

## 変更対象

### `docs/derived-projects.md`

outfit-studio行の次の列だけを更新する。

| 列 | 変更前 | 変更後 |
|---|---|---|
| Lineage evidence | 旧`CLAUDE.md`のSOURCE / UPDATED | PR #26で`AGENTS.md`と3ハーネス構成へ移行済み |
| Harness generation | `legacy-platform-claude` | `current-neutral` |
| Strategy | `migrate-then-sync` | `direct-sync` |
| State | `on-hold` | `synced` |
| Last source | `none` | `v1.3.0 / bd2cd8c` |
| Last inspected | `2026-07-15` | `2026-07-15`（マージ後再確認） |
| Local caution | 未追跡資産とPR #22 | 通常checkoutの未追跡資産は残存するため、次回もclean clone / worktreeを使用 |
| Decision / next action | PR #22のG0裁定 | PR #22は不要としてcloseし、PR #26で同期完了。次回は新releaseとの差分をdirect-sync |

### `.steering/20260715-zzzz-record-outfit-v1-3-0-rollout/`

- Issue #20に対する要求・設計・進捗・検証・振り返りを記録する。
- outfit-studio側のsteeringや通常checkoutは編集しない。

## 不変条件

- 台帳のremote一意キーを維持し、outfit-studio行は1件だけとする。
- outfit-studio以外の候補行を変更しない。
- `Last source`は台帳規則の`vX.Y.Z / <7〜40桁SHA>`形式に従う。
- `synced`は将来releaseへの自動追随を意味せず、次回もユーザー指定を待つ。
- GitHub ActionsとLLM headless modeを起動しない。

## データフロー

```text
1. GitHub上のPR #26 / Issue #25 / merge commitを読み取り確認
2. requirements.mdへ確定証拠を固定
3. outfit-studioの台帳行だけを更新
4. 構造テストでremote一意性・列値・Last source形式を検証
5. git diffで他候補行が不変であることを確認
6. 単一ローカル品質ゲートを実行
7. Issue #20を参照するcommit / PRを作成
```

## エラーハンドリング

- PR #26がMERGEDでない、Issue #25がCLOSEDでない、merge commitが取得できない場合は更新を停止する。
- v1.3.0 tagと`bd2cd8c`の対応が崩れている場合は`Last source`を推測せず停止する。
- 構造テストがoutfit-studio以外の差分やスキーマ不整合を検出した場合は、台帳変更を修正してから再実行する。
- ローカル品質ゲートが失敗した場合は完了扱いにせず、原因を修正する。

## テスト戦略

### 構造テスト

- `tests/procedures/test_derived_project_rollout.py`をoutfit-studioの完了状態に更新する。
- outfit-studioが1行だけであることを既存表解析で確認する。
- `current-neutral` / `direct-sync` / `synced` / `v1.3.0 / bd2cd8c`を期待値として固定する。
- 他候補の既存期待値を維持する。

### 回帰検証

- `uv run pytest tests/procedures/test_derived_project_rollout.py`
- `uv run ruff check .`
- `uv run basedpyright`
- `uv run python3 scripts/local_quality_gate.py`
- `git diff`で変更範囲が台帳、対応テスト、今回steeringに限定されることを確認する。

## 実装順序

1. マージ証拠と同期元を再確認する。
2. 台帳のoutfit-studio行を更新する。
3. 構造テストのoutfit-studio期待値を更新する。
4. 対象テストと4段検証を実行する。
5. tasklistへ完了証跡と振り返りを記録する。
6. Issue #20を参照するcommit・push・PRを作成する。

## セキュリティ・運用考慮事項

- 読み取り済みのGitHub metadataだけを証拠に使い、認証情報を記録しない。
- 通常checkoutの未追跡資産を削除・stash・移送しない。
- 台帳更新を次の候補の自動展開トリガーにしない。
- 製品releaseは作成しない。
