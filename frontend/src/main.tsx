import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'
import { detectApiPrefix } from './api/config'
import { ThemeProvider } from './theme/ThemeContext'

async function bootstrap() {
  try { await detectApiPrefix() } catch {}
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <BrowserRouter>
        <ThemeProvider>
          <App />
        </ThemeProvider>
      </BrowserRouter>
    </React.StrictMode>
  )
}

bootstrap()


