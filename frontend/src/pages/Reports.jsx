import React, { useEffect, useState } from 'react'
import { Container, Box, Typography, Button } from '@mui/material'
import http from '../api/http'
import dayjs from 'dayjs'
export default function Reports() {
  const [month, setMonth] = useState(dayjs().format('YYYY-MM'))
  const [summary, setSummary] = useState(null)
  useEffect(()=>{ http.get(`/reports/monthly?month=${month}`).then(({data})=>setSummary(data)) },[month])
  const pdf = () => { window.open(`/api/reports/pdf?month=${month}`,'_blank') }
  const csv = () => { window.open(`/api/reports/csv`,'_blank') }
  return (
    <Container sx={{ ml: 28, mt: 2 }}>
      <Typography variant="h6">Reports</Typography>
      <Box display="flex" gap={2} mt={2}>
        <input type="month" value={month} onChange={e=>setMonth(e.target.value)} />
        <Button variant="contained" onClick={pdf}>Download PDF</Button>
        <Button variant="outlined" onClick={csv}>Export CSV</Button>
      </Box>
      {summary && (
        <Box mt={2}>
          <Typography>Income: {summary.income}</Typography>
          <Typography>Expense: {summary.expense}</Typography>
          <Typography>Savings: {summary.savings}</Typography>
          <Typography>Budget: {summary.budget}</Typography>
        </Box>
      )}
    </Container>
  )
}
