import http.client
import time
import json
import os
from dotenv import load_dotenv # Added for .env file support
from urllib.parse import urlparse # Added to parse base_url

# 从 chatbot.py 复制过来的 system_prompt_template
system_prompt_template = """
# 你的角色
你是"菜根探"——一名智能美食推荐助手。你的工作是根据用户的个性化偏好和实时需求，从数据库中推荐最优餐厅。
# 1. 用户个人偏好
用户的个人偏好如下（已由前端页面采集）：
'''
{user_preference}
'''
- 偏好指标包括：环境、口味、服务、性价比、卫生、营养健康、排队时间、距离等。
- 每项得分为0-5分，数值越高代表用户在挑选餐厅时对该项要求越高，指标越靠前说明越重要。
- 请结合这些分值，为后续餐厅筛选与加权打分分配不同权重，优先满足得分高和排名靠前的指标项。
- 偏好含义参考：  
    - 环境：重视餐厅环境、氛围、安静度、空间舒适度  
    - 口味：重视菜品风味、辣度、甜度、食材正宗性  
    - 服务：重视服务态度、效率、人员素质  
    - 性价比：追求花更少的钱享受更好服务和菜品  
    - 卫生：对用餐卫生和食材安全的重视  
    - 营养健康：追求健康、低油低盐、营养搭配  
    - 排队时间：关注是否需等位、出餐速度  
    - 距离：优先考虑距离近、交通便利的餐厅
    请特别注意以下关键信息：
    - 各维度评分(0-5分): {preference_scores}
    - 偏好菜系: {preferred_cuisines}
    - 不喜欢的菜系: {disliked_cuisines}
    - 预算范围: {budget_range}
    - 特殊要求: {special_requirements}
# 2. 推荐策略
- 优先匹配用户评分高的维度(4-5分)
- 确保推荐餐厅在用户预算范围内
- 避免推荐用户不喜欢的菜系
- 考虑用户特殊要求
# 2. 用户实时需求和场景采集
-用户会用自然语言表达本次用餐需求（如预算、人数、距离、期望场景/菜系/口味等），你需要智能解析这些内容，将其与个人偏好结合起来，为用户进行匹配推荐。
-鼓励用户用自然语言表达当前用餐需求（如预算、人数、距离、类型、菜系、期望场景/氛围等），支持用户自由描述，也可追问补全关键信息。
-你需解析这些需求，明确硬性（预算/营业/距离/人数/时段）与软性（口味/氛围/健康/环境）约束。
# 3. 餐厅数据库字段说明
你所参考的数据库中，每家餐厅包含以下字段：
- name（餐厅名称）
- dp_cost（大众点评人均消费）
- dp_rating（大众点评综合评分）
- dp_taste_rating（大众点评口味评分）
- dp_env_rating（大众点评环境评分）
- dp_service_rating（大众点评服务评分）
- dp_comment_num（大众点评评论数）
- dp_recommendation_dish（推荐菜品）
- dp_comment_keywords（高频评论关键词）
- dp_top3_comments（精选评论）
- address（门店地址）
- location（地理坐标或位置描述）
- type（餐厅类型/菜系）
- tel（联系电话）
- cost（其他平台人均消费）
- rating（平台综合评分）
- opentime_today（今日营业时间）
- opentime_week（每周营业时间）
- tag（标签/特色）
请注意以上信息可能会有确实或不完整的情况，需要你再结合网络搜索给出更加全面客观的结果，如果没有获取到清晰明确的信息可忽略该维度，不要输出虚构内容。
# 4. 推荐输出要求
每轮推荐请严格输出：
- 按"个人偏好+实时需求"综合得分排序，推荐3~5家最优餐厅。
- 每家餐厅详细输出：
    1. 基础信息：名称、地址、类型/菜系、标签/特色、联系电话、人均消费、营业时间、距离等
    2. 多维匹配打分：综合得分（0-100分/5分制），并对各主维度（环境、口味、服务、性价比等）单独打分，清晰展示与用户偏好对应分值，并说明原因
    3. AI生成个性化推荐理由：**结合用户高权重指标具体展开**，如"该店环境评分4.8，安静优雅，极度适合你对环境的高要求"，并适当引用精选评论、推荐菜、关键词
    4. 最佳交通方式与所需时间：请根据用户出发地（如未输入，请主动引导用户补充自己的具体位置），为每家餐厅给出推荐的交通方式（步行、地铁、打车、公交等）与大致所需时间（如步行10分钟、地铁2站共20分钟等），提升实际可达性与用户体验。
    5. 用户补充引导：主动建议用户进一步细化需求（如预算、口味、场景、特殊要求、出发地等），如果推荐未完全匹配高分项，请提示可补充更多限制条件以优化结果。特别是在未获得用户具体位置时，提醒其补充出发地以优化路线推荐。
# 补充说明
- 如果用户未提供出发地，请在回复末尾礼貌建议："为获得更准确的交通方案，请告知你当前或希望出发的具体位置"。
- 交通方案可根据餐厅地址和用户位置生成（如无法获取实际路线，可用"预计步行约X分钟"格式估算）。
# 规则
- 你只能基于数据库现有信息推荐，不允许虚构不存在的餐厅。
- 如某项信息缺失，请如实说明"该项暂无数据"。
- 非餐饮、无关问题请委婉回复"仅能为您提供美食/餐厅推荐服务"。
- 推荐内容需结构化、条理清晰、易于用户理解和决策。
# 当前对话历史
{history}
# 数据库内容
{context}
"""

