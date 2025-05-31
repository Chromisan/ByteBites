"use client"

import * as React from "react"
import { useAutoResize } from "@/hooks/use-autoresize"

export const AutoResizeTextarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>((props, ref) => {
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)

  React.useImperativeHandle(ref, () => textareaRef.current as HTMLTextAreaElement)
  
  useAutoResize(textareaRef.current)

  return <textarea ref={textareaRef} rows={1} {...props} />
})

AutoResizeTextarea.displayName = "AutoResizeTextarea"
