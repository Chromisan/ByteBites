"use client"

import { useEffect } from "react"

export function useAutoResize(element: HTMLTextAreaElement | null) {
  useEffect(() => {
    if (!element) return

    const resize = () => {
      element.style.height = "auto"
      element.style.height = element.scrollHeight + "px"
    }

    element.addEventListener("input", resize)
    window.addEventListener("resize", resize)
    resize()

    return () => {
      element.removeEventListener("input", resize)
      window.removeEventListener("resize", resize)
    }
  }, [element])
}
