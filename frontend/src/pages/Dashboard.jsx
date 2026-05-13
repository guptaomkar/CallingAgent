// ============================================================
// Dashboard Page — Campaign overview with real-time stats
// File: src/pages/Dashboard.jsx
// ============================================================

import { useState, useEffect } from 'react'
import {
  Phone, PhoneCall, PhoneOff, PhoneMissed,
  TrendingUp, Users, Clock, BarChart3,
  ArrowUpRight, ArrowDownRight, Activity,
  CheckCircle2, XCircle, Calendar,
} from 'lucide-react'
import {
  PieChart, Pie, Cell, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip,
  AreaChart, Area, CartesianGrid,
} from 'recharts'

// Mock data (will be replaced with API calls)
const mockStats = {
  totalCalls: 1247,
  activeCalls: 8,
  connected: 892,
  connectionRate: 71.5,
  interested: 342,
  avgDuration: 203,
}

const outcomeData = [
  { name: 'Interested', value: 342, color: '#34d399' },
  { name: 'Not Interested', value: 218, color: '#fb7185' },
  { name: 'Callback', value: 156, color: '#fbbf24' },
  { name: 'Voicemail', value: 108, color: '#94a3b8' },
  { name: 'No Answer', value: 68, color: '#64748b' },
]

const weeklyData = [
  { day: 'Mon', calls: 180, connected: 128 },
  { day: 'Tue', calls: 210, connected: 155 },
  { day: 'Wed', calls: 165, connected: 112 },
  { day: 'Thu', calls: 240, connected: 178 },
  { day: 'Fri', calls: 198, connected: 142 },
  { day: 'Sat', calls: 140, connected: 98 },
  { day: 'Sun', calls: 114, connected: 79 },
]

const sentimentData = [
  { name: 'Positive', value: 48, color: '#34d399' },
  { name: 'Neutral', value: 35, color: '#fbbf24' },
  { name: 'Negative', value: 17, color: '#fb7185' },
]

const recentCalls = [
  { id: 1, name: 'Rajesh Sharma', phone: '+91 98765 43210', outcome: 'interested', duration: '4:32', time: '2 min ago', sentiment: 'positive' },
  { id: 2, name: 'Priya Patel', phone: '+91 87654 32109', outcome: 'callback_requested', duration: '3:15', time: '5 min ago', sentiment: 'neutral' },
  { id: 3, name: 'Amit Kumar', phone: '+91 76543 21098', outcome: 'not_interested', duration: '1:48', time: '8 min ago', sentiment: 'negative' },
  { id: 4, name: 'Sneha Reddy', phone: '+91 65432 10987', outcome: 'interested', duration: '5:10', time: '12 min ago', sentiment: 'positive' },
  { id: 5, name: 'Vikram Singh', phone: '+91 54321 09876', outcome: 'voicemail', duration: '0:45', time: '15 min ago', sentiment: 'neutral' },
]

const activeCampaigns = [
  { id: 1, name: 'SmartInvest Pro Launch', progress: 72, total: 500, completed: 360, interested: 128 },
  { id: 2, name: 'Q2 Insurance Renewal', progress: 45, total: 300, completed: 135, interested: 52 },
  { id: 3, name: 'Premium Credit Card', progress: 18, total: 750, completed: 135, interested: 41 },
]

