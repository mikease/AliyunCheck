# -*- coding: utf-8 -*-
"""
cron: 0 9 * * *
new Env('阿里云盘每日签到');
"""
import os
import requests
import time

# 尝试导入自定义的 notify 模块
try:
    from notify import send
except ImportError:
    def send(title, content):
        print(f"⚠️ 未找到 notify.py，仅执行本地打印。\n标题: {title}\n内容: {content}")

def run_task(token, index):
    """单个账号签到逻辑"""
    try:
        # 1. 换取 Access Token
        token_url = "https://auth.aliyundrive.com/v2/account/token"
        res = requests.post(token_url, json={
            "grant_type": "refresh_token", 
            "refresh_token": token.strip()
        }, timeout=15)
        data = res.json()
        
        if "access_token" not in data:
            return f"> **账号 [{index}]**: Token 已失效 ❌"

        access_token = data['access_token']
        nick_name = data.get('nick_name', f"用户{index}")
        
        # 2. 执行签到
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        check_url = "https://member.aliyundrive.com/v1/activity/sign_in_list"
        check_res = requests.post(check_url, headers=headers, json={}, timeout=15)
        check_data = check_res.json()

        if check_data.get("success"):
            count = check_data['result']['signInCount']
            return f"> **账号 [{nick_name}]**: 签到成功 (累计 {count} 天) ✅"
        else:
            return f"> **账号 [{nick_name}]**: 签到失败 ({check_data.get('message')}) ❌"
    except Exception as e:
        return f"> **账号 [{index}]**: 异常 ({str(e)}) ⚠️"

def main():
    env_token = os.environ.get("ALI_REFRESH_TOKEN")
    if not env_token:
        print("❌ 错误：未找到环境变量 ALI_REFRESH_TOKEN")
        return

    # 分隔符兼容处理
    token_list = [t.strip() for t in env_token.replace('\n', '&').replace('@', '&').split('&') if t.strip()]
    
    print(f"🚀 发现 {len(token_list)} 个账号，开始执行...")
    results = []
    for i, token in enumerate(token_list):
        res_msg = run_task(token, i + 1)
        print(res_msg.replace('> ', ''))
        results.append(res_msg)
        if i < len(token_list) - 1:
            time.sleep(2)

    # 发送汇总通知
    summary_title = f"📅 阿里云盘签到报告 ({len(token_list)}个账号)"
    summary_content = "### 签到状态汇总\n" + "\n".join(results) + "\n\n--- \n**提示**: 奖励需前往 App 手动领取"
    send(summary_title, summary_content)

if __name__ == "__main__":
    main()