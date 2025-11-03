import gradio as gr
import json
import os
from typing import List
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import re

# 从环境变量读取API配置（更安全）
API_KEY = "ms-b064f11b-4b11-4ae0-a00e-ff98a69c9bd3"
BASE_URL = "https://api-inference.modelscope.cn/v1/"
MODEL_NAME = "deepseek-ai/DeepSeek-V3.2-Exp"

def init_openai_client():
    """初始化OpenAI客户端"""
    if not API_KEY:
        raise ValueError("请设置 MODELSCOPE_API_KEY 环境变量")
    return OpenAI(base_url=BASE_URL, api_key=API_KEY)

def clean_response(text):
    """清理响应文本，移除思考过程标记"""
    if not text:
        return ""
    # 移除 <thinking>...</thinking> 标签及内容
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
    # 移除其他可能的思考过程标记
    text = re.sub(r'\[?思考过程\]?:.*?(?=\n\n|\n【|\n=)', '', text, flags=re.DOTALL)
    # 清理多余的空行
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def validate_inputs(**kwargs):
    """验证输入参数"""
    for key, value in kwargs.items():
        if not value or str(value).strip() == "":
            return False, f"缺少必要参数: {key}"
    return True, ""

def generate_destination_recommendation(season, health_condition, budget, interests):
    """生成目的地推荐"""
    # 将兴趣列表转换为字符串
    if isinstance(interests, list):
        interests_str = "、".join(interests)
    else:
        interests_str = str(interests)

    # 验证输入
    is_valid, msg = validate_inputs(
        season=season, health_condition=health_condition,
        budget=budget, interests=interests_str
    )
    if not is_valid:
        return msg

    client = init_openai_client()
    system_prompt = """你是一个专业的老年旅行规划师。根据用户的季节、健康状况、预算和兴趣，推荐3-5个国内外热门适老目的地。

每个推荐应包括：
- 目的地名称
- 推荐理由（重点考虑避寒、康养、舒适度）
- 最佳旅行时长
- 注意事项（包括健康和安全建议）
- 舒适版活动示例

请用通俗易懂、温馨友好的语言回复，避免过于专业的术语。"""

    user_prompt = f"季节：{season}，健康状况：{health_condition}，预算：{budget}，兴趣偏好：{interests_str}"

    result = ""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True,
            temperature=0.7,
            max_tokens=1500
        )
        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk
        result = clean_response(result)

        # 如果结果为空，返回友好提示
        if not result.strip():
            result = "抱歉，暂时无法生成推荐，请稍后再试或检查网络连接。"

    except Exception as e:
        result = f"[错误] 生成推荐时出错：{str(e)}\n\n请检查：\n1. API密钥是否正确\n2. 网络连接是否正常\n3. API服务是否可用"

    return result

def generate_itinerary_plan(destination, duration, mobility, health_focus):
    """生成行程规划"""
    # 将健康关注点列表转换为字符串
    if isinstance(health_focus, list):
        health_focus_str = "、".join(health_focus)
    else:
        health_focus_str = str(health_focus)

    is_valid, msg = validate_inputs(destination=destination, duration=duration)
    if not is_valid:
        return msg

    client = init_openai_client()
    system_prompt = """你是一个经验丰富的老年旅行行程规划师。请为老年人制定舒缓、贴心的日行程安排。

要求：
- 每天安排半日活动、半日休息
- 避免高强度行程
- 包含健康提示和注意事项
- 提供备用方案（雨天等）
- 语言亲切温和"""

    user_prompt = f"""目的地：{destination}
旅行时长：{duration}
行动能力：{mobility}
健康关注点：{health_focus_str}"""

    result = ""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True,
            temperature=0.7,
            max_tokens=1500
        )
        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk
        result = clean_response(result)

        if not result.strip():
            result = "抱歉，暂时无法生成行程，请稍后再试。"

    except Exception as e:
        result = f"[错误] 生成行程时出错：{str(e)}"

    return result

