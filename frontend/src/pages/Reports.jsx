// ============================================================
// Reports Page — Generate and download Excel reports
// File: src/pages/Reports.jsx
// ============================================================

import { useState } from 'react'
import {
  FileBarChart, Download, RefreshCw, Calendar,
  CheckCircle2, Clock, FileSpreadsheet,
  TrendingUp, Users, Phone, Heart,
  PieChart as PieChartIcon,
} from 'lucide-react'
import {
  PieChart, Pie, Cell, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip,
} from 'recharts'

const mockReports = [
  { id: 'rpt_a1b2', campaign: 'SmartInvest Pro Launch', campaign_id: 'CAMP_001', filename: 'report_CAMP_001_a1b2c3d4.xlsx', generated_at: '2026-04-13 14:30:00', total_calls: 360, interested: 128, connection_rate: 72.1 },
  { id: 'rpt_c3d4', campaign: 'Q2 Insurance Renewal', campaign_id: 'CAMP_002', filename: 'report_CAMP_002_e5f6g7h8.xlsx', generated_at: '2026-04-12 10:15:00', total_calls: 135, interested: 52, connection_rate: 68.5 },
  { id: 'rpt_e5f6', campaign: 'Cloud Migration Promo', campaign_id: 'CAMP_004', filename: 'report_CAMP_004_i9j0k1l2.xlsx', generated_at: '2026-04-10 16:45:00', total_calls: 200, interested: 78, connection_rate: 74.3 },
]

const selectedReportStats = {
  total_calls_attempted: 360,
  total_calls_connected: 259,
  connection_rate: 72.1,
  average_call_duration: 203,
  demo_requests: 45,
  email_requests: 67,
  outcome_breakdown: [
    { name: 'Interested', value: 128, color: '#34d399' },
    { name: 'Not Interested', value: 72, color: '#fb7185' },
    { name: 'Callback', value: 59, color: '#fbbf24' },
    { name: 'Voicemail', value: 68, color: '#94a3b8' },
    { name: 'No Answer', value: 33, color: '#64748b' },
  ],
  sentiment_split: [
    { name: 'Positive', value: 156, color: '#34d399' },
    { name: 'Neutral', value: 128, color: '#fbbf24' },
    { name: 'Negative', value: 76, color: '#fb7185' },
  ],
}

const campaignOptions = [
  { id: 1, name: 'SmartInvest Pro Launch', campaign_id: 'CAMP_001' },
  { id: 2, name: 'Q2 Insurance Renewal', campaign_id: 'CAMP_002' },
  { id: 3, name: 'Premium Credit Card', campaign_id: 'CAMP_003' },
]

