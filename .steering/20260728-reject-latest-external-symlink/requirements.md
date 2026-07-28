# 要求内容

## 概要

`steering_state.py`が`--steering`省略時に選ぶlatest tasklistにも既存のproject root境界検査を適用し、`.steering/`内のsymlinkを介したproject外ファイルの変更を拒否する。

- **関連Issue**: https://github.com/kanan4gh/platform-harness/issues/48
- **使用ハーネス**: Codex
- **軽量パス**: 適用
- **G3受け入れ**: 不要（状態遷移CLIの内部実装と回帰テストのみを変更し、ハーネスのアダプタ構成・権限・フック・設定を変更しない）

## パス判定（通常パス・軽量パスのどちらでも必ず記載する。基準の正は add-feature 手順のステップ4）

- [x] 1. 既存パターンの踏襲のみで、新しいアーキテクチャ要素・新規依存を導入しない
- [x] 2. 変更対象が3ファイル以下(テスト除く)
- [x] 3. 対象文書の更新が不要
- [x] 4. データ形式・API契約の破壊的変更がない

**判定理由**:

- 基準1: **満たす**。`--steering`明示時に使用している`Path.resolve()`後の境界検査へlatest結果も合流させる。新しい層・抽象化・依存は導入しない
- 基準2: **満たす**。変更対象は`scripts/steering_state.py`の1ファイル（テストを除く）
- 基準3: **満たす**。対象をproject root内の`.steering/[日付付き名]/tasklist.md`に限定する契約は既存の手順とエラーメッセージですでに定義されており、今回はlatest経路の実装を既存契約へ一致させる。`AGENTS.md`、ハーネスアダプタ、永続ドキュメント、`docs/procedures/`、テンプレートの更新は不要
- 基準4: **満たす**。既存の不正入力を安全側で拒否する内部検証の修正であり、tasklist形式・CLI引数・外部API契約を変更しない

4項目すべてを満たすため軽量パスを適用する。設計判断が発生しないため`design.md`は作成しない。

## 背景

`resolve_tasklist()`は`--steering`明示時には候補を`Path.resolve()`し、解決後のtasklistがproject rootの`.steering`直下にある日付付きディレクトリへ属することを検証する。一方、`--steering`省略時は`find_latest_tasklist()`の結果を境界検査せず返す。

この差により、辞書順で最新になる`.steering/[日付付き名]`をproject外ディレクトリへのsymlinkにすると、その外部`tasklist.md`が状態遷移の対象となり、原子的置換によってproject外ファイルが変更される。

## ユースケースの軸

**開発者が対象を明示せずsteering状態遷移CLIを実行しても、latest候補がproject外を指すsymlinkなら遷移を拒否し、外部tasklistを変更しない。**

## 実装対象の機能

### 1. latest候補の境界検査

- latest候補を`Path.resolve()`した後、明示対象と同じ境界検査へ通す
- 解決後の対象がproject rootの`.steering/[日付付き名]/tasklist.md`直下でなければ`TransitionError`で拒否する
- 通常のlatest選択と明示対象選択の既存挙動を維持する

### 2. 外部symlinkの回帰テスト

- 辞書順で最新のステアリングディレクトリをproject外へのsymlinkにする
- `--steering`を省略したCLI実行が失敗することを確認する
- 拒否後もsymlink先のtasklist内容が不変であることを確認する

## 受け入れ条件

### latest候補の境界検査

- [ ] 通常のproject内latest tasklistは従来どおり解決される
- [ ] project外ディレクトリを指すlatest symlinkは`TransitionError`で拒否される
- [ ] `--steering`明示時の境界検査と正常系を維持する

### 非変更保証と品質

- [ ] CLIで拒否した後、project外tasklistの内容が変更されない
- [ ] 外部symlinkが辞書順で最新になる回帰テストがある
- [ ] 既存テスト・lint・型検査とローカル品質ゲートがすべて通過する

## 成功指標

- Issue #48の再現条件が終了コード1と境界エラーになり、外部tasklistの内容が実行前後で一致する
- 通常のlatest選択と明示選択に回帰がない
- 同じlatest境界検査の欠落が再導入された場合、回帰テストが決定論的に失敗する

## スコープ外

以下はこのフェーズでは実装しない。

- `.steering`ルート自体の配置契約の変更
- 状態遷移、tasklist形式、latestの辞書順選択規則の変更
- symlinkを全面的に禁止する新しいポリシー
- 状態遷移中にファイルシステム構造を同時変更する競合への追加対策

## 参照ドキュメント

- `AGENTS.md` - steering状態とローカル品質ゲートの正典
- `docs/procedures/steering.md` - 状態遷移とlatest選択の契約
- `docs/procedures/add-feature.md` - 軽量パスと検証フロー
- `scripts/steering_state.py` - 状態遷移CLIと既存の明示対象境界検査
- `scripts/steering_lint.py` - latest tasklist選択の既存実装
