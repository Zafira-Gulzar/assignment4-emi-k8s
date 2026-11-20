// Loan EMI Calculator - Assignment 4 Cloud Computing
// Server-side: Node.js + Express + MongoDB
const express = require('express');
const { MongoClient } = require('mongodb');
const os = require('os');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// MongoDB connection string from MONGO_URL env var.
// Fallback to localhost is ONLY for local dev testing (Milestone 1).
// In Kubernetes (Milestone 2) MONGO_URL is injected from a ConfigMap.
const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017/emidb';

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

let db;

// ---------- Connect to MongoDB ----------
async function connectMongo() {
  const client = new MongoClient(MONGO_URL);
  await client.connect();
  db = client.db('emidb');
  console.log('Connected to MongoDB:', MONGO_URL);
}

// ---------- EMI formula ----------
// EMI = P * r * (1+r)^n / ((1+r)^n - 1),  r = annualRate/12/100
function calculateEMI(P, annualRate, n) {
  const r = annualRate / 12 / 100;
  let emi, totalPayment, totalInterest;
  if (r === 0) {
    emi = P / n;
    totalPayment = P;
    totalInterest = 0;
  } else {
    const pow = Math.pow(1 + r, n);
    emi = (P * r * pow) / (pow - 1);
    totalPayment = emi * n;
    totalInterest = totalPayment - P;
  }
  return { emi, totalPayment, totalInterest };
}

// ---------- Pod identity ----------
function getPodIdentity() {
  // Pod name comes from HOSTNAME env var (set by Kubernetes)
  const podName = process.env.HOSTNAME || os.hostname();
  // Pod IP from network interfaces
  const nets = os.networkInterfaces();
  let podIp = 'unknown';
  for (const name of Object.keys(nets)) {
    for (const net of nets[name]) {
      if (net.family === 'IPv4' && !net.internal) {
        podIp = net.address;
        break;
      }
    }
  }
  return { podName, podIp };
}

// ---------- GET /health (readiness probe) ----------
app.get('/health', async (req, res) => {
  try {
    await db.command({ ping: 1 });
    return res.status(200).json({ status: 'ok', mongo: 'reachable' });
  } catch (e) {
    return res.status(500).json({ status: 'error', mongo: 'unreachable' });
  }
});

// ---------- POST /api/emi ----------
app.post('/api/emi', async (req, res) => {
  try {
    const P = parseFloat(req.body.principal);
    const rate = parseFloat(req.body.rate);
    const n = parseInt(req.body.months, 10);

    // Server-side validation: positive numbers only
    if (!Number.isFinite(P) || P <= 0) {
      return res.status(400).json({ error: 'Loan amount must be a positive number.' });
    }
    if (!Number.isFinite(rate) || rate < 0) {
      return res.status(400).json({ error: 'Annual interest rate must be a non-negative number.' });
    }
    if (!Number.isInteger(n) || n <= 0) {
      return res.status(400).json({ error: 'Tenure must be a positive integer (months).' });
    }

    const { emi, totalPayment, totalInterest } = calculateEMI(P, rate, n);
    const { podName, podIp } = getPodIdentity();

    const doc = {
      principal: P,
      rate: rate,
      months: n,
      emi: parseFloat(emi.toFixed(2)),
      servedBy: podName,
      podIp: podIp,
      createdAt: new Date()
    };

    await db.collection('calculations').insertOne(doc);

    return res.json({
      emi: doc.emi,
      totalPayment: parseFloat(totalPayment.toFixed(2)),
      totalInterest: parseFloat(totalInterest.toFixed(2)),
      servedBy: podName,
      podIp: podIp
    });
  } catch (e) {
    console.error('Error in /api/emi:', e.message);
    return res.status(500).json({ error: 'Internal server error.' });
  }
});

// ---------- GET /api/history (last 10, newest first) ----------
app.get('/api/history', async (req, res) => {
  try {
    const docs = await db.collection('calculations')
      .find({}, { projection: { _id: 0 } })
      .sort({ createdAt: -1 })
      .limit(10)
      .toArray();
    return res.json(docs);
  } catch (e) {
    console.error('Error in /api/history:', e.message);
    return res.status(500).json({ error: 'Internal server error.' });
  }
});

// ---------- Start server ----------
connectMongo().then(() => {
  app.listen(PORT, () => {
    console.log(`EMI Calculator app listening on port ${PORT}`);
  });
}).catch((err) => {
  console.error('Failed to connect to MongoDB:', err.message);
  process.exit(1);
});
