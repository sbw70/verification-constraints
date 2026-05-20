const express = require("express");

const SERVICE_NAME = "conventional-gateway";
const PORT = process.env.PORT || 3101;

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
    token,
    action,
    resource
  } = req.body;

  res.json({
    service: SERVICE_NAME,
    trace_id,
    request_id,
    gateway_forwarded: true,
    token_present: !!token,
    action,
    resource
  });
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
