const express = require("express");
const axios = require("axios");

const SERVICE_NAME = "conventional-app";
const PORT = process.env.PORT || 3102;

const DATA_SERVICE_URL =
  process.env.DATA_SERVICE_URL ||
  "http://conventional-data-service:3103/data-access";

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.post("/execute", async (req, res) => {
  const app_received_at_ms = Date.now();

  const {
    trace_id,
    request_id,
    action,
    resource
  } = req.body;

  try {
    const dataResponse = await axios.post(DATA_SERVICE_URL, {
      trace_id,
      request_id,
      action,
      resource
    });

    const app_responded_at_ms = Date.now();

    res.json({
      service: SERVICE_NAME,
      trace_id,
      request_id,
      application_activated: true,
      downstream_execution: true,
      denied_before_app: false,
      provider_decision_seen: false,
      action,
      resource,
      app_received_at_ms,
      app_responded_at_ms,
      app_elapsed_ms:
        app_responded_at_ms - app_received_at_ms,
      data_response: dataResponse.data
    });
  } catch (err) {
    res.status(500).json({
      service: SERVICE_NAME,
      error: "app failed to reach data service",
      details: err.message
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
