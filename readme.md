# Git-GrassReporter

毎日21時(JST)にGitHubの草(contributions)をチェックし、その日に草が生えていなければDiscordに通知を送るツール

**GitHub Actionsで自動実行 - PCが起動していなくても動作します！**

## 🌟 特徴

- GitHub Actionsで完全自動実行（無料）
- サーバー不要、PCを起動する必要なし
- GitHub APIで正確なコントリビューション取得
- Discordにメンション付きで通知

## 🚀 セットアップ手順

### 1. GitHubリポジトリの作成

このプロジェクトをGitHubにプッシュします：

```bash
cd /home/nyayuta/workspace/etc/Git-GrassReporter

# Gitリポジトリの初期化（まだの場合）
git init
git add .
git commit -m "Initial commit: GitHub Grass Reporter"

# GitHubでリポジトリを作成後、リモートを追加
git remote add origin https://github.com/Nyayuta1060/Git-GrassReporter.git
git branch -M main
git push -u origin main
```

### 2. 必要な情報の取得

#### GitHub Personal Access Token (PAT)

1. https://github.com/settings/tokens にアクセス
2. **Generate new token** → **Generate new token (classic)** を選択
3. 設定:
   - **Note**: `Git-GrassReporter`
   - **Expiration**: `No expiration` または長めに設定
   - **Scopes**: `read:user` にチェック ✅
4. **Generate token** をクリックしてトークンをコピー（後で使うので保存しておく）

#### Discord Webhook URL

1. 通知を送りたいDiscordサーバーの設定を開く
2. **連携サービス** → **ウェブフック** → **新しいウェブフック**
3. 名前とチャンネルを設定
4. **ウェブフックURLをコピー**

#### Discord User ID

1. Discordの設定 → **詳細設定** → **開発者モード** を有効化
2. 自分のアイコンを右クリック → **IDをコピー**

### 3. GitHub Secretsの設定

リポジトリで機密情報を安全に管理します：

1. GitHubリポジトリのページで **Settings** タブを開く
2. 左サイドバーで **Secrets and variables** → **Actions** を選択
3. **New repository secret** をクリックして以下を追加:

| Name | Value | 説明 |
|------|-------|------|
| `GH_USERNAME` | `Nyayuta1060` | GitHubユーザー名 |
| `GH_TOKEN` | `ghp_xxxxxxxxxxxx` | 取得したPersonal Access Token |
| `DISCORD_WEBHOOK_URL` | `https://discord.com/api/webhooks/...` | Discord Webhook URL |
| `DISCORD_USER_ID` | `123456789012345678` | あなたのDiscord User ID |

### 4. GitHub Actionsの有効化

1. リポジトリの **Actions** タブを開く
2. ワークフローの実行を許可する
3. **Check GitHub Grass** ワークフローが表示されることを確認

### 5. 動作確認

#### 手動実行でテスト

1. **Actions** タブを開く
2. **Check GitHub Grass** ワークフローを選択
3. **Run workflow** をクリックして手動実行
4. 実行結果とログを確認

#### 自動実行

- 毎日12:00 UTC（= 21:00 JST）に自動実行されます
- GitHub Actionsのスケジュールは最大15分程度の遅延が発生する場合があります

## 📋 ファイル構成

```
Git-GrassReporter/
├── .github/
│   └── workflows/
│       └── check-grass.yml    # GitHub Actionsワークフロー
├── grass_checker.py            # メインスクリプト
├── requirements.txt            # Python依存パッケージ
├── setup.sh                    # ローカル実行用セットアップ
├── .env.example                # 環境変数テンプレート
├── .gitignore                  # Git除外設定
└── readme.md                   # このファイル
```

## 🔧 トラブルシューティング

### GitHub Actionsが実行されない

- **Actionsタブ**で実行履歴を確認
- リポジトリの**Settings** → **Actions** → **General**で、**Allow all actions and reusable workflows**が選択されているか確認

### GitHub APIエラー

- Personal Access Tokenが正しく設定されているか確認
- トークンに`read:user`権限があるか確認
- トークンの有効期限が切れていないか確認

### Discord通知が届かない

- Webhook URLが正しいか確認
- Discord User IDが正しいか確認（数字のみ）
- WebhookのチャンネルにBotが投稿できる権限があるか確認

### タイムゾーン

- スクリプトはJST（UTC+9）基準で動作
- GitHub Actionsは`12:00 UTC = 21:00 JST`で実行

### ログの確認方法

1. リポジトリの**Actions**タブを開く
2. 実行されたワークフローをクリック
3. **check-grass**ジョブをクリック
4. 各ステップのログを確認

## 🖥️ ローカルでの実行（オプション）

GitHub Actionsとは別に、ローカルでもテスト実行できます：

```bash
# セットアップ
./setup.sh

# .envファイルを編集
nano .env

# テスト実行
source .env
export GITHUB_USERNAME GITHUB_TOKEN DISCORD_WEBHOOK_URL DISCORD_USER_ID
./venv/bin/python grass_checker.py
```

## 📝 仕組み

1. **GitHub Actions**が毎日21時(JST)に起動
2. **GitHub GraphQL API**で今日のコントリビューションを取得
3. コントリビューションが**0件**の場合:
   - Discord Webhookでメッセージ送信
   - 指定されたユーザーにメンション
4. **1件以上**の場合: 何もしない

## 🎯 カスタマイズ

### 実行時刻の変更

`.github/workflows/check-grass.yml`の`cron`を編集：

```yaml
schedule:
  # 毎日15:00 UTC = 00:00 JST（深夜）に実行
  - cron: '0 15 * * *'
```

時刻の計算: `UTC時刻 = JST時刻 - 9時間`

### メッセージの変更

`grass_checker.py`の`check_and_notify`メソッド内のメッセージを編集：

```python
message = f"🌱 {today}の草が生えていません！今日もコミットしましょう！"
```

## 💰 コスト

**完全無料！**

- GitHub Actions: 月2,000分まで無料（このツールは月30分程度）
- Private repositoryでも無料枠内で動作

## 📄 ライセンス

MIT License

## 👤 作者

Nyayuta1060

---

## 🆘 サポート

問題が発生した場合は、リポジトリの**Issues**で報告してください。
