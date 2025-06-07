import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.preferences import router as preferences_router

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含偏好设置路由
app.include_router(preferences_router)

if __name__ == "__main__":
    print("Starting FastAPI server at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
