import { useAuth } from './hooks/useAuth';
import { DashboardPage } from './pages/DashboardPage';
import { LoginPage } from './pages/LoginPage';

export default function App() {
  const { user, loading, authenticated, onLogin, logout } = useAuth();

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  if (!authenticated || !user) {
    return <LoginPage onLogin={onLogin} />;
  }

  return <DashboardPage onLogout={logout} displayName={user.display_name} />;
}
