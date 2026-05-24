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
    token,
    token_type,
    action,
    resource,
    trace = []
  } = req.body;

  const activated_components = [
    ...trace,
    SERVICE_NAME
  ];

  try {
    const dataResponse = await axios.post(DATA_SERVICE_URL, {
      trace_id,
      request_id,
      action,
      resource,
      trace: activated_components
    });

    const providerResponse = await axios.post(PROVIDER_ADAPTER_URL, {
      trace_id,
      request_id,
      token,
      token_type,
      action,
      resource,
      trace: dataResponse.data.activated_components
    });

    const app_responded_at_ms = Date.now();

    res.json({
      service: SERVICE_NAME,
      trace_id,
      request_id,

      path: "conventional",

      application_activated: true,
      downstream_execution: true,
      denied_before_app: false,
      provider_decision_seen: true,

      total_requests_seen: requestCounter,

      token_type,
      action,
      resource,

      app_received_at_ms,
      app_responded_at_ms,
      app_elapsed_ms:
        app_responded_at_ms - app_received_at_ms,

      activated_components:
        providerResponse.data.activated_components,

      data_response: dataResponse.data,
      provider_response: providerResponse.data
    });
  } catch (err) {
    res.status(500).json({
      service: SERVICE_NAME,
      path: "conventional",
      error: "app failed",
      details: err.message,
      total_requests_seen: requestCounter
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
