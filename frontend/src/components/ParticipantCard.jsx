import './ParticipantCard.css'

function ParticipantCard({
  participant,
  initialBalance,
}) {
  const balanceDifference =
    participant.current_balance - initialBalance

  function formatMillions(amount) {
    return `${(amount / 1000000).toFixed(2)} M €`
  }

  return (
    <article className="participant-card">
      <h3>{participant.name}</h3>

      <p>
        Saldo actual: {formatMillions(participant.current_balance)}
      </p>

      <p
        className={
          balanceDifference >= 0
            ? 'balance-positive'
            : 'balance-negative'
        }
      >
        Variación:{' '}
        {balanceDifference >= 0 ? '+' : ''}
        {formatMillions(balanceDifference)}
      </p>
    </article>
  )
}

export default ParticipantCard