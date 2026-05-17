// ============================================================
//  lab.js — Provider-first vs Conventional Live Comparison Lab
//  Phase 0: single-process benchmark harness
// ============================================================

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const os = require('os');

const PORT = process.env.PORT || 3000;
const DB_DELAY_MS = 20;
const VERIFIER_DELAY_MS = 5;
const LOAD_RPS = 20;
const BURST_RPS = 80;
const BURST_DURATION = 5;
const BURST_INTERVAL = 60;

const users = new Map([
  ['admin-token', { id: 'u1', role: 'admin' }],
  ['user-token',  { id: 'u2', role: 'user' }],
]);

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function dbLookup(token) {
  await sleep(DB_DELAY_MS);
  return users.get(token) || null;
}

async function callVerifier(token, resource, action) {
  await sleep(VERIFIER_DELAY_MS);
  return { allowed: token === 'admin-token' };
}

const windowSize = 500;

let metrics = {
  conventional: {
    totalLifetime: 0,
    totalWindow: 0,
    allowed: 0,
    denied: 0,
    timeouts: 0,
    dbTouchedBeforeDenial: 0,
    latencies: [],
    providerSeenAt: [],
    denialTimes: [],
  },
  providerFirst: {
    totalLifetime: 0,
    totalWindow: 0,
    allowed: 0,
    denied: 0,
    timeouts: 0,
    dbTouchedBeforeDenial: 0,
    latencies: [],
    providerSeenAt: [],
    denialTimes: [],
  },
  serviceHealth: {
    conventionalPath: true,
    providerFirstPath: true,
    verifier: true,
    database: true,
  },
};

function pushLimited(arr, val) {
  arr.push(val);
  if (arr.length > windowSize) arr.shift();
}

function record(mode, outcome, data) {
  const m = metrics[mode];

  m.totalLifetime++;
  m.totalWindow++;

  if (outcome === 'allowed') m.allowed++;

  if (outcome === 'denied') {
    m.denied++;
    if (data.dbTouched) m.dbTouchedBeforeDenial++;
    pushLimited(m.denialTimes, data.latency);
  }

  if (outcome === 'timeout') m.timeouts++;

  pushLimited(m.latencies, data.latency);
  pushLimited(m.providerSeenAt, data.providerSeenAt);
}

function avg(arr) {
  if (!arr.length) return 0;
  return arr.reduce((s, v) => s + v, 0) / arr.length;
}

function percentile(arr, q) {
  if (!arr.length) return 0;
  const sorted = [...arr].sort((a, b) => a - b);
  const idx = Math.ceil((q / 100) * sorted.length) - 1;
  return sorted[Math.max(0, idx)];
}

function getStats() {
  const c = metrics.conventional;
  const pf = metrics.providerFirst;

  return {
    timestamp: Date.now(),
    serviceHealth: { ...metrics.serviceHealth },

    throughput: {
      currentRPS: c.totalWindow + pf.totalWindow,
      totalRequests: c.totalLifetime + pf.totalLifetime,
      conventionalRequests: c.totalLifetime,
      providerFirstRequests: pf.totalLifetime,
      validRequests: c.allowed + pf.allowed,
      invalidRequests: c.denied + pf.denied,
    },

    latency: {
      conventional: {
        avg: avg(c.latencies),
        p50: percentile(c.latencies, 50),
        p95: percentile(c.latencies, 95),
        p99: percentile(c.latencies, 99),
      },
      providerFirst: {
        avg: avg(pf.latencies),
        p50: percentile(pf.latencies, 50),
        p95: percentile(pf.latencies, 95),
        p99: percentile(pf.latencies, 99),
      },
    },

    providerTiming: {
      conventional: avg(c.providerSeenAt),
      providerFirst: avg(pf.providerSeenAt),
    },

    denial: {
      conventional: {
        rejectionTime: avg(c.denialTimes),
        denials: c.denied,
        timeouts: c.timeouts,
      },
      providerFirst: {
        rejectionTime: avg(pf.denialTimes),
        denials: pf.denied,
        timeouts: pf.timeouts,
      },
    },

    preDenialActivation: {
      conventionalSystemsTouched: c.dbTouchedBeforeDenial,
      providerFirstSystemsTouched: pf.dbTouchedBeforeDenial,
    },

    dataExposure: {
      conventionalDBBeforeDenial: c.dbTouchedBeforeDenial > 0 ? 'yes' : 'no',
      conventionalDBCount: c.dbTouchedBeforeDenial,
      providerFirstDBBeforeDenial: pf.dbTouchedBeforeDenial > 0 ? 'yes' : 'no',
      providerFirstDBCount: pf.dbTouchedBeforeDenial,
    },

    resource: {
      cpu: (os.loadavg()[0] / os.cpus().length * 100).toFixed(1),
      ram: (process.memoryUsage().rss / 1024 / 1024).toFixed(1),
    },
  };
}

