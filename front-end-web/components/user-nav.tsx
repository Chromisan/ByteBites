"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { useRouter } from 'next/navigation'

export function UserNav() {
  const router = useRouter()
  
  return (
    <Button
      variant="ghost"
      className="relative h-8 w-8 rounded-full"
      onClick={() => router.push('/preferences')}
    >
      <Avatar className="h-8 w-8">
        <AvatarImage src="/placeholder-user.jpg" alt="User photo" />
        <AvatarFallback>U</AvatarFallback>
      </Avatar>
    </Button>
  )
}
