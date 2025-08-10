import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import NetworkView from './components/NetworkView'
import ExtractionManager from './components/ExtractionManager'
import SessionList from './components/SessionList'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<NetworkView />} />
        <Route path="/extract" element={<ExtractionManager />} />
        <Route path="/sessions" element={<SessionList />} />
      </Routes>
    </Layout>
  )
}

export default App 