function resetPerSecondCounters() {
  metrics.conventional.totalWindow = 0;
  metrics.providerFirst.totalWindow = 0;
}

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

app.use(express.json());

app.get('/', (req, res) => {
  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NUVL Lab — Provider-first vs Conventional</title>
<style>
  body { font-family: monospace; background: #0a0a0a; color: #e0e0e0; padding: 20px; }
  h1 { margin-bottom: 4px; }
  .sub { color: #aaa; margin-bottom: 20px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
  .card { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 16px; }
  .card h3 { margin-top: 0; color: #00bcd4; }
  .row { display: flex; justify-content: space-between; gap: 16px; }
  .val { font-weight: bold; color: #fff; }
  .green { color: #4caf50; font-weight: bold; }
  .red { color: #f44336; font-weight: bold; }
  .big { font-size: 1.5em; }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: 4px 8px; border-bottom: 1px solid #333; }
  th { color: #888; }
  footer { margin-top: 24px; color: #888; }
  footer a { color: #00bcd4; }
</style>
</head>
<body>
<h1>NUVL Live Lab</h1>
<div class="sub">Provider-first vs Conventional Request Ordering</div>

<div class="grid">
  <div class="card">
    <h3>Service Health</h3>
    <div class="row"><span>Conventional Path</span><span id="h-conv" class="green">up</span></div>
    <div class="row"><span>Provider-First Path</span><span id="h-prov" class="green">up</span></div>
    <div class="row"><span>Verifier</span><span id="h-ver" class="green">up</span></div>
    <div class="row"><span>Database</span><span id="h-db" class="green">up</span></div>
  </div>

  <div class="card">
    <h3>Throughput</h3>
    <div class="row"><span>Current RPS</span><span id="t-rps" class="val big">0</span></div>
    <div class="row"><span>Total Requests</span><span id="t-total" class="val">0</span></div>
    <div class="row"><span>Conventional</span><span id="t-conv" class="val">0</span></div>
    <div class="row"><span>Provider-First</span><span id="t-pf" class="val">0</span></div>
    <div class="row"><span>Valid</span><span id="t-valid" class="val">0</span></div>
    <div class="row"><span>Invalid</span><span id="t-invalid" class="val">0</span></div>
  </div>

  <div class="card">
    <h3>Latency ms</h3>
    <table>
      <tr><th></th><th>Conventional</th><th>Provider-First</th></tr>
      <tr><td>avg</td><td id="l-c-avg">0</td><td id="l-p-avg">0</td></tr>
      <tr><td>p50</td><td id="l-c-p50">0</td><td id="l-p-p50">0</td></tr>
      <tr><td>p95</td><td id="l-c-p95">0</td><td id="l-p-p95">0</td></tr>
      <tr><td>p99</td><td id="l-c-p99">0</td><td id="l-p-p99">0</td></tr>
    </table>
  </div>

  <div class="card">
    <h3>Provider Timing</h3>
    <div class="row"><span>Conventional Provider Seen At</span><span id="pt-conv" class="val">0</span></div>
    <div class="row"><span>Provider-First Provider Seen At</span><span id="pt-prov" class="val">0</span></div>
  </div>

  <div class="card">
    <h3>Denial Behavior</h3>
    <div class="row"><span>Conv. Rejection Time</span><span id="d-ctime" class="val">0</span></div>
    <div class="row"><span>PF Rejection Time</span><span id="d-ptime" class="val">0</span></div>
    <div class="row"><span>Conv. Denials</span><span id="d-cdeny" class="val">0</span></div>
    <div class="row"><span>PF Denials</span><span id="d-pdeny" class="val">0</span></div>
    <div class="row"><span>Conv. Timeouts</span><span id="d-ctout" class="val">0</span></div>
    <div class="row"><span>PF Timeouts</span><span id="d-ptout" class="val">0</span></div>
  </div>

  <div class="card">
    <h3>Pre-Denial Activation</h3>
    <div class="row"><span>Conv. DB Touches Before Denial</span><span id="pda-conv" class="val">0</span></div>
    <div class="row"><span>PF DB Touches Before Denial</span><span id="pda-prov" class="val">0</span></div>
  </div>

  <div class="card">
    <h3>Data Exposure</h3>
    <div class="row"><span>Conv. DB Before Denial</span><span id="de-conv" class="val">no</span></div>
    <div class="row"><span>PF DB Before Denial</span><span id="de-prov" class="val">no</span></div>
    <div class="row"><span>Conv. DB Count</span><span id="de-ccount" class="val">0</span></div>
    <div class="row"><span>PF DB Count</span><span id="de-pcount" class="val">0</span></div>
  </div>

  <div class="card">
    <h3>Resource Usage</h3>
    <div class="row"><span>CPU %</span><span id="r-cpu" class="val">0</span></div>
    <div class="row"><span>RAM MB</span><span id="r-ram" class="val">0</span></div>
  </div>
</div>

<footer>
  Xer0trust: <a href="https://xer0trust.com">xer0trust.com</a>
</footer>

<script src="/socket.io/socket.io.js"></script>
<script>
  const socket = io();

  function setText(id, value) {
    document.getElementById(id).textContent = value;
  }

  socket.on('stats', (s) => {
    setText('h-conv', s.serviceHealth.conventionalPath ? 'up' : 'down');
    setText('h-prov', s.serviceHealth.providerFirstPath ? 'up' : 'down');
    setText('h-ver', s.serviceHealth.verifier ? 'up' : 'down');
    setText('h-db', s.serviceHealth.database ? 'up' : 'down');

    setText('t-rps', s.throughput.currentRPS);
    setText('t-total', s.throughput.totalRequests);
    setText('t-conv', s.throughput.conventionalRequests);
    setText('t-pf', s.throughput.providerFirstRequests);
    setText('t-valid', s.throughput.validRequests);
    setText('t-invalid', s.throughput.invalidRequests);

    setText('l-c-avg', s.latency.conventional.avg.toFixed(1));
    setText('l-c-p50', s.latency.conventional.p50.toFixed(1));
    setText('l-c-p95', s.latency.conventional.p95.toFixed(1));
    setText('l-c-p99', s.latency.conventional.p99.toFixed(1));

    setText('l-p-avg', s.latency.providerFirst.avg.toFixed(1));
    setText('l-p-p50', s.latency.providerFirst.p50.toFixed(1));
    setText('l-p-p95', s.latency.providerFirst.p95.toFixed(1));
    setText('l-p-p99', s.latency.providerFirst.p99.toFixed(1));

    setText('pt-conv', s.providerTiming.conventional.toFixed(1) + ' ms');
    setText('pt-prov', s.providerTiming.providerFirst.toFixed(1) + ' ms');

    setText('d-ctime', s.denial.conventional.rejectionTime.toFixed(1) + ' ms');
    setText('d-ptime', s.denial.providerFirst.rejectionTime.toFixed(1) + ' ms');
    setText('d-cdeny', s.denial.conventional.denials);
    setText('d-pdeny', s.denial.providerFirst.denials);
    setText('d-ctout', s.denial.conventional.timeouts);
    setText('d-ptout', s.denial.providerFirst.timeouts);

    setText('pda-conv', s.preDenialActivation.conventionalSystemsTouched);
    setText('pda-prov', s.preDenialActivation.providerFirstSystemsTouched);

    setText('de-conv', s.dataExposure.conventionalDBBeforeDenial);
    setText('de-prov', s.dataExposure.providerFirstDBBeforeDenial);
    setText('de-ccount', s.dataExposure.conventionalDBCount);
    setText('de-pcount', s.dataExposure.providerFirstDBCount);

    setText('r-cpu', s.resource.cpu);
    setText('r-ram', s.resource.ram);
  });
</script>
</body>
</html>`);
});

app.get('/api/conventional/data', async (req, res) => {
  const start = Date.now();
  const token = (req.headers.authorization || '').replace('Bearer ', '');

  const dbStart = Date.now();
  const dbUser = await dbLookup(token);

  const providerStart = Date.now();
  const providerSeenAt = providerStart - start;
  const decision = await callVerifier(token, 'data', 'read');

  if (!dbUser || !decision.allowed || dbUser.role !== 'admin') {
    const latency = Date.now() - start;
    record('conventional', 'denied', { latency, providerSeenAt, dbTouched: true });
    return res.status(403).json({ error: 'Forbidden' });
  }

  const latency = Date.now() - start;
  record('conventional', 'allowed', { latency, providerSeenAt, dbTouched: true });
  res.json({ data: 'secret-conventional' });
});

app.get('/api/provider-first/data', async (req, res) => {
  const start = Date.now();
  const token = (req.headers.authorization || '').replace('Bearer ', '');

  const providerStart = Date.now();
  const decision = await callVerifier(token, 'data', 'read');
  const providerSeenAt = providerStart - start;

  if (!decision.allowed) {
    const latency = Date.now() - start;
    record('providerFirst', 'denied', { latency, providerSeenAt, dbTouched: false });
    return res.status(403).json({ error: 'Forbidden' });
  }

  const dbUser = await dbLookup(token);

  if (!dbUser || dbUser.role !== 'admin') {
    const latency = Date.now() - start;
    record('providerFirst', 'denied', { latency, providerSeenAt, dbTouched: true });
    return res.status(403).json({ error: 'Forbidden' });
  }

  const latency = Date.now() - start;
  record('providerFirst', 'allowed', { latency, providerSeenAt, dbTouched: true });
  res.json({ data: 'secret-provider-first' });
});

setInterval(() => {
  const stats = getStats();
  io.emit('stats', stats);
  resetPerSecondCounters();
}, 1000);

function randomToken() {
  return Math.random() < 0.7 ? 'user-token' : 'admin-token';
}

function randomPath() {
  return Math.random() < 0.5 ? 'conventional' : 'provider-first';
}

async function sendRequest() {
  const path = randomPath();
  const token = randomToken();

  const endpoint = path === 'conventional'
    ? '/api/conventional/data'
    : '/api/provider-first/data';

  try {
    await fetch(`http://localhost:${PORT}${endpoint}`, {
      headers: { authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(5000),
    });
  } catch (e) {
    const mode = endpoint.includes('conventional') ? 'conventional' : 'providerFirst';
    record(mode, 'timeout', { latency: 5000, providerSeenAt: 0, dbTouched: false });
  }
}

let loadInterval;

function startLoad(rps) {
  if (loadInterval) clearInterval(loadInterval);
  const intervalMs = 1000 / rps;
  loadInterval = setInterval(sendRequest, intervalMs);
}

setInterval(() => {
  startLoad(BURST_RPS);

  setTimeout(() => {
    startLoad(LOAD_RPS);
  }, BURST_DURATION * 1000);

}, BURST_INTERVAL * 1000);

startLoad(LOAD_RPS);

server.listen(PORT, () => {
  console.log(`NUVL Live Lab running at http://localhost:${PORT}`);
  console.log(`Steady load: ${LOAD_RPS} RPS`);
  console.log(`Burst: ${BURST_RPS} RPS for ${BURST_DURATION}s every ${BURST_INTERVAL}s`);
});
