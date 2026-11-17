# 正典から配布テンプレートを公開する手順

リリース済み`platform-harness`から生成した成果物だけを、配布専用の`kanan4gh/platform-harness-template`へ公開する手順である。正典開発履歴と利用者向けテンプレートを同じGitツリーとして配布しない。

## 原則

- sourceはGitHub Releaseに対応する変更不能な`platform-harness` tagと、そのtagが解決するcommitに固定する。未リリースのbranch、working tree、差し替えたtagをsourceにしない。
- 配布集合は`distribution/template-manifest.json`のexact allowlistを正とする。全コピー後のdenylist削除へ置き換えない。
- 生成、検証、GitHub設定変更は人が開始するローカル手順とする。GitHub Actions自動runと従量課金LLM headless modeを必須経路にしない。
- `.platform-harness-source.json`を配布commitへ含め、source tag/commitとpublisher revisionを追跡できるようにする。
- `platform-harness-template`の内容は生成物だけで構成し、同repository上で直接ファイルを設計・修正しない。修正は正典へ戻し、新しいreleaseから再生成する。

## 実行禁止境界

**この手順または配布生成機構を正典化するPRがマージされる前に、`platform-harness-template`の作成、初回push、repository settings変更を実行してはならない。** 正典化PRのレビュー中は、ローカルの一時directoryで生成・検証するところまでを許可する。

次の条件がすべて成立するまで初回公開へ進まない。

1. 正典化PRが`platform-harness`のdefault branchへマージ済みである。
2. 関連Issueがクローズ済みである。
3. マージcommitを含む`platform-harness` releaseとtagが作成済みである。
4. release tag、commit OID、実行者、実行日を公開記録へ残せる。

## 実行パラメータ

実際のrelease tagへ置き換え、専用の一時directoryを作る。`SOURCE_TAG`はbranch名ではなく、共通preflightで確認するGitHub Releaseのtagでなければならない。

```bash
SOURCE_TAG=vX.Y.Z
PUBLISH_ROOT=$(mktemp -d /private/tmp/platform-harness-template-publish.XXXXXX)
PUBLISHER_CHECKOUT="${PUBLISH_ROOT}/platform-harness"
DISTRIBUTION_OUTPUT="${PUBLISH_ROOT}/distribution"
git clone https://github.com/kanan4gh/platform-harness.git "${PUBLISHER_CHECKOUT}"
git -C "${PUBLISHER_CHECKOUT}" fetch --tags origin
git -C "${PUBLISHER_CHECKOUT}" checkout --detach "refs/tags/${SOURCE_TAG}"
```

各pathを出力して`PUBLISH_ROOT`配下であること、checkoutのoriginが`kanan4gh/platform-harness`であること、statusがcleanであることを、生成コマンドの直前に再確認する。

## 共通preflight

1. 上で作成した`PUBLISHER_CHECKOUT`が新しいclean cloneで、originが`kanan4gh/platform-harness`であることを確認する。既存のdirty checkoutを清掃・stash・上書きして使わない。
2. `git -C "${PUBLISHER_CHECKOUT}" rev-parse --verify "refs/tags/${SOURCE_TAG}^{commit}"`の完全なcommit OIDを記録する。
3. `gh release view "${SOURCE_TAG}" --repo kanan4gh/platform-harness`でGitHub Releaseの存在を確認する。
4. publisher checkoutが記録したrelease tagのdetached HEADに固定され、`git -C "${PUBLISHER_CHECKOUT}" status --porcelain --untracked-files=all`が空であることを確認する。
5. `gh api repos/kanan4gh/platform-harness-template`と`gh api repos/kanan4gh/platform-harness`で、対象repository・default branch・`is_template`の現在値を記録する。初回で新repositoryがまだ存在しない場合は404だけを想定内とする。

tag、origin、default branch、repository所有者を一意に確認できない場合は停止し、推測で続行しない。

## 配布物の生成とローカル検証

cleanなpublisher checkoutで、既存内容を持たない明示的な一時directoryへ生成する。

```bash
python3 "${PUBLISHER_CHECKOUT}/scripts/build_template_distribution.py" \
  --source-repository "${PUBLISHER_CHECKOUT}" \
  --source-tag "${SOURCE_TAG}" \
  --output "${DISTRIBUTION_OUTPUT}"
```

生成後、次をすべて観察・記録する。

1. `.platform-harness-source.json`の`source_repository`、`source_tag`、`source_commit`、`publisher_repository`、`publisher_revision`がpreflight記録と一致する。
2. file setがmanifestの`include_paths`とmetadata 1ファイルだけであり、`forbidden_paths`と`forbidden_prefixes`が0件である。
3. `.steering/`には`example/`の3ファイルだけがあり、日付付きsteeringと蒸留履歴がない。
4. 同じ入力から別の空directoryへ再生成し、path、内容、実行bitが一致する。
5. 使い捨ての検証コピーをGit repositoryとして初期化し、完了済みfixture steeringを追加して`uv run python3 scripts/local_quality_gate.py --steering <fixture名>`を成功させる。
6. 同じ検証コピーへ新しい日付付きsteeringを追加し、通常の`git add -A`でindexへ入ることを確認する。

検証用fixtureは配布物へ戻さず、検証コピーごと破棄する。生成物そのものへ手修正を加えない。

