from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from backend.chatbot import Chatbot
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# 数据模型
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    error: Optional[str] = None
    
class HistoryEntry(BaseModel):
    timestamp: str
    user: str
    bot: str

# 获取Chatbot实例
chatbot = Chatbot.get_instance()

@router.post("/send", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """处理用户的聊天请求"""
    try:
        logger.info(f"收到聊天请求体: {request}")
        logger.info(f"用户消息内容: {request.message}")
        response = chatbot.chat(request.message)
        logger.info(f"成功生成回复: {response[:100]}...")  # 只记录前100个字符
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        logger.error(f"错误类型: {type(e)}")
        return ChatResponse(
            response="",
            error=f"处理请求时发生错误: {str(e)}"
        )

@router.get("/history", response_model=List[HistoryEntry])
async def get_history():
    """获取聊天历史"""
    try:
        logger.info("获取聊天历史")
        history = chatbot.get_history()
        logger.info(f"成功获取历史记录，共 {len(history)} 条")
        return history
    except Exception as e:
        logger.error(f"获取历史记录时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取历史记录时出错: {str(e)}"
        )

@router.post("/clear-history")
async def clear_history():
    """清空聊天历史"""
    try:
        logger.info("清空聊天历史")
        chatbot.clear_history()
        logger.info("聊天历史已清空")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"清空历史记录时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"清空历史记录时出错: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        history = chatbot.get_history()
        return {
            "status": "ok",
            "components": {
                "chatbot": "active",
                "history": len(history)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }
