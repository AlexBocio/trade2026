/**
 * Performance Report Generator - Create PDF reports
 */

import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

export interface PerformanceReportData {
  period: string;
  totalReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  profitFactor: number;
  totalTrades: number;
  avgWin: number;
  avgLoss: number;
  largestWin: number;
  largestLoss: number;
  avgRR: number;
  avgHoldTime: number;
  monthlyReturns: Array<{
    month: string;
    return: number;
    trades: number;
    winRate: number;
  }>;
  bestTrades: Array<{
    symbol: string;
    date: string;
    return: number;
    pnl: number;
  }>;
  worstTrades: Array<{
    symbol: string;
    date: string;
    return: number;
    pnl: number;
  }>;
}

export function generatePerformanceReport(data: PerformanceReportData): void {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.width;
  const pageHeight = doc.internal.pageSize.height;

  // Title Page
  doc.setFontSize(28);
  doc.setFont('helvetica', 'bold');
  doc.text('Trading Performance Report', pageWidth / 2, 40, { align: 'center' });

  doc.setFontSize(16);
  doc.setFont('helvetica', 'normal');
  doc.text(data.period, pageWidth / 2, 55, { align: 'center' });

  doc.setFontSize(12);
  doc.setTextColor(100);
  doc.text(`Generated: ${new Date().toLocaleDateString()}`, pageWidth / 2, 65, { align: 'center' });

  // Add logo or branding
  doc.setDrawColor(0, 255, 136);
  doc.setLineWidth(2);
  doc.line(40, 80, pageWidth - 40, 80);

  // Executive Summary
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(0);
  doc.text('Executive Summary', 20, 100);

  // Key Metrics Box
  const metrics = [
    ['Total Return', `${data.totalReturn > 0 ? '+' : ''}${data.totalReturn.toFixed(2)}%`],
    ['Sharpe Ratio', data.sharpeRatio.toFixed(2)],
    ['Max Drawdown', `${data.maxDrawdown.toFixed(2)}%`],
    ['Win Rate', `${data.winRate.toFixed(1)}%`],
    ['Profit Factor', data.profitFactor.toFixed(2)],
    ['Total Trades', data.totalTrades.toString()],
  ];

  autoTable(doc, {
    startY: 110,
    head: [['Metric', 'Value']],
    body: metrics,
    theme: 'grid',
    headStyles: { fillColor: [0, 255, 136], textColor: [0, 0, 0], fontStyle: 'bold' },
    alternateRowStyles: { fillColor: [245, 245, 245] },
    margin: { left: 20, right: 20 },
  });

  // Monthly Returns Table
  doc.addPage();
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('Monthly Returns', 20, 20);

  const monthlyData = data.monthlyReturns.map((m) => [
    m.month,
    `${m.return > 0 ? '+' : ''}${m.return.toFixed(2)}%`,
    m.trades.toString(),
    `${m.winRate.toFixed(1)}%`,
  ]);

  autoTable(doc, {
    startY: 30,
    head: [['Month', 'Return', 'Trades', 'Win Rate']],
    body: monthlyData,
    theme: 'striped',
    headStyles: { fillColor: [0, 255, 136], textColor: [0, 0, 0] },
    margin: { left: 20, right: 20 },
  });

  // Trade Statistics
  doc.addPage();
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('Trade Statistics', 20, 20);

  const tradeStats = [
    ['Average Win', `${data.avgWin.toFixed(2)}`],
    ['Average Loss', `${data.avgLoss.toFixed(2)}`],
    ['Largest Win', `${data.largestWin.toFixed(2)}`],
    ['Largest Loss', `${data.largestLoss.toFixed(2)}`],
    ['Average R:R Ratio', `${data.avgRR.toFixed(2)}:1`],
    ['Average Hold Time', `${data.avgHoldTime.toFixed(1)} days`],
  ];

  autoTable(doc, {
    startY: 30,
    head: [['Statistic', 'Value']],
    body: tradeStats,
    theme: 'grid',
    headStyles: { fillColor: [0, 255, 136], textColor: [0, 0, 0] },
    margin: { left: 20, right: 20 },
  });

  // Best/Worst Trades
  doc.addPage();
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('Best Trades', 20, 20);

  const bestTrades = data.bestTrades.map((t) => [
    t.symbol,
    new Date(t.date).toLocaleDateString(),
    `${t.return > 0 ? '+' : ''}${t.return.toFixed(2)}%`,
    `${t.pnl.toFixed(2)}`,
  ]);

  autoTable(doc, {
    startY: 30,
    head: [['Symbol', 'Date', 'Return', 'P&L']],
    body: bestTrades,
    theme: 'striped',
    headStyles: { fillColor: [34, 197, 94], textColor: [255, 255, 255] },
    margin: { left: 20, right: 20 },
  });

  const yPos = (doc as any).lastAutoTable.finalY + 20;

  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('Worst Trades', 20, yPos);

  const worstTrades = data.worstTrades.map((t) => [
    t.symbol,
    new Date(t.date).toLocaleDateString(),
    `${t.return.toFixed(2)}%`,
    `${t.pnl.toFixed(2)}`,
  ]);

  autoTable(doc, {
    startY: yPos + 10,
    head: [['Symbol', 'Date', 'Return', 'P&L']],
    body: worstTrades,
    theme: 'striped',
    headStyles: { fillColor: [239, 68, 68], textColor: [255, 255, 255] },
    margin: { left: 20, right: 20 },
  });

  // Footer on all pages
  const pageCount = doc.internal.pages.length - 1;
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(10);
    doc.setTextColor(150);
    doc.text(`Page ${i} of ${pageCount}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
  }

  // Save PDF
  doc.save(`performance-report-${data.period}.pdf`);
}
