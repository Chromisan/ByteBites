import os
from dotenv import load_dotenv
import getpass
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableMap, RunnableLambda
from langchain.memory import ConversationBufferMemory

# ========== 常量定义 ==========
FAISS_REVIEWS_PATH_COSINE = "faiss_index_cosine"
FAISS_INDEX_NAME = "index"

# ========== 初始化模型和向量库 ==========
def init_models():
    print("正在加载模型和向量库...")
    
    # 加载环境变量
    load_dotenv()
    if not os.environ.get("DEEPSEEK_API_KEY"):
        os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("请输入 DeepSeek-AI API key: ")
    
    # 初始化LLM
    llm = ChatOpenAI(
        openai_api_key=os.environ["DEEPSEEK_API_KEY"],
        openai_api_base="https://api.deepseek.com/v1",
        model_name="deepseek-reasoner",
        temperature=0.7
    )
    
    # 初始化嵌入模型
    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-zh",
        model_kwargs={"device": "cpu"},
        encode_kwargs={
            "normalize_embeddings": True,
            "batch_size": 16
        }
    )
    
    # 加载向量库
    vector_db = FAISS.load_local(
        folder_path=FAISS_REVIEWS_PATH_COSINE,
        embeddings=embedding_model,
        index_name=FAISS_INDEX_NAME,
        allow_dangerous_deserialization=True
    )
    
    return llm, vector_db

# ========== 用户偏好处理 ==========
def collect_user_profile():
    print("请根据提示输入你的用餐偏好（1-5分，5分最重视）")
    def ask_score(q):
        while True:
            try:
                s = int(input(q))
                if 1 <= s <= 5:
                    return s
                else:
                    print("请输入1-5之间的整数")
            except:
                print("请输入数字")
    
    cost_performance = ask_score("请用1-5分评价你对'性价比'的重视程度（1-5分）：")
    hygiene = ask_score("请用1-5分评价你对'卫生'的重视程度（1-5分）：")
    taste = ask_score("请用1-5分评价你对'口味'的重视程度（1-5分）：")
    service = ask_score("请用1-5分评价你对'服务'的重视程度（1-5分）：")
    waiting_time = ask_score("请用1-5分评价你对'排队时间'的重视程度（1-5分）：")
    health = ask_score("请用1-5分评价你对'营养健康'的重视程度（1-5分）：")
    environment = ask_score("请用1-5分评价你对'环境氛围'的重视程度（1-5分）：")
    distance = ask_score("请用1-5分评价你对'距离远近'的重视程度（1-5分）：")
    
    preferred_cuisines = input("你偏好的菜系有哪些？（用逗号分隔，如川菜,火锅，可跳过）：").split(",") if input("是否有偏好菜系？(y/n):").lower() == "y" else []
    disliked_cuisines = input("你不喜欢的菜系有哪些？（用逗号分隔，如日料，可跳过）：").split(",") if input("是否有不喜欢的菜系？(y/n):").lower() == "y" else []
    budget_str = input("你的预算范围是多少？（如30-80，单位元）：")
    try:
        budget_range = [int(x) for x in budget_str.split("-")]
    except:
        budget_range = [0, 999]
    special_requirements = input("你还有什么特别的饮食偏好、忌口、禁忌或用餐习惯需要补充吗？（如无可跳过）：") or "无"
    
    user_pref = {
        "环境": environment,
        "口味": taste,
        "服务": service,
        "性价比": cost_performance,
        "卫生": hygiene,
        "营养健康": health,
        "排队时间": waiting_time,
        "距离": distance,
        "偏好菜系": [c.strip() for c in preferred_cuisines if c.strip()],
        "不喜欢的菜系": [c.strip() for c in disliked_cuisines if c.strip()],
        "预算范围": budget_range,
        "特殊要求": special_requirements
    }
    print("【你的用户画像已生成】\n", user_pref)
    return user_pref