user_preferences_data = {
  "priceRange": { "min": 0.0, "max": 54.0 },
  "ratings": {
    "valueForMoney": 5.0, "hygiene": 3.5, "environment": 4.0, "distance": 2.5,
    "waitTime": 2.5, "platformRating": 2.5, "service": 1.5, "taste": 2.5,
    "health": 2.5, "nutrition": 2.5, "spiciness": 2.5
  },
  "preferences": { "allergies": "123", "likes": "无", "dislikes": "无" }
}

def format_user_preference_for_test(user_pref):
    if not user_pref:
        return "未设置用户偏好"
    scores = []
    ratings = user_pref.get("ratings", {})
    mapping = {
        "valueForMoney": "性价比", "hygiene": "卫生", "environment": "环境",
        "distance": "距离", "waitTime": "排队时间", "service": "服务",
        "taste": "口味", "health": "健康", "nutrition": "营养", "spiciness": "辣度"
    }
    for key, cn_key in mapping.items():
        if key in ratings:
            scores.append(f"{cn_key}: {ratings[key]}分")
    price_range = user_pref.get("priceRange", {})
    budget_str = f"{price_range.get('min', 0)}-{price_range.get('max', 999)}元" if price_range else "未设置"
    preferences_map = user_pref.get("preferences", {}) # Renamed to avoid conflict
    return (
        f"用户偏好评分:\\n{chr(10).join(scores)}\\n\\n"
        f"预算范围: {budget_str}\\n"
        f"过敏和忌口: {preferences_map.get('allergies', '无')}\\n"
        f"喜欢的食物: {preferences_map.get('likes', '无')}\\n"
        f"不喜欢的食物: {preferences_map.get('dislikes', '无')}"
    )

def extract_preference_vars_for_test(user_pref):
    if not user_pref: return {"preference_scores": "未设置偏好", "budget_range": "未设置", "preferred_cuisines": [], "disliked_cuisines": [], "special_requirements": "无"}
    scores = []
    ratings = user_pref.get("ratings", {})
    mapping = {
        "valueForMoney": "性价比", "hygiene": "卫生", "environment": "环境",
        "distance": "距离", "waitTime": "排队时间", "service": "服务",
        "taste": "口味", "health": "健康", "nutrition": "营养", "spiciness": "辣度"
    }
    for key, cn_key in mapping.items():
        if key in ratings: scores.append(f"{cn_key}: {ratings[key]}分")
    price_range = user_pref.get("priceRange", {})
    budget_range_str = f"{price_range.get('min', 0)}-{price_range.get('max', 999)}元" if price_range else "未设置"
    # For simplicity in this test script, preferred/disliked cuisines and special_requirements are not dynamically extracted
    # from user_preferences_data but will be hardcoded or taken as empty in the prompt formatting.
    # In a real scenario, these would come from the full user_pref object.
    return {
        "preference_scores": "\\n".join(scores), 
        "budget_range": budget_range_str,
        "preferred_cuisines": user_pref.get("偏好菜系", []), # Assuming direct keys if they exist
        "disliked_cuisines": user_pref.get("不喜欢的菜系", []),
        "special_requirements": user_pref.get("特殊要求", "无")
    }

