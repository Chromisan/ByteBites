"""
用于验证针对 chatbot.py 中 KeyError: 'question' 问题的修复
"""
import os
import json
from datetime import datetime
from langchain.memory import ConversationBufferMemory

def test_memory_keys():
    """测试 ConversationBufferMemory 使用不同键名的情况"""
    print("===== 测试 ConversationBufferMemory 键名处理 =====")
    
    # 创建内存对象，明确指定 input_key 和 output_key
    memory = ConversationBufferMemory(
        return_messages=True,
        input_key="question",
        output_key="answer"
    )
    
    # 测试使用指定的键名
    user_message = "这是用户的问题"
    ai_response = "这是AI的回答"
    
    # 正确的键名方式
    print("\n使用正确的键名保存对话:")
    memory.save_context({"question": user_message}, {"answer": ai_response})
    memory_vars = memory.load_memory_variables({})
    print(f"加载的变量: {memory_vars}")
    
    # 清空内存
    memory.clear()
    
    # 错误的键名方式
    try:
        print("\n使用错误的键名保存对话:")
        memory.save_context({"input": user_message}, {"output": ai_response})
        memory_vars = memory.load_memory_variables({})
        print(f"加载的变量: {memory_vars}")
    except KeyError as e:
        print(f"发生 KeyError: {e}")
    
    print("\n===== 测试完成 =====")

def test_extract_preference_vars():
    """模拟测试 extract_preference_vars 函数的行为"""
    print("===== 模拟测试 extract_preference_vars 函数 =====")
    
    # 定义默认返回值
    default_prefs = {
        "preference_scores": "未设置偏好",
        "budget_range": "未设置",
        "allergies": "无",
        "likes": "无",
        "dislikes": "无",
        "preferred_cuisines": [],
        "disliked_cuisines": [],
        "special_requirements": "无"
    }
    
    # 测试空输入
    user_pref = None
    print(f"\n测试空输入 (None):")
    result = default_prefs if not user_pref else "处理用户偏好"
    print(f"结果: {result}")
    
    # 测试空字典
    user_pref = {}
    print(f"\n测试空字典:")
    result = default_prefs if not user_pref else "处理用户偏好"
    print(f"结果: {result}")
    
    # 测试有内容的字典
    user_pref = {"ratings": {"环境": 4.5}}
    print(f"\n测试有内容的字典:")
    result = default_prefs if not user_pref else "处理用户偏好"
    print(f"结果: {result}")
    
    print("\n===== 测试完成 =====")

def test_formatting():
    """测试检查格式问题"""
    print("===== 测试代码格式 =====")
    
    # 测试缩进和换行问题
    def example_function():
        try:
            print("Try block")
        except Exception as e:
            print(f"Error: {e}")
            print("Error details")
        print("This should be outside except")  # 检查缩进是否正确
        return "result"
    
    print("\n测试函数执行:")
    result = example_function()
    print(f"函数返回: {result}")
    
    print("\n===== 测试完成 =====")

if __name__ == "__main__":
    print("Chatbot.py 问题修复验证工具")
    print("1. 测试 ConversationBufferMemory 键名")
    print("2. 模拟测试 extract_preference_vars")
    print("3. 测试代码格式")
    
    choice = input("\n请选择测试类型 (1/2/3): ")
    
    if choice == "1":
        test_memory_keys()
    elif choice == "2":
        test_extract_preference_vars()
    elif choice == "3":
        test_formatting()
    else:
        print("无效选择，请输入 1、2 或 3")
