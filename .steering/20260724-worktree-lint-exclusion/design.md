# 設計書

## アーキテクチャ概要

metered automation lint は「**policyが検査範囲を一元管理し、lint本体はpolicyに従うだけ**」という設計になっている（`docs/external-automation-policy.md`）。今回の問題はlint本体の欠陥ではなく、**policyが表現していない範囲**（ネストしたリポジトリcheckout）が存在することにある。したがって修正もpolicy側で行い、`iter_target_files` / `_is_excluded` のロジックには手を入れない。

とくに「`.git` の存在で入れ子のcheckoutを自動検出して枝刈りする」案は**採らない**。`.git` マーカーは検査対象側から設置できるため、任意のディレクトリに `.git` を置けば走査から外せてしまう。fail-closedを旨とするlintに、検査対象が制御できる除外条件を持ち込むべきではない（段3レビューでの指摘を記録）。

```
include_paths: .claude          → rglob("*") で再帰走査
                 ├── commands/       … 現行指示面（走査対象のまま）
                 ├── skills/         … 現行指示面（走査対象のまま）
                 ├── hooks/          … 現行指示面（走査対象のまま）
                 ├── settings.json   … 現行指示面（走査対象のまま）
                 └── worktrees/      → exclude_paths へ追加（同一リポジトリの別checkout）
                       └── feature+x/    … tests/ .steering/ .venv/ docs/ideas/ が丸ごと入る
```

**除外の正当性**: `.claude/worktrees/<名前>/` は同一リポジトリの別checkoutであり、
1. その worktree の中で作業する際は、**その worktree 自身がルートとなってゲートが走る**（`.claude/worktrees` がその中に存在しないため走査対象にならず、通常どおり全ファイルが検査される）
2. マージされれば内容は main 側の実体として検査される

つまり除外しても検査されない指示面は生まれない。**新たな指示面ではなく、既に検査済みの指示面の重複**である。これは「実行手順を隠す目的の除外は禁止する」という既存ポリシーに抵触しない。

## コンポーネント設計

### 1. `scripts/metered_automation_policy.json`

**責務**: 検査範囲の宣言。

**実装の要点**:
- `exclude_paths` に `.claude/worktrees` を追加する
- `include_paths` の `.claude` は**残す**（`.claude/` 直下の現行指示面を走査し続けるため）
- 既存ガードとの整合は確認済み:
  - `_safe_relative_path`: 相対・`..` なし → 通過
  - include/exclude の重複チェック: `.claude` と `.claude/worktrees` は別エントリなので `overlap` に入らない
  - 過剰除外ガード: `len(path.parts) == 1` のときだけ発火する。`.claude/worktrees` は2要素なので対象外（`PROTECTED_EXCLUDES` の拡張は不要）
- 除外エントリは**存在を要求されない**（`iter_target_files` が `PolicyError` を投げるのは `include_paths` のみ）。worktree が1つも無い環境でも壊れない

### 2. `docs/external-automation-policy.md`

**責務**: 除外の正典と、その技術的理由の記録。

**実装の要点**:
- 「除外は次に限定する」の箇条書きに `.claude/worktrees/` を追加する
- 理由は「同一リポジトリの別checkoutであり、その worktree 自身のゲート実行で検査される。現行指示面の重複であって新たな指示面ではない」と書く
- 既存の「除外を追加する場合は、技術的理由と誤検出しないテストを同時に追加する」という要求を、本変更自身が満たす

### 3. `tests/lint/test_metered_automation_lint.py`

**責務**: 除外が効くこと、かつ過剰除外でないことの決定論的固定。

**実装の要点**:
- 既存テストのスタイル（`policy_data()` で合成policyを作り `scan()` する）に合わせる
- **1ケースで両方向を検証する**: `.claude/worktrees/<名前>/` 配下の違反は報告されず、同じscanで `.claude/` 直下の違反は報告されること。除外と過剰除外を別テストに分けると、片方だけ通って安心する事故が起きる
- 加えて**実policyの契約テスト**を置く（合成policyのテストだけでは、実policyから `.claude/worktrees` が消えても検出できない）。`scripts/metered_automation_policy.json` を読み、`.claude` が include に、`.claude/worktrees` が exclude にあることを固定する
- 実policyのテストでは `lint.load_policy` を通し、**policyが実際に読み込める**（過剰除外ガード等に抵触しない）ことも同時に確認する

