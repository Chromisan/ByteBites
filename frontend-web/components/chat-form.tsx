// 声明此组件为客户端组件
"use client"

// 导入必要的依赖
import type React from "react"
import { cn } from "@/lib/utils"          // 用于合并class名称的工具函数
import { useChat } from "ai/react"        // Vercel AI SDK的聊天hooks
import { ArrowUpIcon } from "lucide-react" // 发送按钮图标
import { Button } from "@/components/ui/button"
import { AutoResizeTextarea } from "@/components/autoresize-textarea"
import Image from 'next/image'  // 添加在文件顶部的导入部分

// 聊天表单组件定义
export const ChatForm = () => {
  // 初始化聊天功能
  const { messages, input, setInput, append } = useChat({
    api: "/api/chat",         // 聊天API端点
    initialMessages: []       // 初始化空消息列表
  })

  // 处理表单提交事件
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()              // 阻止表单默认提交行为
    if (!input.trim()) return      // 如果输入为空则返回
    void append({ content: input, role: "user" }) // 添加用户消息到对话
    setInput("")                   // 清空输入框
  }

  // 处理按键事件（用于回车发送消息）
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {  // 如果按下回车键且没有按下Shift键
      e.preventDefault()
      handleSubmit(e as unknown as React.FormEvent<HTMLFormElement>)
    }
  }

  // 渲染组件
  return (
    // 主容器
    <div className="flex flex-col h-full bg-white ">
      {/* 欢迎信息区域 */}
      <div className="text-center py-8 relative flex items-center justify-center gap-8 rounded-2xl">
        {/* 上面装饰图片 */}
        <Image
          src="/upfood-icon.png"  
          alt="装饰图"
          width={400}
          height={150}
          className="object-cover rounded-2xl"
        />
        
        <p className="text-gray-700 text-sm max-w-md">
          欢迎来到菜根探！我是您的南大美食助手，专门推荐鼓楼校区周边的美食。您可以告诉我您的预算、口味偏好，我会为您推荐合适的餐厅和美食。
        </p>
                {/* 装饰图片容器 - 移动到消息区域内部的底部 */}
          <Image
            src="/upfood2-icon.png"
            alt="装饰图"
            width={300}
            height={100}
            className="object-cover rounded-2xl"
          />


      </div>

      {/* 消息显示区域 */}
      <div className="flex-1 overflow-y-auto pb-20 ">
        <div className="flex flex-col gap-4 p-6 max-w-3x1 mx-auto w-full  rounded-2xl  min-h-[120px]">
          {/* 遍历并渲染所有消息 */}
          {messages.map((message, index) => (
            <div 
              key={message.id ?? index} 
              className={cn("flex", 
                message.role === "user" ? "justify-end" : "justify-start"  // 用户消息靠右，AI消息靠左
              )}
            >
              <div
                className={cn(
                  "max-w-[70%] rounded-2xl px-4 py-3 text-sm",
                  message.role === "user" 
                    ? "bg-yellow-300 text-black"     // 用户消息样式：绿色背景
                    : "bg-orange-400 text-black"   // AI消息样式：灰色背景
                )}
              >
                {message.content}
              </div>
            </div>
          ))}
        </div>

      </div>
      

      {/* 输入区域 */}
      <form onSubmit={handleSubmit} className="sticky bottom-0 w-full p-4 bg-white border-t">
        <div className="flex gap-2 min-h-[100px]">
          {/* 自适应文本输入框 */}
          <AutoResizeTextarea
            placeholder="您想吃点啥..."
            value={input}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 resize-none rounded-2xl border px-4 py-2 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber-600 min-h-12 max-h-48"
          />
          {/* 发送按钮 */}
          <Button
            type="submit"
            variant="ghost"
            className="shrink-0 h-10 w-10 rounded-full bg-yellow-300 hover:bg-yellow-500"
          >
            <ArrowUpIcon className="h-10 w-10 text-black" />
          </Button>
        </div>
      </form>
    </div>
  )
}
