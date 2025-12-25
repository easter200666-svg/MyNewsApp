import streamlit as st
import asyncio
import edge_tts
import tempfile
import datetime

# --- 页面基础配置 ---
st.set_page_config(page_title="全球深度早报", page_icon="📰", layout="centered")

# --- CSS 样式美化 (让阅读体验更好) ---
st.markdown("""
    <style>
    .stApp {background-color: #f0f2f6;}
    .main-container {background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 30px;}
    .news-title {font-size: 1.8em; font-weight: bold; color: #1f1f1f; margin-bottom: 10px;}
    .meta-tags {color: #666; font-size: 0.9em; margin-bottom: 20px;}
    .category-badge {background-color: #e3f2fd; color: #1565c0; padding: 4px 10px; border-radius: 20px; font-weight: bold; margin-right: 10px;}
    
    /* 原始内容区域样式 */
    .raw-content-box {
        font-family: 'Georgia', serif; /* 使用衬线字体增加阅读仪式感 */
        font-size: 1.1em;
        line-height: 1.8;
        color: #333;
        padding: 20px;
        background-color: #fafafa;
        border-left: 6px solid #bbb;
        margin-bottom: 25px;
    }
    
    /* AI总结区域样式 */
    .ai-summary-box {
        background-color: #e8f5e9; /* 淡淡的绿色代表总结/精华 */
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #c8e6c9;
    }
    .section-header {
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 语音合成核心函数 (保持不变) ---
async def generate_audio(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        await communicate.save(tmp_file.name)
        return tmp_file.name

def get_audio(text, voice_name):
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

# --- 模拟的全球/多行业数据 (未来替换为真实API) ---
def get_todays_news():
    # 这里模拟了翻译后的长篇全文和AI总结
    return [
        {
            "title": "欧盟达成历史性 AI 监管法案",
            "category": "全球政治/科技",
            "source": "Financial Times",
            # --- 上半部分：供阅读思考的全文 ---
            "full_translated": "经过近 40 小时的马拉松式谈判，欧盟政策制定者终于在周六凌晨就目前全球最全面的《人工智能法案》达成临时协议。该法案旨在对 ChatGPT 等基础模型实施严格的透明度要求，并完全禁止社会信用评分系统和部分生物识别监控应用。对于未能合规的企业，最高罚款可达全球营业额的 7%。这一协议被视为全球 AI 监管的里程碑，可能会为美国和其他国家的后续立法设立基准。支持者认为这保护了公民权利，而科技行业代表则担忧过度监管可能会扼杀欧洲的创新能力，导致本土企业在与中美竞争中处于劣势。法案仍需欧洲议会正式投票通过，预计最早于 2026 年全面生效。",
            # --- 下半部分：AI 理解总结 ---
            "ai_summary": "🇪🇺 **核心解读**：全球首个全面 AI 监管法案在欧盟落地。重点在于限制高风险 AI 应用（如监控）并强制大模型提高透明度。这对全球科技巨头（尤其是美国的 OpenAI、谷歌）是重大利空，合规成本激增。对欧洲本土 AI 初创企业来说，短期也是阵痛，但长期看建立了明确的游戏规则。"
        },
        {
            "title": "丰田固态电池取得突破，电动车行业震动",
            "category": "全球制造业/汽车",
            "source": "Nikkei Asia",
            "full_translated": "日本汽车巨头丰田公司今日宣布，其固态电池技术研发取得重大突破，已成功克服电池耐久性瓶颈。据称，搭载新技术的原型车可实现充电 10 分钟续航 1200 公里的惊人表现，且电池体积和重量仅为现有锂离子电池的一半。丰田计划在 2027 年实现小规模量产。市场分析认为，如果数据属实，这将彻底改变电动车行业的竞争格局，目前在液态锂电池领域占据主导地位的中国企业（如宁德时代、比亚迪）将面临严峻的技术挑战。受此消息影响，丰田股价大涨 5%，而多只锂电产业链股票出现下跌。",
            "ai_summary": "🔋 **核心解读**：电动车行业的“核武器”——固态电池可能比预期来得更快。丰田此举意在弯道超车，挑战中国在新能源汽车领域的主导地位。如果 2027 年能落地，现有的“里程焦虑”将不复存在，燃油车将被加速淘汰，全球电池供应链格局将重塑。"
        }
    ]

# --- 主界面逻辑 ---
def main():
    st.title("🌍 全球深度早报")
    st.caption(f"📅 {datetime.date.today().strftime('%Y年%m月%d日')} | 🤖 AI 聚合全球多行业动态")
    
    with st.sidebar:
        st.header("🎙️ 播报设置")
        voice_choice = st.selectbox("选择总结播报声音", ["知性女声", "沉稳男声", "新闻播音"])
        st.info("提示：建议先阅读原文，再听 AI 总结。")

    news_list = get_todays_news()

    for i, item in enumerate(news_list):
        # 使用自定义容器包裹每一条新闻
        st.markdown(f"""
        <div class="main-container">
            <div class="news-title">{item['title']}</div>
            <div class="meta-tags">
                <span class="category-badge">{item['category']}</span>
                来源: {item['source']}
            </div>
        """, unsafe_allow_html=True)

        # --- 板块 1：翻译后的完整原文（上方，供阅读）---
        st.markdown('<div class="section-header">📖 深度阅读 (译文全览)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="raw-content-box">{item["full_translated"]}</div>', unsafe_allow_html=True)
        
        st.markdown("---") # 分割线

        # --- 板块 2：AI 总结与语音（下方，供参考）---
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown('<div class="section-header">🤖 AI 核心解读与总结</div>', unsafe_allow_html=True)
        with col2:
            # 播放按钮放在总结标题旁边
            play_btn = st.button(f"▶️ 播报总结 ({i+1})", key=f"play_{i}")

        if play_btn:
            with st.spinner("正在生成语音..."):
                audio_file = get_audio(item['ai_summary'], voice_choice)
                if audio_file:
                    st.audio(audio_file, format="audio/mp3", start_time=0)

        st.markdown(f'<div class="ai-summary-box">{item["ai_summary"]}</div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True) # 结束 main-container

if __name__ == "__main__":
    main()
