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
import './CohortAnalytics.css'

interface CohortAnalyticsProps {
  trialId: string | null
  onSelectTrial: (id: string) => void
  trials: ClinicalTrialCard[]
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

export function CohortAnalytics({ trialId, onSelectTrial, trials }: CohortAnalyticsProps) {
  const [searchQuery, setSearchQuery] = useState('')

  const { data: overview, isLoading: overviewLoading } = useTrialOverview(trialId);
  const { data: aeData, isLoading: aeLoading } = useCohortAEIncidence(trialId);

  if (!trialId) {
    const filteredTrials = trials.filter(t => 
      t.trialTitle.toLowerCase().includes(searchQuery.toLowerCase()) || 
      t.trialSubtitle.toLowerCase().includes(searchQuery.toLowerCase())
    )

    return (
      <div className="analytics-search-view">
        <div className="projects-section-header">
          <p>Clinical Trials Analytics</p>
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

  if (overviewLoading || aeLoading) return <div style={{ padding: 20 }}>Loading analytics...</div>;

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
      <div className="analytics-header">
        <button className="back-btn" onClick={() => onSelectTrial('')}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Trials
        </button>
        <div>
          <h2>{trial.trialTitle} Stats</h2>
          <p>{trial.trialSubtitle}</p>
        </div>
      </div>

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
    </div>
  )
}
