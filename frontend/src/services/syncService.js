const API_URL = 'http://localhost:8000'

export async function syncLeague(leagueId) {
  const response = await fetch(
    `${API_URL}/leagues/${leagueId}/sync`,
    {
      method: 'POST',
    }
  )

  if (!response.ok) {
    const errorData = await response.json().catch(() => null)

    throw new Error(
      errorData?.detail ?? 'Error al sincronizar la liga'
    )
  }

  return response.json()
}