import { ChatForm } from "@/components/chat-form"
import { UserNav } from "@/components/user-nav" 

export default function ChatbotPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="flex h-16 items-center border-b px-4 w-full justify-end">
        <UserNav />
      </header>
      <div className="flex-1">
        <ChatForm />
      </div>
    </div>
  )
}
