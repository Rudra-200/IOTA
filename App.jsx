import { Routes, Route } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import LoadingSpinner from '@components/common/LoadingSpinner'
import ErrorBoundary from '@components/common/ErrorBoundary'

// Lazy load pages
const HomePage = lazy(() => import('./pages/HomePage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const AskPage = lazy(() => import('./pages/AskPage'))
const DocumentsPage = lazy(() => import('./pages/DocumentsPage'))
const DraftsPage = lazy(() => import('./pages/DraftsPage'))
const CaselawPage = lazy(() => import('./pages/CaselawPage'))
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'))
const ConsultPage = lazy(() => import('./pages/ConsultPage'))
const PricingPage = lazy(() => import('./pages/PricingPage'))
const PrivacyPage = lazy(() => import('./pages/PrivacyPage'))
const SignInPage = lazy(() => import('./pages/SignInPage'))
const SignUpPage = lazy(() => import('./pages/SignUpPage'))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'))

function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/ask" element={<AskPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/drafts" element={<DraftsPage />} />
          <Route path="/caselaw" element={<CaselawPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/consult" element={<ConsultPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/signin" element={<SignInPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  )
}

export default App
