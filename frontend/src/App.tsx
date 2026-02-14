import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import TrainPage from './pages/TrainPage';
import DemoPage from './pages/DemoPage';
import SummaryPage from './pages/SummaryPage';
import SpacesPage from './pages/SpacesPage';
import SpaceDetailPage from './pages/SpaceDetailPage';
import ErrorBoundary from './components/ErrorBoundary';

/**
 * Main App component with routing configuration.
 * 
 * Routes:
 * - / : Landing page
 * - /train : Training page for style analysis
 * - /demo : Conversation demo with autopilot
 * - /summary : Session summary display
 * 
 * Note: Navigation guards are handled within individual components
 * by checking for required state and redirecting if missing.
 */
function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/train" element={<TrainPage />} />
          <Route path="/demo" element={<DemoPage />} />
          <Route path="/summary" element={<SummaryPage />} />
          <Route path="/spaces" element={<SpacesPage />} />
          <Route path="/spaces/:id" element={<SpaceDetailPage />} />
          {/* Catch-all route for 404 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
