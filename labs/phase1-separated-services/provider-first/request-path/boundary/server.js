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
    resource
  } = req.body;

  const trace = [
    SERVICE_NAME
  ];

  const boundary_event = {
    service: SERVICE_NAME,
    trace_id,
    request_id,
    boundary_checked: true,
    token_present: !!token,
    action,
    resource,
    total_requests_seen: requestCounter
  };

  try {

    const verifierResponse = await axios.post(VERIFIER_URL, {
      trace_id,
      request_id,
      token,
      action,
      resource
    });

    const verifier_returned_at_ms = Date.now();

    res.json({
      boundary_event,
      verifier_response: verifierResponse.data,
      trace: [
        ...trace,
        "provider-first-verifier"
      ],
      started_at_ms,
      verifier_returned_at_ms,
      total_elapsed_ms:
        verifier_returned_at_ms - started_at_ms
    });

  } catch (err) {

    res.status(500).json({
      service: SERVICE_NAME,
      error: "boundary failed to reach verifier",
      details: err.message,
      total_requests_seen: requestCounter
    });

  }

});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
