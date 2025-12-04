import React, { useEffect, useState } from 'react'
import { Container, Typography, Button } from '@mui/material'
import http from '../api/http'
import { useAuth } from '../context/AuthContext'
export default function Profile() {
  const [me, setMe] = useState(null)
  const { logout } = useAuth()
  useEffect(()=>{ http.get('/auth/me').then(({data})=>setMe(data)) },[])
  return (
    <Container sx={{ ml: 28, mt: 2 }}>
      <Typography variant="h6">Profile</Typography>
      {me && (
        <>
          <Typography>Name: {me.name}</Typography>
          <Typography>Email: {me.email}</Typography>
          <Button sx={{ mt:2 }} variant="outlined" onClick={logout}>Logout</Button>
        </>
      )}
    </Container>
  )
}
