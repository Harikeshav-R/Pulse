import { useMemo, useState } from 'react'
import './App.css'

import { CohortAnalytics } from './components/CohortAnalytics'
import { VisitCalendar } from './components/VisitCalendar'
import { SettingsView } from './components/SettingsView'

export type ClinicalTrialCard = {
  id: string
  dateLabel: string
  trialTitle: string
  trialSubtitle: string
  progressPercent: number
  progressColor: string
  cardColor?: string
  siteTeamAvatars: string[]
  trialStatusBadge: string
  badgeColor: string
}

type PatientConversation = {
  id: string
  avatar: string
  patientName: string
  text: string
  time: string
}

export const clinicalTrialCards: ClinicalTrialCard[] = [
  {
    id: 'onco-tp1',
    dateLabel: 'Updated today',
    trialTitle: 'ONCO-2026-TP1',
    trialSubtitle: 'Phase II · MT-401 · Advanced NSCLC',
    progressPercent: 72,
    progressColor: '#c2410c',
    cardColor: '#fee2e2',
    siteTeamAvatars: [
      'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=200&q=80',
      'https://images.unsplash.com/photo-1521119989659-a83eee488004?auto=format&fit=crop&w=200&q=80',
    ],
    trialStatusBadge: 'Recruiting',
    badgeColor: '#c2410c',
  },
  {
    id: 'cardio-lv1',
    dateLabel: 'Updated 1h ago',
    trialTitle: 'CARDIO-2025-LV1',
    trialSubtitle: 'Phase III · HFpEF · multi-site EU/US',
    progressPercent: 54,
    progressColor: '#7c3aed',
    cardColor: '#ede9fe',
    siteTeamAvatars: [
      'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80',
      'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=200&q=80',
    ],
    trialStatusBadge: 'Active dosing',
    badgeColor: '#7c3aed',
  },
  {
    id: 'immu-r01',
    dateLabel: 'Updated 3h ago',
    trialTitle: 'IMMU-2026-R01',
    trialSubtitle: 'Phase Ib · combo · solid tumors',
    progressPercent: 38,
    progressColor: '#0e7490',
    siteTeamAvatars: [
      'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=200&q=80',
      'https://images.unsplash.com/photo-1607746882042-944635dfe10e?auto=format&fit=crop&w=200&q=80',
    ],
    trialStatusBadge: 'Enrollment hold',
    badgeColor: '#0e7490',
  },
  {
    id: 'neuro-m18',
    dateLabel: 'Updated 6h ago',
    trialTitle: 'NEURO-2024-M18',
    trialSubtitle: 'Phase II · early Alzheimer’s · biomarker-led',
    progressPercent: 81,
    progressColor: '#be185d',
    cardColor: '#fce7f3',
    siteTeamAvatars: [
      'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=200&q=80',
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80',
    ],
    trialStatusBadge: 'Follow-up',
    badgeColor: '#be185d',
  },
  {
    id: 'endo-g03',
    dateLabel: 'Updated yesterday',
    trialTitle: 'ENDO-2025-G03',
    trialSubtitle: 'Phase II · T2D · CGM sub-study',
    progressPercent: 65,
    progressColor: '#15803d',
    cardColor: '#dcfce7',
    siteTeamAvatars: [
      'https://images.unsplash.com/photo-1542204625-de293a2f7a5c?auto=format&fit=crop&w=200&q=80',
      'https://images.unsplash.com/photo-1504593811423-6dd665756598?auto=format&fit=crop&w=200&q=80',
    ],
    trialStatusBadge: 'On track',
    badgeColor: '#15803d',
  },
  {
    id: 'rare-x12',
    dateLabel: 'Updated today',
    trialTitle: 'RARE-2026-X12',
    trialSubtitle: 'Phase I · pediatric · single-arm',
    progressPercent: 29,
    progressColor: '#1d4ed8',
    cardColor: '#dbeafe',
    siteTeamAvatars: [
      'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=200&q=80',
      'https://images.unsplash.com/photo-1583195764036-6dc248ac07d9?auto=format&fit=crop&w=200&q=80',
    ],
    trialStatusBadge: 'Startup',
    badgeColor: '#1d4ed8',
  },
]

