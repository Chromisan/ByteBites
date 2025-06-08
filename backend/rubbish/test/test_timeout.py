"""
用于测试和检查 chatbot.py 中的超时问题
"""
import os
import time
import json
from dotenv import load_dotenv
import openai
from openai import ChatCompletion

def test_direct_api_call():
    """直接测试 DeepSeek API 的连接和响应情况"""
    print("===== 测试 DeepSeek API 直接调用 =====")
    
    # 加载环境变量
    load_dotenv()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model_name = os.environ.get("DEEPSEEK_MODEL_V3", "deepseek-chat")
    
    if not api_key:
        print("错误: 未设置 DEEPSEEK_API_KEY 环境变量")
        return
    
    print(f"使用基础 URL: {base_url}")
    print(f"使用模型: {model_name}")
    
    # 创建 OpenAI 客户端
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    # 简短的测试消息
    messages = [
        {"role": "system", "content": "你是一个简短的回答助手。请简明扼要地回答问题，不要超过50个字。"},
        {"role": "user", "content": "你好，请介绍一下自己。"}
    ]
    
    try:
        print("\n发送请求...")
        start_time = time.time()
        
        # 发送请求，使用较短的超时时间
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=100,  # 限制生成的标记数量
            temperature=0.7,
            timeout=30  # 30秒超时
        )
        
        duration = time.time() - start_time
        print(f"请求完成，耗时: {duration:.2f}秒")
        
        print("\n响应内容:")
        print(response.choices[0].message.content)
        
    except openai.APITimeoutError as e:
        print(f"\n超时错误: {e}")
        print(f"超时时间: {e.timeout if hasattr(e, 'timeout') else '未知'}")
        if hasattr(e, 'request'):
            print(f"请求信息: {e.request}")
    except Exception as e:
        print(f"\n其他错误: {e}")
        
    print("\n===== 测试完成 =====")

def test_streaming_api():
    """测试流式 API 调用，这可能比非流式调用更快地开始返回内容"""
    print("===== 测试 DeepSeek API 流式调用 =====")
    
    # 加载环境变量
    load_dotenv()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model_name = os.environ.get("DEEPSEEK_MODEL_V3", "deepseek-chat")
    
    if not api_key:
        print("错误: 未设置 DEEPSEEK_API_KEY 环境变量")
        return
    
    # 创建 OpenAI 客户端
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    # 简短的测试消息
    messages = [
        {"role": "system", "content": "你是一个简短的回答助手。请简明扼要地回答问题，不要超过50个字。"},
        {"role": "user", "content": "你好，请介绍一下自己。"}
    ]
    
    try:
        print("\n发送流式请求...")
        start_time = time.time()
        
        # 发送流式请求
        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=100,
            temperature=0.7,
            stream=True,  # 启用流式传输
            timeout=30  # 30秒超时
        )
        
        # 收集所有响应片段
        collected_content = ""
        first_chunk_time = None
        
        for chunk in stream:
            # 记录接收到第一个块的时间
            if first_chunk_time is None:
                first_chunk_time = time.time()
                print(f"接收到第一个响应块，耗时: {first_chunk_time - start_time:.2f}秒")
            
            # 从块中提取内容
            content = chunk.choices[0].delta.content or ""
            collected_content += content
            print(content, end="", flush=True)
        
        print()  # 换行
        
        total_duration = time.time() - start_time
        print(f"\n请求完成，总耗时: {total_duration:.2f}秒")
        if first_chunk_time:
            print(f"完整响应接收时间: {time.time() - first_chunk_time:.2f}秒")
        
    except openai.APITimeoutError as e:
        print(f"\n超时错误: {e}")
    except Exception as e:
        print(f"\n其他错误: {e}")
        
    print("\n===== 测试完成 =====")

if __name__ == "__main__":
    print("DeepSeek API 测试工具")
    print("1. 测试直接 API 调用")
    print("2. 测试流式 API 调用")
    
    choice = input("\n请选择测试类型 (1/2): ")
    
    if choice == "1":
        test_direct_api_call()
    elif choice == "2":
        test_streaming_api()
    else:
        print("无效选择，请输入 1 或 2")
