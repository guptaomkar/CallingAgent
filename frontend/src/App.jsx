// ============================================================
// App Component — Root with Router
// File: src/App.jsx
// ============================================================

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Campaigns from './pages/Campaigns'
import Contacts from './pages/Contacts'
import CallMonitor from './pages/CallMonitor'
import Reports from './pages/Reports'

export default function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <div className="page-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/campaigns" element={<Campaigns />} />
              <Route path="/contacts/:campaignId?" element={<Contacts />} />
              <Route path="/calls" element={<CallMonitor />} />
              <Route path="/reports" element={<Reports />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  )
}