const patientSafetyThreads: PatientConversation[] = [
  {
    id: 't1',
    avatar:
      'https://images.unsplash.com/photo-1544723795-3fb6469f5b39?auto=format&fit=crop&w=200&q=80',
    patientName: 'David T.',
    text: 'Anyone else on Arm A feel nauseous the first few hours after dosing? I don’t want to overreact but it’s been rough since Tuesday.',
    time: '2 min ago',
  },
  {
    id: 't2',
    avatar:
      'https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=200&h=200&q=80',
    patientName: 'Maria G.',
    text: 'David — I had that week one too. Sipping ginger tea and smaller meals helped. Happy to compare notes if your team says it’s okay.',
    time: '8 min ago',
  },
  {
    id: 't3',
    avatar:
      'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80',
    patientName: 'Thomas O.',
    text: 'Thanks both. I’m on a higher dose and fatigue stacks with the nausea. @Robert did you get any relief after they adjusted your schedule?',
    time: '22 min ago',
  },
  {
    id: 't4',
    avatar:
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80',
    patientName: 'Robert K.',
    text: 'Yeah — moving check-ins to afternoons made it easier to catch symptoms early. Still tired but more manageable.',
    time: '35 min ago',
  },
  {
    id: 't5',
    avatar:
      'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=200&q=80',
    patientName: 'Jennifer W.',
    text: 'Sorry I’ve been quiet — long work days. If someone’s missed a diary entry, did the study app let you backfill or do you call the site?',
    time: '1 hr ago',
  },
  {
    id: 't6',
    avatar:
      'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=200&q=80',
    patientName: 'David T.',
    text: 'Jennifer — I used “add note for yesterday” in Pulse and the CRC messaged me same day. Hope that helps.',
    time: '1 hr ago',
  },
]

function matchesTrialSearch(card: ClinicalTrialCard, query: string): boolean {
  const q = query.trim().toLowerCase()
  if (!q) return true
  const haystack = [
    card.id,
    card.trialTitle,
    card.trialSubtitle,
    card.trialStatusBadge,
    card.dateLabel,
  ]
    .join(' ')
    .toLowerCase()
  return haystack.includes(q)
}

