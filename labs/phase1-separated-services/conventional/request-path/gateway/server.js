const express = require("express");
const axios = require("axios");

let requestCounter = 0;

const SERVICE_NAME = "conventional-gateway";
const PORT = process.env.PORT || 3101;

const IDENTITY_URL =
  process.env.IDENTITY_URL ||
  "http://shared-identity:3101/validate-token";

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

  const gateway_received_at_ms = Date.now();

  const {
    trace_id,
    request_id,
    token,
    action,
    resource
  } = req.body;

  const activated_components = [SERVICE_NAME];

  try {
    const identity_started_at_ms = Date.now();

    const identityResponse = await axios.post(IDENTITY_URL, {
      token
    });

    const identity_responded_at_ms = Date.now();

    activated_components.push("shared-identity");

    const appResponse = await axios.post(APP_URL, {
      trace_id,
      request_id,
      token,
      token_type: identityResponse.data.token_type,
      action,
      resource,
      trace: activated_components
    });

    const gateway_responded_at_ms = Date.now();

    const allowed = !!appResponse.data?.provider_response?.allowed;

    res.status(allowed ? 200 : 403).json({
      service: SERVICE_NAME,
      trace_id,
      request_id,

      path: "conventional",
      allowed,
      denied: !allowed,

      gateway_forwarded: true,
      token_present: !!token,
      token_type: identityResponse.data.token_type,

      action,
      resource,

      gateway_received_at_ms,
      gateway_responded_at_ms,
      gateway_elapsed_ms:
        gateway_responded_at_ms - gateway_received_at_ms,

      identity_elapsed_ms:
        identity_responded_at_ms - identity_started_at_ms,

      total_requests_seen: requestCounter,

      activated_components:
        appResponse.data.activated_components || activated_components,

      downstream_execution: true,
      denied_before_app: false,
      provider_decision_seen: true,

      identity_response: identityResponse.data,
      app_response: appResponse.data
    });
  } catch (err) {
    res.status(500).json({
      service: SERVICE_NAME,
      path: "conventional",
      error: "gateway failed",
      details: err.message,
      total_requests_seen: requestCounter
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
