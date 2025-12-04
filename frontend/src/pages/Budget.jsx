import React, { useEffect, useState } from 'react'
import { Container, Box, TextField, Button, Typography, Paper } from '@mui/material'
import http from '../api/http'
import dayjs from 'dayjs'
export default function Budget() {
  const [month, setMonth] = useState(dayjs().format('YYYY-MM'))
  const [amount, setAmount] = useState('')
  const [summary, setSummary] = useState(null)
  const load = async () => {
    const { data } = await http.get(`/budget/remaining?month=${month}`)
    setSummary(data)
  }
  useEffect(()=>{ load() },[])
  const save = async () => {
    await http.post('/budget', { month, amount: parseFloat(amount) })
    load()
  }
  return (
    <Container sx={{ ml: 28, mt: 2 }}>
      <Typography variant="h6">Monthly Budget</Typography>
      <Box display="flex" gap={2} mt={2}>
        <TextField type="month" label="Month" InputLabelProps={{ shrink: true }} value={month} onChange={e=>setMonth(e.target.value)} />
        <TextField label="Amount" value={amount} onChange={e=>setAmount(e.target.value)} />
        <Button variant="contained" onClick={save}>Save</Button>
      </Box>
      <Paper sx={{ p:2, mt:3 }}>
        {summary && (
          <Box>
            <Typography>Target: {summary.target}</Typography>
            <Typography>Spent: {summary.spent}</Typography>
            <Typography>Remaining: {summary.remaining}</Typography>
            <Typography>Exceeded: {summary.exceeded ? 'Yes' : 'No'}</Typography>
          </Box>
        )}
      </Paper>
    </Container>
  )
}
