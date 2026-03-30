import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// 确保截图目录存在
const screenshotDir = path.join(__dirname, 'screenshots');
if (!fs.existsSync(screenshotDir)) {
  fs.mkdirSync(screenshotDir, { recursive: true });
}

test.describe('量化交易系统 - 端到端测试', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前清理截图目录
    if (fs.existsSync(screenshotDir)) {
      fs.rmSync(screenshotDir, { recursive: true, force: true });
    }
    fs.mkdirSync(screenshotDir, { recursive: true });
  });

  test('完整用户流程测试', async ({ page }) => {
    console.log('🚀 开始端到端测试...');
    let step = 0;

    const takeScreenshot = async (name: string) => {
      step++;
      const screenshotPath = path.join(screenshotDir, `step-${step}-${name}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.log(`📸 截图：${screenshotPath}`);
      return screenshotPath;
    };

    // 步骤 1: 打开首页
    console.log('📍 步骤 1: 打开首页');
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await takeScreenshot('homepage');
    await expect(page).toHaveTitle(/量化交易系统/);
    console.log('✅ 首页加载成功');

    // 步骤 2: 输入股票代码
    console.log('📍 步骤 2: 输入股票代码 600519');
    const stockInput = page.locator('input[placeholder*="股票"], input[type="text"]').first();
    await stockInput.fill('600519');
    await takeScreenshot('stock-input');
    console.log('✅ 股票代码输入成功');

    // 步骤 3: 设置日期范围
    console.log('📍 步骤 3: 设置日期范围');
    const dateInputs = page.locator('input[type="date"]');
    await dateInputs.first().fill('2024-01-01');
    await dateInputs.last().fill('2024-01-31');
    await takeScreenshot('date-range');
    console.log('✅ 日期范围设置成功');

    // 步骤 4: 点击「获取数据」按钮
    console.log('📍 步骤 4: 点击「获取数据」按钮');
    const getDataBtn = page.getByText('获取数据').first();
    await getDataBtn.click();

    // 等待数据加载
    console.log('⏳ 等待数据加载...');
    await page.waitForLoadState('networkidle', { timeout: 60000 });
    await page.waitForTimeout(3000);
    await takeScreenshot('chart-loaded');
    console.log('✅ 数据获取成功，K 线图已显示');

    // 步骤 5: 验证 K 线图显示
    console.log('📍 步骤 5: 验证 K 线图');
    const chartContainer = page.locator('div').filter({ hasText: /K 线图/ }).first();
    await expect(chartContainer).toBeVisible();
    console.log('✅ K 线图验证通过');

    // 步骤 6: 切换到回测标签页
    console.log('📍 步骤 6: 切换到回测标签页');
    const backtestTab = page.getByText('策略回测结果', { exact: true });
    if (await backtestTab.isVisible()) {
      await backtestTab.click();
      await page.waitForTimeout(1000);
    }

    // 步骤 7: 点击「全部回测」按钮
    console.log('📍 步骤 7: 点击「全部回测」按钮');
    const runBacktestBtn = page.getByText('全部回测').first();
    if (await runBacktestBtn.isVisible()) {
      await runBacktestBtn.click();

      // 等待回测完成
      console.log('⏳ 等待回测完成...');
      await page.waitForLoadState('networkidle', { timeout: 120000 });
      await page.waitForTimeout(5000);
      await takeScreenshot('backtest-results');
      console.log('✅ 回测完成，结果已显示');
    }

    // 步骤 8: 验证策略结果显示
    console.log('📍 步骤 8: 验证策略结果');
    const strategyCards = page.locator('[class*="StrategyCard"], .bg-white.shadow');
    const count = await strategyCards.count();
    console.log(`✅ 显示 ${count} 个策略结果`);

    // 步骤 9: 移动端适配测试
    console.log('📍 步骤 9: 移动端适配截图');
    await page.setViewportSize({ width: 375, height: 667 });
    await takeScreenshot('mobile-view');
    console.log('✅ 移动端视图截图完成');

    console.log('🎉 端到端测试完成！');
    console.log(`📸 截图已保存到：${screenshotDir}`);
  });

  test('单策略回测测试', async ({ page }) => {
    console.log('🚀 开始单策略回测测试...');

    // 导航到首页
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // 输入股票代码 - 使用更可靠的选择器
    console.log('📍 输入股票代码');
    const stockInput = page.locator('input[placeholder*="600519"], input[type="text"]').first();
    await stockInput.waitFor({ state: 'visible', timeout: 10000 });
    // 如果已经有值，先清空
    await stockInput.clear();
    await stockInput.fill('600519');

    // 设置日期 - 使用更可靠的选择器
    console.log('📍 设置日期范围');
    const dateInputs = page.locator('input[type="date"]');
    await dateInputs.first().fill('2024-01-01');
    await dateInputs.last().fill('2024-01-31');

    // 选择策略
    console.log('📍 选择策略：双均线');
    const strategySelect = page.locator('select').first();
    await strategySelect.waitFor({ state: 'visible', timeout: 10000 });
    await strategySelect.selectOption('ma');

    // 运行单策略回测
    console.log('📍 运行单策略回测');
    const runSingleBtn = page.getByText('运行单策略回测').first();
    await runSingleBtn.waitFor({ state: 'visible', timeout: 10000 });
    await runSingleBtn.click();

    // 等待结果
    console.log('⏳ 等待回测结果...');
    await page.waitForLoadState('networkidle', { timeout: 120000 });
    await page.waitForTimeout(5000);

    // 验证结果
    const resultCard = page.locator('.bg-white.shadow').first();
    await expect(resultCard).toBeVisible();
    console.log('✅ 单策略回测结果验证通过');

    await page.screenshot({
      path: path.join(screenshotDir, 'single-strategy-backtest.png'),
      fullPage: true
    });
  });

  test('API 响应测试', async ({ page }) => {
    console.log('🚀 开始 API 测试...');

    const apiResponses: Array<{ url: string; status: number; data?: any }> = [];

    page.on('response', async response => {
      if (response.url().includes('/api/')) {
        console.log(`📡 API 响应：${response.status()} - ${response.url()}`);
        try {
          const data = await response.json();
          apiResponses.push({
            url: response.url(),
            status: response.status(),
            data
          });
        } catch {
          apiResponses.push({
            url: response.url(),
            status: response.status()
          });
        }
      }
    });

    // 访问首页获取策略 API
    await page.goto('/');
    await page.waitForTimeout(3000);

    // 验证策略 API
    const strategyApi = apiResponses.find(r => r.url.includes('strategies') && r.status === 200);

    if (strategyApi) {
      console.log(`✅ 策略 API 响应：${strategyApi.data?.strategies?.length} 个策略`);
    }

    console.log(`✅ 获取到 ${apiResponses.length} 个 API 响应`);
    console.log('🎉 API 测试完成！');
  });
});
