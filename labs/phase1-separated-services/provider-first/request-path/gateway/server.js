const express = require("express");

const SERVICE_NAME = "provider-first-gateway";
const PORT = process.env.PORT || 4103;

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.post("/request", (req, res) => {
  const {
    trace_id,
    request_id,
    allowed,
    action,
    resource
  } = req.body;

  if (!allowed) {
    return res.status(403).json({
      service: SERVICE_NAME,
      trace_id,
      request_id,
      denied: true,
      reason: "provider-first verifier denied request"
    });
  }

  res.json({
    service: SERVICE_NAME,
    trace_id,
    request_id,
    gateway_forwarded: true,
    action,
    resource
  });
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
