import { useEffect, useRef, useState } from 'react'
import { useLeague } from '../context/LeagueContext.jsx'
import './LeagueSelector.css'

function LeagueSelector() {
  const {
    leagues,
    selectedLeague,
    selectedLeagueId,
    setSelectedLeagueId,
  } = useLeague()

  const [isOpen, setIsOpen] = useState(false)
  const selectorRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(event) {
      if (
        selectorRef.current &&
        !selectorRef.current.contains(event.target)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  function handleSelectLeague(leagueId) {
    setSelectedLeagueId(leagueId)
    setIsOpen(false)
  }

  return (
    <div
      className="league-selector-custom"
      ref={selectorRef}
    >
      <button
        type="button"
        className={`league-selector-button ${
          isOpen ? 'open' : ''
        }`}
        onClick={() => setIsOpen((previous) => !previous)}
        aria-expanded={isOpen}
      >
        <span>{selectedLeague?.name ?? 'Seleccionar liga'}</span>

        <span
          className={`league-selector-arrow ${
            isOpen ? 'open' : ''
          }`}
        >
          ▼
        </span>
      </button>

      {isOpen && (
        <div className="league-selector-menu">
          {leagues.map((league) => {
            const isSelected =
              league.id === selectedLeagueId

            return (
              <button
                key={league.id}
                type="button"
                className={`league-selector-option ${
                  isSelected ? 'selected' : ''
                }`}
                onClick={() =>
                  handleSelectLeague(league.id)
                }
              >
                <span>{league.name}</span>

                {isSelected && (
                  <span className="league-selector-check">
                    ✓
                  </span>
                )}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default LeagueSelector