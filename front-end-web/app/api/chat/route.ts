import { StreamingTextResponse } from 'ai';
import { env } from "@/env.mjs";

export const runtime = 'edge';

if (!env.DEEPSEEK_API_KEY) {
  throw new Error("缺少 DEEPSEEK_API_KEY 环境变量");
}

export async function POST(req: Request) {
  const { messages } = await req.json();
  
  // 创建请求到 DeepSeek API
  const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${env.DEEPSEEK_API_KEY}`
    },
    body: JSON.stringify({
      model: 'deepseek-chat',
      messages: [
        {
          role: "system",
          content: `你是一个专注于南京大学鼓楼校区周边美食推荐的AI助手。你需要：
1. 根据用户的具体需求（如预算、口味偏好、就餐时间等）推荐合适的餐厅
2. 可以提供餐厅的具体位置、价格区间、招牌菜等信息
3. 分享关于推荐餐厅的用户评价和实际就餐体验
4. 注意推荐的餐厅应该在南京大学鼓楼校区3公里范围内
5. 如果用户询问具体菜品，优先推荐当地特色美食和网友好评的招牌菜

请用友好、专业的语气与用户交流，给出具体、实用的建议。对于超出你知识范围的问题，请诚实告知并建议用户自行验证信息。`
        },
        ...messages
      ],
      stream: true,
      temperature: 0.7,
      max_tokens: 1000
    })
  });

  // 返回流响应
  return new StreamingTextResponse(response.body as ReadableStream);
}
