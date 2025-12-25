import requests
import os
import datetime

# --- 配置部分 ---
# 你的 Streamlit 应用网址 (部署成功后获得的那个网址)
APP_URL = "https://mynewsapp-lsjtfy3nulpyixpyxrruqo.streamlit.app/" 

def send_wechat_msg():
    # 从 GitHub Secrets 获取 Token，本地运行时需手动设置环境变量
    token = os.environ.get("PUSHPLUS_TOKEN")
    
    if not token:
        print("❌ 错误：未找到 PUSHPLUS_TOKEN")
        return

    today = datetime.date.today().strftime('%Y-%m-%d')
    title = f"🌍 全球深度早报 ({today})"
    
    #这是发送到微信的内容，支持 Markdown
    content = f"""
### 📅 今日新闻已整理完毕
AI 助手已为您聚合了全球多行业的重要新闻，并生成了深度解读。

**请点击下方链接开始阅读与收听：**
[👉 点击打开全球早报 APP]({APP_URL})

---
*来自 GitHub Actions 自动推送*
    """

    url = 'http://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown"
    }
    
    try:
        response = requests.post(url, json=data)
        print("✅ 推送结果:", response.text)
    except Exception as e:
        print("❌ 推送失败:", e)

if __name__ == "__main__":
    send_wechat_msg()
