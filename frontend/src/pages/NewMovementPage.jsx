import { useEffect, useState } from 'react'
import { getLeagueDashboard } from '../services/dashboardService.js'
import { createMovement } from '../services/movementService.js'
import './NewMovementPage.css'
import { createTransfer } from '../services/transferService.js'
import { useLeague } from '../context/LeagueContext.jsx'

function NewMovementPage() {
  const { selectedLeagueId } = useLeague()
  const [participants, setParticipants] = useState([])

  const [formData, setFormData] = useState({
    league_participant_id: '',
    type: 'purchase',
    amount: '',
    player_name: '',
    description: '',
    occurred_at: '',
  })

  const [transferData, setTransferData] = useState({
    transfer_type: 'clause',
    buyer_league_participant_id: '',
    seller_league_participant_id: '',
    amount: '',
    player_name: '',
    description: '',
    occurred_at: '',
  })

  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [operationType, setOperationType] = useState('movement')


  useEffect(() => {
    async function loadParticipants() {
      try {
        setError('')

        const dashboard = await getLeagueDashboard(selectedLeagueId)

        setParticipants(dashboard.participants)

        setFormData((previousData) => ({
          ...previousData,
          league_participant_id: '',
        }))

        setTransferData((previousData) => ({
          ...previousData,
          buyer_league_participant_id: '',
          seller_league_participant_id: '',
        }))
      } catch {
        setError('No se pudieron cargar los participantes')
      }
    }

    loadParticipants()
  }, [selectedLeagueId])

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }))
  }


  function handleTransferChange(event) {
  const { name, value } = event.target

  setTransferData((previousData) => ({
    ...previousData,
    [name]: value,
  }))
}


  async function handleSubmit(event) {
    event.preventDefault()

    setLoading(true)
    setMessage('')
    setError('')

    try {
      const amount = Number(formData.amount)

      const movementData = {
        league_participant_id: Number(formData.league_participant_id),
        type: formData.type,
        amount:
          formData.type === 'purchase'
            ? -Math.abs(amount)
            : Math.abs(amount),
        player_name: formData.player_name || null,
        description: formData.description || null,
        occurred_at: new Date(formData.occurred_at).toISOString(),
      }

      await createMovement(movementData)

      setMessage('Movimiento creado correctamente')

      setFormData({
        league_participant_id: '',
        type: 'purchase',
        amount: '',
        player_name: '',
        description: '',
        occurred_at: '',
      })
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleTransferSubmit(event) {
  event.preventDefault()

  setMessage('')
  setError('')

  if (
    transferData.buyer_league_participant_id ===
    transferData.seller_league_participant_id
  ) {
    setError('El comprador y el vendedor no pueden ser el mismo participante.')
    return
  }

  const amount = Number(transferData.amount)

  if (amount <= 0) {
    setError('El importe debe ser mayor que 0.')
    return
  }

  try {
    setLoading(true)

    const operationTypes = {
      clause: 'clause',
      transfer: 'participant_transfer',
      loan: 'loan',
    }

    const data = {
      buyer_league_participant_id: Number(
        transferData.buyer_league_participant_id
      ),
      seller_league_participant_id: Number(
        transferData.seller_league_participant_id
      ),
      operation_type: operationTypes[transferData.transfer_type],
      amount: amount,
      player_name: transferData.player_name,
      description: transferData.description || null,
      occurred_at: new Date(transferData.occurred_at).toISOString(),
    }

    await createTransfer(data)

    setMessage('Operación registrada correctamente.')

    setTransferData({
      transfer_type: 'clause',
      buyer_league_participant_id: '',
      seller_league_participant_id: '',
      amount: '',
      player_name: '',
      description: '',
      occurred_at: '',
    })
  } catch (error) {
    console.error(error)
    setError('No se pudo registrar la operación.')
  } finally {
    setLoading(false)
  }
}

return (
  <main className="new-movement-page">
    <div className="form-container">
      <div className="form-header">
        <h1>Nuevo movimiento</h1>
        <p>Registra una operación económica de la liga.</p>
      </div>

      <div className="form-group">
        <label htmlFor="operationType">Tipo de operación</label>

        <select
          id="operationType"
          value={operationType}
          onChange={(event) => setOperationType(event.target.value)}
        >
          <option value="movement">Movimiento individual</option>
          <option value="transfer">Operación entre participantes</option>
        </select>

        <small className="form-help">
          {operationType === 'movement'
            ? 'Movimientos que afectan únicamente al saldo de un participante.'
            : 'Operaciones en las que el dinero pasa de un participante a otro.'}
        </small>
      </div>

      {operationType === 'movement' && (
        <form className="movement-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="league_participant_id">
              Participante
            </label>

            <select
              id="league_participant_id"
              name="league_participant_id"
              value={formData.league_participant_id}
              onChange={handleChange}
              required
            >
              <option value="">Selecciona participante</option>

              {participants.map((participant) => (
                <option
                  key={participant.league_participant_id}
                  value={participant.league_participant_id}
                >
                  {participant.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="type">Tipo</label>

            <select
              id="type"
              name="type"
              value={formData.type}
              onChange={handleChange}
            >
              <option value="purchase">Compra</option>
              <option value="sale">Venta</option>
              <option value="bonus">Bonus</option>
              <option value="adjustment">Ajuste</option>
              <option value="clause_compensation">
                Recuperación de cláusula
              </option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="amount">Importe</label>

            <input
              id="amount"
              name="amount"
              type="number"
              step="1"
              value={formData.amount}
              onChange={handleChange}
              required
            />

            {formData.type === 'adjustment' && (
              <small className="form-help">
                En los ajustes puedes introducir un importe positivo o negativo.
              </small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="player_name">Jugador</label>

            <input
              id="player_name"
              name="player_name"
              type="text"
              value={formData.player_name}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Descripción</label>

            <input
              id="description"
              name="description"
              type="text"
              value={formData.description}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="occurred_at">Fecha</label>

            <input
              id="occurred_at"
              name="occurred_at"
              type="datetime-local"
              value={formData.occurred_at}
              onChange={handleChange}
              required
            />
          </div>

          <button
            className="submit-button"
            type="submit"
            disabled={loading}
          >
            {loading ? 'Guardando...' : 'Guardar movimiento'}
          </button>
        </form>
      )}

      {operationType === 'transfer' && (
  <form className="movement-form" onSubmit={handleTransferSubmit}>
    <div className="form-group">
      <label htmlFor="transfer_type">Tipo</label>

      <select
        id="transfer_type"
        name="transfer_type"
        value={transferData.transfer_type}
        onChange={handleTransferChange}
      >
        <option value="clause">Clausulazo</option>
        <option value="transfer">Compra entre participantes</option>
        <option value="loan">Cesión</option>
      </select>
    </div>

    <div className="form-group">
      <label htmlFor="buyer_league_participant_id">
        Comprador
      </label>

      <select
        id="buyer_league_participant_id"
        name="buyer_league_participant_id"
        value={transferData.buyer_league_participant_id}
        onChange={handleTransferChange}
        required
      >
        <option value="">Selecciona comprador</option>

        {participants.map((participant) => (
          <option
            key={participant.league_participant_id}
            value={participant.league_participant_id}
          >
            {participant.name}
          </option>
        ))}
      </select>
    </div>

    <div className="form-group">
      <label htmlFor="seller_league_participant_id">
        Vendedor
      </label>

      <select
        id="seller_league_participant_id"
        name="seller_league_participant_id"
        value={transferData.seller_league_participant_id}
        onChange={handleTransferChange}
        required
      >
        <option value="">Selecciona vendedor</option>

        {participants.map((participant) => (
          <option
            key={participant.league_participant_id}
            value={participant.league_participant_id}
          >
            {participant.name}
          </option>
        ))}
      </select>
    </div>

    <div className="form-group">
      <label htmlFor="transfer_player_name">
        Jugador
      </label>

      <input
        id="transfer_player_name"
        name="player_name"
        type="text"
        value={transferData.player_name}
        onChange={handleTransferChange}
        required
      />
    </div>

    <div className="form-group">
      <label htmlFor="transfer_amount">
        Importe
      </label>

      <input
        id="transfer_amount"
        name="amount"
        type="number"
        min="1"
        step="1"
        value={transferData.amount}
        onChange={handleTransferChange}
        required
      />
    </div>

    <div className="form-group">
      <label htmlFor="transfer_description">
        Descripción
      </label>

      <input
        id="transfer_description"
        name="description"
        type="text"
        value={transferData.description}
        onChange={handleTransferChange}
      />
    </div>

    <div className="form-group">
      <label htmlFor="transfer_occurred_at">
        Fecha
      </label>

      <input
        id="transfer_occurred_at"
        name="occurred_at"
        type="datetime-local"
        value={transferData.occurred_at}
        onChange={handleTransferChange}
        required
      />
    </div>

<button
  className="submit-button"
  type="submit"
  disabled={loading}
>
  {loading ? 'Guardando...' : 'Registrar clausulazo'}
</button>
  </form>
)}

      {message && (
        <p className="form-success">
          {message}
        </p>
      )}

      {error && (
        <p className="form-error">
          {error}
        </p>
      )}
    </div>
  </main>
)
}

export default NewMovementPage