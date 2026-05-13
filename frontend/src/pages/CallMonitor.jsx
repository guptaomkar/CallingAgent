// ============================================================
// Call Monitor Page — Live call status and transcript view
// File: src/pages/CallMonitor.jsx
// ============================================================

import { useState, useEffect } from 'react'
import {
  Phone, PhoneCall, PhoneOff, PhoneMissed,
  Volume2, Mic, Clock, User, Bot,
  Play, Square, SkipForward, RefreshCw,
} from 'lucide-react'

const mockActiveCalls = [
  {
    id: 1, name: 'Rajesh Sharma', phone: '+91 9876543210',
    status: 'in_progress', duration: 187, campaign: 'SmartInvest Pro',
    currentQuestion: 3, totalQuestions: 5, sentiment: 'positive',
    transcript: [
      { role: 'agent', text: 'Hello, am I speaking with Rajesh Sharma?' },
      { role: 'client', text: 'Yes, this is Rajesh.' },
      { role: 'agent', text: "Hi Rajesh! This is Priya calling from FinServ Solutions. I hope I've caught you at a good time." },
      { role: 'client', text: 'Yes, go ahead.' },
      { role: 'agent', text: 'How would you rate your experience with our existing services on a scale of 1 to 5?' },
      { role: 'client', text: "I'd say about a 4. Pretty good but could be better." },
      { role: 'agent', text: "That's really helpful, I appreciate that! Are you currently investing with any other provider?" },
      { role: 'client', text: "Yes, I have some mutual funds with another company." },
    ],
  },
  {
    id: 2, name: 'Priya Patel', phone: '+91 8765432109',
    status: 'connected', duration: 45, campaign: 'SmartInvest Pro',
    currentQuestion: 1, totalQuestions: 5, sentiment: 'neutral',
    transcript: [
      { role: 'agent', text: 'Hello, am I speaking with Priya Patel?' },
      { role: 'client', text: 'Yes, who is this?' },
    ],
  },
  {
    id: 3, name: 'Amit Kumar', phone: '+91 7654321098',
    status: 'ringing', duration: 0, campaign: 'Insurance Renewal',
    currentQuestion: 0, totalQuestions: 5, sentiment: null,
    transcript: [],
  },
]

const recentCompletedCalls = [
  { id: 101, name: 'Sneha Reddy', outcome: 'interested', duration: 310, campaign: 'SmartInvest Pro' },
  { id: 102, name: 'Vikram Singh', outcome: 'voicemail', duration: 45, campaign: 'SmartInvest Pro' },
  { id: 103, name: 'Meena Iyer', outcome: 'not_interested', duration: 108, campaign: 'Insurance Renewal' },
  { id: 104, name: 'Ravi Prasad', outcome: 'callback_requested', duration: 195, campaign: 'SmartInvest Pro' },
]

