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

  try {
    const identityResponse = await axios.post(IDENTITY_URL, {
      token
    });

    const identity = identityResponse.data;

    const appResponse = await axios.post(APP_URL, {
      trace_id,
      request_id,
      token,
      token_type: identity.token_type,
      token_valid: identity.valid,
      subject: identity.subject,
      role: identity.role,
      action,
      resource,
      trace: [
        SERVICE_NAME,
        "shared-identity"
      ]
    });

    const gateway_responded_at_ms = Date.now();

    const providerDecision =
      appResponse.data.provider_decision || {};

    const allowed = providerDecision.allowed === true;
    const denied = !allowed;

    res.status(allowed ? 200 : 403).json({
      service: SERVICE_NAME,
      trace_id,
      request_id,

      gateway_forwarded: true,
      token_present: !!token,

      identity_seen: true,
      identity_valid: identity.valid,
      token_type: identity.token_type,
      subject: identity.subject,
      role: identity.role,

      denied_before_app: false,
      provider_decision_seen: providerDecision.provider_decision_seen === true,

      allowed,
      denied,
      reason: providerDecision.reason || "provider denied after downstream execution",

      action,
      resource,

      gateway_received_at_ms,
      gateway_responded_at_ms,
      gateway_elapsed_ms:
        gateway_responded_at_ms - gateway_received_at_ms,

      total_requests_seen: requestCounter,

      activated_components: [
        SERVICE_NAME,
        "shared-identity",
        "conventional-app",
        "conventional-data-service",
        "conventional-provider-adapter"
      ],

      app_response: appResponse.data
    });
  } catch (err) {
    const gateway_responded_at_ms = Date.now();

    res.status(500).json({
      service: SERVICE_NAME,
      trace_id,
      request_id,
      error: "conventional gateway failed",
      details: err.message,
      gateway_received_at_ms,
      gateway_responded_at_ms,
      gateway_elapsed_ms:
        gateway_responded_at_ms - gateway_received_at_ms,
      total_requests_seen: requestCounter
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
