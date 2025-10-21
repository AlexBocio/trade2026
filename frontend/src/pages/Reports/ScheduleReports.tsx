/**
 * Schedule Reports - Set up automated report generation
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useReportsStore } from '../../store/useReportsStore';
import { ArrowLeft, Plus, Trash2, Mail } from 'lucide-react';

export function ScheduleReports() {
  const navigate = useNavigate();
  const { scheduledReports, scheduleReport, deleteScheduledReport } = useReportsStore();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    type: 'performance' as 'performance' | 'tax' | 'tearsheet',
    frequency: 'monthly' as 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly',
    email: '',
    enabled: true,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await scheduleReport(formData);
    setShowForm(false);
    setFormData({
      type: 'performance',
      frequency: 'monthly',
      email: '',
      enabled: true,
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/reports')}
          className="p-2 hover:bg-dark-border rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white">Schedule Reports</h1>
          <p className="text-sm text-gray-400">Set up automated report generation and email delivery</p>
        </div>
      </div>

      {/* Add Schedule Button */}
      <div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg flex items-center gap-2 transition"
        >
          <Plus className="w-4 h-4" />
          Schedule New Report
        </button>
      </div>

      {/* Add Schedule Form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-dark-card border border-dark-border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">New Scheduled Report</h3>

          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Report Type</label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              >
                <option value="performance">Performance Report</option>
                <option value="tax">Tax Report</option>
                <option value="tearsheet">Performance Tearsheet</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Frequency</label>
              <select
                value={formData.frequency}
                onChange={(e) => setFormData({ ...formData, frequency: e.target.value as any })}
                className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm text-gray-400 mb-2">Email Address</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="trader@example.com"
              required
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            />
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              className="px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition"
            >
              Schedule Report
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-6 py-2 bg-dark-border hover:bg-gray-700 rounded-lg font-semibold transition"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Scheduled Reports List */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Scheduled Reports</h2>

        {scheduledReports.length === 0 ? (
          <div className="text-center py-12">
            <Mail className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No scheduled reports yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {scheduledReports.map((schedule) => (
              <div
                key={schedule.id}
                className="bg-dark-bg rounded-lg p-4 flex items-center justify-between"
              >
                <div>
                  <div className="flex items-center gap-3">
                    <div className="font-semibold text-white capitalize">
                      {schedule.type} Report
                    </div>
                    <span className="px-2 py-1 bg-blue-900/30 border border-blue-700 rounded text-xs font-semibold text-blue-300">
                      {schedule.frequency.toUpperCase()}
                    </span>
                    {schedule.enabled ? (
                      <span className="px-2 py-1 bg-green-900/30 border border-green-700 rounded text-xs font-semibold text-green-300">
                        ACTIVE
                      </span>
                    ) : (
                      <span className="px-2 py-1 bg-gray-700 border border-gray-600 rounded text-xs font-semibold text-gray-400">
                        PAUSED
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-400 mt-1">
                    <Mail className="w-3 h-3 inline mr-1" />
                    {schedule.email}
                    {schedule.lastSent && (
                      <> • Last sent: {new Date(schedule.lastSent).toLocaleDateString()}</>
                    )}
                    {schedule.nextScheduled && (
                      <> • Next: {new Date(schedule.nextScheduled).toLocaleDateString()}</>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => {
                    if (confirm('Delete this scheduled report?')) {
                      deleteScheduledReport(schedule.id);
                    }
                  }}
                  className="px-4 py-2 bg-dark-border hover:bg-red-900/30 text-red-400 rounded-lg transition"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
