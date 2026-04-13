/**
 * Clarion App Shell
 * Routes with lazy loading. Protected routes redirect to /login.
 * Public routes: /login. Everything else requires authentication.
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { ThemeProvider } from '@/theme/ThemeProvider';
import { AuthProvider } from '@/stores/authContext';
import { ProtectedRoute } from '@/components/common/ProtectedRoute';

const LoginPage = lazy(() => import('@/modules/auth/LoginPage'));
const Dashboard = lazy(() => import('@/modules/dashboard/DashboardPage'));
const CaseList = lazy(() => import('@/modules/cases/CaseListPage'));
const CaseDetail = lazy(() => import('@/modules/cases/CaseDetailPage'));
const ReviewList = lazy(() => import('@/modules/reviews/ReviewListPage'));
const Recommendations = lazy(() => import('@/modules/reviews/RecommendationsPage'));
const Analytics = lazy(() => import('@/modules/analytics/AnalyticsPage'));
const Predictions = lazy(() => import('@/modules/predictions/PredictionsPage'));
const Accounts = lazy(() => import('@/modules/accounts/AccountsPage'));
const AccountDetail = lazy(() => import('@/modules/accounts/AccountDetailPage'));
const Notifications = lazy(() => import('@/modules/notifications/NotificationsPage'));
const AdminPage = lazy(() => import('@/modules/admin/AdminPage'));
const HelpPage = lazy(() => import('@/modules/help/HelpPage'));

function Loader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="w-6 h-6 border-2 border-[var(--clarion-accent)] border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

function S({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<Loader />}>{children}</Suspense>;
}

function P({ children, roles }: { children: React.ReactNode; roles?: string[] }) {
  return <ProtectedRoute roles={roles}>{children}</ProtectedRoute>;
}

export function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public */}
            <Route path="/login" element={<S><LoginPage /></S>} />

            {/* Protected — requires authentication */}
            <Route element={<P><AppLayout /></P>}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<S><Dashboard /></S>} />
              <Route path="/cases" element={<S><CaseList /></S>} />
              <Route path="/cases/:id" element={<S><CaseDetail /></S>} />
              <Route path="/reviews" element={<P roles={['admin','manager']}><S><ReviewList /></S></P>} />
              <Route path="/reviews/recommendations" element={<P roles={['admin','manager']}><S><Recommendations /></S></P>} />
              <Route path="/analytics" element={<S><Analytics /></S>} />
              <Route path="/predictions" element={<S><Predictions /></S>} />
              <Route path="/accounts" element={<S><Accounts /></S>} />
              <Route path="/accounts/:id" element={<S><AccountDetail /></S>} />
              <Route path="/notifications" element={<P roles={['admin','manager']}><S><Notifications /></S></P>} />
              <Route path="/admin" element={<P roles={['admin']}><S><AdminPage /></S></P>} />
              <Route path="/help" element={<S><HelpPage /></S>} />
            </Route>

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
