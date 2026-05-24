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

const PROVIDER_ADAPTER_URL =
  process.env.PROVIDER_ADAPTER_URL ||
  "http://conventional-provider-adapter:3104/provider-check";

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

    const token_type = identityResponse.data.token_type;

    const app_started_at_ms = Date.now();

    const appResponse = await axios.post(APP_URL, {
      trace_id,
      request_id,
      token_type,
      action,
      resource
    });

    const app_responded_at_ms = Date.now();

    activated_components.push("conventional-app");

    if (appResponse.data?.data_response?.service) {
      activated_components.push(appResponse.data.data_response.service);
    }

    const provider_started_at_ms = Date.now();

    const providerResponse = await axios.post(PROVIDER_ADAPTER_URL, {
      trace_id,
      request_id,
      token_type,
      action,
      resource
    });

    const provider_responded_at_ms = Date.now();

    activated_components.push("conventional-provider-adapter");

    const gateway_responded_at_ms = Date.now();

    res.json({
      service: SERVICE_NAME,
      trace_id,
      request_id,

      path: "conventional",

      gateway_forwarded: true,
      token_present: !!token,
      token_type,

      action,
      resource,

      activated_components,
      activation_count: activated_components.length,

      provider_decision_seen: true,
      denied_before_app: false,
      downstream_execution: true,

      gateway_received_at_ms,
      gateway_responded_at_ms,
      gateway_elapsed_ms:
        gateway_responded_at_ms - gateway_received_at_ms,

      identity_elapsed_ms:
        identity_responded_at_ms - identity_started_at_ms,

      app_elapsed_ms:
        app_responded_at_ms - app_started_at_ms,

      provider_adapter_elapsed_ms:
        provider_responded_at_ms - provider_started_at_ms,

      total_requests_seen: requestCounter,

      identity_response: identityResponse.data,
      app_response: appResponse.data,
      provider_response: providerResponse.data
    });
  } catch (err) {
    res.status(500).json({
      service: SERVICE_NAME,
      path: "conventional",
      error: "conventional gateway failed",
      details: err.message,
      total_requests_seen: requestCounter
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
