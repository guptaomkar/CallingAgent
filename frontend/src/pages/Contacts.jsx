// ============================================================
// Contacts Page — Upload and manage contact lists
// File: src/pages/Contacts.jsx
// ============================================================

import { useState, useRef } from 'react'
import {
  Upload, Plus, Search, Download, Trash2,
  FileSpreadsheet, CheckCircle2, AlertCircle,
  Users, Phone, Mail, Filter,
} from 'lucide-react'

const mockContacts = [
  { id: 1, client_name: 'Rajesh Sharma', phone_number: '+91 9876543210', email: 'rajesh@email.com', status: 'completed', is_dnd: false },
  { id: 2, client_name: 'Priya Patel', phone_number: '+91 8765432109', email: 'priya@email.com', status: 'pending', is_dnd: false },
  { id: 3, client_name: 'Amit Kumar', phone_number: '+91 7654321098', email: null, status: 'completed', is_dnd: false },
  { id: 4, client_name: 'Sneha Reddy', phone_number: '+91 6543210987', email: 'sneha@email.com', status: 'in_progress', is_dnd: false },
  { id: 5, client_name: 'Vikram Singh', phone_number: '+91 5432109876', email: null, status: 'failed', is_dnd: false },
  { id: 6, client_name: 'Meena Iyer', phone_number: '+91 4321098765', email: 'meena@email.com', status: 'pending', is_dnd: true },
  { id: 7, client_name: 'Ravi Prasad', phone_number: '+91 3210987654', email: 'ravi@email.com', status: 'pending', is_dnd: false },
  { id: 8, client_name: 'Deepa Nair', phone_number: '+91 2109876543', email: null, status: 'blacklisted', is_dnd: false },
]

export default function Contacts() {
  const [searchQuery, setSearchQuery] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const fileInputRef = useRef(null)

  const filteredContacts = mockContacts.filter(c =>
    c.client_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.phone_number.includes(searchQuery)
  )

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFileUpload(file)
  }

  const handleFileUpload = (file) => {
    // Simulate upload result
    setUploadResult({
      total_rows: 156,
      valid_contacts: 142,
      duplicates_skipped: 8,
      invalid_rows: 4,
      dnd_excluded: 2,
    })
  }

  const statusColors = {
    pending: 'draft',
    queued: 'paused',
    in_progress: 'active',
    completed: 'completed',
    failed: 'failed',
    dnd: 'paused',
    blacklisted: 'failed',
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Contacts</h1>
          <p>Upload and manage your client contact lists</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary"><Download size={16} /> Export</button>
          <button className="btn btn-primary" onClick={() => fileInputRef.current?.click()}>
            <Upload size={16} /> Upload File
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.csv"
            style={{ display: 'none' }}
            onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
          />
        </div>
      </div>

      {/* Upload Zone */}
      <div
        className={`file-upload-zone ${dragOver ? 'dragging' : ''}`}
        style={{ marginBottom: 24 }}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="file-upload-icon">
          <FileSpreadsheet size={28} />
        </div>
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 6 }}>
          Drop your Excel or CSV file here
        </h3>
        <p style={{ color: 'var(--text-tertiary)', fontSize: 14 }}>
          or click to browse. Required columns: client_name, phone_number
        </p>
      </div>

      {/* Upload Result */}
      {uploadResult && (
        <div className="card" style={{ marginBottom: 24, borderColor: 'rgba(99, 102, 241, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
            <CheckCircle2 size={24} style={{ color: 'var(--accent-emerald)' }} />
            <h3 style={{ fontSize: 16, fontWeight: 600 }}>Upload Complete</h3>
          </div>
          <div className="stats-grid" style={{ marginBottom: 0 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: 'var(--text-primary)' }}>{uploadResult.total_rows}</div>
              <div style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>Total Rows</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: 'var(--accent-emerald)' }}>{uploadResult.valid_contacts}</div>
              <div style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>Valid Contacts</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: 'var(--accent-amber)' }}>{uploadResult.duplicates_skipped}</div>
              <div style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>Duplicates</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: 'var(--accent-rose)' }}>{uploadResult.invalid_rows}</div>
              <div style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>Invalid</div>
            </div>
          </div>
        </div>
      )}

      {/* Search & Filter */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
        <div style={{ position: 'relative', flex: 1, maxWidth: 360 }}>
          <Search size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input className="form-input" placeholder="Search contacts..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} style={{ paddingLeft: 40 }} />
        </div>
        <button className="btn btn-secondary btn-sm"><Filter size={14} /> Filter</button>
      </div>

      {/* Contacts Table */}
      <div className="card">
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Phone Number</th>
                <th>Email</th>
                <th>Status</th>
                <th>DND</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredContacts.map((contact) => (
                <tr key={contact.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: '50%',
                        background: 'var(--gradient-primary)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 12, fontWeight: 700, color: 'white', flexShrink: 0,
                      }}>
                        {contact.client_name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{contact.client_name}</span>
                    </div>
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: 13 }}>{contact.phone_number}</td>
                  <td>{contact.email || <span style={{ color: 'var(--text-muted)' }}>—</span>}</td>
                  <td>
                    <span className={`badge ${statusColors[contact.status] || 'draft'}`}>
                      <span className="badge-dot"></span>
                      {contact.status}
                    </span>
                  </td>
                  <td>
                    {contact.is_dnd ? (
                      <span className="badge paused"><AlertCircle size={11} /> DND</span>
                    ) : (
                      <span style={{ color: 'var(--text-muted)' }}>—</span>
                    )}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button className="btn btn-icon btn-secondary btn-sm" title="Call">
                        <Phone size={13} />
                      </button>
                      <button className="btn btn-icon btn-secondary btn-sm" title="Delete" style={{ color: 'var(--accent-rose)' }}>
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
