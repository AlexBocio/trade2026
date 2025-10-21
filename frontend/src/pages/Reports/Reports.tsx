/**
 * Reports Dashboard - Generate and manage performance reports
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useReportsStore } from '../../store/useReportsStore';
import { FileText, Download, Calendar, Mail, TrendingUp, DollarSign, Trash2 } from 'lucide-react';

const reportTemplates = [
  {
    id: 'performance',
    title: 'Performance Report',
    description: 'Comprehensive monthly/yearly performance summary',
    icon: TrendingUp,
    format: 'PDF',
    color: 'from-green-400 to-blue-500',
  },
  {
    id: 'tax',
    title: 'Tax Report',
    description: 'Realized gains/losses for IRS filing',
    icon: DollarSign,
    format: 'CSV',
    color: 'from-yellow-400 to-orange-500',
  },
  {
    id: 'tearsheet',
    title: 'Performance Tearsheet',
    description: '1-page professional summary',
    icon: FileText,
    format: 'PDF',
    color: 'from-purple-400 to-pink-500',
  },
  {
    id: 'trades',
    title: 'All Trades Export',
    description: 'Export all trades with details',
    icon: Download,
    format: 'CSV/Excel',
    color: 'from-blue-400 to-cyan-500',
  },
];

export function Reports() {
  const navigate = useNavigate();
  const { reports, loadReports, generateReport, deleteReport, isGenerating } = useReportsStore();
  const [generatingType, setGeneratingType] = useState<string | null>(null);

  useEffect(() => {
    loadReports();
  }, [loadReports]);

  const handleGenerateReport = async (templateId: string) => {
    setGeneratingType(templateId);
    const config = {
      type: templateId,
      period: 'month',
      startDate: new Date(2025, 9, 1).toISOString(),
      endDate: new Date(2025, 9, 31).toISOString(),
      format: templateId === 'tax' || templateId === 'trades' ? ('CSV' as const) : ('PDF' as const),
    };

    await generateReport(config);
    setGeneratingType(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText className="w-8 h-8 text-green-400" />
          <div>
            <h1 className="text-3xl font-bold text-white">Reports & Exports</h1>
            <p className="text-sm text-gray-400">Generate performance reports and export trading data</p>
          </div>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/reports/schedule')}
            className="px-4 py-2 bg-dark-card border border-dark-border hover:bg-dark-border rounded-lg flex items-center gap-2 transition"
          >
            <Calendar className="w-4 h-4" />
            Schedule Reports
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Total Reports</div>
          <div className="text-2xl font-bold text-white">{reports.length}</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">This Month</div>
          <div className="text-2xl font-bold text-white">
            {reports.filter((r) => {
              const createdDate = new Date(r.createdAt);
              const now = new Date();
              return createdDate.getMonth() === now.getMonth() && createdDate.getFullYear() === now.getFullYear();
            }).length}
          </div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">PDF Reports</div>
          <div className="text-2xl font-bold text-white">{reports.filter((r) => r.format === 'PDF').length}</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">CSV Exports</div>
          <div className="text-2xl font-bold text-white">{reports.filter((r) => r.format === 'CSV').length}</div>
        </div>
      </div>

      {/* Quick Actions - Report Templates */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Quick Generate</h2>
        <div className="grid grid-cols-4 gap-6">
          {reportTemplates.map((template) => (
            <div
              key={template.id}
              className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-green-400 transition"
            >
              <div
                className={`w-12 h-12 rounded-lg bg-gradient-to-br ${template.color} flex items-center justify-center mb-3`}
              >
                <template.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-bold text-white mb-1">{template.title}</h3>
              <p className="text-sm text-gray-400 mb-3">{template.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">{template.format}</span>
                <button
                  onClick={() => handleGenerateReport(template.id)}
                  disabled={generatingType === template.id}
                  className="px-3 py-1.5 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded text-sm font-semibold transition"
                >
                  {generatingType === template.id ? (
                    <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  ) : (
                    'Generate'
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Generated Reports List */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Generated Reports</h2>

        {reports.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 mb-4">No reports generated yet</p>
            <button
              onClick={() => handleGenerateReport('performance')}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition"
            >
              Generate Your First Report
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {reports.map((report) => (
              <div
                key={report.id}
                className="bg-dark-bg rounded-lg p-4 flex items-center justify-between hover:bg-dark-border/50 transition"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-dark-border rounded flex items-center justify-center">
                    {report.format === 'PDF' ? (
                      <FileText className="w-6 h-6 text-red-400" />
                    ) : (
                      <Download className="w-6 h-6 text-green-400" />
                    )}
                  </div>
                  <div>
                    <div className="font-semibold text-white">{report.title}</div>
                    <div className="text-sm text-gray-400">
                      {new Date(report.createdAt).toLocaleString()} • {report.format} • {report.size}
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      /* In production: window.open(report.url, '_blank') */
                      alert('Download functionality - In production, this would download: ' + report.url);
                    }}
                    className="px-4 py-2 bg-dark-border hover:bg-gray-700 rounded-lg flex items-center gap-2 transition"
                  >
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                  {report.format === 'PDF' && (
                    <button
                      onClick={() => navigate(`/reports/${report.id}`)}
                      className="px-4 py-2 bg-dark-border hover:bg-gray-700 rounded-lg transition"
                    >
                      View
                    </button>
                  )}
                  <button
                    onClick={() => {
                      /* Email functionality */
                      alert('Email functionality - In production, this would email the report');
                    }}
                    className="px-4 py-2 bg-dark-border hover:bg-gray-700 rounded-lg transition"
                  >
                    <Mail className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Delete this report?')) {
                        deleteReport(report.id);
                      }
                    }}
                    className="px-4 py-2 bg-dark-border hover:bg-red-900/30 text-red-400 rounded-lg transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
