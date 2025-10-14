# Git-GrassReporter

毎日 21 時(JST)に GitHub の草(contributions)をチェックし、その日に草が生えていなければ Discord に通知を送るツール  
**+ 毎日 0 時(JST)に連続コントリビュート日数をメンション無しで投稿**

**GitHub Actions で自動実行 - PC が起動していなくても動作**

## 特徴

- GitHub Actions で完全自動実行（無料）
- サーバー不要、PC を起動する必要なし
- GitHub API で正確なコントリビューション取得
- Discord にメンション付きで通知
- **毎日 0 時に連続コントリビュート日数を自動投稿（メンション無し）**

## セットアップ手順

### 1. GitHub リポジトリの作成

このプロジェクトを GitHub に push(Fork でも使用可能)：

### 2. 必要な情報の取得

#### GitHub Personal Access Token (PAT)

1. https://github.com/settings/tokens にアクセス
2. **Generate new token** → **Generate new token (classic)** を選択
3. 設定:
   - **Note**: `Git-GrassReporter`
   - **Expiration**: `No expiration` または長めに設定
   - **Scopes**: `read:user` にチェックを入れる
4. **Generate token** をクリックしてトークンをコピー（後で使うので保存しておく）

#### Discord Webhook URL

1. 通知を送りたい Discord サーバーの設定を開く
2. **連携サービス** → **ウェブフック** → **新しいウェブフック**
3. 名前とチャンネルを設定
4. **ウェブフック URL をコピー**

#### Discord User ID

1. Discord の設定 → **詳細設定** → **開発者モード** を有効化
2. 自分のアイコンを右クリック → **ID をコピー**

### 3. GitHub Secrets の設定

リポジトリで機密情報を安全に管理：

1. GitHub リポジトリのページで **Settings** タブを開く
2. 左サイドバーで **Secrets and variables** → **Actions** を選択
3. **New repository secret** をクリックして以下を追加:

| Name                  | Value                                  | 説明                           |
| --------------------- | -------------------------------------- | ------------------------------ |
| `GH_USERNAME`         | `Nyayuta1060`                          | GitHub ユーザー名              |
| `GH_TOKEN`            | `ghp_xxxxxxxxxxxx`                     | 取得した Personal Access Token |
| `DISCORD_WEBHOOK_URL` | `https://discord.com/api/webhooks/...` | Discord Webhook URL            |
| `DISCORD_USER_ID`     | `123456789012345678`                   | あなたの Discord User ID       |

### 4. 機能のオンオフ設定（オプション）

各機能を個別に有効/無効にできます：

1. GitHub リポジトリの **Settings** → **Secrets and variables** → **Actions**
2. **Variables** タブを選択
3. **New repository variable** をクリックして設定:

| Name                  | Value            | 説明                                     |
| --------------------- | ---------------- | ---------------------------------------- |
| `ENABLE_GRASS_CHECK`  | `true` / `false` | 草チェック機能(21 時)(デフォルト: true)  |
| `ENABLE_DAILY_STREAK` | `true` / `false` | 連続日数投稿機能(0 時)(デフォルト: true) |

**注意**: 変数を設定しない場合、両方の機能が有効(true)になります。

1. リポジトリの **Actions** タブを開く
2. ワークフローの実行を許可する
3. **Check GitHub Grass** および **Post Daily Streak** ワークフローが表示されることを確認

### 6. 動作確認

#### 手動実行でテスト

1. **Actions** タブを開く
2. **Check GitHub Grass** または **Post Daily Streak** ワークフローを選択
3. **Run workflow** をクリックして手動実行
4. 実行結果とログを確認

#### 自動実行

- **毎日 12:00 UTC（= 21:00 JST）**: 草のチェックと通知
- **毎日 15:00 UTC（= 00:00 JST）**: 連続コントリビュート日数の投稿（メンション無し）
- GitHub Actions のスケジュールは最大 15 分程度の遅延が発生する場合があります

## ファイル構成

