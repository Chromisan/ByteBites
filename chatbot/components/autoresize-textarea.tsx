// 声明此组件为客户端组件
"use client"

// 导入必要的依赖
import { cn } from "@/lib/utils"          // 用于合并className的工具函数
import { useRef, useEffect, type TextareaHTMLAttributes } from "react"

// 定义组件属性接口
// 继承原生textarea的属性，但排除value和onChange，因为我们要自定义这两个属性
interface AutoResizeTextareaProps extends Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, "value" | "onChange"> {
  value: string                    // 输入框的值
  onChange: (value: string) => void // 值改变时的回调函数
}

// 自适应高度的文本框组件
export function AutoResizeTextarea({ 
  className,     // 自定义样式类名
  value,         // 输入值
  onChange,      // 值变化处理函数
  ...props       // 其他textarea原生属性
}: AutoResizeTextareaProps) {
  // 创建对textarea元素的引用
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // 调整文本框高度的函数
  const resizeTextarea = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = "auto"      // 先重置高度
      textarea.style.height = `${textarea.scrollHeight}px` // 设置为内容实际高度
    }
  }

  // 当输入值改变时，自动调整高度
  useEffect(() => {
    resizeTextarea()
  }, [value])

  // 渲染textarea元素
  return (
    <textarea
      {...props}              // 展开其他属性
      value={value}          // 受控组件的值
      ref={textareaRef}      // 设置引用
      rows={1}               // 初始行数为1
      onChange={(e) => {     // 处理值变化
        onChange(e.target.value)
        resizeTextarea()     // 调整高度
      }}
      // 合并默认样式和自定义样式
      className={cn(
        "resize-none min-h-6 max-h-32 outline-none border-none", // 基础样式
        className  // 自定义样式
      )}
    />
  )
}