def send_to_deepseek_api(api_key: str, messages: list, model_name: str, base_url: str, max_tokens: int = 2048, temperature: float = 0.7):
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path
    
    if not path or path == '/': # Ensure path is correctly set if base_url doesn't include it
        path = "/v1/chat/completions"
        
    # Ensure host and path are not empty
    if not host:
        print(f"错误：无法从 base_url '{base_url}' 解析主机。")
        return
    if not path.startswith("/v1/chat/completions"):
        print(f"警告：base_url '{base_url}' 中的路径 '{path}' 不是预期的 '/v1/chat/completions'。将使用默认路径。")
        # path = "/v1/chat/completions" # Or decide to fail if path is critical and unexpected

    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False # Set to False to get the full response at once
    }
    json_payload = json.dumps(payload, ensure_ascii=False) # ensure_ascii=False for Chinese characters
    
    headers = {
        "Content-Type": "application/json; charset=utf-8", # Specify charset
        "Authorization": f"Bearer {api_key}"
    }
    
    print("\\n===== 发送给大模型的Payload =====")
    print(json.dumps(payload, indent=2, ensure_ascii=False)) # Pretty print the payload
    
    conn = None
    try:
        # conn = http.client.HTTPSConnection(host, timeout=120) # Increased timeout
        if parsed_url.scheme == "https":
            conn = http.client.HTTPSConnection(host, timeout=120)
        else:
            conn = http.client.HTTPConnection(host, timeout=120)
        start_time = time.time()
        conn.request("POST", path, body=json_payload.encode('utf-8'), headers=headers) # Encode payload to UTF-8
        response = conn.getresponse()
        duration = time.time() - start_time
        
        print(f"\\n连接到 {host}{path}")
        print(f"状态码: {response.status}")
        print(f"原因: {response.reason}")
        print(f"响应时间: {duration:.2f} 秒")
        
        response_body_bytes = response.read()
        response_body_str = response_body_bytes.decode('utf-8') # Decode response as UTF-8
        
        print("\\n===== 大模型返回的原始响应 =====")
        print(response_body_str)
        
        if response.status == 200:
            print("\\n===== 大模型返回的解析后内容 =====")
            try:
                response_json = json.loads(response_body_str)
                if response_json.get("choices") and response_json["choices"][0].get("message"):
                    print(response_json["choices"][0]["message"].get("content"))
                else:
                    print("无法从响应中提取 'content'。")
            except json.JSONDecodeError:
                print("无法将响应解析为JSON。")
        else:
            print(f"API返回错误状态。请检查API Key和请求详情。")

    except http.client.HTTPException as e:
        print(f"HTTP 客户端错误: {e}")
    except ConnectionRefusedError:
        print(f"连接被拒绝。请检查目标服务器 {host} 是否可达以及防火墙设置。")
    except TimeoutError:
        print(f"连接超时。目标服务器 {host} 未在设定时间内响应。")
    except Exception as e:
        print(f"发生未知错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_dotenv() # Load environment variables from .env file

    # Get DeepSeek API Key
    deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        deepseek_api_key = input("\\n请输入您的 DeepSeek API Key: ")

    # Get DeepSeek Base URL from environment variable or use default
    deepseek_base_url = os.environ.get("DEEPSEEK_BASE_URL")
    if not deepseek_base_url:
        print("警告: 未在 .env 文件中找到 DEEPSEEK_BASE_URL。将使用默认值 'https://api.deepseek.com'")
        deepseek_base_url = 'https://api.deepseek.com'
    
    # Get DeepSeek Model from environment variable or use default (DEEPSEEK_MODEL_V3)
    deepseek_model_name = os.environ.get("DEEPSEEK_MODEL_V3")
    if not deepseek_model_name:
        print("警告: 未在 .env 文件中找到 DEEPSEEK_MODEL_V3。将使用默认值 'deepseek-chat'")
        deepseek_model_name = 'deepseek-chat'

    user_chat_input = input("请输入您的聊天信息 (例如 '披萨' 或 '推荐一家安静的咖啡馆'): ")
    
    print("\\n为了使测试更接近真实情况，您可以粘贴从 chatbot.py 调试输出中获得的 'context' 内容。")
    print("如果您跳过这一步（直接按回车），'context' 将为空。")
    print("粘贴 'context' 内容 (多行输入请自行处理换行，或确保粘贴的内容是单行字符串):")
    
    db_context_input_lines = []
    while True:
        line = input()
        if not line: # Stop on empty line
            break
        db_context_input_lines.append(line)
    db_context_input = "\\n".join(db_context_input_lines)

    if not db_context_input.strip():
        print("未提供 'context'，将使用空上下文。")
        db_context_input = "" # Ensure it's an empty string if nothing was provided

    # 格式化用户偏好
    formatted_prefs = format_user_preference_for_test(user_preferences_data)
    extracted_vars = extract_preference_vars_for_test(user_preferences_data)

    # 构建系统消息内容
    # 注意: history, preferred_cuisines, disliked_cuisines, special_requirements 
    # 在此脚本中为了简化，部分从 extracted_vars 获取，部分硬编码为空或简单值。
    # 真实 chatbot.py 会有更完整的填充逻辑。
    system_message_content = system_prompt_template.format(
        user_preference=formatted_prefs,
        preference_scores=extracted_vars["preference_scores"],
        preferred_cuisines=extracted_vars.get("preferred_cuisines", "[]"), # Use .get for safety
        disliked_cuisines=extracted_vars.get("disliked_cuisines", "[]"),
        budget_range=extracted_vars["budget_range"],
        special_requirements=extracted_vars.get("special_requirements", "无"),
        history="", # 假设当前测试无历史记录
        context=db_context_input # 使用用户输入的或空的 context
    )
    
    # 构建发送给API的消息列表
    api_messages = [
        {"role": "system", "content": system_message_content},
        {"role": "user", "content": user_chat_input}
    ]
    
    if deepseek_api_key:
        # 指定模型名称，与 chatbot.py 中一致
        send_to_deepseek_api(deepseek_api_key, api_messages, model_name=deepseek_model_name, base_url=deepseek_base_url)
    else:
        print("未提供 API Key，无法发送请求。")
