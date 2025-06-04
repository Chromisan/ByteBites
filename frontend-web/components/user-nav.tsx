"use client"// 声明这是一个客户端组件
// 导入必要的组件和钩子
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { useRouter } from 'next/navigation'

/**
 * 用户导航组件
 * 显示标题与用户头像并处理导航到用户偏好页面
 */
export function UserNav() {
  // 初始化路由器实例，用于页面导航
  const router = useRouter()
  
  


  return (
    <nav className="fixed top-0 z-50 w-full flex items-center justify-between p-4 border-b-2 bg-amber-300">
      {/* 左侧空白区域 */}
      <div className="flex-1" />
      
      {/* 中间标题 */}
      <h1 className="text-3xl font-bold text-black">菜根探</h1>
      
      {/* 右侧用户头像 */}
      <div className="flex-1 flex justify-end">
          <Button
            variant="default"
            className="relative h-8 w-8 rounded-full bg-orange-500 hover:bg-orange-600"
            onClick={() => router.push('/preferences')}
          >
          <Avatar className="h-7 w-7">
            <AvatarImage 
              src="/default_avatar.png" // 默认头像图片路径
              alt="User photo"// 图片替代文本
            />
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
        </Button>
      </div>
    </nav>
  )
}