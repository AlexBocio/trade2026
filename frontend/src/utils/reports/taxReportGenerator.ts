/**
 * Tax Report Generator - Generate CSV tax reports
 */

export interface Trade {
  id: string;
  symbol: string;
  entryDate: string;
  exitDate: string;
  entryPrice: number;
  exitPrice: number;
  quantity: number;
  pnl: number;
  status: string;
  fees: {
    entry: number;
    exit: number;
  };
  washSale?: boolean;
}

export function generateTaxReport(trades: Trade[]): void {
  // Filter only closed trades with realized P&L
  const closedTrades = trades.filter((t) => t.status === 'closed');

  // CSV Header
  const headers = [
    'Date Acquired',
    'Date Sold',
    'Symbol',
    'Quantity',
    'Cost Basis',
    'Sale Proceeds',
    'Gain/Loss',
    'Short/Long Term',
    'Wash Sale',
  ];

  // CSV Rows
  const rows = closedTrades.map((trade) => {
    const holdingDays = Math.floor(
      (new Date(trade.exitDate).getTime() - new Date(trade.entryDate).getTime()) / (1000 * 60 * 60 * 24)
    );
    const isLongTerm = holdingDays >= 365;
    const costBasis = trade.entryPrice * trade.quantity + trade.fees.entry;
    const saleProceeds = trade.exitPrice * trade.quantity - trade.fees.exit;
    const gainLoss = saleProceeds - costBasis;

    return [
      new Date(trade.entryDate).toLocaleDateString(),
      new Date(trade.exitDate).toLocaleDateString(),
      trade.symbol,
      trade.quantity.toString(),
      costBasis.toFixed(2),
      saleProceeds.toFixed(2),
      gainLoss.toFixed(2),
      isLongTerm ? 'Long-Term' : 'Short-Term',
      trade.washSale ? 'Yes' : 'No',
    ];
  });

  // Calculate totals
  const shortTermGains = closedTrades
    .filter((t) => {
      const days = Math.floor(
        (new Date(t.exitDate).getTime() - new Date(t.entryDate).getTime()) / (1000 * 60 * 60 * 24)
      );
      return days < 365;
    })
    .reduce((sum, t) => sum + t.pnl, 0);

  const longTermGains = closedTrades
    .filter((t) => {
      const days = Math.floor(
        (new Date(t.exitDate).getTime() - new Date(t.entryDate).getTime()) / (1000 * 60 * 60 * 24)
      );
      return days >= 365;
    })
    .reduce((sum, t) => sum + t.pnl, 0);

  // Add summary rows
  rows.push([]);
  rows.push(['SUMMARY', '', '', '', '', '', '', '', '']);
  rows.push(['Short-Term Gains', '', '', '', '', '', shortTermGains.toFixed(2), '', '']);
  rows.push(['Long-Term Gains', '', '', '', '', '', longTermGains.toFixed(2), '', '']);
  rows.push(['Total Realized Gains', '', '', '', '', '', (shortTermGains + longTermGains).toFixed(2), '', '']);

  // Convert to CSV
  const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');

  // Download CSV
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', `tax-report-${new Date().getFullYear()}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
