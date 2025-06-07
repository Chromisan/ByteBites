// 声明此组件为客户端组件
"use client"

// 导入必要的依赖
import React, { useState, useEffect } from "react"
import { cn } from "@/lib/utils"          // 用于合并class名称的工具函数
import { useChat } from "ai/react"        // Vercel AI SDK的聊天hooks
import { ArrowUpIcon } from "lucide-react" // 发送按钮图标
import { Button } from "@/components/ui/button"
import { AutoResizeTextarea } from "@/components/autoresize-textarea"
import Image from 'next/image'  // 添加在文件顶部的导入部分

// 类型定义
interface HistoryEntry {
  timestamp: string;
  user: string;
  bot: string;
}

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
}

// 聊天表单组件定义
export const ChatForm = () => {
  const [initialMessages, setInitialMessages] = React.useState<Message[]>([])
  const [isClearing, setIsClearing] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<Message[]>([])

  // 加载历史记录
  React.useEffect(() => {
    fetch('http://localhost:8000/chat/history')
      .then(res => {
        if (!res.ok) {
          throw new Error('Failed to load chat history')
        }
        return res.json()
      })
      .then((history: HistoryEntry[]) => {
        if (!Array.isArray(history)) {
          throw new Error('Invalid history data format')
        }
        const messages: Message[] = []
        history.forEach((entry: HistoryEntry) => {
          messages.push({
            id: entry.timestamp,
            content: entry.user,
            role: 'user'
          })
          messages.push({
            id: entry.timestamp + '_response',
            content: entry.bot,
            role: 'assistant'
          })
        })
        setInitialMessages(messages)
        setMessages(messages) // 设置初始消息
        setErrorMessage(null)
      })
      .catch(err => {
        console.error('Failed to load chat history:', err)
        setErrorMessage('无法加载聊天历史，但您仍然可以继续对话。')
      })
  }, [])

  // 初始化聊天功能
  const [isLoading, setIsLoading] = useState(false);

  const handleChat = async (userMessage: string) => {
    try {
      const response = await fetch('http://localhost:8000/chat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || '聊天请求失败');
      }

      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      return data.response;
    } catch (error) {
      console.error('Chat error:', error);
      throw error;
    }
  };

  // 清除历史记录函数
  const clearHistory = async () => {
    if (isClearing) return
    
    if (!window.confirm('确定要清除所有聊天记录吗？此操作不可撤销。')) {
      return
    }
    
    setIsClearing(true)
    try {
      const response = await fetch('http://localhost:8000/chat/clear-history', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        setInitialMessages([])
        setMessages([]) // 清除当前对话
        setErrorMessage(null)
        // 显示轻量级的成功提示
        const successMessage = document.createElement('div')
        successMessage.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg transition-opacity duration-500'
        successMessage.textContent = '聊天记录已清除'
        document.body.appendChild(successMessage)
        setTimeout(() => {
          successMessage.style.opacity = '0'
          setTimeout(() => {
            document.body.removeChild(successMessage)
          }, 500)
        }, 2000)
      } else {
        const error = await response.text()
        throw new Error(error)
      }
    } catch (err) {
      console.error('Error clearing history:', err)
      setErrorMessage('清除历史记录失败，请稍后重试')
    } finally {
      setIsClearing(false)
    }
  }
  
  // 处理表单提交事件
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    try {
      setIsLoading(true);
      setErrorMessage(null);  // 清除之前的错误信息
      const userMessage = input;
      setInput("");  // 清空输入框

      // 添加用户消息到对话
      const userMsg: Message = { 
        role: 'user', 
        content: userMessage, 
        id: Date.now().toString() 
      };
      setMessages(prev => [...prev, userMsg]);

      // 获取AI回复
      const aiResponse = await handleChat(userMessage);
      
      // 添加AI回复到对话
      const aiMsg: Message = { 
        role: 'assistant', 
        content: aiResponse, 
        id: Date.now().toString() + '_response' 
      };
      setMessages(prev => [...prev, aiMsg]);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '发送消息失败，请重试';
      setErrorMessage(errorMessage);
      console.error('Send message error:', err);
    } finally {
      setIsLoading(false);
    }
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
    <div className="flex flex-col h-full bg-white">
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


        {/* 改进的清除历史按钮样式和位置 */}
        <Button
          onClick={clearHistory}
          disabled={isClearing || initialMessages.length === 0}
          className={cn(
            "absolute top-4 right-4 px-3 py-1 text-sm rounded-lg",
            isClearing ? 
              "bg-gray-300 cursor-not-allowed" : 
              initialMessages.length === 0 ?
                "bg-gray-200 cursor-not-allowed text-gray-500" :
                "bg-red-500 hover:bg-red-600 text-white"
          )}
        >
          {isClearing ? "正在清除..." : 
           initialMessages.length === 0 ? "无历史记录" : 
           "清除历史"}
        </Button>
      </div>

      {/* 消息显示区域 */}      <div className="flex-1 overflow-y-auto pb-20">
        <div className="flex flex-col gap-4 p-6 max-w-3xl mx-auto w-full rounded-2xl min-h-[120px]">
          
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
            placeholder={isLoading ? "正在思考中..." : "您想吃点啥..."}
            value={input}
            disabled={isLoading}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 resize-none rounded-2xl border px-4 py-2 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber-600 min-h-12 max-h-48"
          />          {/* 发送按钮 */}
          <Button
            type="submit"
            variant="ghost"
            disabled={isLoading || !input.trim()}
            className={cn(
              "shrink-0 h-10 w-10 rounded-full",
              isLoading 
                ? "bg-gray-200 cursor-not-allowed"
                : "bg-yellow-300 hover:bg-yellow-500"
            )}
          >
            {isLoading ? (
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-400 border-t-transparent" />
            ) : (
              <ArrowUpIcon className="h-10 w-10 text-black" />
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}
