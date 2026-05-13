// ============================================================
// Campaigns Page — CRUD management for calling campaigns
// File: src/pages/Campaigns.jsx
// ============================================================

import { useState } from 'react'
import {
  Plus, Search, MoreVertical, Play, Pause,
  Edit3, Trash2, Users, Phone, TrendingUp,
  Megaphone, ChevronRight, Copy,
} from 'lucide-react'

const mockCampaigns = [
  {
    id: 1, campaign_id: 'CAMP_001', name: 'SmartInvest Pro Launch',
    agent_name: 'Priya', company_name: 'FinServ Solutions',
    service_name: 'SmartInvest Pro', status: 'active',
    total_contacts: 500, calls_completed: 360, calls_interested: 128,
    language: 'English', created_at: '2026-04-01',
    questions: [
      { id: 'q1', text: 'How would you rate our existing services?' },
      { id: 'q2', text: 'Are you currently investing with any other provider?' },
      { id: 'q3', text: 'Would you be interested in a free portfolio review?' },
    ],
  },
  {
    id: 2, campaign_id: 'CAMP_002', name: 'Q2 Insurance Renewal',
    agent_name: 'Rahul', company_name: 'SecureLife Insurance',
    service_name: 'Premium Shield Plus', status: 'active',
    total_contacts: 300, calls_completed: 135, calls_interested: 52,
    language: 'Hindi', created_at: '2026-04-05',
    questions: [
      { id: 'q1', text: 'When does your current policy expire?' },
      { id: 'q2', text: 'What coverage amount are you looking for?' },
    ],
  },
  {
    id: 3, campaign_id: 'CAMP_003', name: 'Premium Credit Card',
    agent_name: 'Ananya', company_name: 'NexBank',
    service_name: 'Platinum Rewards Card', status: 'draft',
    total_contacts: 750, calls_completed: 0, calls_interested: 0,
    language: 'English', created_at: '2026-04-10',
    questions: [],
  },
  {
    id: 4, campaign_id: 'CAMP_004', name: 'Cloud Migration Promo',
    agent_name: 'Dev', company_name: 'CloudScale Tech',
    service_name: 'CloudScale Enterprise', status: 'completed',
    total_contacts: 200, calls_completed: 200, calls_interested: 78,
    language: 'English', created_at: '2026-03-15',
    questions: [],
  },
]

