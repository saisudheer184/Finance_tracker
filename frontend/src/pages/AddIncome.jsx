import React, { useEffect, useState } from 'react'
import { Container, Box, TextField, Button, Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow, TablePagination } from '@mui/material'
import http from '../api/http'
import dayjs from 'dayjs'
const categories = ['salary','business','freelance','investment','other']
export default function AddIncome() {
  const [category, setCategory] = useState(categories[0])
  const [amount, setAmount] = useState('')
  const [description, setDescription] = useState('')
  const [date, setDate] = useState(dayjs().format('YYYY-MM-DD'))
  const [items, setItems] = useState([])
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [q, setQ] = useState('')
  const load = async (p=page, l=rowsPerPage) => {
    const { data } = await http.get(`/income?page=${p+1}&limit=${l}&q=${q}`)
    setItems(data)
  }
  useEffect(()=>{ load() },[])
  const add = async () => {
    await http.post('/income', { category, amount: parseFloat(amount), description, date })
    setAmount('')
    setDescription('')
    load()
  }
  return (
    <Container sx={{ ml: 28, mt: 2 }}>
      <Box>
        <Typography variant="h6">Add Income</Typography>
        <Box display="flex" gap={2} mt={2}>
          <TextField select SelectProps={{ native: true }} label="Category" value={category} onChange={e=>setCategory(e.target.value)}>
            {categories.map(c=> <option key={c} value={c}>{c}</option>)}
          </TextField>
          <TextField label="Amount" value={amount} onChange={e=>setAmount(e.target.value)} />
          <TextField label="Description" value={description} onChange={e=>setDescription(e.target.value)} />
          <TextField type="date" label="Date" InputLabelProps={{ shrink: true }} value={date} onChange={e=>setDate(e.target.value)} />
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
            </TableRow>
          </TableHead>
          <TableBody>
            {(items.items||[]).map(i=> (
              <TableRow key={i._id}>
                <TableCell>{dayjs(i.date).format('YYYY-MM-DD')}</TableCell>
                <TableCell>{i.category}</TableCell>
                <TableCell>{i.amount}</TableCell>
                <TableCell>{i.description}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination component="div" count={items.total||0} page={page} onPageChange={(e,p)=>{setPage(p);load(p,rowsPerPage)}} rowsPerPage={rowsPerPage} onRowsPerPageChange={e=>{const v=parseInt(e.target.value,10);setRowsPerPage(v);setPage(0);load(0,v)}} />
      </Paper>
    </Container>
  )
}
