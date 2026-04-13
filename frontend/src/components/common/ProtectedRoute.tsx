/**
 * Protected Route
 * Redirects to /login if not authenticated.
 * Optionally restricts by role.
 */
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/stores/authContext';

interface Props {
  children: React.ReactNode;
  roles?: string[];
}

export function ProtectedRoute({ children, roles }: Props) {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--clarion-bg)] flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-[var(--clarion-accent)] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (roles && user && !roles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}
