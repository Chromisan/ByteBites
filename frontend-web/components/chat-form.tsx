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
  }  // 渲染组件
  return (
    // 主容器 - 科技风格增强
    <div className="flex flex-col h-full bg-amber-100/20 overflow-hidden">{/* 欢迎信息区域 - 科技风格重新设计 */}
      <div className="flex flex-col items-center py-12 px-6 bg-gradient-to-b from-amber-100/50 via-amber-50/30 to-white relative backdrop-blur-sm">        <h1 className="text-4xl font-bold text-amber-800 mb-4 tracking-wide drop-shadow-sm">欢迎来到菜根探</h1>
        <p className="text-lg text-amber-900/70 max-w-2xl text-center mb-8 leading-relaxed">
          我是您的南大美食助手，专门推荐鼓楼校区周边的美食。
          告诉我您的预算和口味偏好，让我为您找到最适合的餐厅。
        </p><div className="flex justify-center gap-16 w-full mb-4">
            <Image
              src="/upfood-icon.png"  
              alt="美食图标"
              width={220}
              height={100} 
              className="rounded-2xl shadow-lg hover:scale-105 transition-transform"
              style={{ objectFit: "contain" }}
            />
          
            <Image
              src="/upfood2-icon.png"
              alt="美食图标"
              width={220}
              height={100}
              className="rounded-2xl shadow-lg hover:scale-105 transition-transform"
              style={{ objectFit: "contain" }}
            />
          </div>

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
      </div>      {/* 消息显示区域 - 科技风格增强 */}
      <div className="flex-1 overflow-y-auto pb-20 bg-gradient-to-b from-white via-amber-50/40 to-amber-100/40">
        <div className="flex flex-col gap-4 p-6 max-w-3xl mx-auto w-full rounded-2xl min-h-[120px]">
          
          {/* 遍历并渲染所有消息 */}
          {messages.map((message, index) => (
            <div 
              key={message.id ?? index} 
              className={cn("flex", 
                message.role === "user" ? "justify-end" : "justify-start"  // 用户消息靠右，AI消息靠左
              )}
            >              <div
                className={cn(
                  "max-w-[70%] rounded-2xl px-5 py-4 shadow-md text-base",
                  message.role === "user" 
                    ? "bg-amber-200/90 text-amber-950 border border-amber-300/70 backdrop-blur-sm"  // 用户消息样式
                    : "bg-white/90 text-amber-900 border border-amber-200/70 backdrop-blur-sm"  // AI消息样式
                )}
              >
                {message.content}
              </div>
            </div>
          ))}
        </div>
      </div>      {/* 输入区域 - 科技风格增强 */}
      <form onSubmit={handleSubmit} className="sticky bottom-0 w-full p-4 bg-gradient-to-t from-amber-100/40 to-amber-50/30 border-t border-amber-200/50 shadow-lg backdrop-blur-sm">
        <div className="flex gap-3 max-w-3xl mx-auto">
          {/* 自适应文本输入框 */}
          <AutoResizeTextarea
            placeholder={isLoading ? "正在思考中..." : "请告诉我您的用餐需求..."}
            value={input}
            disabled={isLoading}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 resize-none rounded-xl border border-amber-400/50 px-4 py-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600 min-h-14 max-h-48 shadow-inner bg-white/80 text-amber-900"
          />
          {/* 发送按钮 */}
          <Button
            type="submit"
            variant="ghost"
            disabled={isLoading || !input.trim()}
            className={cn(
              "shrink-0 h-14 w-14 rounded-full shadow-md flex items-center justify-center",
              isLoading 
                ? "bg-gray-200 cursor-not-allowed"
                : "bg-amber-700 hover:bg-amber-800 transition-colors"
            )}
          >
            {isLoading ? (
              <div className="h-6 w-6 animate-spin rounded-full border-3 border-white border-t-transparent" />
            ) : (
              <ArrowUpIcon className="h-6 w-6 text-white" />
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}
