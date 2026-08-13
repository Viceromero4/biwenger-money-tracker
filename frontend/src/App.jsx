import { Route, Routes } from 'react-router-dom'

import DashboardPage from './pages/DashboardPage.jsx'
import MovementsPage from './pages/MovementsPage.jsx'
import NewMovementPage from './pages/NewMovementPage.jsx'
import ParticipantDetailPage from './pages/ParticipantDetailPage.jsx'
import Navbar from './components/Navbar.jsx'
import RegisterParticipantPage from './pages/RegisterParticipantPage.jsx'

function App() {
  return (
    <>
      <Navbar />

      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/movements" element={<MovementsPage />} />
        <Route path="/movements/new" element={<NewMovementPage />} />
        <Route path="/participants/:leagueParticipantId" element={<ParticipantDetailPage />}/>
        <Route path="/participants/new" element={<RegisterParticipantPage />}/>
      </Routes>
    </>
  )
}

export default App