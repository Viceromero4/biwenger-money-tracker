import { useEffect, useState } from 'react'
import { getLeagueDashboard } from '../services/dashboardService.js'
import { useLeague } from '../context/LeagueContext.jsx'
import './NewMovementPage.css'

function RegisterParticipantPage() {
  const { selectedLeagueId } = useLeague()

  const [leagueName, setLeagueName] = useState('')
  const [seasonName, setSeasonName] = useState('')

  const [name, setName] = useState('')
  const [teamName, setTeamName] = useState('')

  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function loadLeague() {
      try {
        setError('')

        const data = await getLeagueDashboard(selectedLeagueId)

        setLeagueName(data.league_name)
        setSeasonName(data.season_name)
      } catch {
        setError('No se pudo cargar la liga.')
      }
    }

    loadLeague()
  }, [selectedLeagueId])

  async function handleSubmit(event) {
    event.preventDefault()

    setMessage('')
    setError('')
    setLoading(true)

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/league-participants/register',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            league_id: selectedLeagueId,
            name,
            team_name: teamName,
          }),
        }
      )

      if (!response.ok) {
        throw new Error('No se pudo registrar el participante.')
      }

      setMessage('Participante añadido correctamente.')

      setName('')
      setTeamName('')
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="new-movement-page">
      <div className="form-container">
        <div className="form-header">
          <h1>Añadir participante</h1>
          <p>Añade un jugador a una liga.</p>
        </div>

        <form className="movement-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Temporada</label>
            <input value={seasonName} disabled />
          </div>

          <div className="form-group">
            <label>Liga</label>
            <input value={leagueName} disabled />
          </div>

          <div className="form-group">
            <label htmlFor="name">Nombre del jugador</label>

            <input
              id="name"
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="teamName">Nombre del equipo</label>

            <input
              id="teamName"
              type="text"
              value={teamName}
              onChange={(event) => setTeamName(event.target.value)}
              required
            />
          </div>

          <button
            className="submit-button"
            type="submit"
            disabled={loading}
          >
            {loading ? 'Añadiendo...' : 'Añadir participante'}
          </button>
        </form>

        {message && (
          <p className="form-success">{message}</p>
        )}

        {error && (
          <p className="form-error">{error}</p>
        )}
      </div>
    </main>
  )
}

export default RegisterParticipantPage