export default function Campaigns() {
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedCampaign, setSelectedCampaign] = useState(null)

  const filteredCampaigns = mockCampaigns.filter(c =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.campaign_id.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getProgressPercent = (c) => {
    if (c.total_contacts === 0) return 0
    return Math.round((c.calls_completed / c.total_contacts) * 100)
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Campaigns</h1>
          <p>Manage your calling campaigns and their configurations</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          <Plus size={16} /> New Campaign
        </button>
      </div>

      {/* Search */}
      <div style={{ marginBottom: 24, maxWidth: 400 }}>
        <div style={{ position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            className="form-input"
            placeholder="Search campaigns..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: 40 }}
          />
        </div>
      </div>

      {/* Campaign Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: 20 }}>
        {filteredCampaigns.map((campaign) => (
          <div key={campaign.id} className="card" style={{ cursor: 'pointer' }}
            onClick={() => setSelectedCampaign(selectedCampaign?.id === campaign.id ? null : campaign)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <span className={`badge ${campaign.status}`}>
                    <span className="badge-dot"></span>
                    {campaign.status}
                  </span>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                    {campaign.campaign_id}
                  </span>
                </div>
                <h3 style={{ fontSize: 17, fontWeight: 700, marginBottom: 4 }}>{campaign.name}</h3>
                <p style={{ fontSize: 13, color: 'var(--text-tertiary)' }}>
                  {campaign.agent_name} • {campaign.company_name} • {campaign.language}
                </p>
              </div>
              <div style={{ display: 'flex', gap: 6 }}>
                {campaign.status === 'active' && (
                  <button className="btn btn-icon btn-secondary" title="Pause">
                    <Pause size={14} />
                  </button>
                )}
                {campaign.status === 'draft' && (
                  <button className="btn btn-icon btn-secondary" style={{ color: 'var(--accent-emerald)' }} title="Launch">
                    <Play size={14} />
                  </button>
                )}
              </div>
            </div>

            {/* Stats Row */}
            <div style={{ display: 'flex', gap: 20, marginBottom: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <Users size={14} style={{ color: 'var(--text-muted)' }} />
                <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{campaign.total_contacts} contacts</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <Phone size={14} style={{ color: 'var(--text-muted)' }} />
                <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{campaign.calls_completed} called</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <TrendingUp size={14} style={{ color: 'var(--accent-emerald)' }} />
                <span style={{ fontSize: 13, color: 'var(--accent-emerald)', fontWeight: 600 }}>{campaign.calls_interested} interested</span>
              </div>
            </div>

            {/* Progress Bar */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>Progress</span>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--accent-primary)' }}>{getProgressPercent(campaign)}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${getProgressPercent(campaign)}%` }}></div>
              </div>
            </div>

            {/* Expanded Details */}
            {selectedCampaign?.id === campaign.id && (
              <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 13, color: 'var(--text-tertiary)', marginBottom: 8, fontWeight: 600 }}>
                  Service: {campaign.service_name}
                </div>
                {campaign.questions.length > 0 && (
                  <div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                      Questions ({campaign.questions.length})
                    </div>
                    {campaign.questions.map((q, i) => (
                      <div key={q.id} style={{ fontSize: 13, color: 'var(--text-secondary)', padding: '4px 0', display: 'flex', gap: 8 }}>
                        <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>Q{i+1}.</span>
                        {q.text}
                      </div>
                    ))}
                  </div>
                )}
                <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                  <button className="btn btn-secondary btn-sm"><Edit3 size={13} /> Edit</button>
                  <button className="btn btn-secondary btn-sm"><Copy size={13} /> Duplicate</button>
                  <button className="btn btn-secondary btn-sm" style={{ color: 'var(--accent-rose)' }}><Trash2 size={13} /> Delete</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Create Campaign Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 style={{ fontSize: 18, fontWeight: 700 }}>Create New Campaign</h2>
              <button className="btn btn-icon btn-secondary" onClick={() => setShowCreateModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="grid-2" style={{ gap: 16 }}>
                <div className="form-group">
                  <label className="form-label">Campaign ID</label>
                  <input className="form-input" placeholder="CAMP_005" />
                </div>
                <div className="form-group">
                  <label className="form-label">Campaign Name</label>
                  <input className="form-input" placeholder="My New Campaign" />
                </div>
              </div>
              <div className="grid-2" style={{ gap: 16 }}>
                <div className="form-group">
                  <label className="form-label">Agent Name</label>
                  <input className="form-input" placeholder="Priya" />
                </div>
                <div className="form-group">
                  <label className="form-label">Company Name</label>
                  <input className="form-input" placeholder="Your Company" />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Service Name</label>
                <input className="form-input" placeholder="SmartInvest Pro" />
              </div>
              <div className="form-group">
                <label className="form-label">Service Description</label>
                <textarea className="form-textarea" placeholder="Describe the service being promoted..." />
              </div>
              <div className="form-group">
                <label className="form-label">Campaign Objective</label>
                <textarea className="form-textarea" placeholder="What is the goal of this campaign?" style={{ minHeight: 80 }} />
              </div>
              <div className="grid-2" style={{ gap: 16 }}>
                <div className="form-group">
                  <label className="form-label">Language</label>
                  <select className="form-select">
                    <option>English</option>
                    <option>Hindi</option>
                    <option>Hinglish</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Tone</label>
                  <select className="form-select">
                    <option value="professional_warm">Professional & Warm</option>
                    <option value="casual">Casual</option>
                    <option value="formal">Formal</option>
                  </select>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>Cancel</button>
              <button className="btn btn-primary">Create Campaign</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
