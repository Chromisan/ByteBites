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

## 第一次运行的初始化步骤
**注：不需要运行此步骤，因为初始化后的数据已经上传到git了。**
### 初始化向量数据库
~~首次运行系统之前，需要先初始化向量数据库。切换到项目根目录，输入以下命令：~~
```powershell
cd ByteBites
$env:PYTHONPATH = "."  # 设置Python路径
python backend/init_vectordb.py  # 初始化向量数据库（首次运行需要，可能需要几分钟）
```

## 启动系统
### 启动后端服务器
切换到项目根目录，输入以下命令行命令启动后端服务器：
```bash
cd backend
$env:PYTHONPATH = "."  # 设置Python路径
python backend/main.py  # 启动后端服务器
```
服务器将在 http://localhost:8000 上运行。

### 启动前端服务器
切换到前端目录，在另一个终端窗口启动前端开发服务器：
```bash
cd ..\frontend-web
pnpm dev
```
这个命令会启动一个本地开发服务器，通常在 http://localhost:3000 上运行。
打开浏览器，访问：http://localhost:3000 即可看到网页。

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

> 注：若报错Module not found: Can't resolve '@/lib/utils'
表示项目的根目录下缺少了 lib/utils.ts 文件。
你需要：
  1. 打开cmd，cd至项目的文件夹，输入：
  mkdir lib
  echo. > lib/utils.ts
  上述操作创建了lib文件夹，并在其中创建了utils.ts文件。
  1. 打开新创建的 utils.ts 文件
   添加代码：
   import { type ClassValue, clsx } from "clsx"
   import { twMerge } from "tailwind-merge"
   
   export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
    }
  2. 打开终端，输入下面的命令，安装需要的依赖：
   pnpm add clsx tailwind-merge