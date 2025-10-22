import { NavLink, Route, Routes, Navigate } from 'react-router-dom';
import BrandingPage from './pages/BrandingPage';
import ClientsPage from './pages/ClientsPage';
import MetricsPage from './pages/MetricsPage';
import './App.css';
import './styles/panel.css';
import { useAgency } from './hooks/useAgency';
import WorkspaceSwitcher from './components/WorkspaceSwitcher';

const App = () => {
  const { branding } = useAgency();

  return (
    <div className="app-shell">
      <header className="app-header" style={{ borderBottomColor: branding.primaryColor }}>
        <div className="branding">
          <img src={branding.logoUrl} alt="Agency logo" className="branding__logo" />
          <div>
            <p className="branding__label">Agency Control Center</p>
            <p className="branding__theme" style={{ color: branding.accentColor }}>
              Theme · {branding.themeName}
            </p>
          </div>
        </div>
        <WorkspaceSwitcher />
      </header>

      <nav className="app-navigation">
        <NavLink to="/branding" className={({ isActive }) => (isActive ? 'nav-link nav-link--active' : 'nav-link')}>
          Branding
        </NavLink>
        <NavLink to="/clients" className={({ isActive }) => (isActive ? 'nav-link nav-link--active' : 'nav-link')}>
          Clients & Roles
        </NavLink>
        <NavLink to="/metrics" className={({ isActive }) => (isActive ? 'nav-link nav-link--active' : 'nav-link')}>
          Workspaces & Metrics
        </NavLink>
      </nav>

      <main className="app-content">
        <Routes>
          <Route path="/" element={<Navigate to="/branding" replace />} />
          <Route path="/branding" element={<BrandingPage />} />
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/metrics" element={<MetricsPage />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