## データフロー

### 修正前（誤検出）

```
main でゲート実行
  → include ".claude" を rglob
    → .claude/worktrees/feature+x/tests/lint/test_metered_automation_lint.py を発見
      → exclude "tests/lint/test_metered_automation_lint.py" は
         ルート相対で一致しないため除外されない
        → fixture内の `claude -p` / `codex exec` を違反として報告 → exit 1
```

### 修正後

```
main でゲート実行
  → include ".claude" を rglob
    → .claude/worktrees/... は exclude ".claude/worktrees" の配下
       (_is_excluded の parents 判定にヒット) → スキップ
    → .claude/commands/ 等は従来どおり走査 → 全緑

worktree 内でゲート実行
  → その worktree がルート。.claude/worktrees は存在しない
    → 全ファイルが従来どおり走査される（検査漏れなし）
```

## エラーハンドリング戦略

policy駆動のため新規の例外機構はない。既存のfail-closed（policy破損・読取失敗・構文解析失敗）はそのまま。誤りの検出経路:

| 誤り | 検出経路 |
|---|---|
| 実policyから `.claude/worktrees` が消える | 実policy契約テスト |
| 除外を広げすぎて `.claude/` 直下が検査されなくなる | 同一テスト内の過剰除外検証 |
| `.claude` が include から外れる | 実policy契約テスト |
| policyが読み込めない形になる | `load_policy` を通す契約テスト＋既存のfail-closedテスト |

## テスト戦略

### ユニットテスト（`tests/lint/test_metered_automation_lint.py` へ追加）

- `test_scan_skips_nested_worktree_checkouts`: 合成policyで `.claude` を include・`.claude/worktrees` を exclude し、`.claude/worktrees/feature+x/tests/run.md` の違反が報告されず、`.claude/commands/run.md` の違反は報告されることを1ケースで確認する
- `test_repository_policy_excludes_worktrees_without_hiding_active_surfaces`: 実policyを `load_policy` で読み、include に `.claude`・exclude に `.claude/worktrees` があることを固定する

### 実挙動検証（段2）

worktree が存在する状態の main で `uv run python3 scripts/local_quality_gate.py` を実行し、修正前は落ちていた metered automation lint (5/5) が全緑になることを観察する。本作業の worktree（`.claude/worktrees/feature+worktree-lint-exclusion`）自体が実データのfixtureになる。

## 依存ライブラリ

追加なし。

## ディレクトリ構造

```
scripts/metered_automation_policy.json      # 変更(exclude_paths に1行追加)
docs/external-automation-policy.md          # 変更(除外リストに1項目追加)
tests/lint/test_metered_automation_lint.py  # 変更(テスト2件追加)
```

## 実装の順序

1. `scripts/metered_automation_policy.json` に除外を追加する
2. `docs/external-automation-policy.md` に理由を記録する
3. テストを追加する

## セキュリティ考慮事項

- 除外が「実行手順を隠す抜け穴」にならないこと。`.claude/` 直下の現行指示面（commands / skills / agents / hooks / settings.json）は走査対象のまま維持し、過剰除外でないことをテストで固定する
- worktree 内の内容は、その worktree 自身のゲート実行とマージ後のmain検査で二重に捕捉される

## パフォーマンス考慮事項

- 副次的効果として、worktree 内の `.venv/`（`uv run` が生成する数千ファイル）を走査しなくなるため、worktree が存在する環境でのlint実行時間が短縮される

## 将来の拡張性

- 別の場所（`../[リポジトリ名]-[タスク名]`）に作る worktree はリポジトリ外のため元から走査されない。本変更でリポジトリ内・外の両方の worktree 配置が揃ってカバーされる
- 他のツールが `.claude/` 配下にネストしたcheckoutを作る運用が増えた場合は、同じ形で `exclude_paths` に追加する
