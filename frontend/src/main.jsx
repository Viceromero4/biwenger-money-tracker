import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import { LeagueProvider } from './context/LeagueContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <LeagueProvider>
        <App />
      </LeagueProvider>
    </BrowserRouter>
  </StrictMode>,
)