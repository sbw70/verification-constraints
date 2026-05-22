const express = require("express");
const axios = require("axios");

let requestCounter = 0;

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
    status: "ok",
    requests_seen: requestCounter
  });
});

app.post("/request", async (req, res) => {

  requestCounter++;

  const gatewayStarted = Date.now();

  const {
    trace_id,
    request_id,
    token,
    action,
    resource
  } = req.body;

  try {

    const appResponse = await axios.post(APP_URL, {
      trace_id,
      request_id,
      action,
      resource
    });

    const gatewayFinished = Date.now();

    res.json({
      service: SERVICE_NAME,
      trace_id,
      request_id,
      gateway_forwarded: true,
      token_present: !!token,
      action,
      resource,

      gateway_received_at_ms: gatewayStarted,
      gateway_responded_at_ms: gatewayFinished,
      gateway_elapsed_ms:
        gatewayFinished - gatewayStarted,

      total_requests_seen: requestCounter,

      app_response: appResponse.data
    });

  } catch (err) {

    res.status(500).json({
      service: SERVICE_NAME,
      error: "gateway failed to reach app",
      details: err.message,
      total_requests_seen: requestCounter
    });

  }

});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
