const express = require("express");
const axios = require("axios");

let requestCounter = 0;

const SERVICE_NAME = "conventional-app";
const PORT = process.env.PORT || 3102;

const DATA_SERVICE_URL =
  process.env.DATA_SERVICE_URL ||
  "http://conventional-data-service:3103/data-access";

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

app.post("/execute", async (req, res) => {
  requestCounter++;

  const app_received_at_ms = Date.now();

  const {
    trace_id,
    request_id,
    token_type,
    token_valid,
    subject,
    role,
    action,
    resource,
    trace = []
  } = req.body;

  try {
    const dataResponse = await axios.post(DATA_SERVICE_URL, {
      trace_id,
      request_id,
      action,
      resource
    });

    const providerResponse = await axios.post(PROVIDER_ADAPTER_URL, {
      trace_id,
      request_id,
      token_type,
      token_valid,
      subject,
      role,
      action,
      resource,
      trace: [
        ...trace,
        SERVICE_NAME,
        "conventional-data-service"
      ]
    });

    const app_responded_at_ms = Date.now();

    res.json({
      service: SERVICE_NAME,
      trace_id,
      request_id,

      application_activated: true,
      downstream_execution: true,
      denied_before_app: false,
      provider_decision_seen: true,

      total_requests_seen: requestCounter,

      token_type,
      token_valid,
      subject,
      role,
      action,
      resource,

      app_received_at_ms,
      app_responded_at_ms,
      app_elapsed_ms:
        app_responded_at_ms - app_received_at_ms,

      trace: [
        ...trace,
        SERVICE_NAME,
        "conventional-data-service",
        "conventional-provider-adapter"
      ],

      data_response: dataResponse.data,
      provider_decision: providerResponse.data
    });
  } catch (err) {
    const app_responded_at_ms = Date.now();

    res.status(500).json({
      service: SERVICE_NAME,
      trace_id,
      request_id,
      error: "app failed during downstream execution",
      details: err.message,
      app_received_at_ms,
      app_responded_at_ms,
      app_elapsed_ms:
        app_responded_at_ms - app_received_at_ms,
      total_requests_seen: requestCounter
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
