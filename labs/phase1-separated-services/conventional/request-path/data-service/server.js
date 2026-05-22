const express = require("express");

const SERVICE_NAME = "conventional-data-service";
const PORT = process.env.PORT || 3103;

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.post("/data-access", (req, res) => {
  const data_received_at_ms = Date.now();

  const {
    trace_id,
    request_id,
    action,
    resource
  } = req.body;

  const data_responded_at_ms = Date.now();

  res.json({
    service: SERVICE_NAME,
    trace_id,
    request_id,
    data_service_touched: true,
    downstream_execution: true,
    action,
    resource,
    mock_data_access: "complete",

    data_received_at_ms,
    data_responded_at_ms,
    data_elapsed_ms:
      data_responded_at_ms - data_received_at_ms
  });
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
