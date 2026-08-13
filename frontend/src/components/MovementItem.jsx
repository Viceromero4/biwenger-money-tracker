import './MovementItem.css'

function MovementItem({ movement, participants }) {
  const participant = participants.find(
    (participant) =>
      participant.league_participant_id === movement.league_participant_id
  )

  const movementTypes = {
    purchase: 'Compra',
    sale: 'Venta',
    bonus: 'Bonus',
    adjustment: 'Ajuste',
    clause_compensation: 'Recuperación de cláusula',
  }

  function formatMillions(amount) {
    return `${(amount / 1000000).toFixed(2)} M €`
  }

  function formatDate(date) {
    return new Date(date).toLocaleString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

    return (
    <article className="movement-item">
        <div className="movement-info">
        <strong>{participant?.name ?? 'Participante desconocido'}</strong>

        <p>
          {movement.operation_type === 'clause'
            ? movement.type === 'purchase'
              ? 'Clausulazo realizado'
              : 'Clausulazo recibido'
            : movementTypes[movement.type] ?? movement.type}
        </p>

        <small>{formatDate(movement.occurred_at)}</small>
        </div>

        <strong
        className={`movement-amount ${
            movement.amount >= 0 ? 'movement-income' : 'movement-expense'
        }`}
        >
        {movement.amount > 0 ? '+' : ''}
        {formatMillions(movement.amount)}
        </strong>
    </article>
    )
}

export default MovementItem