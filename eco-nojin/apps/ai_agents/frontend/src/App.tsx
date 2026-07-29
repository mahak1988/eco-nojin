import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import AgentsDashboard from './pages/AgentsDashboard'
import AgentMonitor from './pages/AgentMonitor'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<AgentsDashboard />} />
        <Route path="monitor" element={<AgentMonitor />} />
        <Route path="*" element={<div className="p-8 text-center">404 Not Found</div>} />
      </Route>
    </Routes>
  )
}