export default function Dashboard() {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase()
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: '#1a2236',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '10px',
          padding: '12px 16px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
        }}>
          <p style={{ color: '#f1f5f9', fontWeight: 600, marginBottom: 4 }}>{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color, fontSize: 13 }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div>
      {/* Page Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Dashboard</h1>
          <p>Real-time overview of your calling campaigns</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="live-indicator" style={{ marginBottom: 4 }}>
            <span className="live-dot"></span>
            Live
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-tertiary)', fontVariantNumeric: 'tabular-nums' }}>
            {currentTime.toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card purple">
          <div className="stat-card-top">
            <div className="stat-icon purple"><Phone size={20} /></div>
            <span className="stat-trend up"><ArrowUpRight size={12} /> 12%</span>
          </div>
          <div className="stat-value">{mockStats.totalCalls.toLocaleString()}</div>
          <div className="stat-label">Total Calls Made</div>
        </div>

        <div className="stat-card green">
          <div className="stat-card-top">
            <div className="stat-icon green"><PhoneCall size={20} /></div>
            <span className="stat-trend up"><ArrowUpRight size={12} /> 8%</span>
          </div>
          <div className="stat-value">{mockStats.connectionRate}%</div>
          <div className="stat-label">Connection Rate</div>
        </div>

        <div className="stat-card amber">
          <div className="stat-card-top">
            <div className="stat-icon amber"><TrendingUp size={20} /></div>
            <span className="stat-trend up"><ArrowUpRight size={12} /> 5%</span>
          </div>
          <div className="stat-value">{mockStats.interested}</div>
          <div className="stat-label">Interested Leads</div>
        </div>

        <div className="stat-card cyan">
          <div className="stat-card-top">
            <div className="stat-icon cyan"><Clock size={20} /></div>
          </div>
          <div className="stat-value">{Math.floor(mockStats.avgDuration / 60)}:{(mockStats.avgDuration % 60).toString().padStart(2, '0')}</div>
          <div className="stat-label">Avg Call Duration</div>
        </div>

        <div className="stat-card rose">
          <div className="stat-card-top">
            <div className="stat-icon rose"><Activity size={20} /></div>
            <span className="live-indicator" style={{ fontSize: 11 }}>
              <span className="live-dot" style={{ width: 6, height: 6 }}></span>
              Active
            </span>
          </div>
          <div className="stat-value">{mockStats.activeCalls}</div>
          <div className="stat-label">Active Calls Now</div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Weekly Calls Chart */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Weekly Call Volume</div>
              <div className="card-subtitle">Calls attempted vs connected this week</div>
            </div>
            <div className="btn btn-secondary btn-sm">This Week</div>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weeklyData}>
                <defs>
                  <linearGradient id="gradientCalls" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3}/>
                    <stop offset="100%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="gradientConnected" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#34d399" stopOpacity={0.3}/>
                    <stop offset="100%" stopColor="#34d399" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="calls" stroke="#6366f1" fill="url(#gradientCalls)" strokeWidth={2} name="Attempted" />
                <Area type="monotone" dataKey="connected" stroke="#34d399" fill="url(#gradientConnected)" strokeWidth={2} name="Connected" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Outcome Pie Chart */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Call Outcomes</div>
              <div className="card-subtitle">Breakdown of all call results</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <div style={{ width: 200, height: 200 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={outcomeData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={3}
                    dataKey="value"
                    strokeWidth={0}
                  >
                    {outcomeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div style={{ flex: 1 }}>
              {outcomeData.map((item) => (
                <div key={item.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ width: 10, height: 10, borderRadius: '50%', background: item.color }}></div>
                    <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{item.name}</span>
                  </div>
                  <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid-2">
        {/* Active Campaigns */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Active Campaigns</div>
              <div className="card-subtitle">{activeCampaigns.length} campaigns running</div>
            </div>
            <button className="btn btn-primary btn-sm">
              View All
            </button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {activeCampaigns.map((campaign) => (
              <div key={campaign.id} style={{
                padding: 16,
                borderRadius: 'var(--radius-md)',
                background: 'var(--bg-glass)',
                border: '1px solid var(--border-subtle)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 2 }}>{campaign.name}</div>
                    <div style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>
                      {campaign.completed}/{campaign.total} calls • {campaign.interested} interested
                    </div>
                  </div>
                  <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--accent-primary)' }}>
                    {campaign.progress}%
                  </span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${campaign.progress}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Calls */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Recent Calls</div>
              <div className="card-subtitle">Latest call activity</div>
            </div>
            <div className="live-indicator">
              <span className="live-dot"></span>
              Live Feed
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {recentCalls.map((call) => (
              <div key={call.id} className="call-card">
                <div className="call-avatar">{getInitials(call.name)}</div>
                <div className="call-info">
                  <div className="call-name">{call.name}</div>
                  <div className="call-meta">{call.phone} • {call.time}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className={`badge ${call.outcome}`}>
                    <span className="badge-dot"></span>
                    {call.outcome.replace('_', ' ')}
                  </span>
                  <div className="call-duration" style={{ marginTop: 4 }}>{call.duration}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sentiment Row */}
      <div className="card" style={{ marginTop: 24 }}>
        <div className="card-header">
          <div>
            <div className="card-title">Sentiment Analysis</div>
            <div className="card-subtitle">Client sentiment across all calls</div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 32, alignItems: 'center' }}>
          {sentimentData.map((item) => (
            <div key={item.name} style={{ flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-secondary)' }}>{item.name}</span>
                <span style={{ fontSize: 14, fontWeight: 700, color: item.color }}>{item.value}%</span>
              </div>
              <div className="progress-bar" style={{ height: 8 }}>
                <div className="progress-fill" style={{
                  width: `${item.value}%`,
                  background: item.color,
                }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
