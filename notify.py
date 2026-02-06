# -*- coding: utf-8 -*-
import os
import requests

def send(title, content):
    """
    PushPlus 通知函数，读取 PUSH_PLUS_TOKEN 环境变量
    """
    token = os.environ.get("PUSH_PLUS_TOKEN")
    if not token:
        print("⚠️ 未发现环境变量 PUSH_PLUS_TOKEN，跳过推送。")
        return

    url = "https://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown",
        "channel": "wechat"
    }
    
    try:
        response = requests.post(url, json=data, timeout=15)
        res_json = response.json()
        if res_json.get("code") == 200:
            print(f"✅ PushPlus 推送成功")
        else:
            print(f"❌ PushPlus 推送失败: {res_json.get('msg')}")
    except Exception as e:
        print(f"⚠️ PushPlus 网络异常: {e}")