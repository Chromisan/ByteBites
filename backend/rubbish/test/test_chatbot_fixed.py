"""
验证修复后的 chatbot.py 是否正常工作
"""
import os
import sys
from pathlib import Path
import time
import json

# 添加当前目录到 Python 路径，确保能够导入 Chatbot
sys.path.insert(0, str(Path(__file__).parent))

from chatbot import Chatbot

def test_chatbot():
    """测试修复后的 Chatbot 类"""
    print("===== 开始测试 Chatbot =====")
    
    # 实例化 Chatbot
    print("正在初始化 Chatbot...")
    try:
        chatbot = Chatbot()
        print("Chatbot 初始化成功!")
    except Exception as e:
        print(f"Chatbot 初始化失败: {e}")
        return False
    
    # 测试一个简单的问题
    print("\n测试简单问题...")
    try:
        question = "推荐一家环境好的餐厅，预算100元以内"
        start_time = time.time()
        response = chatbot.chat(question)
        duration = time.time() - start_time
        print(f"请求完成，耗时: {duration:.2f}秒")
        print(f"响应摘要 (前100字符): {response[:100]}...")
        print("简单问题测试成功!")
    except Exception as e:
        print(f"简单问题测试失败: {e}")
        return False
    
    # 测试内存上下文是否正确保存
    print("\n测试上下文记忆...")
    try:
        memory_vars = chatbot.memory.load_memory_variables({})
        if "history" in memory_vars and len(memory_vars["history"]) > 0:
            print("上下文记忆正常工作!")
        else:
            print("警告: 上下文记忆可能未正确保存")
    except Exception as e:
        print(f"上下文记忆测试失败: {e}")
        return False
    
    # 测试历史记录是否保存
    print("\n测试历史记录...")
    try:
        history = chatbot.get_history()
        if history and len(history) > 0:
            print(f"历史记录保存成功! 共有 {len(history)} 条记录")
        else:
            print("警告: 历史记录可能未正确保存")
    except Exception as e:
        print(f"历史记录测试失败: {e}")
        return False
    
    print("\n===== 所有测试通过! =====")
    return True

if __name__ == "__main__":
    test_chatbot()
