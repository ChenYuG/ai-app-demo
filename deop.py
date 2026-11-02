from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# 使用环境变量读取 Key（如果你没设置环境变量，直接在这里写死也可以）
api_key = os.getenv("DEEPSEEK_API_KEY") 

client = OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com"
)

class ChatRequest(BaseModel):
    question: str

# 核心变化：这里定义了一个“生成器”函数
def generate_stream(user_question: str):
    # 1. 开启 stream=True
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": user_question}],
        stream=True  # 关键参数：告诉大模型别憋着，一点一点吐
    )
    
    # 2. 遍历大模型吐出来的每一小块数据
    for chunk in response:
        # 提取这一小块里的文字
        content = chunk.choices[0].delta.content
        if content is not None:
            # 3. 每次拿到一点文字，就 yield（交出）给前端
            yield content

# 接口返回类型改成 StreamingResponse
@app.post("/chat")
def chat_with_ai(request: ChatRequest):
    # 直接把生成器函数交给 StreamingResponse
    return StreamingResponse(
        generate_stream(request.question), 
        media_type="text/event-stream" # 告诉浏览器这是流式文本
    )