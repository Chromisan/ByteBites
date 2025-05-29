import os
import csv
import random 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser
from browser_use import BrowserConfig
import asyncio

def save_to_csv(data, filename="restaurant_data.csv"):
    """保存数据到CSV文件"""
    headers = ["店铺名称", "地址", "评分", "评论"]
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if os.path.getsize(filename) == 0:
            writer.writeheader()
        writer.writerow(data)

async def search_restaurant(browser, llm, keyword):
    """搜索单个餐厅信息"""
    try:
        # 在每次搜索操作前处理可能的弹窗和验证
        await handle_popups(browser)
        await handle_verification(browser)
        
        agent = Agent(
            task=(
                 "1. 在当前页面的店铺搜索框中输入并搜索以下店铺\n"
                f'2. 搜索 "{keyword}"\n'
                "3. 点击第一个店铺\n"
                "4. 返回店铺名称、地址、评分和所有评论"
            ),
            llm=llm,
            browser=browser,
            use_vision=False,
            #save_conversation_path="logs/conversation"
        )
        
        result = await agent.run()
        
        # 搜索完成后再次处理可能出现的弹窗
        await handle_popups(browser)
        return result
        
    except Exception as e:
        print(f"搜索过程中出错: {str(e)}")
        # 出错时也要尝试处理弹窗
        await handle_popups(browser)
        return None

async def handle_popups(browser):
    """处理各种弹窗的函数"""
    try:
        # 处理APP下载弹窗
        app_popup = await browser.page.query_selector('xpath=//div[contains(@class, "modal-close")]')
        if app_popup:
            await app_popup.click()
            await asyncio.sleep(random.uniform(0.8, 1.5))
        
        # 处理登录提示弹窗
        login_popup = await browser.page.query_selector('xpath=//div[contains(@class, "login-close")]')
        if login_popup:
            await login_popup.click()
            await asyncio.sleep(random.uniform(0.8, 2))
            
        # 处理其他通用弹窗
        other_popups = await browser.page.query_selector_all('xpath=//*[contains(@class, "close") or contains(@class, "popup")]')
        for popup in other_popups:
            await popup.click()
            await asyncio.sleep(random.uniform(0.8, 1))
            
    except Exception as e:
        print(f"处理弹窗时出错: {str(e)}")

async def auto_slide_verification(browser):
    """自动处理滑块验证"""
    try:
        # 查找滑块元素
        slider = await browser.page.query_selector('xpath=//div[contains(@class, "verify-slider")]')
        if slider:
            print("检测到滑块验证，尝试自动滑动...")
            
            # 获取滑块位置和大小
            slider_box = await slider.bounding_box()
            
            # 模拟人工滑动
            await browser.page.mouse.move(
                slider_box['x'] + 5,  # 滑块左边缘位置
                slider_box['y'] + slider_box['height']/2  # 滑块中间位置
            )
            await browser.page.mouse.down()  # 按下鼠标
            
            # 随机速度滑动
            current_x = slider_box['x'] + 5
            target_x = slider_box['x'] + slider_box['width'] + random.uniform(180, 220)
            
            while current_x < target_x:
                move_step = random.uniform(5, 15)  # 随机步长
                current_x += move_step
                await browser.page.mouse.move(
                    current_x,
                    slider_box['y'] + slider_box['height']/2 + random.uniform(-2, 2),  # 添加微小的垂直偏移
                    steps=random.randint(1, 3)  # 随机步数
                )
                await asyncio.sleep(random.uniform(0.01, 0.03))  # 随机延迟
                
            await browser.page.mouse.up()  # 释放鼠标
            await asyncio.sleep(1)  # 等待验证结果
            
            # 检查验证是否成功
            is_success = not await browser.page.query_selector('xpath=//div[contains(@class, "verify-slider")]')
            if is_success:
                print("自动滑块验证成功！")
                return True
            else:
                print("自动滑块验证失败，切换到人工验证...")
                return False
                
    except Exception as e:
        print(f"自动滑块验证出错: {str(e)}")
        return False

# 修改原有的 handle_verification 函数
async def handle_verification(browser):
    """处理验证码"""
    try:
        # 检查是否存在滑块验证
        slider = await browser.page.query_selector('xpath=//div[contains(@class, "verify-slider")]')
        if slider:
            # 首先尝试自动滑动
            if not await auto_slide_verification(browser):
                # 自动验证失败，切换到人工验证
                print("请在30秒内手动完成验证...")
                await browser.page.wait_for_selector('xpath=//div[contains(@class, "verify-slider")]', state='hidden', timeout=30000)
            await asyncio.sleep(random.uniform(0.8, 1.5))
        
        # 处理点击验证码（保持不变）
        click_verify = await browser.page.query_selector('xpath=//div[contains(@class, "verify-image")]')
        if click_verify:
            print("检测到图片验证码，请在30秒内手动完成验证...")
            await browser.page.wait_for_selector('xpath=//div[contains(@class, "verify-image")]', state='hidden', timeout=30000)
            await asyncio.sleep(random.uniform(0.8, 1.5))
            
    except Exception as e:
        print(f"处理验证码时出错: {str(e)}")

async def run_multiple_searches():
    # 配置浏览器
    config = BrowserConfig(headless=False, disable_security=False)
    browser = Browser(config=config)
    
    try:
        # 首次登录
        login_agent = Agent(
            task=(
                '1. 打开 https://www.dianping.com/\n'
                '2. 等待30秒\n'#手动登录，切换到美食页面
                '3. 保持在当前页面\n'
            ),
            llm=llm,
            browser=browser,
            use_vision=False
        )
        await login_agent.run()

        # 搜索关键词列表
        search_keywords = [
            "巴蜀鱼花(南大店)", "陕老顺肉夹馍", "同廣鸣港式烧腊(南京大学店)", "鱼塘鲜专业鱼馆(汉口路店)", 
            "西安特色面馆(汉口路店)", "荆州锅盔(汉口路小区店)", "兰州拉面刀削面(汉口路店)", 
            "张亮麻辣烫(南大店)", "老王馄饨", "石锅房"
        ]

        # 依次搜索每个关键词
        for keyword in search_keywords:
            try:
                result = await search_restaurant(browser, llm, keyword)
                save_to_csv(result)
                print(f"已完成 {keyword} 的搜索并保存")
                await asyncio.sleep(random.uniform(0.8, 1.5))  # 添加延迟避免请求过快
            except Exception as e:
                print(f"搜索 {keyword} 时出错: {str(e)}")
                continue

    finally:
        await browser.close()

if __name__ == '__main__':
    load_dotenv()
    llm = ChatOpenAI(
        base_url=os.getenv("DEEPSEEK_BASE_URL"),
        model=os.getenv("DEEPSEEK_MODEL_NAME"),
        api_key=os.getenv("DEEPSEEK_API_KEY")
    )
    asyncio.run(run_multiple_searches())