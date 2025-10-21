/**
 * Reports Store - Manage report generation and history
 */

import { create } from 'zustand';

export interface Report {
  id: string;
  type: 'performance' | 'tax' | 'tearsheet' | 'trades';
  title: string;
  format: 'PDF' | 'CSV' | 'Excel';
  size: string;
  url: string;
  createdAt: string;
  period?: string;
}

export interface ScheduledReport {
  id: string;
  type: 'performance' | 'tax' | 'tearsheet';
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  email: string;
  enabled: boolean;
  lastSent?: string;
  nextScheduled: string;
}

export interface ReportConfig {
  type: string;
  period: 'day' | 'week' | 'month' | 'quarter' | 'year' | 'ytd' | 'custom';
  startDate?: string;
  endDate?: string;
  format?: 'PDF' | 'CSV' | 'Excel';
}

interface ReportsState {
  reports: Report[];
  scheduledReports: ScheduledReport[];
  isGenerating: boolean;
  loadReports: () => Promise<void>;
  generateReport: (config: ReportConfig) => Promise<Report>;
  scheduleReport: (report: Omit<ScheduledReport, 'id' | 'nextScheduled'>) => Promise<void>;
  deleteReport: (id: string) => void;
  deleteScheduledReport: (id: string) => void;
}

export const useReportsStore = create<ReportsState>((set, get) => ({
  reports: [],
  scheduledReports: [],
  isGenerating: false,

  loadReports: async () => {
    // Mock data - in production, fetch from backend
    const mockReports: Report[] = [
      {
        id: 'rep-1',
        type: 'performance',
        title: 'Performance Report - October 2025',
        format: 'PDF',
        size: '2.3 MB',
        url: '/reports/performance-oct-2025.pdf',
        createdAt: '2025-10-01T10:00:00Z',
        period: 'October 2025',
      },
      {
        id: 'rep-2',
        type: 'tax',
        title: 'Tax Report - Q3 2025',
        format: 'CSV',
        size: '156 KB',
        url: '/reports/tax-q3-2025.csv',
        createdAt: '2025-09-30T15:30:00Z',
        period: 'Q3 2025',
      },
      {
        id: 'rep-3',
        type: 'tearsheet',
        title: 'Performance Tearsheet - 2025 YTD',
        format: 'PDF',
        size: '892 KB',
        url: '/reports/tearsheet-2025-ytd.pdf',
        createdAt: '2025-09-15T09:00:00Z',
        period: '2025 YTD',
      },
    ];

    const mockScheduled: ScheduledReport[] = [
      {
        id: 'sched-1',
        type: 'performance',
        frequency: 'monthly',
        email: 'trader@example.com',
        enabled: true,
        lastSent: '2025-09-30T23:59:00Z',
        nextScheduled: '2025-10-31T23:59:00Z',
      },
      {
        id: 'sched-2',
        type: 'tax',
        frequency: 'quarterly',
        email: 'trader@example.com',
        enabled: true,
        lastSent: '2025-09-30T23:59:00Z',
        nextScheduled: '2025-12-31T23:59:00Z',
      },
    ];

    set({ reports: mockReports, scheduledReports: mockScheduled });
  },

  generateReport: async (config: ReportConfig) => {
    set({ isGenerating: true });

    // Simulate report generation
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const newReport: Report = {
      id: `rep-${Date.now()}`,
      type: config.type as any,
      title: `${config.type.charAt(0).toUpperCase() + config.type.slice(1)} Report - ${config.period}`,
      format: config.format || 'PDF',
      size: '1.2 MB',
      url: `/reports/${config.type}-${Date.now()}.pdf`,
      createdAt: new Date().toISOString(),
      period: config.period,
    };

    set((state) => ({
      reports: [newReport, ...state.reports],
      isGenerating: false,
    }));

    return newReport;
  },

  scheduleReport: async (report: Omit<ScheduledReport, 'id' | 'nextScheduled'>) => {
    const nextScheduled = calculateNextSchedule(report.frequency);

    const newSchedule: ScheduledReport = {
      ...report,
      id: `sched-${Date.now()}`,
      nextScheduled,
    };

    set((state) => ({
      scheduledReports: [newSchedule, ...state.scheduledReports],
    }));
  },

  deleteReport: (id: string) => {
    set((state) => ({
      reports: state.reports.filter((r) => r.id !== id),
    }));
  },

  deleteScheduledReport: (id: string) => {
    set((state) => ({
      scheduledReports: state.scheduledReports.filter((r) => r.id !== id),
    }));
  },
}));

function calculateNextSchedule(frequency: ScheduledReport['frequency']): string {
  const now = new Date();
  let next = new Date(now);

  switch (frequency) {
    case 'daily':
      next.setDate(next.getDate() + 1);
      break;
    case 'weekly':
      next.setDate(next.getDate() + 7);
      break;
    case 'monthly':
      next.setMonth(next.getMonth() + 1);
      break;
    case 'quarterly':
      next.setMonth(next.getMonth() + 3);
      break;
    case 'yearly':
      next.setFullYear(next.getFullYear() + 1);
      break;
  }

  return next.toISOString();
}
