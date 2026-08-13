const API_URL = 'http://127.0.0.1:8000'

export async function createTransfer(transferData) {
  const response = await fetch(`${API_URL}/transfers`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(transferData),
  })

  if (!response.ok) {
    throw new Error('Error al crear la transferencia')
  }

  return response.json()
}