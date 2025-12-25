import streamlit as st
import asyncio
import edge_tts
import tempfile
import datetime
import os

# --- 页面配置 ---
st.set_page_config(page_title="全球早报", page_icon="🌍", layout="centered")

# --- 样式优化 ---
st.markdown("""
    <style>
    .stApp {background-color: #f5f5f5;}
    .main-card {background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;}
    .category-tag {background-color: #e3f2fd; color: #1565c0; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold;}
    h3 {margin-top: 0;}
    </style>
    """, unsafe_allow_html=True)

# --- 语音合成函数 ---
async def generate_audio(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        await communicate.save(tmp_file.name)
        return tmp_file.name

def get_audio(text, voice_name):
    # 声音映射
    voices = {
        "知性女声": "zh-CN-XiaoxiaoNeural",
        "沉稳男声": "zh-CN-YunxiNeural",
        "新闻播音": "zh-CN-YunjianNeural"
    }
    selected_voice = voices.get(voice_name, "zh-CN-XiaoxiaoNeural")
    try:
        return asyncio.run(generate_audio(text, selected_voice))
    except Exception as e:
        st.error(f"语音生成失败: {e}")
        return None

# --- 模拟新闻数据 (此处实际应为 API 调用) ---
def get_news():
    return [
        {
            "title": "GPT-5 预览版发布，逻辑能力提升 40%",
            "category": "科技",
            "date": "2025-12-07",
            "summary": "OpenAI 再次炸场！GPT-5 预览版在逻辑推理能力上提升了 40%，并彻底解决了数学幻觉问题。这对谷歌 Gemini 构成了巨大压力，AI 行业竞赛进入白热化阶段。",
            "raw": "OpenAI announced the release of GPT-5 Preview today..."
        },
        {
            "title": "美联储宣布大幅降息",
            "category": "财经",
            "date": "2025-12-07",
            "summary": "超预期降息！美联储直接降息 50 个基点，市场反应剧烈，黄金和比特币大涨。这意味着全球资金流动性将变宽松，你的投资组合可能需要调整了。",
            "raw": "The Federal Reserve announced a 50 basis point rate cut..."
        }
    ]

# --- 主界面 ---
def main():
    st.title("🌍 全球早报 AI 版")
    st.caption(f"📅 {datetime.date.today()} | 每日自动更新")
    
    with st.sidebar:
        st.header("⚙️ 设置")
        voice_choice = st.selectbox("选择播报声音", ["知性女声", "沉稳男声", "新闻播音"])
        st.info("手机端点击左上角 '>' 展开菜单")

    news_list = get_news()

    for i, item in enumerate(news_list):
        # 使用自定义容器样式
        with st.container():
            st.markdown(f"""
            <div class="main-card">
                <h3>{item['title']}</h3>
                <span class="category-tag">{item['category']}</span>
                <span style="color:gray; font-size:0.8em; margin-left:10px;">{item['date']}</span>
                <p style="margin-top:10px;"><b>🤖 AI 核心解读：</b></p>
                <p>{item['summary']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 播放按钮
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button(f"▶️ 听解读", key=f"play_{i}"):
                    audio_file = get_audio(item['summary'], voice_choice)
                    if audio_file:
                        st.audio(audio_file, format="audio/mp3", start_time=0)
            
            with st.expander("📄 查看原始新闻 (英文/翻译)"):
                st.write(item['raw'])

if __name__ == "__main__":

    main()
