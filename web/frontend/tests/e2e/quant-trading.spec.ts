/**
 * 量化交易系统 - 端到端测试
 *
 * 测试场景根据使用手册 (USAGE.md) 设计
 * 验证功能真正可用，而不是只验证"点击了按钮"
 */

import { test, expect, type Page } from '@playwright/test';

// 增加超时设置

// 测试数据
const TEST_STOCK = {
  code: '600519',        // 贵州茅台
  name: '贵州茅台',
  startDate: '2024-01-01',
  endDate: '2024-01-31',
};

const POPULAR_STOCKS = [
  { code: '600519', name: '贵州茅台' },
  { code: '000858', name: '五粮液' },
  { code: '601318', name: '中国平安' },
];

/**
 * 测试 1: 首页加载
 */
test.describe('首页加载', () => {
  test('应该成功加载首页', async ({ page }) => {
    await page.goto('/');

    // 检查页面标题
    await expect(page).toHaveTitle(/量化交易系统/);

    // 检查 header 是否显示
    const header = page.locator('header');
    await expect(header).toBeVisible();
    await expect(header).toContainText('量化交易系统');
    await expect(header).toContainText('股票策略回测与分析平台');
  });

  test('应该显示输入表单', async ({ page }) => {
    await page.goto('/');

    // 检查股票代码输入框 - 使用 label 定位
    const stockLabel = page.locator('text=股票代码');
    await expect(stockLabel).toBeVisible();

    const stockInput = stockLabel.locator('..').locator('input[type="text"]');
    await expect(stockInput).toBeVisible();

    // 检查日期选择器
    const dateInputs = page.locator('input[type="date"]');
    await expect(dateInputs).toHaveCount(2);

    // 检查按钮
    const getDataBtn = page.getByRole('button', { name: '获取数据' });
    const backtestBtn = page.getByRole('button', { name: '全部回测' });
    await expect(getDataBtn).toBeVisible();
    await expect(backtestBtn).toBeVisible();
  });

  test('应该显示热门股票', async ({ page }) => {
    await page.goto('/');

    // 检查热门股票区域
    const popularSection = page.locator('text=热门股票');
    await expect(popularSection).toBeVisible();

    // 检查每个热门股票按钮
    for (const stock of POPULAR_STOCKS) {
      const stockBtn = page.getByRole('button', { name: stock.name });
      await expect(stockBtn).toBeVisible();
    }
  });
});

/**
 * 测试 2: 股票输入功能
 */
test.describe('股票输入功能', () => {
  let stockInput: ReturnType<Page['locator']>;

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    const stockLabel = page.locator('text=股票代码');
    stockInput = stockLabel.locator('..').locator('input[type="text"]');
  });

  test('应该允许输入股票代码', async ({ page }) => {
    await stockInput.clear();
    await stockInput.fill('000001');
    const value = await stockInput.inputValue();
    expect(value).toBe('000001');
  });

  test('应该可以通过点击热门股票填充代码', async ({ page }) => {
    const maotaiBtn = page.getByRole('button', { name: '贵州茅台' });
    await maotaiBtn.click();
    await expect(stockInput).toHaveValue('600519');
  });

  test('应该可以选择日期', async ({ page }) => {
    const dateInputs = page.locator('input[type="date"]');
    await dateInputs.first().fill(TEST_STOCK.startDate);
    await expect(dateInputs.first()).toHaveValue(TEST_STOCK.startDate);
    await dateInputs.last().fill(TEST_STOCK.endDate);
    await expect(dateInputs.last()).toHaveValue(TEST_STOCK.endDate);
  });
});

/**
 * 测试 3: K 线图功能 - 核心功能验证
 */
test.describe('K 线图功能', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('应该显示 K 线图标签页', async ({ page }) => {
    const klineTab = page.getByRole('button', { name: 'K 线图', exact: true });
    await expect(klineTab).toBeVisible();
  });

  test('点击获取数据后应该显示 K 线图', async ({ page }) => {
    // 使用默认日期范围，不手动设置
    // 点击获取数据
    await page.getByRole('button', { name: '获取数据' }).click();

    // ✅ 等待 K 线图显示（canvas 元素出现）
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible({ timeout: 30000 });

    console.log('K 线图显示成功');
  });
});

/**
 * 测试 4: 策略回测功能 - 核心功能验证
 */
