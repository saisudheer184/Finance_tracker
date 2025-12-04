import React, { useState } from 'react'
import { Container, Box, TextField, Button, Typography } from '@mui/material'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
export default function Register() {
  const { register } = useAuth()
  const nav = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const onSubmit = async (e) => {
    e.preventDefault()
    try {
      await register(name, email, password)
      nav('/')
    } catch (err) {
      setError('Registration failed')
    }
  }
  return (
    <Container maxWidth="xs">
      <Box mt={8}>
        <Typography variant="h5">Register</Typography>
        <Box component="form" onSubmit={onSubmit} mt={2}>
          <TextField label="Name" fullWidth margin="normal" value={name} onChange={e=>setName(e.target.value)} />
          <TextField label="Email" fullWidth margin="normal" value={email} onChange={e=>setEmail(e.target.value)} />
          <TextField label="Password" type="password" fullWidth margin="normal" value={password} onChange={e=>setPassword(e.target.value)} />
          {error && <Typography color="error">{error}</Typography>}
          <Button type="submit" variant="contained" fullWidth sx={{ mt:2 }}>Register</Button>
        </Box>
      </Box>
    </Container>
  )
}
