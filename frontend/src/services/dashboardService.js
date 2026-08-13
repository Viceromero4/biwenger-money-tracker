const API_URL = 'http://127.0.0.1:8000'

export async function getLeagueDashboard(leagueId) {
  const response = await fetch(`${API_URL}/dashboard/league/${leagueId}`)

  if (!response.ok) {
    throw new Error('Error al obtener el dashboard de la liga')
  }

  return response.json()
}