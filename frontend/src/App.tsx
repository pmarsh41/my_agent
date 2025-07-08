import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container } from '@mui/material';
import { Toaster } from 'react-hot-toast';
import SmartMealAnalyzer from './components/SmartMealAnalyzer';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Meals from './pages/Meals';
import History from './pages/History';
import Navigation from './components/Navigation';

// Create Material-UI theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#3a86ff', // Protein Blue
    },
    secondary: {
      main: '#43aa8b', // Leaf Green
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navigation />
          <main className="pt-16">
            <Container maxWidth="lg" sx={{ py: 4 }}>
              <Routes>
                <Route path="/" element={<SmartMealAnalyzer />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/meals" element={<Meals />} />
                <Route path="/history" element={<History />} />
              </Routes>
            </Container>
          </main>
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;