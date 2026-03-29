import { useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts'
import { useTrialOverview, useCohortAEIncidence } from '../hooks/useAlerts'
import type { ClinicalTrialCard } from '../App'
import { PatientListPage } from '../pages/PatientListPage'
import { PatientDetailPage } from '../pages/PatientDetailPage'
import { AlertQueuePage } from '../pages/AlertQueuePage'
import './CohortAnalytics.css'

interface CohortAnalyticsProps {
  trialId: string | null
  onSelectTrial: (id: string) => void
  trials: ClinicalTrialCard[]
  onAddTrial?: (trial: ClinicalTrialCard) => void
}

const mockHRTrend = [
  { day: 'Day -14', hr: 72 },
  { day: 'Day -10', hr: 74 },
  { day: 'Day -7', hr: 73 },
  { day: 'Day -5', hr: 78 },
  { day: 'Day -3', hr: 82 },
  { day: 'Day -1', hr: 85 },
  { day: 'Today', hr: 88 },
]

export function CohortAnalytics({ trialId, onSelectTrial, trials, onAddTrial }: CohortAnalyticsProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [isAddingTrial, setIsAddingTrial] = useState(false)
  const [newTrialInfo, setNewTrialInfo] = useState('')
  const [activeSubView, setActiveSubView] = useState<'stats' | 'patients'>('stats')
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null)

  const fetchCohortStats = !!trialId && !trialId.startsWith('new-')
  const { data: overview, isLoading: overviewLoading } = useTrialOverview(trialId, fetchCohortStats)
  const { data: aeData, isLoading: aeLoading } = useCohortAEIncidence(trialId, 30, fetchCohortStats)

  if (!trialId) {
    const filteredTrials = trials.filter(t => 
      t.trialTitle.toLowerCase().includes(searchQuery.toLowerCase()) || 
      t.trialSubtitle.toLowerCase().includes(searchQuery.toLowerCase())
    )

    if (isAddingTrial) {
      return (
        <div className="analytics-search-view">
          <div className="projects-section-header">
            <p>Add New Clinical Trial</p>
          </div>
          <div className="add-trial-form">
            <div className="form-group">
              <label>Trial Information</label>
              <textarea 
                value={newTrialInfo}
                onChange={(e) => setNewTrialInfo(e.target.value)}
                placeholder="e.g., Phase I/II study of CAR-T cell therapy targeting CD19 in relapsed/refractory B-cell acute lymphoblastic leukemia."
                rows={4}
              />
            </div>
            <div className="form-group">
              <label>Preclinical Data (PDF/Doc)</label>
              <input type="file" />
            </div>
            <div className="form-group">
              <label>Patient Data (CSV/Excel)</label>
              <input type="file" />
            </div>
            <div className="form-actions">
              <button className="cancel-btn" onClick={() => setIsAddingTrial(false)}>Cancel</button>
              <button className="submit-btn" onClick={() => {
                const newTrial: ClinicalTrialCard = {
                  id: `new-${Date.now()}`,
                  dateLabel: 'Just now',
                  trialTitle: 'NEW-TRIAL',
                  trialSubtitle: newTrialInfo.length > 50 ? newTrialInfo.substring(0, 50) + '...' : newTrialInfo,
                  progressPercent: 0,
                  progressColor: '#3b82f6',
                  cardColor: '#eff6ff',
                  siteTeamAvatars: [],
                  trialStatusBadge: 'Setup',
                  badgeColor: '#3b82f6',
                }
                onAddTrial?.(newTrial)
                setIsAddingTrial(false)
              }}>Add Trial</button>
            </div>
          </div>
        </div>
      )
    }

    return (
      <div className="analytics-search-view">
        <div className="projects-section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <p>Clinical Trials Analytics</p>
          <button className="add-btn-primary" onClick={() => setIsAddingTrial(true)}>+ Add Trial</button>
        </div>
        <div className="analytics-search-box">
          <input 
            type="text" 
            placeholder="Search trial by name or protocol..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="analytics-trials-list">
          {filteredTrials.map(trial => (
            <div 
              key={trial.id} 
              className="analytics-trial-card"
              style={{ borderLeftColor: trial.badgeColor }}
              onClick={() => onSelectTrial(trial.id)}
            >
              <h3>{trial.trialTitle}</h3>
              <p>{trial.trialSubtitle}</p>
              <span className="badge" style={{ backgroundColor: trial.cardColor, color: trial.badgeColor }}>
                {trial.trialStatusBadge}
              </span>
            </div>
          ))}
          {filteredTrials.length === 0 && <p className="no-results">No trials found matching "{searchQuery}"</p>}
        </div>
      </div>
    )
  }

  const trial = trials.find(t => t.id === trialId)
  if (!trial) return <p>Trial not found.</p>

  const isNewTrial = trialId.startsWith('new-')

  if (fetchCohortStats && (overviewLoading || aeLoading)) {
    return <div style={{ padding: 20 }}>Loading analytics...</div>
  }

  // Process data for charts
  const riskDistribution = overview?.risk_distribution || { low: 0, medium: 0, high: 0 };
  const riskChartData = [
    { name: 'Low Risk', value: riskDistribution.low || 0, color: '#10b981' },
    { name: 'Medium Risk', value: riskDistribution.medium || 0, color: '#f59e0b' },
    { name: 'High Risk', value: riskDistribution.high || 0, color: '#ef4444' },
  ];

  // Process AE data
  // aeData shape: { "Nausea": { count: 12, by_grade: { 1: 5, 2: 4, 3: 3 } } ... } or something similar.
  // We need array format for Recharts.
  const symptomsData = aeData ? Object.entries(aeData).map(([name, stats]) => {
    const s = stats as { by_grade?: Record<string, number> };
    return {
      name,
      grade1: s.by_grade?.['1'] || 0,
      grade2: s.by_grade?.['2'] || 0,
      grade3: s.by_grade?.['3'] || 0,
    };
  }) : [];

  return (
    <div className="analytics-stats-view" style={{ '--theme-color': trial.progressColor } as React.CSSProperties}>
      <div className="analytics-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <button className="back-btn" onClick={() => {
            onSelectTrial('')
            setActiveSubView('stats')
            setSelectedPatientId(null)
          }}>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            Back to Trials
          </button>
          <div>
            <h2>{trial.trialTitle} {activeSubView === 'stats' ? 'Stats' : 'Patients'}</h2>
            <p>{trial.trialSubtitle}</p>
          </div>
        </div>
        <button 
          className="add-btn-primary" 
          onClick={() => {
            setActiveSubView(v => v === 'stats' ? 'patients' : 'stats')
            setSelectedPatientId(null)
          }}
        >
          {activeSubView === 'stats' ? 'Patients' : 'Stats'}
        </button>
      </div>

      {activeSubView === 'patients' ? (
        selectedPatientId ? (
          <PatientDetailPage 
            patientId={selectedPatientId} 
            onBack={() => setSelectedPatientId(null)} 
          />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
            <PatientListPage trialId={trialId} onSelectPatient={setSelectedPatientId} />
            <hr style={{ border: 'none', borderTop: '1px solid var(--muted-border)' }} />
            <AlertQueuePage trialId={trialId} />
          </div>
        )
      ) : isNewTrial ? (
        <div className="analytics-new-trial-empty">
          <p className="analytics-new-trial-empty-title">No analytics yet</p>
          <p className="analytics-new-trial-empty-copy">
            This trial is still in setup. Cohort KPIs, adverse-event summaries, risk distribution, and wearable trends will
            appear here after patients are enrolled and visit, symptom, and device data are flowing.
          </p>
        </div>
      ) : (
        <>
          <div className="kpi-grid">
        <div className="kpi-card">
          <p className="kpi-title">Total Enrolled</p>
          <h3 className="kpi-value">{overview?.total_patients || 0}</h3>
          <p className="kpi-trend">Across {overview?.total_sites || 0} active sites</p>
        </div>
        <div className="kpi-card">
          <p className="kpi-title">Check-ins Completed (7d)</p>
          <h3 className="kpi-value">{overview?.checkins_last_7_days || 0}</h3>
          <p className="kpi-trend">Total submitted</p>
        </div>
        <div className="kpi-card">
          <p className="kpi-title">Open Alerts</p>
          <h3 className="kpi-value" style={{ color: (overview?.open_alerts?.critical || 0) > 0 ? '#ef4444' : 'inherit' }}>
            {overview?.open_alerts?.critical || 0}
          </h3>
          <p className="kpi-trend">Critical alerts pending</p>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container span-2">
          <h3>Adverse Events Reported (CTCAE Grades)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={symptomsData.length > 0 ? symptomsData : [{ name: 'None', grade1: 0, grade2: 0, grade3: 0 }]}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--muted-border)" />
              <XAxis dataKey="name" tick={{fill: 'var(--secondary-color)'}} />
              <YAxis tick={{fill: 'var(--secondary-color)'}} />
              <Tooltip cursor={{fill: 'var(--link-color-hover)'}} contentStyle={{backgroundColor: 'var(--surface-bg)', border: '1px solid var(--muted-border)'}} />
              <Legend />
              <Bar dataKey="grade1" name="Grade 1 (Mild)" stackId="a" fill="#3b82f6" />
              <Bar dataKey="grade2" name="Grade 2 (Mod)" stackId="a" fill="#f59e0b" />
              <Bar dataKey="grade3" name="Grade 3 (Severe)" stackId="a" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Patient Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={riskChartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {riskChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} stroke="transparent" />
                ))}
              </Pie>
              <Tooltip contentStyle={{backgroundColor: 'var(--surface-bg)', border: '1px solid var(--muted-border)'}} />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container span-3">
          <h3>Top Watchlist: Wearable Anomaly (Resting HR Trend)</h3>
          <p className="chart-desc">Aggregate view of patients approaching high risk</p>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={mockHRTrend}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--muted-border)" />
              <XAxis dataKey="day" tick={{fill: 'var(--secondary-color)'}} />
              <YAxis domain={['dataMin - 5', 'auto']} tick={{fill: 'var(--secondary-color)'}} />
              <Tooltip contentStyle={{backgroundColor: 'var(--surface-bg)', border: '1px solid var(--muted-border)'}} />
              <Line type="monotone" dataKey="hr" name="Resting HR (bpm)" stroke="#ef4444" strokeWidth={3} dot={{r: 4}} activeDot={{r: 8}} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      </>
      )}
    </div>
  )
}
