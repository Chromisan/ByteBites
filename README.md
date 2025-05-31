# 关于网页版前端使用
## 确保电脑上安装了Node.js
所有的前端动态功能（包括点击按钮跳转页面、滑动条、用户输入数据等）都需要用到javascript，而javascript运行环境则需要Node.js（前端依赖都通过package.json管理）。如果你的电脑上没有安装过Node.js，应该在官网下载并安装它。

可以通过命令行命令
```bash
node -v  # 应显示版本号（如v18.16.0）
npm -v   # 应显示版本号（如9.5.1）
```
来检查是否安装成功。npm就是Node.js的包管理器，用来安装和管理Node.js的第三方模块，相当于Python的pip。

## 安装pnpm
pnpm是npm的替代品，可以加速Node.js项目的依赖安装。
输入以下命令行命令：
```bash
cd front-end-web
npm install -g pnpm@latest-10
```

## 使用pnpm安装前端所用到的依赖包
输入以下命令行命令：
```bash
pnpm install
```

## 运行开发服务器
输入以下命令行命令：
```bash
pnpm dev
```
这个命令会启动一个本地开发服务器，通常在 http://localhost:3000 上运行。
打开浏览器，访问：http://localhost:3000 即可看到网页。

> 注：若报错Module not found: Can't resolve '@/lib/utils'
表示项目的根目录下缺少了 lib/utils.ts 文件。
你需要：
  1. 打开cmd，cd至项目的文件夹，输入：
  mkdir lib
  echo. > lib/utils.ts
  上述操作创建了lib文件夹，并在其中创建了utils.ts文件。
  2. 打开新创建的 utils.ts 文件
   添加代码：
   import { type ClassValue, clsx } from "clsx"
   import { twMerge } from "tailwind-merge"
   
   export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
    }
  3. 打开终端，输入下面的命令，安装需要的依赖：
   pnpm add clsx tailwind-merge