function App() {
  const [darkMode, setDarkMode] = useState(false)
  const [isGridView, setIsGridView] = useState(true)
  const [messagesOpen, setMessagesOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'analytics' | 'calendar' | 'settings'>('overview')
  const [selectedTrialId, setSelectedTrialId] = useState<string | null>(null)
  const [trialSearchQuery, setTrialSearchQuery] = useState('')

  const filteredHomeTrials = useMemo(
    () => clinicalTrialCards.filter((card) => matchesTrialSearch(card, trialSearchQuery)),
    [trialSearchQuery],
  )

  const status = useMemo(() => {
    const recruiting = clinicalTrialCards.filter((c) => c.trialStatusBadge === 'Recruiting').length
    const enrolledApprox = 48 * clinicalTrialCards.length
    return {
      activeTrials: clinicalTrialCards.length,
      recruitingTrials: recruiting,
      enrolledPatients: enrolledApprox,
    }
  }, [])

  return (
    <div className={`app-container ${darkMode ? 'dark' : ''}`}>
      <div className="app-header">
        <div className="app-header-left">
          <span className="app-icon" />
          <p className="app-name">Pulse</p>
          <div className="search-wrapper">
            <input
              className="search-input"
              type="search"
              placeholder="Search trials by name, protocol, or status"
              value={trialSearchQuery}
              onChange={(e) => setTrialSearchQuery(e.target.value)}
              aria-label="Filter clinical trials"
              autoComplete="off"
            />
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
          </div>
        </div>
        <div className="app-header-right">
          <button className={`mode-switch ${darkMode ? 'active' : ''}`} title="Switch Theme" onClick={() => setDarkMode((prev) => !prev)}>
            <svg className="moon" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" width="24" height="24" viewBox="0 0 24 24">
              <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
            </svg>
          </button>
          <button
            type="button"
            className="add-btn"
            title="Open calendar"
            aria-label="Open calendar"
            onClick={() => {
              setActiveTab('calendar')
              setMessagesOpen(false)
            }}
          >
            <svg className="btn-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
          </button>
          <button
            type="button"
            className="notification-btn"
            title="Open settings"
            aria-label="Open settings"
            onClick={() => {
              setActiveTab('settings')
              setMessagesOpen(false)
            }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
          </button>
          <button type="button" className="profile-btn">
            <span>CRC</span>
          </button>
        </div>
        {activeTab === 'overview' && (
          <button className="messages-btn" onClick={() => setMessagesOpen(true)} title="Open patient conversations">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
            </svg>
          </button>
        )}
      </div>

      <div className="app-content">
        <div className="app-sidebar">
          <a href="#" className={`app-sidebar-link ${activeTab === 'overview' ? 'active' : ''}`} aria-label="Overview" onClick={(e) => { e.preventDefault(); setActiveTab('overview'); }}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
          </a>
          <a href="#" className={`app-sidebar-link ${activeTab === 'analytics' ? 'active' : ''}`} aria-label="Cohort Analytics" onClick={(e) => { e.preventDefault(); setActiveTab('analytics'); setSelectedTrialId(null); setMessagesOpen(false); }}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M21.21 15.89A10 10 0 118 2.83M22 12A10 10 0 0012 2v10z" />
            </svg>
          </a>
          <a href="#" className={`app-sidebar-link ${activeTab === 'calendar' ? 'active' : ''}`} aria-label="Visit Calendar" onClick={(e) => { e.preventDefault(); setActiveTab('calendar'); setMessagesOpen(false); }}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
          </a>
          <a href="#" className={`app-sidebar-link ${activeTab === 'settings' ? 'active' : ''}`} aria-label="Settings" onClick={(e) => { e.preventDefault(); setActiveTab('settings'); setMessagesOpen(false); }}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
            </svg>
          </a>
        </div>

        <div className="projects-section">
          {activeTab === 'analytics' ? (
            <CohortAnalytics
              trialId={selectedTrialId}
              onSelectTrial={(id) => {
                setSelectedTrialId(id)
                setActiveTab('analytics')
              }}
              trials={clinicalTrialCards}
            />
          ) : activeTab === 'calendar' ? (
            <VisitCalendar />
          ) : activeTab === 'settings' ? (
            <SettingsView darkMode={darkMode} setDarkMode={setDarkMode} />
          ) : (
            <>
          <div className="projects-section-header">
            <p>Clinical Trials</p>
            <p className="time">March 2026</p>
          </div>
          <div className="projects-section-line">
            <div className="projects-status">
              <div className="item-status">
                <span className="status-number">{status.activeTrials}</span>
                <span className="status-type">Active Trials</span>
              </div>
              <div className="item-status">
                <span className="status-number">{status.recruitingTrials}</span>
                <span className="status-type">Recruiting</span>
              </div>
              <div className="item-status">
                <span className="status-number">{status.enrolledPatients}</span>
                <span className="status-type">Patients Enrolled</span>
              </div>
            </div>
            <div className="view-actions">
              <button className={`view-btn list-view ${!isGridView ? 'active' : ''}`} title="List View" onClick={() => setIsGridView(false)}>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="8" y1="6" x2="21" y2="6" />
                  <line x1="8" y1="12" x2="21" y2="12" />
                  <line x1="8" y1="18" x2="21" y2="18" />
                  <line x1="3" y1="6" x2="3.01" y2="6" />
                  <line x1="3" y1="12" x2="3.01" y2="12" />
                  <line x1="3" y1="18" x2="3.01" y2="18" />
                </svg>
              </button>
              <button className={`view-btn grid-view ${isGridView ? 'active' : ''}`} title="Grid View" onClick={() => setIsGridView(true)}>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="7" height="7" />
                  <rect x="14" y="3" width="7" height="7" />
                  <rect x="14" y="14" width="7" height="7" />
                  <rect x="3" y="14" width="7" height="7" />
                </svg>
              </button>
            </div>
          </div>

          <div className={`project-boxes ${isGridView ? 'jsGridView' : 'jsListView'}`}>
            {filteredHomeTrials.length === 0 ? (
              <p className="trial-grid-empty" role="status">
                No trials match &ldquo;{trialSearchQuery.trim()}&rdquo;. Try another name, protocol code, or status.
              </p>
            ) : (
              filteredHomeTrials.map((card) => (
              <div className="project-box-wrapper" key={card.id}>
                <div 
                  className="project-box" 
                  style={{ backgroundColor: card.cardColor, cursor: 'pointer' }}
                  onClick={() => {
                    setSelectedTrialId(card.id)
                    setActiveTab('analytics')
                  }}
                >
                  <div className="project-box-header">
                    <span>{card.dateLabel}</span>
                    <div className="more-wrapper">
                      <button className="project-btn-more" aria-label={`More actions for ${card.trialTitle}`}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <circle cx="12" cy="12" r="1" />
                          <circle cx="12" cy="5" r="1" />
                          <circle cx="12" cy="19" r="1" />
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div className="project-box-content-header">
                    <p className="box-content-header">{card.trialTitle}</p>
                    <p className="box-content-subheader">{card.trialSubtitle}</p>
                  </div>
                  <div className="box-progress-wrapper">
                    <p className="box-progress-header">Trial progress</p>
                    <div className="box-progress-bar">
                      <span className="box-progress" style={{ width: `${card.progressPercent}%`, backgroundColor: card.progressColor }} />
                    </div>
                    <p className="box-progress-percentage">{card.progressPercent}%</p>
                  </div>
                  <div className="project-box-footer">
                    <div className="participants">
                      {card.siteTeamAvatars.map((src, index) => (
                        <img src={src} alt={`Site team ${index + 1}`} key={src} />
                      ))}
                      <button className="add-participant" style={{ color: card.badgeColor }} title="Add site lead">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M12 5v14M5 12h14" />
                        </svg>
                      </button>
                    </div>
                    <div className="days-left" style={{ color: card.badgeColor }}>
                      {card.trialStatusBadge}
                    </div>
                  </div>
                </div>
              </div>
              ))
            )}
          </div>
            </>
          )}
        </div>

        {activeTab === 'overview' && (
          <div className={`messages-section ${messagesOpen ? 'show' : ''}`}>
            <button className="messages-close" onClick={() => setMessagesOpen(false)} title="Close conversations">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="15" y1="9" x2="9" y2="15" />
                <line x1="9" y1="9" x2="15" y2="15" />
              </svg>
            </button>
            <div className="projects-section-header">
              <p>Patient conversations</p>
            </div>
            <div className="messages">
              {patientSafetyThreads.map((msg) => (
                <div className="message-box" key={msg.id}>
                  <img src={msg.avatar} alt="" />
                  <div className="message-content">
                    <div className="message-header">
                      <div className="name">{msg.patientName}</div>
                      <div className="star-checkbox">
                        <input type="checkbox" id={msg.id} />
                        <label htmlFor={msg.id}>
                          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                          </svg>
                        </label>
                      </div>
                    </div>
                    <p className="message-line">{msg.text}</p>
                    <p className="message-line time">{msg.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
