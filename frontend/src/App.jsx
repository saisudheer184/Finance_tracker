import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import AuthProvider, { useAuth } from './context/AuthContext'
import ThemeModeProvider, { useThemeMode } from './context/ThemeContext'
import Sidebar from './components/Sidebar'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import AddIncome from './pages/AddIncome'
import AddExpense from './pages/AddExpense'
import Budget from './pages/Budget'
import Reports from './pages/Reports'
import Profile from './pages/Profile'
const AppShell = () => {
  const { mode } = useThemeMode()
  const theme = createTheme({ palette: { mode } })
  const { token } = useAuth()
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {token && <Sidebar />}
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route element={<ProtectedRoute />}> 
          <Route path="/" element={<Dashboard />} />
          <Route path="/income" element={<AddIncome />} />
          <Route path="/expenses" element={<AddExpense />} />
          <Route path="/budget" element={<Budget />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
        <Route path="*" element={<Navigate to={token ? '/' : '/login'} replace />} />
      </Routes>
    </ThemeProvider>
  )
}
export default function App() {
  return (
    <ThemeModeProvider>
      <AuthProvider>
        <AppShell />
      </AuthProvider>
    </ThemeModeProvider>
  )
}
