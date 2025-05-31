"use client"

import type React from "react"
import Image from "next/image"
import { cn } from "@/lib/utils"
import { useChat } from "ai/react"
import { ArrowUpIcon, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from "@/components/ui/tooltip"
import { AutoResizeTextarea } from "@/components/autoresize-textarea"

export function ChatForm({ className, ...props }: React.ComponentProps<"form">) {
  const { messages, input, setInput, append } = useChat({
    api: "/api/chat",
  })

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    void append({ content: input, role: "user" })
    setInput("")
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as unknown as React.FormEvent<HTMLFormElement>)
    }
  }

  const header = (
    <div className="text-center py-8">
      <p className="text-gray-700 text-sm max-w-md mx-auto">
        欢迎来到菜根探！我是您的美食助手，可以为您推荐菜谱、介绍美食文化，或者回答任何关于饮食的问题。
      </p>
    </div>
  )

  const messageList = (
    <div className="flex flex-col gap-4 p-6">
      {messages.map((message, index) => (
        <div key={index} className={cn("flex", message.role === "user" ? "justify-end" : "justify-start")}>
          <div
            className={cn(
              "max-w-[70%] rounded-2xl px-4 py-3 text-sm",
              message.role === "user" ? "bg-green-500 text-white" : "bg-orange-400 text-white",
            )}
          >
            {message.content}
          </div>
        </div>
      ))}
    </div>
  )

  return (
    <div className="min-h-screen bg-[#c9d4c5] relative overflow-hidden">
      {/* Left side food icons with blur effect */}
      <div className="absolute left-2 xl:left-8 top-1/2 -translate-y-1/2 flex flex-col gap-6">
        <div className="relative">
          <div
            className="absolute inset-0 bg-[#c9d4c5] opacity-0 
            [mask-image:linear-gradient(to_right,transparent_0%,rgba(0,0,0,0.7)_10%,rgba(0,0,0,1)_20%)] 
            pointer-events-none z-10"
          ></div>
          <div className="relative overflow-hidden">
            <Image
              src="/food-icons-left.png"
              alt="Food icons"
              width={76}
              height={380}
              className="object-contain"
              style={{
                maskImage: "linear-gradient(to right, transparent, #c9d4c5 5%, #c9d4c5 95%, transparent)",
                WebkitMaskImage: "linear-gradient(to right, transparent, #c9d4c5 5%, #c9d4c5 95%, transparent)",
              }}
            />
          </div>
        </div>
      </div>

      {/* Right side food icons with blur effect */}
      <div className="absolute right-2 xl:right-8 top-1/2 -translate-y-1/2 flex flex-col gap-6">
        <div className="relative">
          <div
            className="absolute inset-0 bg-[#c9d4c5] opacity-0 
            [mask-image:linear-gradient(to_left,transparent_0%,rgba(0,0,0,0.7)_10%,rgba(0,0,0,1)_20%)] 
            pointer-events-none z-10"
          ></div>
          <div className="relative overflow-hidden">
            <Image
              src="/food-icons-right.png"
              alt="Food icons"
              width={78}
              height={400}
              className="object-contain"
              style={{
                maskImage: "linear-gradient(to left, transparent, #c9d4c5 5%, #c9d4c5 95%, transparent)",
                WebkitMaskImage: "linear-gradient(to left, transparent, #c9d4c5 5%, #c9d4c5 95%, transparent)",
              }}
            />
          </div>
        </div>
      </div>

      <main className={cn("mx-auto flex h-screen max-h-screen w-full max-w-4xl flex-col", className)} {...props}>
        {/* Header with title and user icon */}
        <div className="flex items-center justify-between p-6">
          <div className="flex-1" />
          <h1 className="text-3xl font-bold text-black">菜根探</h1>
          <div className="flex-1 flex justify-end">
            <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        {/* Chat area */}
        <div className="flex-1 mx-8 lg:mx-12 mb-6 bg-yellow-100 rounded-3xl overflow-hidden flex flex-col shadow-md">
          <div className="flex-1 overflow-y-auto">{messages.length ? messageList : header}</div>

          {/* Input area */}
          <div className="p-6">
            <TooltipProvider>
              <form
                onSubmit={handleSubmit}
                className="bg-white rounded-2xl border border-gray-200 p-4 flex items-center gap-3"
              >
                <AutoResizeTextarea
                  onKeyDown={handleKeyDown}
                  onChange={(v) => setInput(v)}
                  value={input}
                  placeholder="输入文字，你想吃啥？"
                  className="flex-1 bg-transparent border-none outline-none resize-none text-gray-700 placeholder-gray-500"
                />
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      type="submit"
                      size="sm"
                      className="w-10 h-10 rounded-full bg-green-600 hover:bg-green-700 text-white p-0"
                    >
                      <ArrowUpIcon size={16} />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent sideOffset={12}>发送</TooltipContent>
                </Tooltip>
              </form>
            </TooltipProvider>
          </div>
        </div>
      </main>
    </div>
  )
}
