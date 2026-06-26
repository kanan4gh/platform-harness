# 要求内容

## 概要

テンプレートとして複製した際に、README.md がプロジェクト固有の内容として育てられるよう、プレースホルダー形式に差し替える。

## 背景

platform-harness を "Use this template" で複製すると、README.md がこのリポジトリ（platform-harness）の説明のままになる。
新しいプロジェクトでは、自分のプロジェクト用の README として育てていきたい。

関連Issue: https://github.com/kanan4gh/platform-harness/issues/2

## ユースケースの軸

> **テンプレート利用者が "Use this template" でリポジトリを作成すると、README.md がプロジェクト固有の内容として自分で育てられる状態になっている。**

## 実装対象の機能

### 1. README.md をプレースホルダー形式に差し替え

- プロジェクト名・説明をプレースホルダーにする
- 「何を書けばいいか」をガイドするコメントを含める

### 2. 現在の README 内容を `docs/harness-guide.md` に移動

- platform-harness テンプレートの使い方ガイドとして保存
- README から harness-guide.md へのリンクを設置

## 受け入れ条件

### README.md

- [ ] プロジェクト名がプレースホルダー（`# Your Project Name`）になっている
- [ ] プロジェクト概要がプレースホルダーになっている
- [ ] テンプレート利用ガイドへのリンクがある
- [ ] テンプレート利用者が自分のプロジェクトに合わせて書き換えやすい構成になっている

### docs/harness-guide.md

- [ ] 現在の README.md の内容が移動されている
- [ ] セットアップ手順・含まれるツール・スペック駆動開発フローが含まれる

## スコープ外

- CLAUDE.md の変更
- docs/ 以下の他のドキュメントの変更

## 参照ドキュメント

- `docs/product-requirements.md`
- `docs/repository-structure.md`
