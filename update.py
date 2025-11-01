import re

# Read the original file
with open('travel_assistant.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# New simplified version of functions
new_functions = {}

new_functions['generate_destination_recommendation'] = '''def generate_destination_recommendation(
    season: str,
    health_condition: str,
    budget: str,
    interests: str
) -> str:
    """生成目的地推荐"""
    client = init_openai_client()

    system_prompt = """你是一个专业的老年旅行规划师，专门为55岁以上的老年人推荐合适的旅行目的地。
请根据用户的季节、健康状况、预算和兴趣，推荐3-5个国内外热门适老目的地。
每个推荐应包括：
1. 目的地名称
2. 推荐理由（气候舒适、无障碍设施完善、医疗条件好等）
3. 最佳旅行时长
4. 注意事项

请用通俗易懂的语言回复，避免使用过于专业的术语。"""

    user_prompt = f"""
请为我推荐旅行目的地：
- 季节：{season}
- 健康状况：{health_condition}
- 预算：{budget}
- 兴趣偏好：{interests}

请推荐3-5个目的地，每个推荐包含详细信息。"""

    result = ""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True
        )

        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk

    except Exception as e:
        result = f"[错误] 生成推荐时出错：{str(e)}\n\n请检查API配置或网络连接。\n\n季节：{season}\n健康状况：{health_condition}\n预算：{budget}\n兴趣：{interests}"

    return result
'''

new_functions['generate_itinerary_plan'] = '''def generate_itinerary_plan(
    destination: str,
    duration: str,
    mobility: str,
    health_focus: str
) -> str:
    """生成详细行程规划"""
    client = init_openai_client()

    system_prompt = """你是一个经验丰富的老年旅行行程规划师。
请为老年人制定舒缓、贴心的日行程安排，特别注意：
1. 节奏舒缓，每天不超过2-3个主要活动
2. 包含无障碍设施信息
3. 标注附近的医院或药店位置
4. 预留充足的休息时间
5. 考虑老年人作息习惯（早起、午休）

用通俗易懂的语言描述，避免过于紧凑的行程。"""

    user_prompt = f"""
请为以下目的地制定{duration}的详细行程：
- 目的地：{destination}
- 行动能力：{mobility}
- 健康关注点：{health_focus}

请按天制定行程，每天包含：时间安排、活动内容、交通方式、住宿推荐、注意事项。"""

    result = ""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True
        )

        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk

    except Exception as e:
        result = f"[错误] 生成行程时出错：{str(e)}\n\n请检查API配置或网络连接。\n\n目的地：{destination}\n旅行时长：{duration}\n行动能力：{mobility}\n健康关注：{health_focus}"

    return result
'''

new_functions['generate_checklist'] = '''def generate_checklist(destination: str, duration: str, special_needs: str) -> str:
    """生成行前检查清单"""
    client = init_openai_client()

    system_prompt = """你是一个细心的老年旅行助手。
请为老年人制定详细的行前准备清单，包括：

必带物品：
- 证件类（身份证、医保卡、老年证等）
- 药品类（常用药、急救药、处方药等）
- 衣物类（根据目的地的气候准备）
- 用品类（老花镜、助听器、拐杖、雨伞等）

可选物品：
- 娱乐用品（书籍、相机、象棋等）
- 保健用品（血压计、血糖仪、按摩器等）

请用大字体、清晰的格式展示，方便老年人阅读和勾选。"""

    user_prompt = f"""
请为以下旅行准备行前清单：
- 目的地：{destination}
- 旅行时长：{duration}
- 特殊需求：{special_needs}

请按类别分组，并标注哪些是必需品，哪些是可选的。"""

    result = ""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True
        )

        for chunk in response:
            answer_chunk = chunk.choices[0].delta.content
            if answer_chunk:
                result += answer_chunk

    except Exception as e:
        result = f"[错误] 生成清单时出错：{str(e)}\n\n请检查API配置或网络连接。\n\n目的地：{destination}\n旅行时长：{duration}\n特殊需求：{special_needs}"

    return result
'''

# Process line by line
output_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if we're at the start of one of the functions to replace
    replaced = False
    for func_name in new_functions:
        if line.strip().startswith(f'def {func_name}('):
            # Replace this function
            output_lines.append(new_functions[func_name] + '\n')
            
            # Skip until we find the next function or the end of this function
            # Find the next function definition at the same indentation level
            indent_level = len(line) - len(line.lstrip())
            i += 1
            while i < len(lines):
                next_line = lines[i]
                # Check if this is a function definition at the same or higher level
                if next_line.strip() and not next_line.strip().startswith('#'):
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent_level and next_line.strip().startswith('def '):
                        break
                i += 1
            i -= 1  # Back up one because we'll increment at the end of loop
            replaced = True
            break
    
    if not replaced:
        output_lines.append(line)
    
    i += 1

# Write the result
with open('travel_assistant.py', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print("File updated successfully!")
