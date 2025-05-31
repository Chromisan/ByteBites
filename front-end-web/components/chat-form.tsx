"use client"

import type React from "react"
import { cn } from "@/lib/utils"
import { useChat } from "ai/react"
import { ArrowUpIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { AutoResizeTextarea } from "@/components/autoresize-textarea"

export const ChatForm = () => {
  const { messages, input, setInput, append } = useChat({
    api: "/api/chat",
    initialMessages: []
  })

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!input.trim()) return
    void append({ content: input, role: "user" })
    setInput("")
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as unknown as React.FormEvent<HTMLFormElement>)
    }
  }

  return (
    <div className="flex flex-col h-full">      <div className="text-center py-8">
        <p className="text-gray-700 text-sm max-w-md mx-auto">
          欢迎来到菜根探！我是您的南大美食助手，专门推荐鼓楼校区周边的美食。您可以告诉我您的预算、口味偏好，我会为您推荐合适的餐厅和美食。
        </p>
      </div><div className="flex-1 overflow-y-auto pb-20">
        <div className="flex flex-col gap-4 p-6">
          {messages.map((message, index) => (
            <div 
              key={message.id ?? index} 
              className={cn("flex", message.role === "user" ? "justify-end" : "justify-start")}
            >
              <div
                className={cn(                  "max-w-[70%] rounded-2xl px-4 py-3 text-sm",
                  message.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900",
                )}
              >
                {message.content}
              </div>
            </div>
          ))}
        </div>
      </div>
      <form onSubmit={handleSubmit} className="sticky bottom-0 w-full p-4 bg-white border-t">
        <div className="flex gap-2">
          <AutoResizeTextarea
            placeholder="输入您的问题..."
            value={input}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 resize-none rounded-2xl border px-4 py-2 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-green-600 min-h-12 max-h-48"
          />
          <Button
            type="submit"
            variant="ghost"
            className="shrink-0 h-12 w-12 rounded-2xl hover:bg-gray-100"
          >
            <ArrowUpIcon className="h-6 w-6 text-green-600" />
          </Button>
        </div>
      </form>
    </div>
  )
}
