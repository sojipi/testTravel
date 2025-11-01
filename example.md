对应需求描述示例
1、整体需求描述：
基于gradio做一个应用：用户输入公众号文章内容后，点击一键生成按钮，自动生成标题、摘要内容和一个基于摘要英文promp生成的文章配图。

2、前端核心模块，依次运行
用户输入框：提醒用户输入公众号文章内容；
1）标题输出框：根据用户输入自动生成5个适合公众号的标题，64字内；展示思考过程，思考输出和最终标题输出用两个独立框，左右布局；流式输出并多行完整展示；
2）摘要输出框：根据用户输入自动生成适合公众号的摘要，120字内；展示思考过程，思考输出和最终摘要输出用两个独立框，左右布局；流式输出并多行完整展示；
3）文章配图prompt输出框：根据摘要内容自动生成英文prompt，用于文生图；展示思考过程，思考输出和最终promp输出用两个独立框，左右布局；流式输出并多行完整展示；
注意：最终promp输出框只输出用于文生图的英文prompt，简洁有效；
promp输出框可编辑，然后可点击重新生成按钮即可重新生成图片；
4）文章配图输出框：根据生成的英文prompt或者编辑的英文prompt，生成适合的配图；生成2张图，尺寸都为1024x500
整体视觉风格：青色+紫色风格的科技风

3、服务端API
1）标题输出、摘要输出、prompt输出均调用以下API，格式如下，请严格遵守
from openai import OpenAI

client = OpenAI(
    base_url='https://api-inference.modelscope.cn/v1/',
    api_key='换成你的魔搭token', # ModelScope Token
)

response = client.chat.completions.create(
    model='deepseek-ai/DeepSeek-R1', # ModelScope Model-Id
    messages=[
        {
            'role': 'system',
            'content': 'You are a helpful assistant.'
        },
        {
            'role': 'user',
            'content': '你好'
        }
    ],
    stream=True
)
done_reasoning = False
for chunk in response:
    reasoning_chunk = chunk.choices[0].delta.reasoning_content
    answer_chunk = chunk.choices[0].delta.content
    if reasoning_chunk != '':
        print(reasoning_chunk, end='',flush=True)
    elif answer_chunk != '':
        if not done_reasoning:
            print('\n\n === Final Answer ===\n')
            done_reasoning = True
        print(answer_chunk, end='',flush=True)
2）文章配图调用API：
import requests
import json
from PIL import Image
from io import BytesIO

url = 'https://api-inference.modelscope.cn/v1/images/generations'

payload = {
    'model': 'djyzcp123/gjerc',#ModelScope Model-Id,required
    'prompt': 'A golden cat'# required
}
headers = {
    'Authorization': 'Bearer 换成你的魔搭token',
    'Content-Type': 'application/json'
}

response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), headers=headers)

response_data = response.json()
image = Image.open(BytesIO(requests.get(response_data['images'][0]['url']).content))
image.save('result_image.jpg')