export default function CallMonitor() {
  const [selectedCall, setSelectedCall] = useState(mockActiveCalls[0])
  const [timer, setTimer] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => setTimer(t => t + 1), 1000)
    return () => clearInterval(interval)
  }, [])

  const formatDuration = (seconds) => {
    const min = Math.floor(seconds / 60)
    const sec = seconds % 60
    return `${min}:${sec.toString().padStart(2, '0')}`
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'in_progress': return 'var(--accent-emerald)'
      case 'connected': return 'var(--accent-primary)'
      case 'ringing': return 'var(--accent-amber)'
      default: return 'var(--text-muted)'
    }
  }

  const getInitials = (name) => name.split(' ').map(n => n[0]).join('').toUpperCase()

  return (
    <div>
      {/* Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Call Monitor</h1>
          <p>Real-time view of active and recent calls</p>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <div className="live-indicator"><span className="live-dot"></span> Live</div>
          <button className="btn btn-secondary btn-sm"><RefreshCw size={14} /> Refresh</button>
        </div>
      </div>

      {/* Active Calls Count */}
      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 24 }}>
        <div className="stat-card green" style={{ padding: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="stat-icon green"><PhoneCall size={18} /></div>
            <div>
              <div style={{ fontSize: 24, fontWeight: 800 }}>{mockActiveCalls.filter(c => c.status === 'in_progress').length}</div>
              <div style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>In Progress</div>
            </div>
          </div>
        </div>
        <div className="stat-card purple" style={{ padding: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="stat-icon purple"><Phone size={18} /></div>
            <div>
              <div style={{ fontSize: 24, fontWeight: 800 }}>{mockActiveCalls.filter(c => c.status === 'connected').length}</div>
              <div style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>Connected</div>
            </div>
          </div>
        </div>
        <div className="stat-card amber" style={{ padding: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="stat-icon amber"><PhoneMissed size={18} /></div>
            <div>
              <div style={{ fontSize: 24, fontWeight: 800 }}>{mockActiveCalls.filter(c => c.status === 'ringing').length}</div>
              <div style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>Ringing</div>
            </div>
          </div>
        </div>
        <div className="stat-card cyan" style={{ padding: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="stat-icon cyan"><Clock size={18} /></div>
            <div>
              <div style={{ fontSize: 24, fontWeight: 800 }}>{recentCompletedCalls.length}</div>
              <div style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>Completed Today</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        {/* Active Calls List */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Active Calls</div>
            <div className="live-indicator" style={{ fontSize: 11 }}>
              <span className="live-dot"></span>
              {mockActiveCalls.length} calls
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {mockActiveCalls.map((call) => (
              <div
                key={call.id}
                className="call-card"
                onClick={() => setSelectedCall(call)}
                style={{
                  cursor: 'pointer',
                  borderColor: selectedCall?.id === call.id ? 'var(--accent-primary)' : undefined,
                  background: selectedCall?.id === call.id ? 'rgba(99, 102, 241, 0.06)' : undefined,
                }}
              >
                <div className="call-avatar" style={{
                  background: call.status === 'in_progress' ? 'var(--gradient-success)' : 'var(--gradient-primary)',
                }}>
                  {getInitials(call.name)}
                </div>
                <div className="call-info">
                  <div className="call-name">{call.name}</div>
                  <div className="call-meta">
                    {call.campaign} • Q{call.currentQuestion}/{call.totalQuestions}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{
                    fontSize: 11, fontWeight: 600,
                    color: getStatusColor(call.status),
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    marginBottom: 4,
                  }}>
                    {call.status === 'in_progress' ? '● Active' : call.status === 'ringing' ? '◎ Ringing' : '● Connected'}
                  </div>
                  <div className="call-duration">
                    {formatDuration(call.duration + (call.status === 'in_progress' ? timer : 0))}
                  </div>
                </div>
              </div>
            ))}

            {/* Recent Completed */}
            <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Recently Completed
              </div>
              {recentCompletedCalls.map((call) => (
                <div key={call.id} className="call-card" style={{ padding: 10, opacity: 0.7 }}>
                  <div className="call-avatar" style={{ width: 32, height: 32, fontSize: 11 }}>{getInitials(call.name)}</div>
                  <div className="call-info">
                    <div className="call-name" style={{ fontSize: 13 }}>{call.name}</div>
                    <div className="call-meta">{call.campaign}</div>
                  </div>
                  <span className={`badge ${call.outcome}`} style={{ fontSize: 11 }}>
                    {call.outcome.replace('_', ' ')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Live Transcript */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Live Transcript</div>
              <div className="card-subtitle">
                {selectedCall ? `${selectedCall.name} — ${selectedCall.campaign}` : 'Select a call'}
              </div>
            </div>
            {selectedCall && (
              <div style={{ display: 'flex', gap: 6 }}>
                <button className="btn btn-icon btn-secondary" title="Mute"><Mic size={14} /></button>
                <button className="btn btn-icon btn-secondary" title="End Call" style={{ color: 'var(--accent-rose)' }}>
                  <PhoneOff size={14} />
                </button>
              </div>
            )}
          </div>

          {selectedCall?.transcript.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, maxHeight: 500, overflowY: 'auto' }}>
              {selectedCall.transcript.map((msg, idx) => (
                <div key={idx} style={{
                  display: 'flex',
                  gap: 10,
                  flexDirection: msg.role === 'agent' ? 'row' : 'row-reverse',
                }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: '50%',
                    background: msg.role === 'agent' ? 'var(--gradient-primary)' : 'rgba(255,255,255,0.08)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    flexShrink: 0,
                  }}>
                    {msg.role === 'agent' ? <Bot size={14} color="white" /> : <User size={14} color="var(--text-secondary)" />}
                  </div>
                  <div style={{
                    background: msg.role === 'agent' ? 'rgba(99, 102, 241, 0.1)' : 'var(--bg-glass)',
                    border: '1px solid',
                    borderColor: msg.role === 'agent' ? 'rgba(99, 102, 241, 0.2)' : 'var(--border-subtle)',
                    borderRadius: msg.role === 'agent' ? '4px 14px 14px 14px' : '14px 4px 14px 14px',
                    padding: '10px 14px',
                    maxWidth: '80%',
                    fontSize: 13,
                    lineHeight: 1.5,
                    color: 'var(--text-secondary)',
                  }}>
                    {msg.text}
                  </div>
                </div>
              ))}
              {/* Typing indicator */}
              {selectedCall.status === 'in_progress' && (
                <div style={{ display: 'flex', gap: 10 }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: '50%',
                    background: 'rgba(255,255,255,0.08)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <User size={14} color="var(--text-muted)" />
                  </div>
                  <div style={{
                    background: 'var(--bg-glass)', border: '1px solid var(--border-subtle)',
                    borderRadius: '14px 4px 14px 14px', padding: '10px 16px',
                    display: 'flex', gap: 4, alignItems: 'center',
                  }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse-live 1s ease-in-out infinite' }}></div>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse-live 1s ease-in-out 0.2s infinite' }}></div>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse-live 1s ease-in-out 0.4s infinite' }}></div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon"><Volume2 size={28} /></div>
              <h3>No Active Transcript</h3>
              <p>Select a call to view the live conversation transcript</p>
            </div>
          )}

          {/* Question Progress */}
          {selectedCall && selectedCall.totalQuestions > 0 && (
            <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontSize: 12, color: 'var(--text-tertiary)', fontWeight: 600 }}>Question Progress</span>
                <span style={{ fontSize: 12, color: 'var(--accent-primary)', fontWeight: 600 }}>
                  {selectedCall.currentQuestion}/{selectedCall.totalQuestions}
                </span>
              </div>
              <div className="progress-bar" style={{ height: 6 }}>
                <div className="progress-fill" style={{ width: `${(selectedCall.currentQuestion / selectedCall.totalQuestions) * 100}%` }}></div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
