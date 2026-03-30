import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '量化交易系统',
  description: '股票策略回测与分析平台',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  )
}