## 初回公開

この節は「実行禁止境界」の4条件と共通preflight・ローカル検証を完了した後にだけ実行する。

1. `kanan4gh/platform-harness-template`が存在しないことを再確認する。既に存在する場合は所有者、内容、default branch、settingsを調査し、初回公開として上書きしない。
2. `gh repo create kanan4gh/platform-harness-template --public --description "Generated distribution of kanan4gh/platform-harness"`で空の配布repositoryを作成する。
3. 検証済み生成物を次のコマンドで新しいGit repositoryとして初期化し、`.platform-harness-source.json`を含む全ファイルを1 commitにしてpushする。実行直前に`DISTRIBUTION_OUTPUT`とremote URLを再確認する。

```bash
git -C "${DISTRIBUTION_OUTPUT}" init -b main
git -C "${DISTRIBUTION_OUTPUT}" config user.name "platform-harness publisher"
git -C "${DISTRIBUTION_OUTPUT}" config user.email "publisher@example.invalid"
git -C "${DISTRIBUTION_OUTPUT}" add -A
git -C "${DISTRIBUTION_OUTPUT}" commit -m "chore: publish ${SOURCE_TAG} template distribution"
git -C "${DISTRIBUTION_OUTPUT}" remote add origin https://github.com/kanan4gh/platform-harness-template.git
git -C "${DISTRIBUTION_OUTPUT}" push -u origin main
```

commit本文または公開記録へsource commit OIDも記録する。
4. GitHub上の`main` treeとローカル生成物について、file set、blob内容、実行bit、metadataを再照合する。不一致があれば設定変更へ進まない。
5. `gh api --method PATCH repos/kanan4gh/platform-harness-template -F is_template=true`を実行し、取得し直した`is_template`が`true`であることを確認する。
6. GitHub上で「Use this template」が利用可能で、既定branchが検証済みcommitを指すことを人が確認する。
7. 新templateが使用可能になった後に限り、`gh api --method PATCH repos/kanan4gh/platform-harness -F is_template=false`を実行する。旧設定を先に解除しない。
8. source release、生成metadata、配布commit、settings確認結果、GitHub Actions自動run 0件、従量課金LLM headless mode 0件を公開記録へ残す。

初回公開に失敗した場合は、`platform-harness`の既存template設定を維持する。作成途中の新repositoryを削除して隠蔽せず、`is_template=false`のまま原因と再開条件を記録する。

## 継続更新

配布更新の単位は`1 platform-harness release × 1 template feature branch × 1 PR`とする。

1. 共通preflightと生成・ローカル検証を新しいrelease tagで繰り返す。
2. `platform-harness-template`を新しい一時directoryへclean cloneし、origin、default branch、現在commit、現在metadataを記録する。
3. `distribution/<source-tag>`形式のfeature branchを最新default branchから作る。
4. clone内の`.git/`を除くtracked成果物を、検証済み生成物のexact file setへ同期する。削除対象と追加対象を事前に一覧化し、clone外のpathや未確認remoteへ同期しない。
5. 同期後に生成物とのfile set、blob内容、実行bit、metadataの一致を再検証する。
6. source tag/commitを本文へ記載したcommitを作り、feature branchをpushしてPRを作成する。PR本文には生成コマンド、ローカル品質ゲート、決定性比較、禁止path 0件を記録する。
7. 人がPRをレビュー・マージする。マージ後にdefault branchのmetadataとsource releaseの対応、`is_template=true`を再確認する。

配布repository上の直接修正、未リリースmainからの生成、検査を省略した直接pushを行わない。

## ロールバック

### 配布PRのマージ前

- PRをマージせずcloseし、現行template commitを維持する。
- 修正は`platform-harness`へ戻し、新releaseから新しい配布PRを作る。

### 配布PRのマージ後

1. 影響が継続する場合は、`gh api --method PATCH repos/kanan4gh/platform-harness-template -F is_template=false`で新規利用を一時停止する。
2. 問題を導入した配布PRを特定し、default branch上で`git revert`するrollback branchとPRを作る。履歴を書き換えるforce-pushは使わない。
3. revert後のtree、metadata、ローカル品質ゲート、禁止path、steering追跡契約を再検証する。
4. 人がrollback PRをマージし、復旧commitを確認した後に`is_template=true`へ戻す。
5. 原因修正は正典側の新PRと新releaseで行う。既存release tagの差し替えや、生成物だけの手修正を行わない。

新repository自体の利用不能時に旧`platform-harness`を一時的にtemplateへ戻すかは、人が正典開発履歴を配布する既知リスクと停止時間を比較して明示判断する。自動で旧設定へ戻さない。

## 公開記録

初回・更新・ロールバックごとに、関連Issueまたはsteeringへ次を残す。

```markdown
## Template distribution record
- operation: initial / update / rollback
- source release / commit: vX.Y.Z / SHA
- publisher revision: SHA
- generated metadata: [内容または配布commitへのリンク]
- template commit / PR: SHA / URL
- deterministic comparison: pass / fail
- forbidden paths: 0件
- generated steering: example 3ファイルのみ
- user steering git add contract: pass / fail
- local quality gate: 日時 / 結果
- repository settings: new is_template / canonical is_template
- GitHub Actions自動run: 0件
- 従量課金LLM headless mode: 0件
```
