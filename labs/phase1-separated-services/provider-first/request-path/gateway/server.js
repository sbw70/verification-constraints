const express = require("express");
const axios = require("axios");

let requestCounter = 0;

const SERVICE_NAME = "provider-first-gateway";
const PORT = process.env.PORT || 4103;

const BOUNDARY_URL =
  process.env.BOUNDARY_URL ||
  "http://provider-first-boundary:4101/boundary-check";

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok",
    requests_seen: requestCounter
  });
});

app.post("/gateway", async (req, res) => {

  requestCounter++;

  const gateway_received_at_ms = Date.now();

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

  try {
    const gateway_forwarded_at_ms = Date.now();

    const boundaryResponse = await axios.post(BOUNDARY_URL, {
      trace_id,
      request_id,
      token,
      action,
      resource
    });

    const gateway_responded_at_ms = Date.now();

    res.json({
      service: SERVICE_NAME,
      trace_id,
      request_id,
      forwarded_to_boundary: true,
      gateway_received_at_ms,
      gateway_forwarded_at_ms,
      gateway_responded_at_ms,
      gateway_elapsed_ms:
        gateway_responded_at_ms - gateway_received_at_ms,
      total_requests_seen: requestCounter,
      trace,
      boundary_response: boundaryResponse.data
    });
  } catch (err) {
    res.status(500).json({
      service: SERVICE_NAME,
      error: "gateway failed to reach boundary",
      details: err.message,
      total_requests_seen: requestCounter
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
