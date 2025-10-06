#!/usr/bin/env python3
"""
GitHub Grass Reporter
毎日21時にGitHubの草(contributions)をチェックし、
その日に草が生えていなければDiscordに通知を送る
"""

import os
import sys
from datetime import datetime, timezone, timedelta
import requests
from typing import Optional


class GrassChecker:
    def __init__(self, github_username: str, github_token: str, 
                 discord_webhook_url: str, discord_user_id: str):
        """
        Args:
            github_username: GitHubユーザー名
            github_token: GitHub Personal Access Token
            discord_webhook_url: Discord Webhook URL
            discord_user_id: メンション対象のDiscord User ID
        """
        self.github_username = github_username
        self.github_token = github_token
        self.discord_webhook_url = discord_webhook_url
        self.discord_user_id = discord_user_id
        
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
    
    def send_discord_notification(self, message: str) -> bool:
        """
        Discordに通知を送信
        
        Args:
            message: 送信するメッセージ
            
        Returns:
            送信成功時True、失敗時False
        """
        payload = {
            "content": f"<@{self.discord_user_id}> {message}"
        }
        
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
    
    def check_and_notify(self) -> bool:
        """
        草をチェックして、必要なら通知を送信
        
        Returns:
            処理成功時True、失敗時False
        """
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
    
    # 必須パラメータのチェック
    if not all([github_username, github_token, discord_webhook_url, discord_user_id]):
        print("エラー: 必要な環境変数が設定されていません", file=sys.stderr)
        print("必要な環境変数:", file=sys.stderr)
        print("  - GITHUB_USERNAME", file=sys.stderr)
        print("  - GITHUB_TOKEN", file=sys.stderr)
        print("  - DISCORD_WEBHOOK_URL", file=sys.stderr)
        print("  - DISCORD_USER_ID", file=sys.stderr)
        sys.exit(1)
    
    checker = GrassChecker(
        github_username=github_username,
        github_token=github_token,
        discord_webhook_url=discord_webhook_url,
        discord_user_id=discord_user_id
    )
    
    success = checker.check_and_notify()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
