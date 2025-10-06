#!/bin/bash
# Git-GrassReporter セットアップスクリプト

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Git-GrassReporter セットアップ ==="
echo ""

# Python3のチェック
if ! command -v python3 &> /dev/null; then
    echo "エラー: Python3がインストールされていません"
    exit 1
fi

echo "Python3: $(python3 --version)"

# 仮想環境の作成
if [ ! -d "venv" ]; then
    echo "仮想環境を作成中..."
    python3 -m venv venv
fi

# 仮想環境の有効化
source venv/bin/activate

# 依存パッケージのインストール
echo "依存パッケージをインストール中..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=== 設定ファイルの作成 ==="

# .envファイルの作成
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".envファイルを作成しました"
    echo "エディタで .env ファイルを編集して、必要な情報を設定してください:"
    echo "  1. GITHUB_TOKEN: https://github.com/settings/tokens から作成"
    echo "     必要なスコープ: 'read:user'"
    echo "  2. DISCORD_WEBHOOK_URL: Discordサーバーの設定から作成"
    echo "  3. DISCORD_USER_ID: Discordで右クリック→IDをコピー"
    echo ""
else
    echo ".envファイルは既に存在します"
fi

# cronジョブの設定例を表示
echo ""
echo "=== 自動実行の設定 (cron) ==="
echo "毎日21時(JST)に実行するには、以下のコマンドを実行してください:"
echo ""
echo "  crontab -e"
echo ""
echo "そして、以下の行を追加してください:"
echo ""
echo "  0 21 * * * cd $SCRIPT_DIR && ./venv/bin/python grass_checker.py >> $SCRIPT_DIR/logs/grass_checker.log 2>&1"
echo ""

# ログディレクトリの作成
mkdir -p logs

# 実行権限の付与
chmod +x grass_checker.py

echo ""
echo "=== セットアップ完了 ==="
echo ""
echo "次のステップ:"
echo "  1. .env ファイルを編集して設定を行う"
echo "  2. テスト実行: ./venv/bin/python grass_checker.py"
echo "  3. cron に登録して自動実行を設定"
echo ""
