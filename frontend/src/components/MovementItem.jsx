import './MovementItem.css'
import { formatCurrency } from '../utils/formatCurrency.js'

function MovementItem({ movement, participants }) {
  const participant = participants.find(
    (participant) =>
      participant.league_participant_id === movement.league_participant_id
  )

  function formatDate(date) {
    return new Date(date).toLocaleString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  function getMovementLabel() {
    const player = movement.player_name
      ? ` · ${movement.player_name}`
      : ''

    if (movement.operation_type === 'clause') {
      return movement.type === 'purchase'
        ? `Clausulazo realizado${player}`
        : `Clausulazo recibido${player}`
    }

    if (movement.operation_type === 'loan') {
      return movement.type === 'purchase'
        ? `Cesión recibida${player}`
        : `Cesión realizada${player}`
    }

    switch (movement.type) {
      case 'purchase':
        return `Compra${player}`

      case 'sale':
        return `Venta${player}`

      case 'bonus':
        return 'Bonus'

      case 'round_bonus':
        return movement.description
          ? `Pago de jornada · ${movement.description}`
          : 'Pago de jornada'

      case 'adjustment':
        return `Ajuste${player}`

      case 'clause_compensation':
        return `Recuperación de cláusula${player}`

      default:
        return movement.type
    }
  }

  return (
    <article className="movement-item">
      <div className="movement-info">
        <strong>
          {participant?.name ?? 'Participante desconocido'}
        </strong>

        <p>{getMovementLabel()}</p>

        <small>{formatDate(movement.occurred_at)}</small>
      </div>

      <strong
        className={`movement-amount ${
          movement.amount >= 0
            ? 'movement-income'
            : 'movement-expense'
        }`}
      >
        {movement.amount > 0 ? '+' : ''}
        {formatCurrency(movement.amount)}
      </strong>
    </article>
  )
}

export default MovementItem