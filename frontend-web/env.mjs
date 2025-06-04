import { createEnv } from "@t3-oss/env-nextjs"
import { z } from "zod"

export const env = createEnv({
  server: {
    DEEPSEEK_API_KEY: z.string().min(1),
  },
  client: {},
  runtimeEnv: {
    DEEPSEEK_API_KEY: process.env.DEEPSEEK_API_KEY ?? "",
  },
  skipValidation: process.env.NODE_ENV === "test"
})
