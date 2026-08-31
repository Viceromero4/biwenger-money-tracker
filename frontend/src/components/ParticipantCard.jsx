import { Link } from 'react-router-dom'

import './ParticipantCard.css'
import { formatCurrency } from '../utils/formatCurrency.js'

function ParticipantCard({
  participant,
  initialBalance,
}) {
  const balanceDifference =
    participant.current_balance - initialBalance

  return (
    <Link
      to={`/participants/${participant.league_participant_id}`}
      className="participant-card-link"
    >
      <article className="participant-card">
        <h3>{participant.name}</h3>

        <p>
          Saldo actual: {formatCurrency(participant.current_balance)}
        </p>

        <p
          className={
            balanceDifference >= 0
              ? 'balance-positive'
              : 'balance-negative'
          }
        >
          Variación:{' '}
          {balanceDifference > 0 ? '+' : ''}
          {formatCurrency(balanceDifference)}
        </p>
      </article>
    </Link>
  )
}

export default ParticipantCard