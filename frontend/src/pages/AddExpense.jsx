import React, { useEffect, useState } from 'react'
import { Container, Box, TextField, Button, Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow, TablePagination, Snackbar, Alert } from '@mui/material'
import http from '../api/http'
import dayjs from 'dayjs'
const categories = ['food','bills','transport','entertainment','rent','health','shopping','education','other']
export default function AddExpense() {
  const [category, setCategory] = useState(categories[0])
  const [amount, setAmount] = useState('')
  const [description, setDescription] = useState('')
  const [date, setDate] = useState(dayjs().format('YYYY-MM-DD'))
  const [receipt, setReceipt] = useState(null)
  const [items, setItems] = useState([])
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [q, setQ] = useState('')
  const [snack, setSnack] = useState(false)
  const load = async (p=page, l=rowsPerPage) => {
    const { data } = await http.get(`/expenses?page=${p+1}&limit=${l}&q=${q}`)
    setItems(data)
  }
  useEffect(()=>{ load() },[])
  const add = async () => {
    const form = new FormData()
    form.append('category', category)
    form.append('amount', parseFloat(amount))
    form.append('description', description)
    form.append('date', date)
    if (receipt) form.append('receipt', receipt)
    const { data } = await http.post('/expenses', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (data.budgetExceeded) setSnack(true)
    setAmount('')
    setDescription('')
    setReceipt(null)
    load()
  }
  return (
    <Container sx={{ ml: 28, mt: 2 }}>
      <Box>
        <Typography variant="h6">Add Expense</Typography>
        <Box display="flex" gap={2} mt={2}>
          <TextField select SelectProps={{ native: true }} label="Category" value={category} onChange={e=>setCategory(e.target.value)}>
            {categories.map(c=> <option key={c} value={c}>{c}</option>)}
          </TextField>
          <TextField label="Amount" value={amount} onChange={e=>setAmount(e.target.value)} />
          <TextField label="Description" value={description} onChange={e=>setDescription(e.target.value)} />
          <TextField type="date" label="Date" InputLabelProps={{ shrink: true }} value={date} onChange={e=>setDate(e.target.value)} />
          <Button variant="contained" component="label">Upload<input hidden type="file" onChange={e=>setReceipt(e.target.files[0])} /></Button>
          <Button variant="contained" onClick={add}>Add</Button>
        </Box>
      </Box>
      <Paper sx={{ mt:3 }}>
        <Box p={2} display="flex" gap={2}>
          <TextField label="Search" value={q} onChange={e=>setQ(e.target.value)} />
          <Button onClick={()=>load()}>Search</Button>
        </Box>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Receipt</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(items.items||[]).map(i=> (
              <TableRow key={i._id}>
                <TableCell>{dayjs(i.date).format('YYYY-MM-DD')}</TableCell>
                <TableCell>{i.category}</TableCell>
                <TableCell>{i.amount}</TableCell>
                <TableCell>{i.description}</TableCell>
                <TableCell>{i.receiptUrl ? <a href={i.receiptUrl} target="_blank">View</a> : ''}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination component="div" count={items.total||0} page={page} onPageChange={(e,p)=>{setPage(p);load(p,rowsPerPage)}} rowsPerPage={rowsPerPage} onRowsPerPageChange={e=>{const v=parseInt(e.target.value,10);setRowsPerPage(v);setPage(0);load(0,v)}} />
      </Paper>
      <Snackbar open={snack} autoHideDuration={4000} onClose={()=>setSnack(false)}>
        <Alert severity="warning" sx={{ width: '100%' }}>Budget exceeded</Alert>
      </Snackbar>
    </Container>
  )
}
