const express = require("express");
const axios = require("axios");

let requestCounter = 0;

const SERVICE_NAME = "provider-first-app";
const PORT = process.env.PORT || 4104;

const DATA_SERVICE_URL =
  process.env.DATA_SERVICE_URL ||
  "http://provider-first-data-service:4105/data-access";

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

    const app_responded_at_ms = Date.now();

    res.json({
      service: SERVICE_NAME,
      trace_id,
      request_id,

      path: "provider-first",

      application_activated: true,
      downstream_execution: true,

      token_type,
      action,
      resource,

      app_received_at_ms,
      app_responded_at_ms,
      app_elapsed_ms:
        app_responded_at_ms - app_received_at_ms,

      total_requests_seen: requestCounter,

      activated_components:
        dataResponse.data.activated_components,

      data_response: dataResponse.data
    });
  } catch (err) {
    res.status(500).json({
      service: SERVICE_NAME,
      path: "provider-first",
      error: "provider-first app failed",
      details: err.message,
      total_requests_seen: requestCounter
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
