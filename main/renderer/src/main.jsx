import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Log application startup
console.log('🎉 [RENDERER] DeployBot React application starting...')

// Render the application
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

console.log('✅ [RENDERER] DeployBot React application rendered successfully') 