```
Git-GrassReporter/
├── .github/
│   └── workflows/
│       ├── check-grass.yml         # 草チェック (21:00 JST)
│       └── daily-streak.yml        # 連続日数投稿 (00:00 JST)
├── grass_checker.py                # メインスクリプト
├── requirements.txt                # Python依存パッケージ
├── setup.sh                        # ローカル実行用セットアップ
├── .env.example                    # 環境変数テンプレート
├── .gitignore                      # Git除外設定
└── readme.md                       # このファイル
```

## トラブルシューティング

### GitHub Actions が実行されない

- **Actions タブ**で実行履歴を確認
- リポジトリの**Settings** → **Actions** → **General**で、**Allow all actions and reusable workflows**が選択されているか確認

### GitHub API エラー

- Personal Access Token が正しく設定されているか確認
- トークンに`read:user`権限があるか確認
- トークンの有効期限が切れていないか確認

### Discord 通知が届かない

- Webhook URL が正しいか確認
- Discord User ID が正しいか確認（数字のみ）
- Webhook のチャンネルに Bot が投稿できる権限があるか確認

### タイムゾーン

- スクリプトは JST（UTC+9）基準で動作
- GitHub Actions は`12:00 UTC = 21:00 JST`で実行

### ログの確認方法

1. リポジトリの**Actions**タブを開く
2. 実行されたワークフローをクリック
3. **check-grass**ジョブをクリック
4. 各ステップのログを確認

## ローカルでの実行（オプション）

GitHub Actions とは別に、ローカルでもテスト実行できます：

```bash
# セットアップ
./setup.sh

# .envファイルを編集
nano .env

# テスト実行（草チェック）
source .env
export GITHUB_USERNAME GITHUB_TOKEN DISCORD_WEBHOOK_URL DISCORD_USER_ID
./venv/bin/python grass_checker.py

# テスト実行（連続日数投稿）
./venv/bin/python grass_checker.py daily-streak
```

## 仕組み

### 草チェック（毎日 21 時 JST）

1. **GitHub Actions**が毎日 21 時(JST)に起動
2. **GitHub GraphQL API**で今日のコントリビューションを取得
3. コントリビューションが**0 件**の場合:
   - Discord Webhook でメッセージ送信
   - 指定されたユーザーにメンション
4. **1 件以上**の場合: 何もしない

### 連続日数投稿（毎日 0 時 JST）

1. **GitHub Actions**が毎日 0 時(JST)に起動
2. **GitHub GraphQL API**で連続コントリビュート日数を計算
3. **メンション無し**で現在の連続日数を Discord に投稿
4. 連続日数に応じて異なる絵文字とメッセージを表示

## カスタマイズ

### 機能のオンオフ

GitHub Actions を無効化せずに、機能だけを個別にオンオフできます：

1. **Settings** → **Secrets and variables** → **Actions** → **Variables** タブ
2. 以下の変数を追加または編集:
   - `ENABLE_GRASS_CHECK`: `false` にすると草チェック機能(21 時)を無効化
   - `ENABLE_DAILY_STREAK`: `false` にすると連続日数投稿機能(0 時)を無効化

**使用例**:

- 連続日数投稿だけ欲しい → `ENABLE_GRASS_CHECK` を `false` に設定
- 草チェックだけ欲しい → `ENABLE_DAILY_STREAK` を `false` に設定

### 実行時刻の変更

ワークフローファイルの`cron`を編集：

**草チェック** (`.github/workflows/check-grass.yml`):

```yaml
schedule:
  # 毎日12:00 UTC = 21:00 JST に実行
  - cron: "0 12 * * *"
```

**連続日数投稿** (`.github/workflows/daily-streak.yml`):

```yaml
schedule:
  # 毎日15:00 UTC = 00:00 JST に実行
  - cron: "0 15 * * *"
```

時刻の計算: `UTC時刻 = JST時刻 - 9時間`

### メッセージの変更

`grass_checker.py`の`check_and_notify`メソッド内のメッセージを編集：

```python
message = f"🌱 {today}の草が生えていません！今日もコミットしましょう！"
```

## コスト

**完全無料**

- GitHub Actions: 月 2,000 分まで無料（このツールは月 30 分程度）
- Private repository でも無料枠内で動作

## ライセンス

MIT License

## 作者

Nyayuta1060

---

## サポート

問題が発生した場合は、リポジトリの**Issues**で報告してください。
