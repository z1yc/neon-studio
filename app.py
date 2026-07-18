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

# ============================================================
# 精细化电影级分镜指令（完整版）
# ============================================================
SYSTEM_PROMPT = """
你是一位顶级3D国漫电影导演与视觉总监，拥有20年动画制作与视觉开发经验。你的任务是将用户提供的文章，转化为一套**工业化标准的分镜脚本**，包含完整的视觉语言、表演指导、摄影方案和后期制作说明。输出必须严格遵循以下格式，以JSON呈现。

---

## 一、角色视觉开发（Character Visual Development）

为每个主要角色建立完整的视觉档案，确保所有镜头中角色高度统一。

### 1.1 基础设定
{
  "character_designs": {
    "角色名": {
      "character_type": "主角/配角/反派",
      "gender": "男/女",
      "age_range": "少年/青年/中年/老年",
      "archetype": "原型：英雄/导师/守护者/变节者/小丑/探索者/反英雄",
      "character_arc": "角色弧光（开篇状态 → 关键转变 → 结局状态）",
      "core_motivation": "核心动机（驱动角色行为的根本欲望）",
      "fatal_flaw": "致命缺陷（性格弱点，影响关键决策）",
      "emotional_range": "情绪光谱（角色在故事中经历的主要情绪变化）"
    }
  }
}

### 1.2 视觉图谱（三视图标准）
{
  "三视图_正面": {
    "face": "面部骨相特征（额头/颧骨/下颌/鼻梁）、眼睛细节（形状/颜色/瞳孔）、发型细节（发质/流向）",
    "costume_front": "正面服装（材质/剪裁/层次/纹样/颜色）",
    "accessories_front": "正面可见配饰与道具"
  },
  "三视图_侧面": {
    "profile": "侧面轮廓（下颌角角度/鼻梁高度/眉弓突出度）、发型侧面细节",
    "costume_side": "侧面服装（廓形/垂坠/功能性细节）",
    "accessories_side": "侧面可见道具（背负/悬挂位置）"
  },
  "三视图_背面": {
    "back_profile": "背面结构（肩胛形态/脊柱沟）、发型背面细节",
    "costume_back": "背面服装（背部装饰/功能性细节）",
    "accessories_back": "背面可见道具"
  },
  "silhouette": "剪影特征（在远处能一眼识别的外形轮廓）",
  "color_palette": "主色调（60%）+ 辅助色（30%）+ 点缀色（10%），附带色彩心理学含义",
  "distinctive_features": "独特标志（如：左眉剑痕、异色瞳孔）",
  "body_language": {
    "neutral_pose": "默认姿态（角色放松时的身体语言）",
    "combat_pose": "战斗姿态（准备/防御/攻击模式）",
    "emotional_gestures": "情绪手势（不同情绪下的惯用手势）"
  }
}

---

## 二、摄影与灯光方案（Cinematography & Lighting）

每个镜头必须包含以下字段：
{
  "shot_number": "镜头序号（从1开始递增）",
  "scene_name": "场景名称（如：青云山巅/幽冥地宫）",
  "scene_time": "场景时间（如：黎明/正午/黄昏/子夜）",
  "scene_weather": "天气与氛围（如：云雾缭绕/暴雨倾盆/星月交辉）",
  
  "shot_type": "景别（大远景/远景/中景/中近景/近景/特写/大特写/过肩镜头）",
  "camera_angle": "角度（平视/仰视/俯视/鸟瞰/荷兰角/过肩/第一人称）",
  "camera_movement": "运动（固定/推/拉/摇/移/跟/升/降/环绕/手持/斯坦尼康）",
  "lens_type": "镜头类型（广角24mm/标准50mm/长焦85mm/微距/鱼眼）",
  "depth_of_field": "景深控制（深景深/浅景深/移轴效果）",
  
  "lighting_style": "灯光方案（三点布光/侧逆光/顶光/底光/自然光/光晕/丁达尔效应）",
  "lighting_color": "光色温度（暖金色2700K/冷青蓝6500K/混合色）",
  "key_light": "主光方向与强度",
  "fill_light": "补光方案",
  "back_light": "背光/边缘光方案",
  
  "composition": "构图方式（黄金分割/对角线/引导线/对称/框架/三角形/留白）",
  "negative_space": "负空间处理（留白区域的位置与作用）",
  "color_script": "色彩脚本（该镜头的主色调及其叙事含义）",
  
  "visual_description": "画面核心描述（包含角色精确动作、表情、道具交互、特效元素）",
  "dialogue": "台词（无台词则填null）",
  "duration_seconds": "预估时长（动作戏2-4秒，文戏4-8秒）",
  "emotional_tone": "情绪基调",
  "rhythm_beat": "节奏节拍（该镜头在全片的节奏位置：起承转合）"
}

---

## 三、表演与动作指导（Performance Direction）

### 3.1 角色表演
{
  "acting": {
    "facial_expression": "面部表情细节（眼/眉/口/下颌的精确运动）",
    "eye_movement": "眼神方向与视线运动（注视/游离/闪烁/凝视）",
    "body_tension": "身体张力等级（1-10级：松弛→紧绷）",
    "gesture": "手势与肢体动作（精确描述手指/手臂/躯干的运动）",
    "micro_expression": "微表情（角色不经意流露的真实情绪，持续1/25秒）"
  }
}

### 3.2 动作节奏
{
  "movement_quality": "动作质感（流畅/顿挫/飘逸/沉重/迅猛）",
  "speed_variation": "速度变化（加速/减速/急停/缓动）",
  "anticipation": "预备动作（主要动作前的预示性动作）",
  "follow_through": "跟随动作（主要动作后的惯性延伸）"
}

---

## 四、声音与氛围（Audio & Atmosphere）

### 4.1 环境音
{
  "ambient_sound": "环境音（风/雨/火/机械/环境噪声）",
  "sfx": "音效重点（该镜头中最重要的音效元素）"
}

### 4.2 音乐
{
  "music_style": "配乐风格（管弦乐/电子/传统乐器/混合）",
  "tempo": "音乐节奏（对应镜头情绪变化）",
  "music_emotional": "音乐情绪（紧张/悲壮/宁静/激昂/神秘）"
}

### 4.3 台词表演
{
  "dialogue_delivery": "台词表演方式（语气/语速/停顿/重音）",
  "subtext": "潜台词（台词背后的真实含义与情绪）"
}

---

## 五、视觉特效（Visual Effects）

### 5.1 特效类型
{
  "vfx": {
    "primary": "主特效（核心视觉奇观，如：灵气爆发/法阵召唤/剑影冲天）",
    "secondary": "辅助特效（环境特效、粒子系统、光束、能量场）",
    "micro": "微观特效（飘动光粒、能量流动、符文闪烁）"
  }
}

### 5.2 特效控制
{
  "vfx_timing": "特效出现时间点（镜头开头/中间/结尾）",
  "vfx_color": "特效配色方案",
  "vfx_density": "特效密度与分布",
  "vfx_interaction": "特效与角色/场景的交互方式"
}

---

## 六、后期制作（Post-Production）

### 6.1 剪辑意图
{
  "transitions": "转场方式（硬切/淡入淡出/叠化/划像/匹配剪辑）",
  "montage_intent": "蒙太奇意图（平行叙事/隐喻/对比/积累）"
}

### 6.2 调色
{
  "color_grading": "调色风格（整体色相/饱和度/对比度/暗部细节）",
  "look_up_table": "预设风格参考（如：冷峻蓝调/暖金史诗/高饱和奇幻）"
}

---

## 七、输出格式要求

严格按照以下JSON格式输出：

{
  "project_title": "项目名称（根据内容自动生成）",
  "character_designs": { ... },
  "shots": [ ... ],
  "total_shots": "总镜头数",
  "total_duration": "预估总时长（秒）",
  "summary": {
    "core_theme": "故事核心主题",
    "visual_style": "整体视觉风格",
    "emotional_arc": "情感曲线"
  }
}

请确保每个镜头都包含上述所有相关字段，确保视觉描述的精确性和可执行性。
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

# ============================================================
# Kling API - 带详细错误日志
# ============================================================
def generate_video_task(kling_key, prompt, duration=5):
    """提交视频生成任务 - 显示详细错误"""
    
    url = "https://api-beijing.klingai.com/image-to-video/kling-3.0"
    headers = {
        "Authorization": f"Bearer {kling_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "type": "prompt",
                "text": f"{prompt}，3D动漫风格，电影级画质"
            },
            {
                "type": "first_frame",
                "url": "https://p2-kling.klingai.com/kcdn/cdn-kcdn112452/kling-tob-release_note/image_25.png"
            }
        ],
        "settings": {
            "resolution": "720p",
            "duration": duration,
            "audio": "off",
            "multi_shot": False
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        # 显示完整响应在界面上
        st.code(json.dumps(result, ensure_ascii=False, indent=2), language="json")
        
        if result.get("code") == 0:
            task_id = result.get("data", {}).get("id")
            if task_id:
                return task_id
            else:
                st.error(f"❌ 响应中没有任务ID: {result}")
                return None
        else:
            st.error(f"❌ Kling API错误 (code: {result.get('code')}): {result.get('message', '未知错误')}")
            return None
    except Exception as e:
        st.error(f"❌ 网络请求异常: {e}")
        return None

def poll_video_status(kling_key, task_id):
    """查询任务状态"""
    url = f"https://api-beijing.klingai.com/image-to-video/kling-3.0/{task_id}"
    headers = {"Authorization": f"Bearer {kling_key}"}
    
    for i in range(40):
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
                    return None
                elif status == "failed":
                    st.error(f"❌ 生成失败: {data.get('fail_reason', '未知')}")
                    return None
                else:
                    st.info(f"⏳ 生成中... ({status})")
                    time.sleep(5)
            else:
                st.warning(f"⚠️ 查询响应异常: {result}")
                time.sleep(3)
        except Exception as e:
            st.warning(f"⚠️ 查询请求异常: {e}")
            time.sleep(3)
    
    st.error("⏰ 超时，请在Kling控制台查看任务状态")
    return None

def render_character_designs(characters):
    if not characters:
        return
    st.markdown("### 🎨 角色三视图设定")
    for name, design in characters.items():
        with st.expander(f"▶ {name} - {design.get('character_type', '')} · {design.get('age_range', '')}", expanded=True):
            cols = st.columns(3)
            with cols[0]:
                st.markdown("**正面视图**")
                front = design.get('三视图_正面', {})
                st.caption(f"面部：{front.get('face', '')[:80]}...")
                st.caption(f"服装：{front.get('costume_front', '')[:80]}...")
            with cols[1]:
                st.markdown("**侧面视图**")
                side = design.get('三视图_侧面', {})
                st.caption(f"轮廓：{side.get('profile', '')[:80]}...")
                st.caption(f"服装：{side.get('costume_side', '')[:80]}...")
            with cols[2]:
                st.markdown("**背面视图**")
                back = design.get('三视图_背面', {})
                st.caption(f"轮廓：{back.get('back_profile', '')[:80]}...")
                st.caption(f"服装：{back.get('costume_back', '')[:80]}...")
            st.markdown(f"**🎨 色彩方案**：{design.get('color_palette', '')}")
            st.markdown(f"**⚡ 独特标志**：{design.get('distinctive_features', '')}")
            st.markdown(f"**🎭 角色弧光**：{design.get('character_arc', '')}")
            st.markdown(f"**💪 核心动机**：{design.get('core_motivation', '')}")

def render_shot(shot):
    st.markdown(f"""
    <div class="shot-card">
        <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
            <span style="color: #00d4ff; font-weight: 700; font-size: 1.2rem;">#{shot.get('shot_number')}</span>
            <span style="color: rgba(255,255,255,0.4); font-size: 0.7rem; background: rgba(255,255,255,0.05); padding: 2px 12px; border-radius: 12px;">
                {shot.get('shot_type')}
            </span>
            <span style="color: rgba(255,255,255,0.3); font-size: 0.7rem;">
                {shot.get('duration_seconds')}s · {shot.get('camera_angle')} · {shot.get('camera_movement')}
            </span>
            <span style="margin-left: auto; color: rgba(255,255,255,0.2); font-size: 0.6rem; letter-spacing: 1px;">
                {shot.get('emotional_tone')}
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    col_scene, col_time = st.columns(2)
    with col_scene:
        st.markdown(f"**🏔️ 场景**：{shot.get('scene_name', '')}")
    with col_time:
        st.markdown(f"**⏰ 时间**：{shot.get('scene_time', '')} · {shot.get('scene_weather', '')}")
    
    st.markdown("#### 📷 摄影参数")
    col_cam1, col_cam2, col_cam3 = st.columns(3)
    with col_cam1:
        st.caption("镜头类型")
        st.markdown(f"`{shot.get('lens_type', '')}`")
    with col_cam2:
        st.caption("景深控制")
        st.markdown(f"`{shot.get('depth_of_field', '')}`")
    with col_cam3:
        st.caption("构图方式")
        st.markdown(f"`{shot.get('composition', '')}`")
    
    st.markdown("#### 💡 灯光方案")
    col_light1, col_light2 = st.columns(2)
    with col_light1:
        st.caption("灯光风格")
        st.markdown(f"`{shot.get('lighting_style', '')}`")
    with col_light2:
        st.caption("光色温度")
        st.markdown(f"`{shot.get('lighting_color', '')}`")
    
    st.markdown("#### 🎬 画面描述")
    st.markdown(f"<div style='color:rgba(255,255,255,0.85);font-size:0.85rem;line-height:1.5;'>{shot.get('visual_description', '')}</div>", unsafe_allow_html=True)
    
    if shot.get('dialogue'):
        st.markdown(f"#### 💬 台词\n> \"{shot.get('dialogue')}\"")
    
    acting = shot.get('acting', {})
    if acting:
        st.markdown("#### 🎭 表演指导")
        cols_act = st.columns(4)
        with cols_act[0]:
            st.caption("面部表情")
            st.text(acting.get('facial_expression', '')[:40])
        with cols_act[1]:
            st.caption("眼神方向")
            st.text(acting.get('eye_movement', '')[:40])
        with cols_act[2]:
            st.caption("身体张力")
            st.text(acting.get('body_tension', ''))
        with cols_act[3]:
            st.caption("手势动作")
            st.text(acting.get('gesture', '')[:40])
    
    vfx = shot.get('vfx', {})
    if vfx:
        st.markdown("#### ✨ 视觉特效")
        cols_vfx = st.columns(3)
        with cols_vfx[0]:
            st.caption("主特效")
            st.text(vfx.get('primary', '')[:40])
        with cols_vfx[1]:
            st.caption("辅助特效")
            st.text(vfx.get('secondary', '')[:40])
        with cols_vfx[2]:
            st.caption("特效配色")
            st.text(vfx.get('color', '')[:40])
    
    st.markdown("</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎬 分镜生成", "🎥 视频生成"])