export default function Reports() {
  const [selectedReport, setSelectedReport] = useState(null)
  const [generating, setGenerating] = useState(false)

  const handleGenerate = () => {
    setGenerating(true)
    setTimeout(() => setGenerating(false), 2000)
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: '#1a2236', border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 10, padding: '10px 14px', boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
        }}>
          <p style={{ color: '#f1f5f9', fontWeight: 600, fontSize: 13 }}>
            {payload[0].name}: {payload[0].value}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Reports</h1>
          <p>Generate and download campaign Excel reports</p>
        </div>
      </div>

      {/* Generate Report Card */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div className="card-title">Generate New Report</div>
        </div>
        <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end' }}>
          <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
            <label className="form-label">Select Campaign</label>
            <select className="form-select">
              <option value="">Choose a campaign...</option>
              {campaignOptions.map((c) => (
                <option key={c.id} value={c.id}>{c.name} ({c.campaign_id})</option>
              ))}
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Date From</label>
            <input type="date" className="form-input" />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Date To</label>
            <input type="date" className="form-input" />
          </div>
          <button
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={generating}
            style={{ height: 42 }}
          >
            {generating ? (
              <><RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> Generating...</>
            ) : (
              <><FileBarChart size={16} /> Generate Report</>
            )}
          </button>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Reports List */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Generated Reports</div>
            <span style={{ fontSize: 13, color: 'var(--text-tertiary)' }}>{mockReports.length} reports</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {mockReports.map((report) => (
              <div
                key={report.id}
                style={{
                  display: 'flex', alignItems: 'center', gap: 14, padding: 14,
                  borderRadius: 'var(--radius-md)', cursor: 'pointer',
                  background: selectedReport?.id === report.id ? 'rgba(99, 102, 241, 0.06)' : 'var(--bg-glass)',
                  border: `1px solid ${selectedReport?.id === report.id ? 'var(--accent-primary)' : 'var(--border-subtle)'}`,
                  transition: 'all var(--transition-fast)',
                }}
                onClick={() => setSelectedReport(report)}
              >
                <div style={{
                  width: 42, height: 42, borderRadius: 'var(--radius-md)',
                  background: 'rgba(52, 211, 153, 0.12)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--accent-emerald)', flexShrink: 0,
                }}>
                  <FileSpreadsheet size={20} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 2 }}>{report.campaign}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>
                    {report.total_calls} calls • {report.interested} interested • {report.connection_rate}% rate
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                    <Calendar size={10} style={{ display: 'inline', verticalAlign: 'middle' }} /> {report.generated_at}
                  </div>
                </div>
                <a
                  href={`/api/v1/reports/download/${report.filename}`}
                  className="btn btn-secondary btn-sm"
                  onClick={(e) => e.stopPropagation()}
                  download
                >
                  <Download size={13} /> Download
                </a>
              </div>
            ))}
          </div>
        </div>

        {/* Report Preview Stats */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Report Preview</div>
            <div className="card-subtitle">
              {selectedReport ? selectedReport.campaign : 'Select a report to preview'}
            </div>
          </div>

          {selectedReport ? (
            <div>
              {/* Quick stats */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 20 }}>
                <div style={{ textAlign: 'center', padding: 12, background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)' }}>
                  <Phone size={16} style={{ color: 'var(--accent-primary)', marginBottom: 4 }} />
                  <div style={{ fontSize: 20, fontWeight: 800 }}>{selectedReportStats.total_calls_attempted}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>Total Calls</div>
                </div>
                <div style={{ textAlign: 'center', padding: 12, background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)' }}>
                  <TrendingUp size={16} style={{ color: 'var(--accent-emerald)', marginBottom: 4 }} />
                  <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--accent-emerald)' }}>{selectedReportStats.connection_rate}%</div>
                  <div style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>Connection Rate</div>
                </div>
                <div style={{ textAlign: 'center', padding: 12, background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)' }}>
                  <Clock size={16} style={{ color: 'var(--accent-cyan)', marginBottom: 4 }} />
                  <div style={{ fontSize: 20, fontWeight: 800 }}>{Math.floor(selectedReportStats.average_call_duration / 60)}:{(selectedReportStats.average_call_duration % 60).toString().padStart(2, '0')}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>Avg Duration</div>
                </div>
              </div>

              {/* Outcome Chart */}
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 12 }}>Outcome Breakdown</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
                  <div style={{ width: 120, height: 120 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={selectedReportStats.outcome_breakdown} cx="50%" cy="50%" innerRadius={35} outerRadius={55} paddingAngle={2} dataKey="value" strokeWidth={0}>
                          {selectedReportStats.outcome_breakdown.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div style={{ flex: 1 }}>
                    {selectedReportStats.outcome_breakdown.map((item) => (
                      <div key={item.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '3px 0' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <div style={{ width: 8, height: 8, borderRadius: '50%', background: item.color }}></div>
                          <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{item.name}</span>
                        </div>
                        <span style={{ fontSize: 13, fontWeight: 600 }}>{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Extra stats */}
              <div style={{ display: 'flex', gap: 16 }}>
                <div style={{ flex: 1, padding: 10, background: 'rgba(99, 102, 241, 0.06)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--accent-primary)' }}>{selectedReportStats.demo_requests}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>Demo Requests</div>
                </div>
                <div style={{ flex: 1, padding: 10, background: 'rgba(34, 211, 238, 0.06)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--accent-cyan)' }}>{selectedReportStats.email_requests}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>Email Requests</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="empty-state" style={{ padding: 40 }}>
              <div className="empty-state-icon"><PieChartIcon size={28} /></div>
              <h3>No Report Selected</h3>
              <p>Click on a report to preview its statistics</p>
            </div>
          )}
        </div>
      </div>

      {/* Report Tabs Info */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">Report Structure</div>
          <div className="card-subtitle">Each Excel report contains 5 organized tabs</div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12 }}>
          {[
            { name: 'All Calls', desc: 'Every call regardless of outcome', color: 'var(--accent-primary)' },
            { name: 'Interested', desc: 'Only interested clients', color: 'var(--accent-emerald)' },
            { name: 'Callbacks', desc: 'Clients who requested a callback', color: 'var(--accent-amber)' },
            { name: 'No Contact', desc: 'Voicemail + no answer entries', color: 'var(--text-tertiary)' },
            { name: 'Summary', desc: 'Campaign-level statistics', color: 'var(--accent-cyan)' },
          ].map((tab) => (
            <div key={tab.name} style={{
              padding: 16, borderRadius: 'var(--radius-md)',
              background: 'var(--bg-glass)', border: '1px solid var(--border-subtle)',
              textAlign: 'center',
            }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: tab.color, marginBottom: 4 }}>{tab.name}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{tab.desc}</div>
            </div>
          ))}
        </div>
      </div>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
