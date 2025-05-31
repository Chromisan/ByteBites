import { type CoreMessage, streamText } from "ai"
import { openai } from "@ai-sdk/openai"

export async function POST(req: Request) {
  const { messages }: { messages: CoreMessage[] } = await req.json()

  const result = streamText({
    model: openai("gpt-4o-mini"),
    system:
      "你是菜根探的美食助手，专门帮助用户解答关于美食、菜谱、饮食文化的问题。你可以推荐菜谱、介绍各地美食、提供烹饪技巧，并且总是以友好、专业的态度回答用户的问题。",
    messages,
  })

  return result.toDataStreamResponse()
}
