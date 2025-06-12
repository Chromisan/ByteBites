# ByteBites - 智能餐厅推荐系统

ByteBites 是一款基于大型语言模型 (LLM) 的智能餐厅推荐聊天机器人。它旨在通过自然语言对话，根据用户的个性化偏好 (如口味、菜系、预算、用餐场合等) 和实时需求 (如当前位置、时间)，从现有的餐厅数据库中为用户推荐最合适的餐厅。

## 主要功能

*   **个性化推荐**: 理解用户的复杂查询，并提供个性化的餐厅建议。
*   **多轮对话**: 支持多轮对话，允许用户逐步定义他们的需求。
*   **Markdown 输出**: 以美观易读的 Markdown 格式展示餐厅信息和推荐理由，包括表格和重点标记。
*   **前端交互界面**: 提供一个现代化的 Web 聊天界面，方便用户与机器人进行交互。

## 技术栈

*   **后端**: Python, FastAPI, Langchain, OpenAI (或其他 LLM), FAISS (向量数据库)
*   **前端**: Next.js, React, TypeScript, Tailwind CSS
*   **数据**: 餐厅信息存储在结构化数据中，并通过向量数据库进行高效检索。

# 关于网页版前端使用
## 准备工作
### 确保电脑上安装了Node.js
所有的前端动态功能（包括点击按钮跳转页面、滑动条、用户输入数据等）都需要用到javascript，而javascript运行环境则需要Node.js（前端依赖都通过package.json管理）。如果你的电脑上没有安装过Node.js，应该在官网下载并安装它。

可以通过命令行命令
```bash
node -v  # 应显示版本号（如v18.16.0）
npm -v   # 应显示版本号（如9.5.1）
```
来检查是否安装成功。npm就是Node.js的包管理器，用来安装和管理Node.js的第三方模块，相当于Python的pip。

### 安装pnpm
pnpm是npm的替代品，可以加速Node.js项目的依赖安装。
输入以下命令行命令：
```bash
cd frontend-web
npm install -g pnpm@latest-10
```

### 使用pnpm安装前端所用到的依赖包
输入以下命令行命令：
```bash
pnpm install
```

## 部署与启动

### 1. 环境配置

*   **Python 环境**: 建议使用虚拟环境 (如 venv 或 conda)。安装 `requirements.txt` 中的依赖：
    ```bash
    pip install -r backend/requirements.txt
    ```
*   **Node.js 环境**: 确保已安装 Node.js 和 pnpm (参见上面的“准备工作”)。

*   **环境变量**:
    *   在 `backend` 目录下创建一个 `.env` 文件，并配置必要的环境变量，例如 OpenAI API 密钥：
        ```env
        OPENAI_API_KEY="your_openai_api_key_here"
        # 其他可能的配置，如数据库连接字符串等
        ```

### 2. 初始化向量数据库 (首次运行)
**注：如果 `backend/vector_store/faiss_index` 目录已存在并且包含数据，则可以跳过此步骤。**
切换到项目根目录 (`ByteBites`)，然后执行初始化脚本：
```powershell
# 在项目根目录 ByteBites 下运行
$env:PYTHONPATH = "."  # Windows PowerShell，设置 Python 模块搜索路径
# 对于 bash/zsh:
# export PYTHONPATH="."
python backend/init_vectordb.py
```
此脚本会读取餐厅数据，生成文本嵌入，并构建 FAISS 索引用于高效相似性搜索。根据数据量大小，这可能需要几分钟。

### 3. 启动后端 FastAPI 服务器
切换到项目根目录 (`ByteBites`)，然后启动后端服务器：
```powershell
# 在项目根目录 ByteBites 下运行
$env:PYTHONPATH = "." # Windows PowerShell
# 对于 bash/zsh:
# export PYTHONPATH="."
python backend/main.py
```
服务器默认将在 `http://localhost:8000` 上运行。您应该会在终端看到类似 "Uvicorn running on http://0.0.0.0:8000" 的输出。

### 4. 启动前端 Next.js 开发服务器
打开一个新的终端窗口。切换到前端目录 (`frontend-web`)，然后启动开发服务器：
```bash
cd frontend-web
pnpm install # 确保所有依赖已安装
pnpm dev
```
这个命令会启动一个本地开发服务器，通常在 `http://localhost:3001` 上运行 (注意端口号可能与旧文档中的 3000 不同，以 Next.js 默认或 `package.json` 配置为准)。

### 5. 访问应用
打开您的网络浏览器，并访问前端服务器的地址 (通常是 `http://localhost:3001`)。您现在应该可以看到 ByteBites 的聊天界面。

## 使用指南

1.  **打开应用**: 在浏览器中输入前端应用的 URL (例如 `http://localhost:3001`)。
2.  **开始对话**: 您会看到一个聊天输入框。在输入框中输入您对餐厅的要求。例如：
    *   "我想找一家适合情侣约会的西餐厅，预算在人均200元左右。"
    *   "附近有什么好吃的川菜馆吗？要辣一点的。"
    *   "推荐几家有素食选择的餐厅。"
3.  **发送消息**: 输入完毕后，点击发送按钮或按 Enter 键。
4.  **查看推荐**: 聊天机器人会处理您的请求，并在聊天界面中以 Markdown 格式返回推荐的餐厅列表和详细理由。这可能包括：
    *   一个包含餐厅名称、菜系、地址、人均消费和推荐指数的表格。
    *   对每家推荐餐厅的更详细描述，包括特色菜、环境氛围以及为什么它符合您的需求。
5.  **进一步提问**: 如果您对推荐不满意，或者想了解更多信息，可以继续提问。例如：
    *   "第一家餐厅有包间吗？"
    *   "还有其他类似价位的日料店推荐吗？"
    *   "帮我看看[餐厅名称]的评价怎么样。"
6.  **享受美食**: 根据机器人的推荐，选择您心仪的餐厅，祝您用餐愉快！

## 生产环境部署 (可选)

### 前端
```bash
cd frontend-web
pnpm build  # 构建生产版本
pnpm start  # 启动生产服务器
```

### 后端
对于后端生产环境，建议使用 Gunicorn 或类似 WSGI 服务器配合 Uvicorn worker 运行 FastAPI 应用，并考虑使用 Supervisor 或 systemd 进行进程管理。

例如，使用 Gunicorn:
```bash
# 在 backend 目录下
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0:8000
```

## 停止服务
如果想取消进程，在命令行中输入：
```bash
Stop-Process -Name "node" -Force  # 停止前端服务器
Stop-Process -Name "python" -Force  # 停止后端服务器
```
或者在各自的终端窗口中按 Ctrl+C 来优雅地停止服务器。

## 启动顺序说明
1. 首先启动后端服务器
2. 然后启动前端服务器
3. 最后在浏览器中访问前端页面

请注意：
- 后端服务器必须在前端服务器之前启动
- 确保后端服务器运行在 http://localhost:8000
- 确保前端服务器运行在 http://localhost:3000
- 两个服务器都需要保持运行状态

## 常见问题排查
1. 如果出现"无法加载聊天历史"错误：
   - 检查后端服务器是否正常运行
   - 检查终端中是否有错误信息
   - 确认环境变量 PYTHONPATH 已正确设置

2. 如果前端无法连接到后端：
   - 确保后端服务器正在运行
   - 检查浏览器控制台是否有错误信息
   - 验证是否能访问 http://localhost:8000/chat/health

3. 如果遇到 Python 导入错误：
   - 确保在正确的目录下运行命令
   - 确保已设置 PYTHONPATH
   - 确保已安装所有必要的 Python 依赖（requirements.txt）