def generate_checklist(destination, duration, special_needs):
    """生成旅行清单（结构化数据）"""
    # 生成唯一ID用于保存
    import time
    import json
    checklist_id = f"{destination}_{duration}_{int(time.time())}"

    is_valid, msg = validate_inputs(destination=destination, duration=duration)
    if not is_valid:
        return msg

    client = init_openai_client()
    system_prompt = """你是一个专业的老年旅行助手。请为老年人制定详细的行前准备清单，包含交通、酒店、景点预订指引。

请以JSON格式返回，包含以下结构：
{
  "checklist": [
    {
      "category": "证件类",
      "items": [
        {"name": "物品名称", "required": true, "note": "备注说明"}
      ]
    }
  ],
  "booking_guides": {
    "transport": {
      "guide": "交通预订指引文字",
      "platforms": ["推荐平台1", "推荐平台2"]
    },
    "hotel": {
      "guide": "酒店预订指引文字",
      "platforms": ["推荐平台1", "推荐平台2"]
    },
    "attractions": {
      "guide": "景点预订指引文字",
      "platforms": ["推荐平台1", "推荐平台2"]
    }
  },
  "tips": ["温馨提示1", "温馨提示2"]
}

清单类别应包括：证件类、药品类、衣物类、电子设备、日用品等。
每个类别列出具体物品，标注【必带】(required: true)和【可选】(required: false)。
交通、酒店、景点指引要详细具体，包含预订流程和推荐平台。
只返回JSON，不要其他文字。"""

    user_prompt = f"目的地：{destination}，旅行时长：{duration}，特殊需求：{special_needs}"

    result = ""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True,
            temperature=0.6,
            max_tokens=2000
        )
        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk
        result = clean_response(result)

        if not result.strip():
            result = "抱歉，暂时无法生成清单，请稍后再试。"
            return result

        # 尝试解析JSON
        try:
            import json
            # 提取JSON部分（处理可能的markdown代码块）
            json_match = None
            if "```json" in result:
                json_match = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                json_match = result.split("```")[1].split("```")[0].strip()
            else:
                json_match = result.strip()

            data = json.loads(json_match)

            # 保存到本地
            save_checklist_data(checklist_id, destination, duration, data)

            # 格式化为可读文本
            formatted_result = format_checklist_output(checklist_id, destination, duration, data)
            return formatted_result

        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            return f"⚠️ 数据解析异常，请检查返回格式。\n\n原始结果：\n{result}"

    except Exception as e:
        result = f"[错误] 生成清单时出错：{str(e)}"
        return result

    return result

