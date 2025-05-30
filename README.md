# 关于网页版前端
## 确保电脑上安装了Node.js
为了实现动态网页组件功能（react组件），需要安装shadcn服务。这要通过Node.js安装（前端依赖都通过package.json管理）。如果你的电脑上没有安装过Node.js，应该在官网下载并安装它。

可以通过命令行命令
```bash
node -v  # 应显示版本号（如v18.16.0）
npm -v   # 应显示版本号（如9.5.1）
```
来检查是否安装成功。npm就是Node.js的包管理器，用来安装和管理Node.js的第三方模块，相当于Python的pip。

## Node服务初始化
输入以下命令行命令：
```bash
cd front-end/react-app # 跳转到react组件库所在的文件夹
npm install  # 自动安装所有依赖
```

注：如果试图在一片空白的、没有部署过任何前端代码的库中，从v0.dev等线上前端开发代码平台部署前端，可以这样做：
首先输入以下命令行命令来初始化shadcn服务：
```bash
cd front-end/react-app # 跳转到react组件库所在的文件夹
npx shadcn@latest init    # 首次初始化
```

