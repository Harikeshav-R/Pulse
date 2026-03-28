import './SettingsView.css'

interface SettingsViewProps {
  darkMode: boolean
  setDarkMode: React.Dispatch<React.SetStateAction<boolean>>
}

export function SettingsView({ darkMode, setDarkMode }: SettingsViewProps) {
  return (
    <div className="settings-wrapper">
      <div className="projects-section-header">
        <p>Settings</p>
      </div>
      
      <div className="settings-container">
        <div className="settings-section">
          <h3>Profile & Account</h3>
          <div className="settings-card">
            <div className="profile-info">
              <div className="profile-details">
                <h4>Sarah Jenkins</h4>
                <p>Clinical Research Coordinator</p>
                <button className="settings-btn secondary">Edit Profile</button>
              </div>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <h3>Preferences</h3>
          <div className="settings-card">
            <div className="setting-row">
              <div>
                <h4>Dark Mode</h4>
                <p>Toggle the appearance of the dashboard</p>
              </div>
              <label className="switch">
                <input 
                  type="checkbox" 
                  checked={darkMode} 
                  onChange={(e) => setDarkMode(e.target.checked)} 
                />
                <span className="slider round"></span>
              </label>
            </div>
            
            <div className="setting-row">
              <div>
                <h4>Language</h4>
                <p>Select your preferred language</p>
              </div>
              <select className="settings-select">
                <option>English (US)</option>
                <option>Spanish (ES)</option>
                <option>French (FR)</option>
              </select>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <h3>Notifications</h3>
          <div className="settings-card">
            <div className="setting-row">
              <div>
                <h4>Email Alerts</h4>
                <p>Receive updates for critical patient reports</p>
              </div>
              <label className="switch">
                <input type="checkbox" defaultChecked />
                <span className="slider round"></span>
              </label>
            </div>
            
            <div className="setting-row">
              <div>
                <h4>In-App Notifications</h4>
                <p>Show toast notifications inside the dashboards</p>
              </div>
              <label className="switch">
                <input type="checkbox" defaultChecked />
                <span className="slider round"></span>
              </label>
            </div>
            
            <div className="setting-row">
              <div>
                <h4>Daily Summary</h4>
                <p>Receive a daily digest of trial progress</p>
              </div>
              <label className="switch">
                <input type="checkbox" />
                <span className="slider round"></span>
              </label>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <h3>Security & Data</h3>
          <div className="settings-card">
            <div className="setting-row action-row">
              <div>
                <h4>Data Export</h4>
                <p>Download your historical clinical trial data</p>
              </div>
              <button className="settings-btn primary">Export CSV</button>
            </div>
            <div className="setting-row action-row">
              <div>
                <h4>Password</h4>
                <p>Update your authentication credentials</p>
              </div>
              <button className="settings-btn secondary">Change Password</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
