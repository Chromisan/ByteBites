from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os
from typing import Dict, Union

router = APIRouter()  # 使用 APIRouter 而不是 FastAPI 实例

class UserPreferences(BaseModel):
    priceRange: Dict[str, float]
    ratings: Dict[str, float]
    preferences: Dict[str, str]

@router.post("/api/preferences")
async def save_preferences(preferences: UserPreferences):
    try:
        # 确保保存路径存在
        save_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(save_dir, exist_ok=True)
        
        # 使用绝对路径保存文件
        file_path = os.path.join(save_dir, "user_preferences.json")
        
        # 打印调试信息
        print(f"Saving preferences to: {file_path}")
        print(f"Preferences data: {preferences.dict()}")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(preferences.dict(), f, ensure_ascii=False, indent=2)
        
        print("Successfully saved preferences")
        return {"status": "success"}
    except Exception as e:
        print(f"Error saving preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
