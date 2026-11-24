# 設計

## 実装アプローチ

### 1. `scripts/steering_state.py`

- サブパーサ定義を `_add_finish_arguments(parser)` に共通化し、`finish`(help付き)と旧名(help無し=一覧非表示)の2つを登録する
- `add_subparsers(metavar="{pause,resume,finish}")` で usage 行からも旧名を隠す
  - argparseの `aliases=` は `--help` に `finish (旧名)` と表示されるため使わない
  - 既知の残差: 不正なサブコマンドを渡したときのargparseエラーの選択肢一覧には旧名が出る(`--help` ではないため受け入れ条件の範囲外。設計判断として記録)
- `main()` で旧名を `finish` に正規化してから分岐する。成功メッセージも `-> finish` に統一する
- 関数 `complete_text` は `finish_text` に改名する(内部APIで外部参照なし)
- `pause_text` のエラーメッセージ「pauseではなく…を使用してください」の案内先を `finish` に変更する
- 遷移エラー文言の `completeへ` 等は状態値を指すため変更しない

### 2. 参照更新

| ファイル | 変更 |
|---|---|
| `docs/procedures/add-feature.md` | ステップ7のコマンドを `finish` に |
| `docs/procedures/steering.md` | 完了節のコマンド、モード3の「状態操作の…」を `finish` に。worktreeガードの注意書きを追加 |
| `docs/procedures/harness-acceptance.md` | 操作名一覧と手順7のコマンドを `finish` に |
| `docs/procedures/templates/tasklist.md` | 末尾注記のコマンドを `finish` に |
| `docs/procedures/templates/harness-acceptance-record.md` | 状態遷移項目の操作名を `finish` に |
| `.claude/commands/add-feature.md` | ステップ7のコマンドを `finish` に |
| `.claude/README.md` | ワークフロー説明の実行コマンドを `finish` に |
| `.claude/skills/steering/SKILL.md` `.kiro/skills/steering/SKILL.md` `.agents/skills/steering/SKILL.md` | `pause / resume / finish` に |
| `.codex/README.md` `.kiro/README.md` | 完了コマンドを `finish` に |
| `CLAUDE.md` | 機構による担保の状態遷移を `pause / resume / finish` に |

状態値(`` `complete` ``へ遷移、`状態: complete`、`active / paused / complete`)と `--require-complete` は変更しない。

### 3. テスト

- `tests/lint/test_steering_state.py`: `finish_text` へ改名。CLIで `finish` と旧名の両方が同じ終了コード・同じtasklist結果になること、`--help` に旧名が出ないことを追加
- `tests/procedures/test_add_feature_ordering.py` `tests/adapters/test_harness_acceptance.py`: 期待文字列を `steering_state.py finish` に
- 新規 `tests/procedures/test_guard_forbidden_words.py`(再発防止):
  - 禁止語リスト `FORBIDDEN_COMMAND_WORDS = ("complete",)` を管理
  - 対象: `AGENTS.md` `CLAUDE.md` `docs/procedures/**/*.md` `.claude/**/*.md` `.codex/**/*.md` `.kiro/**/*.md` `.agents/**/*.md`
  - 抽出対象「コマンド例」: インラインコードスパンとフェンスドコードブロックの行のうち、コマンド起動を含むもの(`python3` / `uv run` / `steering_state.py` / `steering_lint.py` / `grep` / `echo` / `Bash(` を含む)
  - 判定: 禁止語が単独の語(前後が英数字・`_`・`-` でない)として現れたら違反。`--require-complete` 等の部分一致は自然に除外される。状態値はコマンド起動を含まないので対象外
  - 検査器自身の健全性確認として、陽性例・陰性例のテストも置く

## 段3レビュー後の追加変更(計画との差分)

- `scripts/steering_lint.py`: C3違反(paused かつ未完了なし)の案内文を「resumeでactiveへ戻してからfinishを実行してください」に変更。旧文言は状態値へ遷移せよとだけ述べ、旧コマンドへの誘導になりうるうえ、finish は paused から直接遷移できないため不正確だった
- `distribution/template-manifest.json`: 再発防止テストを配布対象(include_paths)に追加。派生プロジェクトこそガードで停止した当事者であり、テストが配布されないと再混入を防げない
- 再発防止テストの検査対象に `README.md`・`docs/*.md`・`.steering/example/*.md` を追加し、フェンス判定を同種・同長以上の記号列でのみ閉じる方式にした
- `description` は `__doc__` の1行目を `partition` で取り出す(`python -OO` で `__doc__` が None でも落ちない)

## トレードオフ

- 旧名をargparseの `aliases` で登録すると実装は1行だが `--help` に表示される。受け入れ条件を優先し、help無しの別サブパーサとして登録する
- 注意書きは禁止語をコード扱いせず地の文で書く(コマンド例として書くと再発防止テストと矛盾し、読者がそのまま実行しうるため)

## 影響範囲

- 派生プロジェクト・既存スクリプトの旧名呼び出しはエイリアスで動き続ける
- 既存 `.steering/` の状態値は不変のため `steering_lint.py` の結果は変わらない
