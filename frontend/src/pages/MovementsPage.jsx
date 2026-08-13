import { useEffect, useState } from 'react'
import './MovementsPage.css'

import { getLeagueDashboard } from '../services/dashboardService.js'
import { getLeagueMovements } from '../services/movementService.js'
import MovementItem from '../components/MovementItem.jsx'
import { useLeague } from '../context/LeagueContext.jsx'

function MovementsPage() {
  const { selectedLeagueId } = useLeague()

  const [participants, setParticipants] = useState([])
  const [movements, setMovements] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadMovements() {
      try {
        setLoading(true)
        setError(null)

        const dashboardData = await getLeagueDashboard(selectedLeagueId)
        const movementsData = await getLeagueMovements(selectedLeagueId)

        setParticipants(dashboardData.participants)
        setMovements(movementsData)
      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    loadMovements()
  }, [selectedLeagueId])

  if (loading) {
    return <p>Cargando movimientos...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <main className="movements-page">
      <h1>Movimientos</h1>

      <p>
        Historial completo de movimientos de la liga.
      </p>

      <section className="movements-list">
        {movements.map((movement) => (
          <MovementItem
            key={movement.id}
            movement={movement}
            participants={participants}
          />
        ))}
      </section>
    </main>
  )
}

export default MovementsPage