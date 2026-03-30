/**
 * Playwright 配置文件
 */
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',

  // 超时设置
  timeout: 120 * 1000,  // 全局超时 2 分钟
  expect: {
    timeout: 30000  // 期望超时 30 秒
  },

  // 失败重试
  retries: process.env.CI ? 2 : 0,

  // 并行执行
  workers: process.env.CI ? 1 : undefined,

  // 报告器
  reporter: 'html',

  // 共享配置
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  // 浏览器配置 - 只在 Desktop Chrome 上运行
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Web 服务器配置（用于自动启动）
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
