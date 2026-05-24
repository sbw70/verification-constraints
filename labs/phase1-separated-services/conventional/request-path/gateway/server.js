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
    const identityResponse = await axios.post(IDENTITY_URL, {
      token
    });

    activated_components.push("shared-identity");

    const {
      valid,
      token_type,
      subject,
      role,
      reason: identity_reason
    } = identityResponse.data;

    const appResponse = await axios.post(
      APP_URL,
      {
        trace_id,
        request_id,
        token,
        token_valid: valid,
        token_type,
        subject,
        role,
        identity_reason,
        action,
        resource,
        activated_components
      },
      {
        validateStatus: () => true
      }
    );

    const gateway_responded_at_ms = Date.now();

    const providerAllowed =
      appResponse.data?.provider_response?.allowed === true;

    res.status(providerAllowed ? 200 : 403).json({
      service: SERVICE_NAME,
      trace_id,
      request_id,

      gateway_forwarded: true,
      token_present: !!token,
      token_valid: valid,
      token_type,
      subject,
      role,
      identity_reason,

      action,
      resource,

      gateway_received_at_ms,
      gateway_responded_at_ms,
      gateway_elapsed_ms:
        gateway_responded_at_ms - gateway_received_at_ms,

      total_requests_seen: requestCounter,

      activated_components:
        appResponse.data?.activated_components ||
        activated_components,

      app_response: appResponse.data
    });
  } catch (err) {
    const gateway_responded_at_ms = Date.now();

    res.status(500).json({
      service: SERVICE_NAME,
      trace_id,
      request_id,
      error: "gateway failed",
      details: err.message,

      gateway_received_at_ms,
      gateway_responded_at_ms,
      gateway_elapsed_ms:
        gateway_responded_at_ms - gateway_received_at_ms,

      total_requests_seen: requestCounter,
      activated_components
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