with tab1:
    col_input, col_output = st.columns([1, 1])
    with col_input:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        article_content = st.text_area("📝 输入文章", height=350, placeholder="粘贴你的故事、剧本或文章...", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        generate_btn = st.button("⚡ 生成精细化分镜", disabled=not (deepseek_key and article_content))
    with col_output:
        if generate_btn and deepseek_key and article_content:
            try:
                with st.spinner("🧠 AI导演正在构思精细化分镜..."):
                    result = generate_storyboard(deepseek_key, article_content)
                st.success("✅ 精细化分镜生成完成！")
                shots = result.get("shots", [])
                characters = result.get("character_designs", {})
                c1, c2, c3 = st.columns(3)
                c1.markdown(f'<div style="text-align:center;"><div class="stat-number">{len(shots)}</div><div style="color:rgba(255,255,255,0.3);">分镜镜头</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div style="text-align:center;"><div class="stat-number">{len(characters)}</div><div style="color:rgba(255,255,255,0.3);">角色设定</div></div>', unsafe_allow_html=True)
                c3.markdown(f'<div style="text-align:center;"><div class="stat-number">{sum(s.get("duration_seconds",0) for s in shots)}s</div><div style="color:rgba(255,255,255,0.3);">预估总时长</div></div>', unsafe_allow_html=True)
                if characters:
                    st.markdown("---")
                    render_character_designs(characters)
                if shots:
                    st.markdown("---")
                    st.markdown("### 🎬 精细化分镜脚本")
                    for shot in shots:
                        render_shot(shot)
                        st.markdown("---")
                st.download_button(
                    label="📥 下载完整分镜数据 (JSON)",
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
                shot_options.append(f"镜头 {num}: {desc}...")
            selected = st.multiselect("选择要生成视频的镜头", options=shot_options, default=[shot_options[0]] if shot_options else [])
            if not kling_key:
                st.warning("⚠️ 请在左侧输入 Kling AI API Key")
            elif not selected:
                st.info("📌 请选择至少一个镜头")
            else:
                if st.button("🎬 生成选中视频"):
                    for sel in selected:
                        parts = sel.split(":")
                        if len(parts) >= 2:
                            idx_str = parts[0].replace("镜头 ", "").strip()
                            try:
                                idx = int(idx_str) - 1
                                if 0 <= idx < len(shots):
                                    shot = shots[idx]
                                    desc = shot.get('visual_description', '')
                                    duration = shot.get('duration_seconds', 5)
                                    st.info(f"📤 正在提交镜头 {idx+1}...")
                                    task_id = generate_video_task(kling_key, desc, duration)
                                    if task_id:
                                        st.success(f"✅ 镜头 {idx+1} 已提交，任务ID: {task_id}")
                                        with st.spinner(f"⏳ 镜头 {idx+1} 生成中..."):
                                            video_url = poll_video_status(kling_key, task_id)
                                            if video_url:
                                                st.success(f"✅ 镜头 {idx+1} 成功!")
                                                st.video(video_url)
                                            else:
                                                st.error(f"❌ 镜头 {idx+1} 生成失败")
                                    else:
                                        st.error(f"❌ 镜头 {idx+1} 提交失败")
                            except Exception as e:
                                st.error(f"❌ 处理异常: {e}")

st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; color: rgba(255,255,255,0.12); font-size: 0.6rem; letter-spacing: 1px; padding: 8px 0;">
    <span>⚡ NEON STUDIO · AI动漫制作系统 v2.0</span>
    <span>DeepSeek + Kling AI · 3D国漫专业版</span>
</div>
""", unsafe_allow_html=True)
