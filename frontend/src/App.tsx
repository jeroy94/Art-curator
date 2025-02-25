import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import ArtistSubmissionForm from './components/ArtistSubmissionForm';
import AdminDashboard from './components/AdminDashboard';
import Login from './components/Login';
import HomePage from './components/HomePage';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// Composant pour protéger les routes admin
function PrivateRoute({ children }: { children: JSX.Element | JSX.Element[] }) {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/admin/login" />;
  }
  return children;
}

function App() {
  const handleLogin = (token: string) => {
    localStorage.setItem('token', token);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
  };

  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Routes>
          {/* Page d'accueil */}
          <Route path="/" element={<HomePage />} />
          
          {/* Routes artistes */}
          <Route path="/register" element={<ArtistSubmissionForm />} />
          
          {/* Routes administratives */}
          <Route path="/admin/login" element={
            <Login onLogin={handleLogin} />
          } />
          <Route path="/admin" element={
            <PrivateRoute>
              <AdminDashboard onLogout={handleLogout} />
            </PrivateRoute>
          } />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
