// ============================================================
// Sidebar Navigation Component
// File: src/components/Sidebar.jsx
// ============================================================

import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Megaphone,
  Users,
  Phone,
  FileBarChart,
  Settings,
  Bot,
} from 'lucide-react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/campaigns', label: 'Campaigns', icon: Megaphone },
  { path: '/contacts', label: 'Contacts', icon: Users },
  { path: '/calls', label: 'Call Monitor', icon: Phone, badge: 'Live' },
  { path: '/reports', label: 'Reports', icon: FileBarChart },
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <Bot size={22} color="white" />
          </div>
          <div>
            <div className="sidebar-logo-text">CallAgent AI</div>
            <div className="sidebar-logo-version">v1.0</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Main Menu</div>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `sidebar-nav-item ${isActive ? 'active' : ''}`
            }
          >
            <item.icon />
            <span>{item.label}</span>
            {item.badge && (
              <span className="sidebar-badge">{item.badge}</span>
            )}
          </NavLink>
        ))}

        <div className="sidebar-section-label">System</div>
        <NavLink to="/settings" className="sidebar-nav-item">
          <Settings />
          <span>Settings</span>
        </NavLink>
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-status">
          <span className="sidebar-status-dot"></span>
          <span>System Online</span>
        </div>
      </div>
    </aside>
  )
}
