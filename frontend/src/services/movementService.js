const API_URL = 'http://127.0.0.1:8000'

export async function getLeagueMovements(leagueId) {
  const response = await fetch(`${API_URL}/movements/league/${leagueId}`)

  if (!response.ok) {
    throw new Error('Error al obtener los movimientos de la liga')
  }

  return response.json()
}

export async function createMovement(movementData) {
  const response = await fetch(`${API_URL}/movements`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(movementData),
  })

  if (!response.ok) {
    throw new Error('Error al crear el movimiento')
  }

  return response.json()
}