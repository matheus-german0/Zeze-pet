// server_example.js
const express = require('express');
const app = express();
app.use(express.json());

// rota exemplo: criar invoice (persistência demo em memória)
let invoices = [];
app.post('/api/invoices', (req, res) => {
  const inv = req.body; invoices.push(inv); res.json({ok:true, invoice:inv});
});

app.listen(3000, ()=>console.log('API exemplo rodando na porta 3000'));
