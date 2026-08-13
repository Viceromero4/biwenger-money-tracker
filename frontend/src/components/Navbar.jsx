import { NavLink } from 'react-router-dom'
import './Navbar.css'

import LeagueSelector from './LeagueSelector.jsx'

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        Biwenger Money Tracker
      </div>

      <LeagueSelector />

      <div className="navbar-links">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `navbar-link ${isActive ? 'active' : ''}`
          }
        >
          Dashboard
        </NavLink>

        <NavLink
          to="/movements"
          className={({ isActive }) =>
            `navbar-link ${isActive ? 'active' : ''}`
          }
        >
          Movimientos
        </NavLink>

        <NavLink
          to="/movements/new"
          className={({ isActive }) =>
            `navbar-link navbar-link-new ${isActive ? 'active' : ''}`
          }
        >
          + Nuevo movimiento
        </NavLink>

        <NavLink
          to="/participants/new"
          className={({ isActive }) =>
            `navbar-link ${isActive ? 'active' : ''}`
          }
        >
          + Participante
        </NavLink>
      </div>
    </nav>
  )
}

export default Navbar