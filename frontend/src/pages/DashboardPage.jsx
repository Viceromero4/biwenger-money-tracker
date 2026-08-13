import { useEffect, useState } from 'react'
import { getLeagueDashboard } from '../services/dashboardService.js'
import ParticipantCard from '../components/ParticipantCard.jsx'
import './DashboardPage.css'
import { getLeagueMovements } from '../services/movementService.js'
import MovementItem from '../components/MovementItem.jsx'
import { useLeague } from '../context/LeagueContext.jsx'

function formatMillions(amount) {
  return `${(amount / 1000000).toFixed(2)} M €`
}

function DashboardPage() {
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [movements, setMovements] = useState([])
  const { selectedLeagueId } = useLeague()

  useEffect(() => {
    async function loadDashboard() {
      try {
        const data = await getLeagueDashboard(selectedLeagueId)
        setDashboard(data)
        const movementsData = await getLeagueMovements(selectedLeagueId)
        setMovements(movementsData)
      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    loadDashboard()
  }, [selectedLeagueId])

  if (loading) {
    return <p>Cargando dashboard...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  const sortedParticipants = [...dashboard.participants].sort(
  (a, b) => b.current_balance - a.current_balance

)

const latestMovements = movements.slice(0, 5)

return (
  <main className="dashboard">
  <header className="dashboard-header">
    <div>
      <p className="dashboard-label">Liga</p>
      <h1>{dashboard.league_name}</h1>
    </div>

    <div className="dashboard-summary">
      <div className="summary-item">
        <span>Temporada</span>
        <strong>{dashboard.season_name}</strong>
      </div>

      <div className="summary-item">
        <span>Saldo inicial</span>
        <strong>{formatMillions(dashboard.initial_balance)}</strong>
      </div>

      <div className="summary-item">
        <span>Participantes</span>
        <strong>{dashboard.participants.length}</strong>
      </div>
    </div>
  </header>

    <section>
      <h2>Participantes</h2>

      <div className="participants-grid">
        {sortedParticipants.map((participant) => (
          <ParticipantCard
            key={participant.league_participant_id}
            participant={participant}
            initialBalance={dashboard.initial_balance}
          />
        ))}
      </div>
    </section>
    <section>
      <h2>Últimos movimientos</h2>

      {latestMovements.map((movement) => (
        <MovementItem
          key={movement.id}
          movement={movement}
          participants={dashboard.participants}
        />
      ))}
    </section>
  </main>
)
}

export default DashboardPage