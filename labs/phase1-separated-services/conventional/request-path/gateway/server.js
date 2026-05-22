const express = require("express");
const axios = require("axios");

const SERVICE_NAME = "conventional-gateway";
const PORT = process.env.PORT || 3101;

const APP_URL =
  process.env.APP_URL ||
  "http://conventional-app:3102/execute";

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.post("/request", async (req, res) => {
  const gateway_received_at_ms = Date.now();

  const {
    trace_id,
    request_id,
    token,
    action,
    resource
  } = req.body;

  try {
    const gateway_forwarded_at_ms = Date.now();

    const appResponse = await axios.post(APP_URL, {
      trace_id,
      request_id,
      action,
      resource
    });

    const gateway_responded_at_ms = Date.now();

    res.json({
      service: SERVICE_NAME,
      trace_id,
      request_id,
      gateway_forwarded: true,
      token_present: !!token,
      action,
      resource,

      gateway_received_at_ms,
      gateway_forwarded_at_ms,
      gateway_responded_at_ms,
      gateway_elapsed_ms:
        gateway_responded_at_ms - gateway_received_at_ms,

      app_response: appResponse.data
    });
  } catch (err) {
    res.status(500).json({
      service: SERVICE_NAME,
      error: "gateway failed to reach app",
      details: err.message
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
