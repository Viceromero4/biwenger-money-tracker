import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import { getLeagueDashboard } from '../services/dashboardService.js'
import { getLeagueMovements } from '../services/movementService.js'
import MovementItem from '../components/MovementItem.jsx'
import { useLeague } from '../context/LeagueContext.jsx'
import { formatCurrency } from '../utils/formatCurrency.js'

import './ParticipantDetailPage.css'

function ParticipantDetailPage() {
  const { leagueParticipantId } = useParams()
  const { selectedLeagueId } = useLeague()

  const [participant, setParticipant] = useState(null)
  const [participants, setParticipants] = useState([])
  const [movements, setMovements] = useState([])
  const [initialBalance, setInitialBalance] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadParticipantDetail() {
      try {
        setLoading(true)
        setError(null)

        const dashboardData = await getLeagueDashboard(selectedLeagueId)
        const movementsData = await getLeagueMovements(selectedLeagueId)

        const participantId = Number(leagueParticipantId)

        const foundParticipant = dashboardData.participants.find(
          (participant) =>
            participant.league_participant_id === participantId
        )

        if (!foundParticipant) {
          throw new Error('Participante no encontrado')
        }

        const participantMovements = movementsData.filter(
          (movement) =>
            movement.league_participant_id === participantId
        )

        setParticipant(foundParticipant)
        setParticipants(dashboardData.participants)
        setMovements(participantMovements)
        setInitialBalance(dashboardData.initial_balance)
      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    loadParticipantDetail()
  }, [leagueParticipantId, selectedLeagueId])

  if (loading) {
    return <p>Cargando participante...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  const balanceDifference =
    participant.current_balance - initialBalance

  return (
    <main className="participant-detail-page">
      <header className="participant-detail-header">
        <div>
          <p className="participant-detail-label">
            Participante
          </p>

          <h1>{participant.name}</h1>
        </div>

        <div className="participant-balance-card">
          <span>Saldo actual</span>

          <strong>
            {formatCurrency(participant.current_balance)}
          </strong>

          <small
            className={
              balanceDifference >= 0
                ? 'balance-positive'
                : 'balance-negative'
            }
          >
            Variación:{' '}
            {balanceDifference > 0 ? '+' : ''}
            {formatCurrency(balanceDifference)}
          </small>
        </div>
      </header>

      <section className="participant-movements-section">
        <div className="participant-section-header">
          <div>
            <h2>Movimientos</h2>
            <p>
              Historial económico de {participant.name}
            </p>
          </div>

          <span className="movements-count">
            {movements.length} movimientos
          </span>
        </div>

        <div className="participant-movements-list">
          {movements.length === 0 ? (
            <p>Este participante todavía no tiene movimientos.</p>
          ) : (
            movements.map((movement) => (
              <MovementItem
                key={movement.id}
                movement={movement}
                participants={participants}
              />
            ))
          )}
        </div>
      </section>
    </main>
  )
}

export default ParticipantDetailPage