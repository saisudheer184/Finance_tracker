import React, { useState } from 'react'
import { Container, Box, TextField, Button, Typography } from '@mui/material'
import { useAuth } from '../context/AuthContext'
import { Link, useNavigate } from 'react-router-dom'
export default function Login() {
  const { login } = useAuth()
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const onSubmit = async (e) => {
    e.preventDefault()
    try {
      await login(email, password)
      nav('/')
    } catch (err) {
      setError('Invalid credentials')
    }
  }
  return (
    <Container maxWidth="xs">
      <Box mt={8}>
        <Typography variant="h5">Login</Typography>
        <Box component="form" onSubmit={onSubmit} mt={2}>
          <TextField label="Email" fullWidth margin="normal" value={email} onChange={e=>setEmail(e.target.value)} />
          <TextField label="Password" type="password" fullWidth margin="normal" value={password} onChange={e=>setPassword(e.target.value)} />
          {error && <Typography color="error">{error}</Typography>}
          <Button type="submit" variant="contained" fullWidth sx={{ mt:2 }}>Login</Button>
        </Box>
        <Box mt={2}><Link to="/register">Create account</Link></Box>
      </Box>
    </Container>
  )
}
