import os
from dotenv import load_dotenv
load_dotenv()

"""from langchain_deepseek import ChatDeepSeek
llm = ChatDeepSeek(
    model=os.getenv("DEEPSEEK_MODEL_NAME"),
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # api_key="...",
    # other params...
)"""

from langchain_openai import ChatOpenAI
from browser_use import Agent,Browser
from browser_use import BrowserConfig
from browser_use.browser.context import BrowserContext
import asyncio

# Basic configuration
config = BrowserConfig(
    headless=False,
    disable_security=False
)

browser = Browser(config=config)

# dotenv
load_dotenv()

# Initialize the model
llm=ChatOpenAI(base_url=os.getenv("DEEPSEEK_BASE_URL"),
                model=os.getenv("DEEPSEEK_MODEL_NAME"),
                  api_key=os.getenv("DEEPSEEK_API_KEY")
                  )

async def run_search():
    agent = Agent(
		task=(	'1. 打开 https://www.dianping.com/'
		        '2. 使用以下登录凭证登录：\n'
            f'Authorization: Bearer {os.getenv("DIANPING_TOKEN")}\n'
            '3. 把地址转到当前Ip的区域'
			'4. 点击美食模块'
			"5. 在搜索框中搜索 '肯德基'，按好评降序排列搜索结果 "
            "6. 叉掉弹窗，点击第一个店铺，返回店铺名称、地址、评分"
            "7. 返回这个店铺的所有评论"
		),
		llm=llm,
		browser=browser,#重用浏览器实例
		use_vision=False,#使用没有视觉支持的模型时禁用
        save_conversation_path="logs/conversation"  #Save chat logs调试用
	)
    await agent.run()
    await browser.close()#记得手动关闭浏览器

if __name__ == '__main__':
	asyncio.run(run_search())

"""
			'1. 打开 https://www.dianping.com'
			'2. 点击美食模块'
			"3. 在搜索框中搜索 '肯德基'，按好评降序排列搜索结果 "
			"4. 叉掉'移步至大众点评App查看/使用更多内容'的弹屏"
            "5. 点击第一个店铺，返回店铺名称、地址、评分、与所有评论"
"""

#多轮对话
"""
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
conversation_history = [
    SystemMessage(
        content="你是一个美食家以及营养学专家，你将只回答与美食与饮食有关的问题；如果用户问及与吃饭无关的问题，直接回答不知道."
        )
    ]
while True:
    #get user input
    user_input = input("User: ")
    #exit condition
    if user_input.lower() == "exit":
        print("Exiting the conversation. Goodbye!")
        break
    # Add user input to conversation history
    conversation_history.append(HumanMessage(content=user_input))
    # Get model response
    response = llm.invoke(conversation_history)
    # Add model response to conversation history
    conversation_history.append(AIMessage(content=response.content))
    # Print model response
    print(f"AI: {response.content}")
    """