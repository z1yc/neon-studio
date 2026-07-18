import streamlit as st
import json
import os
import time
import requests
from openai import OpenAI
from datetime import datetime

st.set_page_config(
    page_title="⚡ NEON STUDIO · AI动漫制作系统",
    page_icon="⚡",
    layout="wide"
)

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
    .field-label { color: rgba(255,255,255,0.3); font-size: 0.6rem; text-transform: uppercase; letter-spacing: 1px; }
    .field-value { color: rgba(255,255,255,0.85); font-size: 0.85rem; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

col_logo, col_status = st.columns([3, 1])
with col_logo:
    st.markdown('<div class="neon-title">⚡ NEON STUDIO</div><div style="color:rgba(255,255,255,0.4);font-size:0.9rem;letter-spacing:4px;">AI 动漫制作系统 · 3D国漫工业级</div>', unsafe_allow_html=True)
with col_status:
    st.markdown('<div style="text-align:right;"><span class="status-tag">● 系统就绪</span></div>', unsafe_allow_html=True)

st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔑 API密钥设置")
    deepseek_key = st.text_input("DeepSeek API Key", type="password", placeholder="sk-...")
    kling_key = st.text_input("Kling AI API Key", type="password", placeholder="api-key-kling-...")
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

SYSTEM_PROMPT = """
你是一位顶级3D国漫电影导演与视觉总监，拥有20年动画制作与视觉开发经验。你的任务是将用户提供的文章，转化为一套**工业化标准的分镜脚本**，包含完整的视觉语言、表演指导、摄影方案和后期制作说明。输出必须严格遵循以下格式，以JSON呈现。

---

## 一、角色视觉开发

{
  "character_designs": {
    "角色名": {
      "character_type": "主角/配角/反派",
      "gender": "男/女",
      "age_range": "少年/青年/中年/老年",
      "archetype": "原型：英雄/导师/守护者/变节者/小丑/探索者/反英雄",
      "character_arc": "角色弧光（开篇状态 → 关键转变 → 结局状态）",
      "core_motivation": "核心动机",
      "fatal_flaw": "致命缺陷",
      "三视图_正面": {"face": "", "costume_front": "", "accessories_front": ""},
      "三视图_侧面": {"profile": "", "costume_side": "", "accessories_side": ""},
      "三视图_背面": {"back_profile": "", "costume_back": "", "accessories_back": ""},
      "silhouette": "剪影特征",
      "color_palette": "主色调+辅助色+点缀色",
      "distinctive_features": "独特标志"
    }
  }
}

## 二、分镜脚本

{
  "shots": [
    {
      "shot_number": 1,
      "scene_name": "场景名",
      "scene_time": "黎明/正午/黄昏/子夜",
      "scene_weather": "天气与氛围",
      "shot_type": "大远景/远景/中景/近景/特写",
      "camera_angle": "平视/仰视/俯视",
      "camera_movement": "固定/推/拉/摇/移",
      "lens_type": "广角/标准/长焦",
      "depth_of_field": "深景深/浅景深",
      "lighting_style": "三点布光/侧逆光/自然光",
      "lighting_color": "暖金色/冷青蓝",
      "composition": "黄金分割/对角线/对称",
      "visual_description": "画面详细描述",
      "dialogue": "台词或null",
      "duration_seconds": 5,
      "emotional_tone": "情绪",
      "acting": {"facial_expression": "", "eye_movement": "", "body_tension": "", "gesture": ""},
      "vfx": {"primary": "", "secondary": "", "micro": ""}
    }
  ]
}

## 三、输出格式要求

严格按照JSON格式输出：
{
  "project_title": "项目名称",
  "character_designs": { ... },
  "shots": [ ... ],
  "total_shots": "总镜头数",
  "total_duration": "预估总时长（秒）"
}
"""

def generate_storyboard(api_key, article):
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"请将以下文章转化为工业级分镜脚本：\n\n{article}"}
        ],
        temperature=0.35,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def generate_video_task(kling_key, prompt, duration=5):
    """提交视频生成任务"""
    url = "https://api.klingai.com/v1/videos/generations"
    headers = {
        "Authorization": f"Bearer {kling_key}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "duration": duration,
        "mode": "std",
        "style": "anime"
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        if result.get("code") == 0:
            return result.get("data", {}).get("task_id")
        else:
            st.error(f"❌ 提交失败: {result.get('message', '未知错误')}")
            return None
    except Exception as e:
        st.error(f"❌ 请求异常: {e}")
        return None

def poll_video_status(kling_key, task_id):
    """轮询视频生成状态"""
    url = f"https://api.klingai.com/v1/videos/generations/{task_id}"
    headers = {"Authorization": f"Bearer {kling_key}"}
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            result = response.json()
            if result.get("code") == 0:
                data = result.get("data", {})
                status = data.get("status")
                if status == "succeed":
                    videos = data.get("videos", [])
                    if videos:
                        return videos[0].get("url")
                    task_result = data.get("task_result", {})
                    if task_result.get("videos"):
                        return task_result["videos"][0].get("url")
                    return None
                elif status == "failed":
                    st.error(f"❌ 生成失败: {data.get('fail_reason', '未知')}")
                    return None
                else:
                    time.sleep(3)
            else:
                time.sleep(3)
        except:
            time.sleep(3)
    return None

def render_character_designs(characters):
    if not characters:
        return
    st.markdown("### 🎨 角色三视图设定")
    for name, design in characters.items():
        with st.expander(f"▶ {name}", expanded=True):
            cols = st.columns(3)
            with cols[0]:
                st.markdown("**正面视图**")
                front = design.get('三视图_正面', {})
                st.caption(front.get('face', '')[:80])
            with cols[1]:
                st.markdown("**侧面视图**")
                side = design.get('三视图_侧面', {})
                st.caption(side.get('profile', '')[:80])
            with cols[2]:
                st.markdown("**背面视图**")
                back = design.get('三视图_背面', {})
                st.caption(back.get('back_profile', '')[:80])
            st.markdown(f"**色彩**：{design.get('color_palette', '')}")
            st.markdown(f"**标志**：{design.get('distinctive_features', '')}")

def render_shot(shot):
    st.markdown(f"""
    <div class="shot-card">
        <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
            <span style="color: #00d4ff; font-weight: 700; font-size: 1.2rem;">#{shot.get('shot_number')}</span>
            <span style="color: rgba(255,255,255,0.4); font-size: 0.7rem; background: rgba(255,255,255,0.05); padding: 2px 12px; border-radius: 12px;">
                {shot.get('shot_type')}
            </span>
            <span style="color: rgba(255,255,255,0.3); font-size: 0.7rem;">
                {shot.get('duration_seconds')}s · {shot.get('camera_angle')}
            </span>
            <span style="margin-left: auto; color: rgba(255,255,255,0.2); font-size: 0.6rem;">
                {shot.get('emotional_tone')}
            </span>
        </div>
        <div style="margin-top: 8px; color: rgba(255,255,255,0.7); font-size: 0.85rem;">
            {shot.get('visual_description')}
        </div>
        <div style="margin-top: 4px; color: rgba(255,255,255,0.3); font-size: 0.7rem;">
            灯光: {shot.get('lighting_style', '')} · 构图: {shot.get('composition', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎬 分镜生成", "🎥 视频生成"])

with tab1:
    col_input, col_output = st.columns([1, 1])
    with col_input:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        article_content = st.text_area("📝 输入文章", height=350, placeholder="粘贴你的故事、剧本或文章...", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        generate_btn = st.button("⚡ 生成精细化分镜", disabled=not (deepseek_key and article_content))
        if not deepseek_key:
            st.caption("⚠️ 请在左侧输入 DeepSeek API Key")
    with col_output:
        st.markdown("### 📊 生成结果")
        if generate_btn and deepseek_key and article_content:
            try:
                with st.spinner("🧠 AI导演正在构思..."):
                    result = generate_storyboard(deepseek_key, article_content)
                st.success("✅ 分镜生成完成！")
                shots = result.get("shots", [])
                characters = result.get("character_designs", {})
                c1, c2, c3 = st.columns(3)
                c1.markdown(f'<div style="text-align:center;"><div class="stat-number">{len(shots)}</div><div style="color:rgba(255,255,255,0.3);">镜头数</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div style="text-align:center;"><div class="stat-number">{len(characters)}</div><div style="color:rgba(255,255,255,0.3);">角色数</div></div>', unsafe_allow_html=True)
                c3.markdown(f'<div style="text-align:center;"><div class="stat-number">{sum(s.get("duration_seconds",0) for s in shots)}s</div><div style="color:rgba(255,255,255,0.3);">总时长</div></div>', unsafe_allow_html=True)
                if characters:
                    st.markdown("---")
                    render_character_designs(characters)
                if shots:
                    st.markdown("---")
                    st.markdown("### 🎬 分镜脚本")
                    for shot in shots:
                        render_shot(shot)
                st.download_button(
                    label="📥 下载JSON",
                    data=json.dumps(result, ensure_ascii=False, indent=2),
                    file_name=f"storyboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                st.session_state['storyboard_result'] = result
            except Exception as e:
                st.error(f"⚠️ 生成失败：{e}")
        else:
            st.info("等待输入素材")

with tab2:
    st.markdown("### 🎥 从分镜生成视频")
    st.caption("选择分镜，一键生成视频")
    
    if 'storyboard_result' not in st.session_state:
        st.info("📌 请先在「分镜生成」tab生成分镜脚本")
    else:
        shots = st.session_state['storyboard_result'].get('shots', [])
        if not shots:
            st.info("📌 请先生成分镜脚本")
        else:
            shot_options = []
            for s in shots:
                num = s.get('shot_number', 0)
                desc = s.get('visual_description', '')[:30]
                shot_options.append(f"{num}: {desc}...")
            
            selected = st.multiselect("选择要生成视频的镜头", options=shot_options, default=[shot_options[0]] if shot_options else [])
            
            if not kling_key:
                st.warning("⚠️ 请在左侧输入 Kling AI API Key")
            elif not selected:
                st.info("📌 请选择至少一个镜头")
            else:
                if st.button("🎬 生成视频"):
                    with st.spinner("⏳ 正在生成视频..."):
                        for sel in selected:
                            parts = sel.split(":")
                            if parts:
                                try:
                                    idx = int(parts[0].strip()) - 1
                                    if 0 <= idx < len(shots):
                                        shot = shots[idx]
                                        desc = shot.get('visual_description', '')
                                        duration = shot.get('duration_seconds', 5)
                                        task_id = generate_video_task(kling_key, desc, duration)
                                        if task_id:
                                            with st.spinner(f"⏳ 镜头 {idx+1} 生成中..."):
                                                video_url = poll_video_status(kling_key, task_id)
                                                if video_url:
                                                    st.success(f"✅ 镜头 {idx+1} 成功!")
                                                    st.video(video_url)
                                                else:
                                                    st.error(f"❌ 镜头 {idx+1} 生成失败")
                                        else:
                                            st.error(f"❌ 镜头 {idx+1} 提交失败")
                                except:
                                    st.error(f"❌ 无法解析: {sel}")

st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; color: rgba(255,255,255,0.12); font-size: 0.6rem; letter-spacing: 1px; padding: 8px 0;">
    <span>⚡ NEON STUDIO · AI动漫制作系统 v2.0</span>
    <span>DeepSeek + Kling AI · 3D国漫专业版</span>
</div>
""", unsafe_allow_html=True)
