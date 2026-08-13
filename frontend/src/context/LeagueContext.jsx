import { createContext, useContext, useState } from 'react'

const LeagueContext = createContext()

const leagues = [
  {
    id: 2,
    name: 'Puribet',
  },
  {
    id: 3,
    name: 'Festeros',
  },
  {
    id: 4,
    name: 'Segunda Puribet',
  },
]

export function LeagueProvider({ children }) {
  const [selectedLeagueId, setSelectedLeagueId] = useState(2)

  const selectedLeague = leagues.find(
    (league) => league.id === selectedLeagueId
  )

  return (
    <LeagueContext.Provider
      value={{
        leagues,
        selectedLeague,
        selectedLeagueId,
        setSelectedLeagueId,
      }}
    >
      {children}
    </LeagueContext.Provider>
  )
}

export function useLeague() {
  return useContext(LeagueContext)
}