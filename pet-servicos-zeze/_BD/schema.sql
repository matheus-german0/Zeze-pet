-- schema.sql
-- Modelo mínimo para módulo financeiro

CREATE TABLE users (
  id VARCHAR(50) PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  name VARCHAR(200) NOT NULL,
  phone VARCHAR(50),
  email VARCHAR(200),
  password VARCHAR(200) NOT NULL,
  role VARCHAR(30) NOT NULL -- admin, user, finance
);

CREATE TABLE appointments (
  id VARCHAR(50) PRIMARY KEY,
  user_id VARCHAR(50) REFERENCES users(id),
  service VARCHAR(100),
  price DECIMAL(10,2),
  date DATE,
  time TIME,
  status VARCHAR(30)
);

CREATE TABLE invoices (
  id VARCHAR(50) PRIMARY KEY,
  appointment_id VARCHAR(50) REFERENCES appointments(id),
  user_id VARCHAR(50) REFERENCES users(id),
  total DECIMAL(10,2) NOT NULL,
  status VARCHAR(30) NOT NULL, -- issued, paid, canceled
  issued_at TIMESTAMP,
  due_date DATE
);

CREATE TABLE payments (
  id VARCHAR(50) PRIMARY KEY,
  invoice_id VARCHAR(50) REFERENCES invoices(id),
  method VARCHAR(50), -- boleto, cartao, pix, dinheiro
  amount DECIMAL(10,2) NOT NULL,
  paid_at TIMESTAMP,
  reference TEXT
);

CREATE TABLE finances (
  id VARCHAR(50) PRIMARY KEY,
  type VARCHAR(20) NOT NULL, -- receita, despesa
  description TEXT,
  amount DECIMAL(10,2) NOT NULL,
  date DATE NOT NULL
);