test.describe('策略回测功能', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('应该显示回测结果标签页', async ({ page }) => {
    const backtestTab = page.getByRole('button', { name: '策略回测结果', exact: true });
    await expect(backtestTab).toBeVisible();
  });

  test('点击全部回测后应该显示回测结果', async ({ page }) => {
    // 设置股票代码
    const stockLabel = page.locator('text=股票代码');
    const stockInput = stockLabel.locator('..').locator('input[type="text"]');
    await stockInput.fill(TEST_STOCK.code);

    // 点击全部回测
    const backtestBtn = page.getByRole('button', { name: '全部回测' });
    await backtestBtn.click();

    // 等待 API 响应
    const response = await page.waitForResponse(
      res => res.url().includes('/api/backtest/all')
    );
    expect(response.status()).toBe(200);

    // ✅ 验证回测结果真的显示出来了
    // 检查是否有策略卡片显示
    const strategyCards = page.locator('div.bg-white').filter({ hasText: /收益率|回撤/ });
    await expect(strategyCards.first()).toBeVisible({ timeout: 30000 });

    // ✅ 验证有回测数据显示（检查是否有百分比数字）
    const returnText = page.locator('text=%').first();
    await expect(returnText).toBeVisible();

    console.log('回测结果显示成功');
  });
});

/**
 * 测试 5: 响应式设计
 */
test.describe('响应式设计', () => {
  test('应该在移动端正常显示', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    const header = page.locator('header');
    await expect(header).toBeVisible();

    const stockLabel = page.locator('text=股票代码');
    const stockInput = stockLabel.locator('..').locator('input[type="text"]');
    await expect(stockInput).toBeVisible();
  });
});

/**
 * 测试 6: 后端 API 测试
 */
test.describe('后端 API 测试', () => {
  const API_BASE = 'http://localhost:8000';

  test('应该可以访问 API 根路径', async ({ request }) => {
    const response = await request.get(API_BASE + '/');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.status).toBe('running');
  });

  test('应该可以获取策略列表', async ({ request }) => {
    const response = await request.get(API_BASE + '/api/strategies');
    const data = await response.json();
    expect(data.strategies).toHaveLength(7);
  });

  test('应该可以获取股票数据', async ({ request }) => {
    const response = await request.post(API_BASE + '/api/stock/data', {
      data: {
        stock_code: TEST_STOCK.code,
        start_date: TEST_STOCK.startDate,
        end_date: TEST_STOCK.endDate,
      }
    });
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.stock_code).toBe(TEST_STOCK.code);
  });

  test('应该可以运行回测', async ({ request }) => {
    const response = await request.post(API_BASE + '/api/backtest', {
      data: {
        stock_code: TEST_STOCK.code,
        start_date: TEST_STOCK.startDate,
        end_date: TEST_STOCK.endDate,
        strategy: 'ma',
        params: { fast_period: 5, slow_period: 20 }
      }
    });
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.results).toHaveProperty('total_return');
  });

  test('应该可以运行全部策略回测', async ({ request }) => {
    const response = await request.post(API_BASE + '/api/backtest/all', {
      data: {
        stock_code: TEST_STOCK.code,
        start_date: TEST_STOCK.startDate,
        end_date: TEST_STOCK.endDate,
      }
    }, { timeout: 180000 });  // 3 分钟超时
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data.results)).toBeTruthy();
  });
});

/**
 * 测试 7: 完整使用流程 - 模拟真实用户操作
 */
test.describe('完整使用流程测试', () => {
  test('用户完整使用流程', async ({ page }) => {
    console.log('=== 开始完整使用流程测试 ===');

    // 步骤 1: 访问首页
    await page.goto('/');
    // 等待页面完全加载
    await page.waitForLoadState('networkidle');
    console.log('步骤 1: 访问首页 ✓');

    // 步骤 2: 选择股票
    const maotaiBtn = page.getByRole('button', { name: '贵州茅台' });
    await maotaiBtn.click();
    await page.waitForTimeout(500);  // 等待输入框更新
    console.log('步骤 2: 选择股票 ✓');

    // 设置较短的日期范围以加快回测速度
    const startDateInput = page.locator('input[type="date"]').first();
    await startDateInput.fill('2024-01-01');
    const endDateInput = page.locator('input[type="date"]').last();
    await endDateInput.fill('2024-01-31');
    await page.waitForTimeout(300);
    console.log('日期范围已设置：2024-01-01 至 2024-01-31');

    // 步骤 3: 点击获取数据
    const getDataBtn = page.getByRole('button', { name: '获取数据' });
    await getDataBtn.click();
    console.log('步骤 3: 点击获取数据 ✓');

    // 步骤 4: 验证 K 线图显示
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible({ timeout: 60000 });
    console.log('步骤 4: K 线图显示 ✓');

    // 步骤 5: 切换到回测标签页
    const backtestTab = page.getByRole('button', { name: '策略回测结果' });
    await backtestTab.click();
    console.log('步骤 5: 切换到回测标签页 ✓');

    // 步骤 6: 点击全部回测
    const runBacktestBtn = page.getByRole('button', { name: '全部回测' });
    await runBacktestBtn.click();
    console.log('步骤 6: 点击全部回测 ✓');

    // 步骤 7: 验证回测结果显示
    const returnText = page.locator('text=%').first();
    await expect(returnText).toBeVisible({ timeout: 60000 });
    console.log('步骤 7: 回测结果显示 ✓');

    console.log('=== 完整使用流程测试完成 ===');
  });
});