def format_user_preference(user_pref):
    scores = "\n".join([f"{k}: {v}分" for k,v in user_pref.items() if isinstance(v, int)])
    budget_range = user_pref.get('预算范围', [])
    if isinstance(budget_range, list) and len(budget_range) >= 2:
        budget_str = f"{budget_range[0]}-{budget_range[1]}元"
    elif isinstance(budget_range, list) and len(budget_range) == 1:
        budget_str = f"{budget_range[0]}元"
    else:
        budget_str = "未填写"
    return (
        f"用户偏好评分:\n{scores}\n\n"
        f"偏好菜系: {', '.join(user_pref.get('偏好菜系', []))}\n"
        f"不喜欢的菜系: {', '.join(user_pref.get('不喜欢的菜系', []))}\n"
        f"预算范围: {budget_str}\n"
        f"特殊要求: {user_pref.get('特殊要求', '无')}"
    )

def extract_preference_vars(user_pref):
    scores = []
    for k in ["环境", "口味", "服务", "性价比", "卫生", "营养健康", "排队时间", "距离"]:
        if k in user_pref:
            scores.append(f"{k}: {user_pref[k]}分")
    return {
        "preference_scores": "\n".join(scores),
        "preferred_cuisines": ", ".join(user_pref.get("偏好菜系", [])),
        "disliked_cuisines": ", ".join(user_pref.get("不喜欢的菜系", [])),
        "budget_range": f"{user_pref.get('预算范围', [0,0])[0]}-{user_pref.get('预算范围', [0,0])[1]}元",
        "special_requirements": user_pref.get("特殊要求", "无"),
    }

# ========== 系统提示词定义 ==========
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

# ========== LangChain工作流 ==========
def setup_chain(llm, vector_db):
    memory = ConversationBufferMemory(memory_key="history", return_messages=True)
    
    human_prompt_template = """
    {question}
    user_preference={user_preference}
    """
    
    system_prompt = SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=["history", "context"],
            template=system_prompt_template
        )
    )
    
    human_prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=["question"],
            template=human_prompt_template
        ),
    )
    
    messages = [system_prompt, human_prompt]
    total_prompt_template = ChatPromptTemplate(
        input_variables=[
            "history", "context", "question", "user_preference",
            "preference_scores", "preferred_cuisines", "disliked_cuisines", 
            "budget_range", "special_requirements"
        ],
        messages=messages,
    )
    
    reviews_retriever = RunnableLambda(lambda x: x["question"]) | vector_db.as_retriever(search_kwargs={'k': 20,})

    review_chain = (
        RunnableMap({
            "history": RunnablePassthrough(lambda _: memory.load_memory_variables({})),
            "context": reviews_retriever,
            "question": RunnablePassthrough(),
            "user_preference": lambda x: format_user_preference(user_preference),
            "preference_scores": lambda x: extract_preference_vars(user_preference)["preference_scores"],
            "preferred_cuisines": lambda x: extract_preference_vars(user_preference)["preferred_cuisines"],
            "disliked_cuisines": lambda x: extract_preference_vars(user_preference)["disliked_cuisines"],
            "budget_range": lambda x: extract_preference_vars(user_preference)["budget_range"],
            "special_requirements": lambda x: extract_preference_vars(user_preference)["special_requirements"],
        })
        | total_prompt_template
        | llm
        | StrOutputParser()
    )
    
    return review_chain, memory

# ========== 主流程 ==========
def main():
    print("欢迎使用智能美食推荐系统！")
    
    # 初始化模型和向量库
    llm, vector_db = init_models()
    
    # 采集用户偏好
    global user_preference
    user_preference = collect_user_profile()
    
    # 设置对话链和记忆
    review_chain, memory = setup_chain(llm, vector_db)
    
    # 开始对话
    print("\n请输入你的本次用餐需求（如'预算50元内，想吃辣的，适合2人，距离不远'）：")
    while True:
        question = input("你的用餐需求/问题：")
        if not question.strip():
            print("输入为空，已退出。")
            break
            
        input_data = {
            "question": question,
            "user_preference": format_user_preference(user_preference)
        }
        
        try:
            response = review_chain.invoke(input_data)
            memory.save_context({"input": question}, {"output": response})
            print("\n=== 推荐结果 ===")
            print(response)
        except Exception as e:
            print(f"发生错误: {str(e)}")
            print("请重试或联系管理员。")
            
        again = input("\n是否继续提问？(y继续，其他退出)：")
        if again.lower() != "y":
            break

if __name__ == "__main__":
    main()
