const express = require("express");
const axios = require("axios");

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

app.post("/gateway", async (req, res) => {

  const received_at_ms = Date.now();

  const {
    trace_id,
    request_id,
    token,
    action,
    resource,
    trace = []
  } = req.body;

  const updated_trace = [
    ...trace,
    SERVICE_NAME
  ];

  try {

    const boundaryResponse = await axios.post(
      "http://provider-first-boundary:4101/boundary-check",
      {
        trace_id,
        request_id,
        token,
        action,
        resource,
        trace: updated_trace
      }
    );

    const responded_at_ms = Date.now();

    res.json({
      service: SERVICE_NAME,

      trace_id,
      request_id,

      forwarded_to_boundary: true,

      gateway_received_at_ms:
        received_at_ms,

      gateway_responded_at_ms:
        responded_at_ms,

      gateway_elapsed_ms:
        responded_at_ms - received_at_ms,

      trace: updated_trace,

      boundary_response:
        boundaryResponse.data
    });

  } catch (err) {

    res.status(500).json({
      service: SERVICE_NAME,
      error: "boundary_forward_failed",
      details: err.message
    });

  }

});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
