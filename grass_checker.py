#!/usr/bin/env python3
"""
GitHub Grass Reporter
毎日21時にGitHubの草(contributions)をチェックし、
その日に草が生えていなければDiscordに通知を送る
毎日0時に連続コントリビュート日数を投稿
"""

import os
import sys
from datetime import datetime, timezone, timedelta
import requests
from typing import Optional


class GrassChecker:
    def __init__(self, github_username: str, github_token: str, 
                 discord_webhook_url: str, discord_user_id: str,
                 enable_grass_check: bool = True,
                 enable_daily_streak: bool = True):
        """
        Args:
            github_username: GitHubユーザー名
            github_token: GitHub Personal Access Token
            discord_webhook_url: Discord Webhook URL
            discord_user_id: メンション対象のDiscord User ID
            enable_grass_check: 草チェック機能の有効/無効(デフォルト: True)
            enable_daily_streak: 連続日数投稿機能の有効/無効(デフォルト: True)
        """
        self.github_username = github_username
        self.github_token = github_token
        self.discord_webhook_url = discord_webhook_url
        self.discord_user_id = discord_user_id
        self.enable_grass_check = enable_grass_check
        self.enable_daily_streak = enable_daily_streak
        
    def get_contribution_streak(self) -> Optional[int]:
        """
        前日までの連続コントリビュート日数を取得
        (当日を含まない - 0時時点では当日のコントリビューションはまだないため)
        
        Returns:
            連続日数、取得失敗時はNone
        """
        # GitHub GraphQL APIを使用
        query = """
        query($userName:String!) {
          user(login: $userName) {
            contributionsCollection {
              contributionCalendar {
                weeks {
                  contributionDays {
                    contributionCount
                    date
                  }
                }
              }
            }
          }
        }
        """
        
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json",
        }
        
        variables = {"userName": self.github_username}
        
        try:
            response = requests.post(
                "https://api.github.com/graphql",
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # 全てのコントリビューションデータを日付順に取得
            weeks = data.get("data", {}).get("user", {}).get(
                "contributionsCollection", {}
            ).get("contributionCalendar", {}).get("weeks", [])
            
            # 日付をキーとした辞書に変換
            contributions_dict = {}
            for week in weeks:
                for day in week.get("contributionDays", []):
                    date_str = day.get("date")
                    if date_str:
                        contributions_dict[date_str] = day.get("contributionCount", 0)
            
            # 連続日数をカウント（前日から遡る）
            streak = 0
            jst = timezone(timedelta(hours=9))
            yesterday = datetime.now(jst).date() - timedelta(days=1)
            
            # デバッグ: 昨日の日付を出力
            print(f"[DEBUG] 昨日の日付 (計算開始点): {yesterday}")
            
            # 昨日から遡って連続日数をカウント
            current_date = yesterday
            while True:
                date_str = current_date.isoformat()
                contribution_count = contributions_dict.get(date_str, 0)
                
                # デバッグ: 最初の数日分を出力
                if streak < 5:
                    print(f"[DEBUG] date={date_str}, count={contribution_count}")
                
                if contribution_count > 0:
                    streak += 1
                    current_date = current_date - timedelta(days=1)
                else:
                    if streak < 5:
                        print(f"[DEBUG] ストリーク終了: {date_str} のコントリビューションが0")
                    break
            
            print(f"[DEBUG] 最終的な連続日数: {streak}日")
            return streak
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API エラー: {e}", file=sys.stderr)
            return None
        except (KeyError, TypeError) as e:
            print(f"レスポンス解析エラー: {e}", file=sys.stderr)
            return None
    
    def get_today_contributions(self) -> Optional[int]:
        """
        今日のGitHub Contributionsを取得
        
        Returns:
            今日のコントリビューション数、取得失敗時はNone
        """
        # GitHub GraphQL APIを使用
        query = """
        query($userName:String!) {
          user(login: $userName) {
            contributionsCollection {
              contributionCalendar {
                weeks {
                  contributionDays {
                    contributionCount
                    date
                  }
                }
              }
            }
          }
        }
        """
        
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json",
        }
        
        variables = {"userName": self.github_username}
        
        try:
            response = requests.post(
                "https://api.github.com/graphql",
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # 今日の日付(JST)
            jst = timezone(timedelta(hours=9))
            today = datetime.now(jst).date().isoformat()
            
            # コントリビューションデータから今日の分を探す
            weeks = data.get("data", {}).get("user", {}).get(
                "contributionsCollection", {}
            ).get("contributionCalendar", {}).get("weeks", [])
            
            for week in weeks:
                for day in week.get("contributionDays", []):
                    if day.get("date") == today:
                        return day.get("contributionCount", 0)
            
            return 0
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API エラー: {e}", file=sys.stderr)
            return None
        except (KeyError, TypeError) as e:
            print(f"レスポンス解析エラー: {e}", file=sys.stderr)
            return None
    
    def send_discord_notification(self, message: str, mention: bool = True) -> bool:
        """
        Discordに通知を送信
        
        Args:
            message: 送信するメッセージ
            mention: メンションを含めるかどうか(デフォルト: True)
            
        Returns:
            送信成功時True、失敗時False
        """
        if mention:
            content = f"<@{self.discord_user_id}> {message}"
        else:
            content = message
            
        payload = {"content": content}
        
        try:
            response = requests.post(
                self.discord_webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Discord通知エラー: {e}", file=sys.stderr)
            return False
    
    def post_daily_streak(self) -> bool:
        """
        連続コントリビュート日数を投稿(メンション無し)
        
        Returns:
            処理成功時True、失敗時False
        """
        if not self.enable_daily_streak:
            print("連続日数投稿機能は無効になっています")
            return True
        
        print(f"[{datetime.now()}] 連続日数投稿開始...")
        
        streak = self.get_contribution_streak()
        
        if streak is None:
            print("連続日数の取得に失敗しました", file=sys.stderr)
            return False
        
        print(f"前日までの連続コントリビュート日数: {streak}日")
        
        jst = timezone(timedelta(hours=9))
        yesterday = (datetime.now(jst) - timedelta(days=1)).strftime("%Y年%m月%d日")

        message = f"📊 {yesterday}までの連続コントリビュート: **{streak}** 日"

        if self.send_discord_notification(message, mention=False):
            print("連続日数をDiscordに投稿しました")
            return True
        else:
            print("Discord投稿に失敗しました", file=sys.stderr)
            return False
    
    def check_and_notify(self) -> bool:
        """
        草をチェックして、必要なら通知を送信
        
        Returns:
            処理成功時True、失敗時False
        """
        if not self.enable_grass_check:
            print("草チェック機能は無効になっています")
            return True
        
        print(f"[{datetime.now()}] 草チェック開始...")
        
        contributions = self.get_today_contributions()
        
        if contributions is None:
            print("草の取得に失敗しました", file=sys.stderr)
            return False
        
        print(f"今日のコントリビューション数: {contributions}")
        
        if contributions == 0:
            jst = timezone(timedelta(hours=9))
            today = datetime.now(jst).strftime("%Y年%m月%d日")
            message = f"🌱 {today}の草が生えていません！今日もコミットしましょう！"
            
            if self.send_discord_notification(message):
                print("Discord通知を送信しました")
                return True
            else:
                print("Discord通知の送信に失敗しました", file=sys.stderr)
                return False
        else:
            print("草が生えています。通知は送信しません")
            return True


def main():
    """メイン処理"""
    # 環境変数から設定を読み込む
    github_username = os.getenv("GITHUB_USERNAME")
    github_token = os.getenv("GITHUB_TOKEN")
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    discord_user_id = os.getenv("DISCORD_USER_ID")
    
    # 機能のオンオフ設定(デフォルトは両方有効)
    enable_grass_check = os.getenv("ENABLE_GRASS_CHECK", "true").lower() in ("true", "1", "yes")
    enable_daily_streak = os.getenv("ENABLE_DAILY_STREAK", "true").lower() in ("true", "1", "yes")
    
    # 必須パラメータのチェック
    if not all([github_username, github_token, discord_webhook_url, discord_user_id]):
        print("エラー: 必要な環境変数が設定されていません", file=sys.stderr)
        print("必要な環境変数:", file=sys.stderr)
        print("  - GITHUB_USERNAME", file=sys.stderr)
        print("  - GITHUB_TOKEN", file=sys.stderr)
        print("  - DISCORD_WEBHOOK_URL", file=sys.stderr)
        print("  - DISCORD_USER_ID", file=sys.stderr)
        print("\nオプション環境変数:", file=sys.stderr)
        print("  - ENABLE_GRASS_CHECK (デフォルト: true)", file=sys.stderr)
        print("  - ENABLE_DAILY_STREAK (デフォルト: true)", file=sys.stderr)
        sys.exit(1)
    
    checker = GrassChecker(
        github_username=github_username,
        github_token=github_token,
        discord_webhook_url=discord_webhook_url,
        discord_user_id=discord_user_id,
        enable_grass_check=enable_grass_check,
        enable_daily_streak=enable_daily_streak
    )
    
    # コマンドライン引数でモードを判定
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    
    if mode == "daily-streak":
        # 連続日数を投稿(毎日0時用)
        success = checker.post_daily_streak()
    else:
        # 通常のチェックモード(毎日21時用)
        success = checker.check_and_notify()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
