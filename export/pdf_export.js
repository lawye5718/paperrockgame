const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function exportFlowChartToPDF() {
  // 启动浏览器
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    // 创建新页面
    const page = await browser.newPage();
    
    // 设置视口大小以适应图表
    await page.setViewport({ width: 1400, height: 1000 });
    
    // 获取文件的绝对路径
    const htmlPath = path.resolve(__dirname, 'index.html');
    const fileUrl = `file://${htmlPath}`;
    
    // 导航到页面
    await page.goto(fileUrl, {
      waitUntil: 'networkidle0'
    });
    
    // 等待图表渲染完成
    await page.waitForTimeout(5000);
    
    // 生成PDF
    const pdfPath = path.resolve(__dirname, '../北海案件关系图.pdf');
    await page.pdf({
      path: pdfPath,
      format: 'A4',
      landscape: true,
      printBackground: true,
      margin: {
        top: '20px',
        right: '20px',
        bottom: '20px',
        left: '20px'
      }
    });
    
    console.log(`PDF已成功生成: ${pdfPath}`);
  } catch (error) {
    console.error('导出PDF时出错:', error);
  } finally {
    // 关闭浏览器
    await browser.close();
  }
}

// 执行导出
exportFlowChartToPDF();