import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import getpass
import time # Added for timing
import traceback # Added for detailed traceback
import openai # Added for openai.APITimeoutError
import torch # Added for torch.cuda.is_available()

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
# 使用绝对路径
FAISS_REVIEWS_PATH_COSINE = Path(__file__).parent / "faiss_index_cosine"
FAISS_INDEX_NAME = "index"
HISTORY_PATH = Path(__file__).parent / "data" / "chat_history.json"
PREF_PATH = Path(__file__).parent / "data" / "user_preferences.json"

class Chatbot:
    _instance = None  # 单例模式实例

    def __init__(self):
        """初始化Chatbot"""
        if not HISTORY_PATH.parent.exists():
            HISTORY_PATH.parent.mkdir(parents=True)
        if not HISTORY_PATH.exists():
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False)
                
        if not PREF_PATH.parent.exists():
            PREF_PATH.parent.mkdir(parents=True)
        if not PREF_PATH.exists():
            with open(PREF_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False)
        
        print("正在初始化模型...")
        self.llm, self.vector_db = self._init_models()
        self.memory = ConversationBufferMemory(
            return_messages=True,
            output_key="answer",
            input_key="question"
        )
        self.chain = self._setup_chain()
        print("模型初始化完成")

    def _init_models(self):
        """初始化LLM和向量数据库"""
        # 加载环境变量
        load_dotenv()
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        base_url = os.environ.get("DEEPSEEK_BASE_URL")
        model_name = os.environ.get("DEEPSEEK_MODEL_V3") # 使用 DEEPSEEK_MODEL_V3

        if not api_key:
            raise ValueError("未设置DEEPSEEK_API_KEY环境变量")
        if not base_url:
            # raise ValueError("未设置DEEPSEEK_BASE_URL环境变量") # 或者提供一个默认值
            print("警告: 未设置DEEPSEEK_BASE_URL环境变量，将使用默认值 'https://api.deepseek.com'")
            base_url = "https://api.deepseek.com"
        if not model_name:
            # raise ValueError("未设置DEEPSEEK_MODEL_V3环境变量") # 或者提供一个默认值
            print(f"警告: 未设置DEEPSEEK_MODEL_V3环境变量，将使用默认值 'deepseek-chat'")
            model_name = "deepseek-chat"
          # 初始化LLM
        try:
            # 使用流式模式，可能会更快地开始返回响应，减少超时风险
            llm = ChatOpenAI(
                openai_api_key=api_key,
                openai_api_base=base_url, # 使用从 .env 读取的 base_url
                model_name=model_name,    # 使用从 .env 读取的 model_name
                temperature=0.7,
                request_timeout=120,      # 保持较长超时，但流式模式通常能更快返回
                max_retries=3,
                streaming=True            # 启用流式处理
            )
            print(f"成功初始化LLM: model={model_name}, base_url={base_url}, streaming=True")
        except Exception as e:
            print(f"初始化LLM时出错: {str(e)}")
            raise
        
        # 初始化嵌入模型和向量库
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"使用设备: {device}")
            
            embedding_model = HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-zh",
                model_kwargs={"device": device},
                encode_kwargs={
                    "normalize_embeddings": True,
                    "batch_size": 32 if device == "cuda" else 16
                }
            )
            
            vector_db = FAISS.load_local(
                folder_path=FAISS_REVIEWS_PATH_COSINE,
                embeddings=embedding_model,
                index_name=FAISS_INDEX_NAME,
                allow_dangerous_deserialization=True
            )
            return llm, vector_db
            
        except Exception as e:
            print(f"初始化向量库时出错: {str(e)}")
            raise

    @classmethod
    def get_instance(cls) -> 'Chatbot':
        """获取Chatbot单例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def chat(self, message: str) -> str:
        """处理用户消息并返回回复"""
        print(f"\\n===== Chatbot.chat: Received message at {datetime.now()} =====\\nUser message: {message}")
        
        start_time = time.time() # Start timing before any processing

        try:
            # 用户偏好现在在链中加载，这里准备链的输入
            input_data = {
                "question": message,
            }
            print(f"\\n===== Chatbot.chat: Input data for chain =====\\n{json.dumps(input_data, indent=2, ensure_ascii=False)}")
            
            print(f"\\n===== Chatbot.chat: Invoking chain at {datetime.now()} =====")
            chain_start_time = time.time()
            response = self.chain.invoke(input_data)
            chain_end_time = time.time()
            print(f"\\n===== Chatbot.chat: Chain invoked successfully in {chain_end_time - chain_start_time:.2f} seconds at {datetime.now()} =====")
            
            # 键名必须与初始化 ConversationBufferMemory 时的 input_key 和 output_key 一致
            self.memory.save_context({"question": message}, {"answer": response})
            
            # 保存对话历史
            self._append_history(message, response)
            
            response_snippet = response[:500] + '...' if len(response) > 500 else response
            print(f"\\n===== Chatbot.chat: Sending response snippet to frontend =====\\n{response_snippet}")
            return response
            
        except openai.APITimeoutError as e:
            current_time = time.time()
            duration = current_time - start_time
            print(f"\\n!!!!! Chatbot.chat: OpenAI APITimeoutError after {duration:.2f} seconds at {datetime.now()} !!!!!")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            if hasattr(e, 'request'):
                print(f"Request details (if available): {e.request}")
            print("Traceback:")
            traceback.print_exc()
            return f"处理超时，请稍后再试或尝试简化您的问题。错误详情: OpenAI API Timeout"
            
        except Exception as e:
            current_time = time.time()
            duration = current_time - start_time
            print(f"\\n!!!!! Chatbot.chat: Generic error after {duration:.2f} seconds at {datetime.now()} !!!!!")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            return f"处理您的请求时发生错误。错误详情: {str(e)}"

    def _load_user_preference(self) -> Dict:
        """加载用户偏好设置"""
        if PREF_PATH.exists():
            try:
                with open(PREF_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载用户偏好时出错: {str(e)}")
        return {}

    def _append_history(self, user_msg: str, bot_msg: str):
        """添加新的对话记录"""
        try:
            # 读取现有历史
            history = []
            if HISTORY_PATH.exists():
                with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                    history = json.load(f)
            
            # 添加新对话
            history.append({
                "timestamp": datetime.now().isoformat(),
                "user": user_msg,
                "bot": bot_msg
            })
            
            # 保存历史
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存对话历史时出错: {str(e)}")

    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        try:
            if HISTORY_PATH.exists():
                with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"读取对话历史时出错: {str(e)}")
            return []

    def clear_history(self):
        """清空对话历史"""
        try:
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False)
            self.memory.clear()
        except Exception as e:
            print(f"清空对话历史时出错: {str(e)}")
            raise

    def _setup_chain(self):
        """设置对话链和记忆"""

        def log_retrieved_context(docs: List[Any]) -> List[Any]: # Assuming docs are Langchain Document objects
            print("\\n===== Retrieved Context for LLM =====")
            try:
                context_str = "\\n".join([doc.page_content for doc in docs])
                print(f"Number of documents retrieved: {len(docs)}")
                print(f"Total context length: {len(context_str)} characters")
                # Print a snippet of the context
                snippet = context_str[:1000] + "..." if len(context_str) > 1000 else context_str
                print(f"Context snippet:\\n{snippet}")
            except Exception as e:
                print(f"Error logging retrieved context: {e}")
                print(f"Raw docs: {docs}")
            print("===== End Retrieved Context =====\\n")
            return docs

        reviews_retriever = (
            RunnableLambda(lambda x: x["question"]) 
            | self.vector_db.as_retriever(search_kwargs={'k': 20})
            | RunnableLambda(log_retrieved_context) # Log the retrieved context
        )
        
        # 准备prompt模板
        chat_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate(
                prompt=PromptTemplate(
                    input_variables=["history", "context", "user_preference", "preference_scores", 
                                   "preferred_cuisines", "disliked_cuisines", "budget_range", 
                                   "special_requirements"],
                    template=system_prompt_template
                )
            ),
            HumanMessagePromptTemplate(
                prompt=PromptTemplate(
                    input_variables=["question"],
                    template="{question}"
                )
            )
        ])

        def log_data_for_llm(data: Any) -> Any:
            print("\\n===== Data to be sent to LLM =====")
            try:
                if hasattr(data, 'to_messages'): # For ChatPromptValue
                    messages = data.to_messages()
                    print(f"Number of messages: {len(messages)}")
                    for i, message in enumerate(messages):
                        content_snippet = message.content[:1000] + '...' if len(message.content) > 1000 else message.content
                        print(f"Message {i+1}: Role: {message.type}, Content Snippet:\\n{content_snippet}")
                elif hasattr(data, 'text'): # For StringPromptValue
                    print(data.text[:2000] + "..." if len(data.text) > 2000 else data.text)
                elif isinstance(data, str): # For plain string prompts
                    print(data[:2000] + "..." if len(data) > 2000 else data)
                else: # Fallback for other types
                    print(f"Data type: {type(data)}")
                    # Attempt to pretty-print if it's a dict or list, otherwise use str()
                    if isinstance(data, (dict, list)):
                        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
                    else:
                        print(str(data)[:2000] + "..." if len(str(data)) > 2000 else str(data))
            except Exception as e:
                print(f"Error logging data for LLM: {e}")
                print(f"Raw data: {data}")
            print("===== End Data to be sent to LLM =====\\n")
            return data

        review_chain = (
            RunnableMap({
                "history": RunnableLambda(lambda _: self.memory.load_memory_variables({}).get("history", [])), # Ensure history is a list
                "context": reviews_retriever,
                "question": RunnableLambda(lambda x: x["question"]), # Pass question explicitly
                "user_preference": RunnableLambda(lambda _: format_user_preference(self._load_user_preference())),
                "preference_scores": RunnableLambda(lambda _: extract_preference_vars(self._load_user_preference())["preference_scores"]),
                "preferred_cuisines": RunnableLambda(lambda _: extract_preference_vars(self._load_user_preference()).get("preferred_cuisines", [])),
                "disliked_cuisines": RunnableLambda(lambda _: extract_preference_vars(self._load_user_preference()).get("disliked_cuisines", [])),
                "budget_range": RunnableLambda(lambda _: extract_preference_vars(self._load_user_preference()).get("budget_range", "未设置")),
                "special_requirements": RunnableLambda(lambda _: extract_preference_vars(self._load_user_preference()).get("special_requirements", "无"))            })
            | chat_template
            | RunnableLambda(log_data_for_llm) # Log data before sending to LLM
            | self.llm
            | StrOutputParser()
        )
        
        return review_chain

# ========== 初始化模型和向量库 ==========
def init_models():
    print("正在加载模型和向量库...")
    
    # 加载环境变量
    load_dotenv()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL")
    model_name = os.environ.get("DEEPSEEK_MODEL_V3") # 使用 DEEPSEEK_MODEL_V3

    if not api_key:
        api_key = getpass.getpass("未找到DEEPSEEK_API_KEY, 请输入 DeepSeek-AI API key: ")
    if not base_url:
        print("警告: 未设置DEEPSEEK_BASE_URL环境变量，将使用默认值 'https://api.deepseek.com'")
        base_url = "https://api.deepseek.com"
    if not model_name:
        print(f"警告: 未设置DEEPSEEK_MODEL_V3环境变量，将使用默认值 'deepseek-chat'")
        model_name = "deepseek-chat"
      # 初始化LLM
    try:
        llm = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=base_url, # 使用从 .env 读取的 base_url
            model_name=model_name,    # 使用从 .env 读取的 model_name
            temperature=0.7,
            request_timeout=120,  # 从 30 修改为 120
            max_retries=3,      # 最多重试3次
            streaming=True      # 启用流式处理
        )
    except Exception as e:
        print(f"初始化LLM时出错: {str(e)}")
        raise
    
    # 初始化嵌入模型
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用设备: {device}")
        
        embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh",
            model_kwargs={"device": device},
            encode_kwargs={
                "normalize_embeddings": True,
                "batch_size": 32 if device == "cuda" else 16  # GPU时增加batch size
            }
        )
    except Exception as e:
        print(f"初始化嵌入模型时出错: {str(e)}")
        raise    # 加载向量库
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
    """格式化前端保存的用户偏好为AI可理解的格式"""
    if not user_pref:
        return "未设置用户偏好"
        
    # 评分项处理
    scores = []
    ratings = user_pref.get("ratings", {})
    mapping = {
        "valueForMoney": "性价比",
        "hygiene": "卫生",
        "environment": "环境",
        "distance": "距离",
        "waitTime": "排队时间",
        "service": "服务",
        "taste": "口味",
        "health": "健康",
        "nutrition": "营养",
        "spiciness": "辣度"
    }
    for key, cn_key in mapping.items():
        if key in ratings:
            scores.append(f"{cn_key}: {ratings[key]}分")
            
    # 预算处理
    price_range = user_pref.get("priceRange", {})
    if price_range:
        min_price = price_range.get("min", 0)
        max_price = price_range.get("max", 999)
        budget_str = f"{min_price}-{max_price}元"
    else:
        budget_str = "未设置"
        
    # 特殊偏好处理
    preferences = user_pref.get("preferences", {})
    allergies = preferences.get("allergies", "无")
    likes = preferences.get("likes", "无")
    dislikes = preferences.get("dislikes", "无")
    
    return (
        f"用户偏好评分:\n{chr(10).join(scores)}\n\n"
        f"预算范围: {budget_str}\n"
        f"过敏和忌口: {allergies}\n"
        f"喜欢的食物: {likes}\n"
        f"不喜欢的食物: {dislikes}"
    )

def extract_preference_vars(user_pref):
    """从用户偏好中提取各项指标"""
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
    
    if not user_pref:
        return default_prefs
    
    # 评分项处理    
    scores = []
    ratings = user_pref.get("ratings", {})
    mapping = {
        "valueForMoney": "性价比",
        "hygiene": "卫生",
        "environment": "环境",
        "distance": "距离",
        "waitTime": "排队时间",
        "service": "服务",
        "taste": "口味",
        "health": "健康",
        "nutrition": "营养",
        "spiciness": "辣度"
    }
    for key, cn_key in mapping.items():
        if key in ratings:
            scores.append(f"{cn_key}: {ratings[key]}分")
            
    # 预算处理
    price_range = user_pref.get("priceRange", {})
    if price_range:
        min_price = price_range.get("min", 0)
        max_price = price_range.get("max", 999)
        budget_range = f"{min_price}-{max_price}元"
    else:
        budget_range = "未设置"
        
    # 特殊偏好处理
    preferences = user_pref.get("preferences", {})
    
    return {
        "preference_scores": "\n".join(scores),
        "budget_range": budget_range,
        "allergies": preferences.get("allergies", "无"),
        "likes": preferences.get("likes", "无"),
        "dislikes": preferences.get("dislikes", "无"),
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
    """设置对话链和记忆"""
    memory = ConversationBufferMemory(
        return_messages=True,
        output_key="answer",
        input_key="question"
    )
    
    # 准备prompt模板
    chat_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=["history", "context", "user_preference", "preference_scores", 
                               "preferred_cuisines", "disliked_cuisines", "budget_range", 
                               "special_requirements"],
                template=system_prompt_template
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=["question"],
                template="{question}"
            )
        )
    ])
    
    reviews_retriever = RunnableLambda(lambda x: x["question"]) | vector_db.as_retriever(search_kwargs={'k': 20,})
    
    review_chain = (
        RunnableMap({
            "history": RunnablePassthrough(lambda _: memory.load_memory_variables({}).get("history", [])),
            "context": reviews_retriever,
            "question": RunnablePassthrough(),
            "user_preference": RunnableLambda(lambda x: format_user_preference(user_preference)),
            "preference_scores": RunnableLambda(lambda x: extract_preference_vars(user_preference)["preference_scores"]),
            "preferred_cuisines": RunnableLambda(lambda x: extract_preference_vars(user_preference).get("preferred_cuisines", [])),
            "disliked_cuisines": RunnableLambda(lambda x: extract_preference_vars(user_preference).get("disliked_cuisines", [])),
            "budget_range": RunnableLambda(lambda x: extract_preference_vars(user_preference).get("budget_range", "未设置")),
            "special_requirements": RunnableLambda(lambda x: extract_preference_vars(user_preference).get("special_requirements", "无"))
        })
        | chat_template
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
            memory.save_context({"question": question}, {"answer": response})
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