def save_checklist_data(checklist_id, destination, duration, data):
    """保存清单数据到本地JSON文件"""
    import json
    import os
    from datetime import datetime

    # 创建保存目录
    save_dir = "checklist_data"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 准备保存的数据
    save_data = {
        "id": checklist_id,
        "destination": destination,
        "duration": duration,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": data
    }

    # 保存到文件
    file_path = os.path.join(save_dir, f"{checklist_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

def format_checklist_output(checklist_id, destination, duration, data):
    """格式化清单输出为可读文本（带checkbox）"""
    # 首先尝试加载之前的勾选状态
    import json
    import os
    save_dir = "checklist_data"
    checked_file = os.path.join(save_dir, f"{checklist_id}_checked.json")
    checked_items = []

    if os.path.exists(checked_file):
        try:
            with open(checked_file, 'r', encoding='utf-8') as f:
                checked_data = json.load(f)
                checked_items = checked_data.get("checked", [])
        except:
            pass

    # 构建HTML输出
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 100%;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="margin: 0; font-size: 24px;">📋 旅行清单 - {destination} ({duration})</h2>
            <p style="margin: 10px 0 0 0; font-size: 14px;">ID: {checklist_id}</p>
        </div>

        <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 10px 0; color: #2e7d32;">📦 行前准备清单</h3>
            <p style="margin: 0; color: #558b2f; font-size: 13px;">💡 提示：勾选框会保存在本地，下次进入时自动恢复勾选状态</p>
            <div id="progress_bar_{checklist_id}" style="display: none; margin-top: 15px;">
                <div style="background: #e0e0e0; height: 30px; border-radius: 15px; overflow: hidden;">
                    <div id="progress_fill_{checklist_id}" style="background: linear-gradient(90deg, #4caf50, #66bb6a); height: 100%; width: 0%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; transition: width 0.3s;">0 / 0 (0%)</div>
                </div>
            </div>
        </div>
    """

    # 生成每个类别的清单
    item_counter = 0
    for category in data.get("checklist", []):
        category_name = category.get("category", "")
        items = category.get("items", [])
        html += f"""
        <div style="margin-bottom: 25px; border: 2px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
            <div style="background: #f5f5f5; padding: 12px 15px; font-weight: bold; font-size: 16px; border-bottom: 1px solid #e0e0e0;">
                🔹 {category_name}
            </div>
            <div style="padding: 15px; background: white;">
        """

        for item in items:
            name = item.get("name", "")
            required = item.get("required", False)
            note = item.get("note", "")
            required_text = "【必带】" if required else "【可选】"
            item_id = f"{checklist_id}_{item_counter}"

            # 检查是否已勾选
            is_checked = item_id in checked_items
            checkbox_checked = 'checked' if is_checked else ''

            html += f"""
                <div style="display: flex; align-items: flex-start; margin-bottom: 12px; padding: 8px; border-radius: 6px; transition: background 0.2s;" onmouseover="this.style.background='#f9f9f9'" onmouseout="this.style.background='transparent'">
                    <input type="checkbox" id="{item_id}" {checkbox_checked} onchange="saveCheckStatus('{checklist_id}', '{item_id}', this.checked)" style="width: 20px; height: 20px; margin-right: 12px; margin-top: 2px; cursor: pointer;">
                    <label for="{item_id}" style="cursor: pointer; flex: 1; {('font-weight: bold;' if required else '') if required_text == '【必带】' else ''}">
                        <span style="color: {'#d32f2f' if required else '#757575'}; font-size: 12px; font-weight: bold;">{required_text}</span>
                        <span style="color: #333; margin-left: 8px;">{name}</span>
                        {f'<br><span style="color: #666; font-size: 13px; margin-left: 33px;">💡 {note}</span>' if note else ''}
                    </label>
                </div>
            """
            item_counter += 1

        html += """
            </div>
        </div>
        """

    # 预订指引部分（纯文本）
    html += """
        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 10px 0; color: #1565c0;">🎫 预订指引</h3>
        </div>
    """

    booking_guides = data.get("booking_guides", {})
    if booking_guides:
        # 交通指引
        if "transport" in booking_guides:
            html += f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #2196f3; background: #f5f5f5;">
                <h4 style="margin: 0 0 10px 0; color: #1976d2;">✈️ 交通预订</h4>
                <p style="margin: 0; color: #555; line-height: 1.6;">{booking_guides['transport'].get('guide', '')}</p>
            """
            platforms = booking_guides['transport'].get('platforms', [])
            if platforms:
                html += '<p style="margin: 10px 0 5px 0; color: #333; font-weight: bold;">推荐平台：</p><ul style="margin: 0; color: #555;">'
                for platform in platforms:
                    html += f'<li style="margin-bottom: 5px;">{platform}</li>'
                html += '</ul>'
            html += "</div>"

        # 酒店指引
        if "hotel" in booking_guides:
            html += f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #4caf50; background: #f5f5f5;">
                <h4 style="margin: 0 0 10px 0; color: #388e3c;">🏨 酒店预订</h4>
                <p style="margin: 0; color: #555; line-height: 1.6;">{booking_guides['hotel'].get('guide', '')}</p>
            """
            platforms = booking_guides['hotel'].get('platforms', [])
            if platforms:
                html += '<p style="margin: 10px 0 5px 0; color: #333; font-weight: bold;">推荐平台：</p><ul style="margin: 0; color: #555;">'
                for platform in platforms:
                    html += f'<li style="margin-bottom: 5px;">{platform}</li>'
                html += '</ul>'
            html += "</div>"

        # 景点指引
        if "attractions" in booking_guides:
            html += f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #ff9800; background: #f5f5f5;">
                <h4 style="margin: 0 0 10px 0; color: #f57c00;">🎯 景点预订</h4>
                <p style="margin: 0; color: #555; line-height: 1.6;">{booking_guides['attractions'].get('guide', '')}</p>
            """
            platforms = booking_guides['attractions'].get('platforms', [])
            if platforms:
                html += '<p style="margin: 10px 0 5px 0; color: #333; font-weight: bold;">推荐平台：</p><ul style="margin: 0; color: #555;">'
                for platform in platforms:
                    html += f'<li style="margin-bottom: 5px;">{platform}</li>'
                html += '</ul>'
            html += "</div>"

    # 温馨提示
    tips = data.get("tips", [])
    if tips:
        html += """
        <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 10px 0; color: #e65100;">💡 温馨提示</h3>
        """
        for tip in tips:
            html += f'<p style="margin: 8px 0; color: #555;">• {tip}</p>'
        html += "</div>"

    # 底部信息
    html += f"""
        <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; text-align: center; color: #666; font-size: 13px; margin-top: 20px;">
            <p style="margin: 5px 0;">💾 此清单已自动保存至本地（checklist_data目录）</p>
            <p style="margin: 5px 0; color: #2196f3; font-weight: bold;">勾选状态将自动保存到：checklist_data/{checklist_id}_checked.json</p>
        </div>
    </div>

    <script>
        // 从localStorage加载已保存的状态
        function loadCheckedItems(checklistId) {
            const checkedItems = JSON.parse(localStorage.getItem('checklist_' + checklistId) || '[]');
            checkedItems.forEach(function(itemId) {
                const checkbox = document.getElementById(itemId);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
            updateProgress(checklistId, checkedItems);
        }

        // 保存checkbox状态到localStorage
        function saveCheckStatus(checklistId, itemId, isChecked) {
            let checkedItems = JSON.parse(localStorage.getItem('checklist_' + checklistId) || '[]');

            if (isChecked && checkedItems.indexOf(itemId) === -1) {
                checkedItems.push(itemId);
            } else if (!isChecked) {
                checkedItems = checkedItems.filter(function(id) {
                    return id !== itemId;
                });
            }

            localStorage.setItem('checklist_' + checklistId, JSON.stringify(checkedItems));
            console.log('已保存勾选状态:', checkedItems);

            updateProgress(checklistId, checkedItems);
        }

        // 更新进度显示
        function updateProgress(checklistId, checkedItems) {
            const totalItems = document.querySelectorAll('input[type="checkbox"]').length;
            const progressBar = document.getElementById('progress_bar_' + checklistId);
            const progressFill = document.getElementById('progress_fill_' + checklistId);

            if (progressBar && progressFill && totalItems > 0) {
                const percentage = Math.round((checkedItems.length / totalItems) * 100);

                // 显示进度条
                progressBar.style.display = 'block';

                // 更新进度条宽度和文字
                progressFill.style.width = percentage + '%';
                progressFill.textContent = checkedItems.length + ' / ' + totalItems + ' (' + percentage + '%)';
            }
        }

        // 页面加载时恢复状态
        document.addEventListener('DOMContentLoaded', function() {
            loadCheckedItems('{checklist_id}');
        });
    </script>
    """

    return html

def load_checklist_history():
    """加载所有保存的清单历史记录"""
    import json
    import os

    history = []
    save_dir = "checklist_data"

    if not os.path.exists(save_dir):
        return []

    for filename in os.listdir(save_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(save_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    history.append({
                        "id": data.get("id", ""),
                        "destination": data.get("destination", ""),
                        "duration": data.get("duration", ""),
                        "timestamp": data.get("timestamp", ""),
                        "filename": filename
                    })
            except Exception as e:
                print(f"加载文件 {filename} 出错：{e}")

    # 按时间倒序排列
    history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return history

def delete_checklist_record(filename):
    """删除指定的清单记录"""
    import os

    save_dir = "checklist_data"
    file_path = os.path.join(save_dir, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def generate_travel_story(photos, custom_input):
    """生成旅行故事"""
    # Note: This function currently only uses text input, photos processing could be added later
    is_valid, msg = validate_inputs(custom_input=custom_input)
    if not is_valid:
        return "请先上传照片并填写补充信息"

    client = init_openai_client()
    system_prompt = """你是一个温暖的老年旅行故事讲述者。请根据照片和文字生成温馨、感人的旅行游记。

要求：
- 语言亲切温馨，充满正能量
- 重点描述旅行中的美好体验和感受
- 适当加入健康、舒适、康养相关的内容
- 篇幅适中，条理清晰"""

    user_prompt = f"用户补充信息：{custom_input}\n注意：照片功能暂未完全实现，请基于补充信息生成游记。"

    result = ""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True,
            temperature=0.8,
            max_tokens=1500
        )
        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk
        result = clean_response(result)

        if not result.strip():
            result = "抱歉，暂时无法生成游记，请再提供一些补充信息。"

    except Exception as e:
        result = f"[错误] 生成游记时出错：{str(e)}"

    return result

def create_app():
    """创建Gradio应用"""
    # 兴趣偏好选项
    interest_options = [
        "避寒康养", "海岛度假", "文化历史", "温泉养生", "自然风光",
        "美食体验", "摄影采风", "休闲购物", "传统建筑", "民俗体验",
        "慢节奏游", "海滨漫步", "茶文化", "寺庙祈福", "古镇风情",
        "田园风光", "动物观赏", "艺术展览", "传统戏曲", "手工体验",
        "健康养生", "中医理疗", "瑜伽冥想", "森林浴", "阳光浴"
    ]

    # 健康关注点选项
    health_focus_options = [
        "避免过度疲劳", "饮食清淡", "需要靠近医院", "避免高原地区",
        "需要无障碍设施", "避免长时间步行", "注意防晒", "避免潮湿环境",
        "需要安静环境", "控制血压", "控制血糖", "关注空气质量",
        "需要携带药物", "保护心脏", "保持关节灵活", "预防感冒",
        "避免拥挤", "需要良好睡眠", "避免剧烈运动", "注意保暖",
        "多喝水", "定期休息", "避免暴晒", "饮食规律", "适度活动"
    ]

    with gr.Blocks(
        title="🧳 银发族智能旅行助手",
        theme=gr.themes.Soft(primary_hue="purple", secondary_hue="cyan"),
        css="""
        .gr-button {font-size: 18px !important; padding: 12px 20px !important;}
        .gr-textbox input {font-size: 16px !important;}
        .gr-multiselect {min-height: 120px !important;}
        """
    ) as app:
        gr.HTML('''
        <h1 style="text-align:center; font-size:48px; margin-bottom:10px;">
            🧳 银发族智能旅行助手
        </h1>
        <p style="text-align:center; font-size:18px; color:#666; margin-bottom:30px;">
            专为中老年朋友设计的温暖贴心的旅行规划伙伴
        </p>
        ''')

        with gr.Tabs():
            # Tab 1: 智能推荐与规划
            with gr.Tab("🌍 智能推荐与规划"):
                with gr.Row():
                    with gr.Column(scale=1):
                        season = gr.Dropdown(
                            ["春季", "夏季", "秋季", "冬季"],
                            label="🌸 季节",
                            value="秋季",
                            info="选择您计划出行的季节"
                        )
                        health = gr.Dropdown(
                            ["身体健康", "有慢性病但控制良好", "行动不便但可独立出行"],
                            label="🏥 健康状况",
                            value="身体健康",
                            info="真实反映您的健康状况，便于推荐更合适的目的地"
                        )
                        budget = gr.Dropdown(
                            ["经济实惠", "舒适型", "豪华型"],
                            label="💰 预算范围",
                            value="舒适型",
                            info="选择您的预算档次"
                        )
                        interests = gr.CheckboxGroup(
                            choices=interest_options,
                            value=["避寒康养", "温泉养生"],
                            label="🎨 兴趣偏好",
                            info="可选择多个您感兴趣的主题"
                        )
                        btn1 = gr.Button("🔍 推荐目的地", variant="primary", size="lg")
                        output1 = gr.Textbox(
                            label="✨ 推荐结果",
                            lines=20,
                            max_lines=30,
                            info="系统将为您推荐3-5个适合的目的地"
                        )

                    with gr.Column(scale=1):
                        dest = gr.Textbox(
                            label="📍 目的地",
                            info="填写您想去或已选择的目的地"
                        )
                        dur = gr.Dropdown(
                            ["3-5天", "一周左右", "10-15天", "15天以上"],
                            label="⏰ 旅行时长",
                            value="一周左右"
                        )
                        mobility = gr.Dropdown(
                            ["行走自如", "需要少量休息", "需要轮椅辅助"],
                            label="🚶 行动能力",
                            value="行走自如"
                        )
                        health_focus = gr.CheckboxGroup(
                            choices=health_focus_options,
                            value=["避免过度疲劳", "饮食清淡", "定期休息"],
                            label="❤️ 健康关注点",
                            info="可选择多个您的健康关注点"
                        )
                        btn2 = gr.Button("📋 制定行程", variant="primary", size="lg")
                        output2 = gr.Textbox(
                            label="✨ 行程安排",
                            lines=20,
                            max_lines=30,
                            info="为您量身定制的舒缓行程安排"
                        )
                        btn3_origin = gr.Textbox(
                            label="🏠 出发地（继续生成清单用）",
                            value="",
                            info="填写您的出发城市，用于生成交通预订指引"
                        )
                        btn3 = gr.Button("🎁 继续生成清单", variant="secondary", size="lg")
                        output2_hint = gr.HTML(
                            value="""
                            <div style="padding:15px; background:#f0f8ff; border-radius:8px; margin-top:10px;">
                                <p style="color:#4169E1; font-size:14px; margin:0;">
                                    💡 提示：行程制定完成后，点击上方"🎁 继续生成清单"按钮，可直接为此行程生成专属清单！
                                </p>
                            </div>
                            """
                        )
                        output3 = gr.Textbox(
                            label="🎁 一键清单生成结果",
                            lines=20,
                            max_lines=30,
                            info="点击上方按钮生成清单，结果将显示在此处"
                        )

                btn1.click(
                    fn=generate_destination_recommendation,
                    inputs=[season, health, budget, interests],
                    outputs=[output1]
                )
                btn2.click(
                    fn=generate_itinerary_plan,
                    inputs=[dest, dur, mobility, health_focus],
                    outputs=[output2]
                )

                # "继续生成清单"按钮：使用当前行程页面的输入直接生成清单
                def continue_to_checklist(destination, duration, health_focus, origin):
                    # 将健康关注点转换为特殊需求描述
                    if isinstance(health_focus, list):
                        special_needs = "、".join(health_focus)
                    else:
                        special_needs = str(health_focus)

                    # 如果有出发地，添加到特殊需求中
                    if origin and origin.strip():
                        special_needs = f"出发地：{origin}。" + special_needs

                    return generate_checklist(destination, duration, special_needs)

                btn3.click(
                    fn=continue_to_checklist,
                    inputs=[dest, dur, health_focus, btn3_origin],
                    outputs=[output3]
                )

            # Tab 2: 清单与导游服务
            with gr.Tab("📝 清单与导游服务"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML('''
                        <div style="padding:15px; background:#fff3cd; border-radius:8px; margin-bottom:15px;">
                            <p style="color:#856404; font-size:14px; margin:0;">
                                💡 小贴士：刚从行程规划页面过来？您的目的地和时长信息已自动填充！如果需要修改，请直接编辑下方输入框。
                            </p>
                        </div>
                        ''')
                        checklist_origin = gr.Textbox(
                            label="🏠 出发地",
                            value="",
                            info="填写您的出发城市（例如：北京、上海、广州等）"
                        )
                        checklist_dest = gr.Textbox(
                            label="📍 目的地",
                            value="",
                            info="填写目的地（从行程规划页面过来时将自动填充）"
                        )
                        checklist_dur = gr.Dropdown(
                            ["3-5天", "一周左右", "10-15天", "15天以上"],
                            label="⏰ 旅行时长",
                            value="一周左右",
                            info="选择旅行时长"
                        )
                        checklist_needs = gr.Textbox(
                            label="⚕️ 特殊需求",
                            value="身体健康，常规旅行",
                            info="例如：高血压、糖尿病、需携带医疗器械等"
                        )
                        btn3 = gr.Button("📋 生成清单", variant="primary", size="lg")
                        output3_for_tab2 = gr.Textbox(
                            label="✨ 清单内容",
                            lines=20,
                            max_lines=30,
                            info="详细的行前准备清单，按类别分组"
                        )

                # 历史记录区域
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML('''
                        <div style="padding:15px; background:#e7f3ff; border-radius:8px; margin-top:20px; margin-bottom:15px;">
                            <p style="color:#0066cc; font-size:14px; margin:0; font-weight:bold;">
                                📚 历史记录 - 保存的清单
                            </p>
                        </div>
                        ''')
                        btn_refresh_history = gr.Button("🔄 刷新历史记录", variant="secondary", size="lg")
                        history_output = gr.Dropdown(
                            choices=[],
                            label="📜 选择历史记录",
                            info="选择一个已保存的清单记录查看"
                        )
                        btn_load_history = gr.Button("📖 加载选中记录", variant="secondary", size="lg")
                        btn_delete_history = gr.Button("🗑️ 删除选中记录", variant="stop", size="lg")
                        history_detail = gr.Textbox(
                            label="📄 记录详情",
                            lines=20,
                            max_lines=30,
                            info="选择历史记录后将显示在此处"
                        )

                # 事件绑定
                btn3.click(
                    fn=generate_checklist,
                    inputs=[checklist_dest, checklist_dur, checklist_needs],
                    outputs=[output3_for_tab2]
                )

                # 历史记录事件
                def refresh_history():
                    history = load_checklist_history()
                    choices = [(f"{h['destination']} ({h['duration']}) - {h['timestamp']}", h['filename']) for h in history]
                    return gr.Dropdown.update(choices=choices, value=None)

                btn_refresh_history.click(
                    fn=refresh_history,
                    outputs=[history_output]
                )

                def load_history_record(filename):
                    if not filename:
                        return "请先选择一条历史记录"
                    import json
                    import os

                    save_dir = "checklist_data"
                    file_path = os.path.join(save_dir, filename)

                    if not os.path.exists(file_path):
                        return "记录不存在或已被删除"

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # 重新格式化显示
                        checklist_data = data.get("data", {})
                        result = format_checklist_output(
                            data.get("id", ""),
                            data.get("destination", ""),
                            data.get("duration", ""),
                            checklist_data
                        )
                        return result
                    except Exception as e:
                        return f"加载记录时出错：{str(e)}"

                btn_load_history.click(
                    fn=load_history_record,
                    inputs=[history_output],
                    outputs=[history_detail]
                )

                def delete_history_record(filename):
                    if not filename:
                        return "请先选择一条历史记录", None

                    if delete_checklist_record(filename):
                        return f"✅ 已删除记录：{filename}", None
                    else:
                        return f"❌ 删除失败：记录不存在", filename

                btn_delete_history.click(
                    fn=delete_history_record,
                    inputs=[history_output],
                    outputs=[history_detail, history_output]
                )

            # Tab 3: 旅行游记生成
            with gr.Tab("🎬 旅行游记生成"):
                with gr.Row():
                    with gr.Column(scale=1):
                        photos = gr.File(
                            file_count="multiple",
                            file_types=["image"],
                            label="📷 上传旅行照片"
                        )
                        story_input = gr.Textbox(
                            label="✍️ 补充信息",
                            lines=8,
                            info="描述您的旅行感受、希望突出的内容等"
                        )
                        btn4 = gr.Button("✨ 生成游记", variant="primary", size="lg")
                        output4 = gr.Textbox(
                            label="✨ 游记内容",
                            lines=20,
                            max_lines=30,
                            info="根据您的照片和描述生成的温馨游记"
                        )

                btn4.click(
                    fn=generate_travel_story,
                    inputs=[photos, story_input],
                    outputs=[output4]
                )

        # 添加底部说明
        gr.HTML('''
        <div style="text-align:center; margin-top:30px; padding:20px; background:#f5f5f5; border-radius:10px;">
            <p style="color:#666; font-size:14px;">
                💡 温馨提示：此应用为AI生成内容，仅供参考。具体行程请结合自身实际情况调整。<br/>
                🏥 建议出行前咨询医生，携带必要药品，关注目的地医疗资源。
            </p>
        </div>
        ''')

    return app

if __name__ == "__main__":
    print("正在启动银发族智能旅行助手...")
    print("请在浏览器中访问: http://localhost:7860")
    print("按 Ctrl+C 停止服务")
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        inbrowser=True,
        share=False,
        show_error=True
    )
