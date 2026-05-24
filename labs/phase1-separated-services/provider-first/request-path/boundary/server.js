const express = require("express");
const axios = require("axios");

let requestCounter = 0;

const SERVICE_NAME = "provider-first-boundary";
const PORT = process.env.PORT || 4101;

const VERIFIER_URL =
  process.env.VERIFIER_URL ||
  "http://provider-first-verifier:4102/verify";

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok",
    requests_seen: requestCounter
  });
});

app.post("/boundary-check", async (req, res) => {
  requestCounter++;

  const started_at_ms = Date.now();

  const {
    trace_id,
    request_id,
    token,
    action,
    resource,
    trace = []
  } = req.body;

  const activated_components = [
    ...trace,
    SERVICE_NAME
  ];

  try {
    const verifierResponse = await axios.post(VERIFIER_URL, {
      trace_id,
      request_id,
      token,
      action,
      resource,
      trace: activated_components
    });

    const verifier_returned_at_ms = Date.now();

    res.json({
      service: SERVICE_NAME,
      path: "provider-first",

      trace_id,
      request_id,

      boundary_checked: true,
      token_present: !!token,

      action,
      resource,

      started_at_ms,
      verifier_returned_at_ms,
      total_elapsed_ms:
        verifier_returned_at_ms - started_at_ms,

      total_requests_seen: requestCounter,

      activated_components:
        verifierResponse.data.activated_components,

      verifier_response: verifierResponse.data
    });
  } catch (err) {
    res.status(500).json({
      service: SERVICE_NAME,
      path: "provider-first",
      error: "boundary failed to reach verifier",
      details: err.message,
      total_requests_seen: requestCounter
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
