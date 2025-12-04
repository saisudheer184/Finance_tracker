import React, { useEffect, useState } from 'react'
import { Container, Grid, Paper, Typography } from '@mui/material'
import http from '../api/http'
import IncomeExpenseChart from '../components/charts/IncomeExpenseChart'
import CategoryPieChart from '../components/charts/CategoryPieChart'
import SavingsChart from '../components/charts/SavingsChart'
import TrendChart from '../components/charts/TrendChart'
import dayjs from 'dayjs'
export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [trend, setTrend] = useState([])
  useEffect(() => {
    const month = dayjs().format('YYYY-MM')
    http.get(`/reports/monthly?month=${month}`).then(({ data }) => {
      setSummary(data)
    })
    Promise.all([1,2,3,4].map(i=>{
      const m = dayjs().subtract(4-i,'month').format('YYYY-MM')
      return http.get(`/reports/monthly?month=${m}`)
    })).then(res => {
      const data = res.map(r=>r.data).map(d=>({ label: d.month, spend: d.expense, income: d.income, savings: d.savings }))
      setTrend(data)
    })
  }, [])
  const chartData = trend
  const categoryData = (summary?.topCategories || []).map(c=>({ category: c._id, total: c.total }))
  const savingsData = trend.map(t=>({ label: t.label, savings: t.savings }))
  const incExp = trend.map(t=>({ label: t.label, income: t.income, expense: t.spend }))
  return (
    <Container sx={{ ml: 28, mt: 2 }}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <Paper sx={{ p:2 }}>
            <Typography variant="h6">Income vs Expenses</Typography>
            <IncomeExpenseChart data={incExp} />
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Paper sx={{ p:2 }}>
            <Typography variant="h6">Category-wise Expenses</Typography>
            <CategoryPieChart data={categoryData} />
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Paper sx={{ p:2 }}>
            <Typography variant="h6">Savings</Typography>
            <SavingsChart data={savingsData} />
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Paper sx={{ p:2 }}>
            <Typography variant="h6">Spending Trend</Typography>
            <TrendChart data={chartData} />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  )
}
