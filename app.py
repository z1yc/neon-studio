
import streamlit as st
import json
import os
import time
import requests
from openai import OpenAI
from datetime import datetime

# ==========================================
# 页面配置
# ==========================================
st.set_page_config(
    page_title="⚡ NEON STUDIO · AI动漫制作系统",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# 自定义CSS
# ==========================================
st.markdown("""
<style>
    .stApp { background: #0a0a0f; }
    .neon-title { font-size: 2.8rem; font-weight: 700; background: linear-gradient(135deg, #00d4ff, #7b2ffc, #ff6fd8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .glass-card { background: rgba(255,255,255,0.03); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 24px; }
    .shot-card { background: rgba(255,255,255,0.02); border-left: 2px solid rgba(0,180,255,0.2); border-radius: 8px; padding: 16px 20px; margin-bottom: 12px; }
    .stat-number { font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #00d4ff, #7b2ffc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    div.stButton > button { background: linear-gradient(135deg, rgba(0,180,255,0.2), rgba(123,47,252,0.2)) !important; border: 1px solid rgba(0,180,255,0.3) !important; border-radius: 12px !important; color: #fff !important; font-weight: 600 !important; padding: 12px 32px !important; width: 100% !important; transition: all 0.3s ease !important; }
    div.stButton > button:hover { transform: scale(1.02); border-color: #00d4ff !important; box-shadow: 0 0 40px rgba(0,180,255,0.15) !important; }
    .status-tag { display: inline-block; padding: 4px 16px; border-radius: 20px; font-size: 0.75rem; border: 1px solid rgba(0,180,255,0.2); color: #00d4ff; background: rgba(0,180,255,0.05); }
    .divider-line { height: 1px; background: linear-gradient(90deg, transparent, rgba(0,180,255,0.2), transparent); margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 头部
# ==========================================
col_logo, col_status = st.columns([3, 1])
with col_logo:
    st.markdown('<div class="neon-title">⚡ NEON STUDIO</div><div style="color:rgba(255,255,255,0.4);font-size:0.9rem;letter-spacing:4px;">AI 动漫制作系统 · 3D国漫工业级</div>', unsafe_allow_html=True)
with col_status:
    st.markdown('<div style="text-align:right;"><span class="status-tag">● 系统就绪</span></div>', unsafe_allow_html=True)

st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

# ==========================================
# 侧边栏 - API设置
# ==========================================
with st.sidebar:
    st.markdown("### 🔑 API密钥设置")
    
    deepseek_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        placeholder="sk-...",
        help="在 platform.deepseek.com 获取"
    )
    
    kling_key = st.text_input(
        "Kling AI API Key",
        type="password",
        placeholder="api-key-kling-...",
        help="在 klingai.com 获取"
    )
    
    st.markdown("---")
    st.markdown("### ⚡ 系统状态")
    
    if deepseek_key:
        st.success("✅ DeepSeek 已连接")
    else:
        st.warning("⚠️ 请输入 DeepSeek API Key")
    
    if kling_key:
        st.success("✅ Kling AI 已连接")
    else:
        st.warning("⚠️ 请输入 Kling AI API Key")

# ==========================================
# 电影级分镜指令
# ==========================================
SYSTEM_PROMPT = """
你是一位顶级3D国漫电影导演与视觉总监。将文章转化为工业化标准的分镜脚本。

输出JSON格式：
{
  "project_title": "项目名称",
  "character_designs": {
    "角色名": {
      "character_type": "主角/配角/反派",
      "三视图_正面": {"face": "", "costume_front": "", "accessories_front": ""},
      "三视图_侧面": {"profile": "", "costume_side": "", "accessories_side": ""},
      "三视图_背面": {"back_profile": "", "costume_back": "", "accessories_back": ""},
      "color_palette": "主色调+辅助色+点缀色",
      "distinctive_features": "独特标志"
    }
  },
  "shots": [
    {
      "shot_number": 1,
      "scene_name": "场景名",
      "scene_time": "黎明/正午/黄昏/子夜",
      "shot_type": "大远景/远景/中景/近景/特写",
      "camera_angle": "平视/仰视/俯视",
      "camera_movement": "固定/推/拉/摇/移",
      "lighting_style": "三点布光/侧逆光/自然光",
      "composition": "黄金分割/对角线/对称",
      "visual_description": "画面详细描述",
      "dialogue": "台词或null",
      "duration_seconds": 5,
      "emotional_tone": "情绪",
      "acting": {"facial_expression": "", "eye_movement": "", "body_tension": ""},
      "vfx": {"primary": "", "secondary": ""}
    }
  ]
}
"""

# ==========================================
# 核心功能
# ==========================================
def generate_storyboard(api_key, article):
    """生成分镜脚本"""
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"分析文章：

{article}"}
        ],
        temperature=0.35,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def generate_video(kling_key, prompt, duration=5):
    """调用Kling AI生成视频"""
    url = "https://api.klingai.com/v1/videos/generations"
    headers = {
        "Authorization": f"Bearer {kling_key}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "duration": duration,
        "mode": "pro",
        "style": "anime"
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        if result.get("code") == 0:
            return result.get("data", {}).get("task_id")
        return None
    except:
        return None

# ==========================================
# 主界面
# ==========================================
tab1, tab2 = st.tabs(["🎬 分镜生成", "🎥 视频生成"])

# ========== Tab 1: 分镜生成 ==========
with tab1:
    col_input, col_output = st.columns([1, 1])
    
    with col_input:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        article_content = st.text_area(
            "📝 输入文章",
            height=350,
            placeholder="粘贴你的故事、剧本或文章...

AI将自动提取角色和情节生成工业级分镜。",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        generate_btn = st.button(
            "⚡ 生成分镜脚本",
            disabled=not (deepseek_key and article_content)
        )
        
        if not deepseek_key:
            st.caption("⚠️ 请在左侧输入 DeepSeek API Key")
        elif not article_content:
            st.caption("📌 请输入文章内容")
    
    with col_output:
        st.markdown("### 📊 生成结果")
        
        if generate_btn and deepseek_key and article_content:
            try:
                with st.spinner("🧠 AI导演正在构思..."):
                    result = generate_storyboard(deepseek_key, article_content)
                
                st.success("✅ 分镜生成完成！")
                
                shots = result.get("shots", [])
                characters = result.get("character_designs", {})
                
                # 统计
                c1, c2, c3 = st.columns(3)
                c1.markdown(f'<div style="text-align:center;"><div class="stat-number">{len(shots)}</div><div style="color:rgba(255,255,255,0.3);">镜头数</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div style="text-align:center;"><div class="stat-number">{len(characters)}</div><div style="color:rgba(255,255,255,0.3);">角色数</div></div>', unsafe_allow_html=True)
                c3.markdown(f'<div style="text-align:center;"><div class="stat-number">{sum(s.get("duration_seconds",0) for s in shots)}s</div><div style="color:rgba(255,255,255,0.3);">总时长</div></div>', unsafe_allow_html=True)
                
                # 角色
                if characters:
                    st.markdown("---")
                    st.markdown("### 🎨 角色三视图")
                    for name, design in characters.items():
                        with st.expander(f"▶ {name}"):
                            cols = st.columns(3)
                            front = design.get('三视图_正面', {})
                            side = design.get('三视图_侧面', {})
                            back = design.get('三视图_背面', {})
                            cols[0].write(f"**正面**
{front.get('face', '')[:60]}...")
                            cols[1].write(f"**侧面**
{side.get('profile', '')[:60]}...")
                            cols[2].write(f"**背面**
{back.get('back_profile', '')[:60]}...")
                            st.caption(f"色彩: {design.get('color_palette', '')}")
                            st.caption(f"标志: {design.get('distinctive_features', '')}")
                
                # 分镜
                if shots:
                    st.markdown("---")
                    st.markdown("### 🎬 分镜脚本")
                    for shot in shots:
                        st.markdown(f"""
                        <div class="shot-card">
                            <b>#{shot.get('shot_number')}</b>
                            <span style="color:rgba(255,255,255,0.4);background:rgba(255,255,255,0.05);padding:2px 12px;border-radius:12px;font-size:0.7rem;">{shot.get('shot_type')}</span>
                            <span style="color:rgba(255,255,255,0.3);font-size:0.7rem;">{shot.get('duration_seconds')}s · {shot.get('camera_angle')} · {shot.get('camera_movement')}</span>
                            <span style="float:right;color:rgba(255,255,255,0.2);font-size:0.6rem;">{shot.get('emotional_tone')}</span>
                            <div style="margin-top:4px;color:rgba(255,255,255,0.7);font-size:0.85rem;">{shot.get('visual_description')}</div>
                            <div style="margin-top:4px;color:rgba(255,255,255,0.3);font-size:0.7rem;">灯光: {shot.get('lighting_style', '')} · 构图: {shot.get('composition', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 下载
                st.download_button(
                    label="📥 下载完整JSON",
                    data=json.dumps(result, ensure_ascii=False, indent=2),
                    file_name=f"storyboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                # 保存到session_state供视频生成使用
                st.session_state['storyboard_result'] = result
                
            except Exception as e:
                st.error(f"⚠️ 生成失败：{e}")
                st.info("请检查：API密钥是否正确，DeepSeek账户是否有余额")
        else:
            st.markdown('<div style="text-align:center;padding:60px 20px;color:rgba(255,255,255,0.12);"><div style="font-size:3rem;">◈</div><div>等待输入素材</div></div>', unsafe_allow_html=True)

# ========== Tab 2: 视频生成 ==========
with tab2:
    st.markdown("### 🎥 从分镜生成视频")
    st.caption("选择分镜中的镜头，一键生成视频")
    
    if 'storyboard_result' in st.session_state:
        shots = st.session_state['storyboard_result'].get('shots', [])
        
        if shots:
            selected_shots = st.multiselect(
                "选择要生成视频的镜头",
                options=[f"镜头 {s.get('shot_number')}: {s.get('visual_description', '')[:30]}..." for s in shots],
                default=[f"镜头 {shots[0].get('shot_number')}: {shots[0].get('visual_description', '')[:30]}..."]

            )
            
            if selected_shots and kling_key:
                if st.button("🎬 生成选中视频"):
                    with st.spinner("⏳ 正在生成视频..."):
                        for selection in selected_shots:
                            idx = int(selection.split(" ")[1]) - 1
                            shot = shots[idx]
                            desc = shot.get('visual_description', '')
                            
                            task_id = generate_video(kling_key, desc, shot.get('duration_seconds', 5))
                            if task_id:
                                st.success(f"✅ 镜头 {idx+1} 已提交，任务ID: {task_id}")
                            else:
                                st.error(f"❌ 镜头 {idx+1} 提交失败")
            elif not kling_key:
                st.warning("⚠️ 请在左侧输入 Kling AI API Key")
            elif not selected_shots:
                st.info("📌 请选择至少一个镜头")
        else:
            st.info("📌 请先在「分镜生成」tab生成分镜脚本")
    else:
        st.info("📌 请先在「分镜生成」tab生成分镜脚本")

# ==========================================
# 页脚
# ==========================================
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; color: rgba(255,255,255,0.12); font-size: 0.6rem; letter-spacing: 1px; padding: 8px 0;">
    <span>⚡ NEON STUDIO · AI动漫制作系统 v2.0</span>
    <span>DeepSeek + Kling AI · 3D国漫专业版</span>
</div>
""", unsafe_allow_html=True)
