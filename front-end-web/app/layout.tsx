import type { Metadata } from 'next'
import './globals.css'
import { PreferenceProvider } from '@/context/PreferenceContext'

export const metadata: Metadata = {
  title: 'v0 App',
  description: 'Created with v0',
  generator: 'v0.dev',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>
        <PreferenceProvider>
          {children}
        </PreferenceProvider>
      </body>
    </html>
  )
}
