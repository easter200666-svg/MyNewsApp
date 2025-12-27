import streamlit as st
import asyncio
import edge_tts
import tempfile
import datetime
import feedparser
import google.generativeai as genai
import os

# --- 1. 配置与初始化 ---
st.set_page_config(page_title="全球深度早报 (实时版)", page_icon="📡", layout="centered")

# 获取后台设置的 API Key
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ 未检测到 API Key！请在 Streamlit Secrets 中配置 GEMINI_API_KEY。")
    st.stop()

# 配置 Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')# 使用快速且免费的模型

# --- 2. 样式优化 ---
st.markdown("""
    <style>
    .stApp {background-color: #f0f2f6;}
    .main-container {background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 30px;}
    .news-title {font-size: 1.6em; font-weight: bold; color: #1f1f1f; margin-bottom: 10px;}
    .meta-info {color: #666; font-size: 0.85em; margin-bottom: 20px;}
    .raw-box {font-family: 'Georgia', serif; font-size: 1.05em; line-height: 1.7; color: #333; padding: 15px; background-color: #fafafa; border-left: 5px solid #ccc; margin-bottom: 20px;}
    .ai-box {background-color: #e8f5e9; padding: 15px; border-radius: 8px; border: 1px solid #c8e6c9;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 核心功能函数 ---

async def generate_audio(text, voice):
    """生成语音文件"""
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        await communicate.save(tmp_file.name)
        return tmp_file.name

def get_audio(text, voice_name):
    voices = {"知性女声": "zh-CN-XiaoxiaoNeural", "沉稳男声": "zh-CN-YunxiNeural", "新闻播音": "zh-CN-YunjianNeural"}
    try:
        return asyncio.run(generate_audio(text, voices.get(voice_name, "zh-CN-XiaoxiaoNeural")))
    except Exception as e:
        return None

def fetch_rss_news():
    """从 RSS 获取实时新闻链接和简介"""
    # 这里精选了几个高质量源，你可以随意更换
    rss_url = "http://feeds.bbci.co.uk/news/world/rss.xml" # BBC 国际
    # 或者用: "https://www.cnbc.com/id/100727362/device/rss/rss.html" (CNBC 世界)
    
    feed = feedparser.parse(rss_url)
    news_items = []
    # 只取前 3 条，避免等待时间过长
    for entry in feed.entries[:3]:
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary,
            "published": entry.get("published", str(datetime.date.today()))
        })
    return news_items

def ai_process_news(news_item):
    """调用 Gemini 进行翻译和总结"""
    prompt = f"""
    请扮演一位专业的高级新闻编辑。
    我给你一段新闻（英文），请你完成两个任务，输出必须是严格的 JSON 格式：
    
    新闻标题: {news_item['title']}
    新闻摘要: {news_item['summary']}
    
    任务一：【深度翻译】
    将新闻内容翻译成流畅、有深度的中文。这是给读者详细阅读的原文部分。
    
    任务二：【AI 核心解读】
    用中文总结这条新闻的核心影响、行业意义或未来趋势。这是给读者快速抓重点的总结部分。
    
    请按此格式返回：
    {{
        "translated_title": "中文标题",
        "full_translation": "这里放详细的中文翻译内容...",
        "ai_summary": "这里放AI的核心解读..."
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # 简单的清洗，防止返回 markdown 标记
        import json
        text = response.text.replace("```json", "").replace("```", "")
        return json.loads(text)
    except Exception as e:
        return {
            "translated_title": news_item['title'],
            "full_translation": "AI 处理繁忙或出错，请查看原文链接。",
            "ai_summary": f"处理失败: {e}"
        }

# --- 4. 主程序 ---
def main():
    st.title("📡 全球深度早报 (实时版)")
    st.caption(f"📅 {datetime.date.today()} | 🔴 实时连线 BBC/Reuters")
    
    with st.sidebar:
        st.header("设置")
        voice_choice = st.selectbox("播报声音", ["知性女声", "沉稳男声", "新闻播音"])
        if st.button("🔄 强制刷新新闻"):
            st.rerun()

    # 获取新闻 (加个缓存装饰器会更好，这里为了演示实时性先不加)
    with st.spinner('正在从全球网络抓取最新头条...'):
        raw_news = fetch_rss_news()

    st.success(f"已获取 {len(raw_news)} 条最新全球资讯，正在进行 AI 深度编译...")
    progress_bar = st.progress(0)

    for i, item in enumerate(raw_news):
        # AI 处理
        processed = ai_process_news(item)
        progress_bar.progress((i + 1) / len(raw_news))
        
        # 渲染界面
        st.markdown(f"""
        <div class="main-container">
            <div class="news-title">{processed['translated_title']}</div>
            <div class="meta-info">📅 {item['published']} | 🔗 <a href="{item['link']}">原文链接</a></div>
        """, unsafe_allow_html=True)

        # 上半部分：原文翻译
        st.markdown(f"**📖 深度阅读 (译文)**")
        st.markdown(f'<div class="raw-box">{processed["full_translation"]}</div>', unsafe_allow_html=True)

        # 下半部分：AI 总结 + 语音
        st.markdown("---")
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**🤖 AI 核心解读**")
            st.markdown(f'<div class="ai-box">{processed["ai_summary"]}</div>', unsafe_allow_html=True)
        with c2:
            if st.button(f"▶️ 听解读", key=f"btn_{i}"):
                audio = get_audio(processed['ai_summary'], voice_choice)
                if audio:
                    st.audio(audio, format='audio/mp3', start_time=0)
        
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

