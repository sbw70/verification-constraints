const express = require("express");
const axios = require("axios");

const SERVICE_NAME = "provider-first-gateway";
const PORT = process.env.PORT || 4103;
const BOUNDARY_URL =
  process.env.BOUNDARY_URL || "http://provider-first-boundary:4101/boundary-check";

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.post("/gateway", async (req, res) => {
  const gateway_received_at_ms = Date.now();

  const {
    trace_id,
    request_id,
    token,
    action,
    resource
  } = req.body;

  if (!token) {
    return res.status(400).json({
      service: SERVICE_NAME,
      error: "missing_token",
      trace_id,
      request_id
    });
  }

  const internal_trace = [SERVICE_NAME];

  try {
    const gateway_forwarded_at_ms = Date.now();

    const boundaryResponse = await axios.post(
      BOUNDARY_URL,
      {
        trace_id,
        request_id,
        token,
        action,
        resource,
        trace: internal_trace
      },
      {
        timeout: 200
      }
    );

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
      trace: internal_trace,
      boundary_response: boundaryResponse.data
    });

  } catch (err) {
    const gateway_responded_at_ms = Date.now();

    console.error("boundary_forward_failed", err.message);

    res.status(502).json({
      service: SERVICE_NAME,
      trace_id,
      request_id,
      error: "boundary_forward_failed",
      details: "boundary unreachable",
      gateway_received_at_ms,
      gateway_responded_at_ms,
      gateway_elapsed_ms:
        gateway_responded_at_ms - gateway_received_at_ms,
      trace: internal_trace
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
