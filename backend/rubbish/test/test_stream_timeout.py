"""
测试 ChatOpenAI 的流式响应和超时参数
"""
import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage

def test_streaming_api(streaming=True, timeout=120):
    """测试不同的流式和超时参数组合"""
    print(f"===== 测试 ChatOpenAI 调用 =====")
    print(f"流式响应: {streaming}")
    print(f"超时设置: {timeout}秒")
    
    # 加载环境变量
    load_dotenv()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model_name = os.environ.get("DEEPSEEK_MODEL_V3", "deepseek-chat")
    
    if not api_key:
        print("错误: 未设置 DEEPSEEK_API_KEY 环境变量")
        return
    
    # 创建 ChatOpenAI 实例
    llm = ChatOpenAI(
        openai_api_key=api_key,
        openai_api_base=base_url,
        model_name=model_name,
        temperature=0.7,
        request_timeout=timeout,
        max_retries=1,
        streaming=streaming
    )
    
    # 创建简单消息
    messages = [
        SystemMessage(content="你是一个简短的回答助手。请简明扼要地回答问题，不要超过50个字。"),
        HumanMessage(content="你好，请介绍一下自己。")
    ]
    
    print("\n发送请求...")
    try:
        start_time = time.time()
        
        # 使用 ChatOpenAI 发送请求
        response = llm.invoke(messages)
        
        duration = time.time() - start_time
        print(f"请求完成，耗时: {duration:.2f}秒")
        
        print("\n响应内容:")
        if hasattr(response, 'content'):
            print(response.content)
        else:
            print(response)
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n错误: {e}")
        print(f"错误发生时间: {duration:.2f}秒")
    
    print("\n===== 测试完成 =====")

if __name__ == "__main__":
    print("ChatOpenAI 流式和超时参数测试工具")
    print("1. 测试带流式响应 (streaming=True)")
    print("2. 测试不带流式响应 (streaming=False)")
    print("3. 测试短超时 (timeout=30)")
    print("4. 测试长超时 (timeout=120)")
    
    choice = input("\n请选择测试类型 (1/2/3/4): ")
    
    if choice == "1":
        test_streaming_api(streaming=True, timeout=120)
    elif choice == "2":
        test_streaming_api(streaming=False, timeout=120)
    elif choice == "3":
        test_streaming_api(streaming=True, timeout=30)
    elif choice == "4":
        test_streaming_api(streaming=False, timeout=120)
    else:
        print("无效选择，请输入 1、2、3 或 4")
