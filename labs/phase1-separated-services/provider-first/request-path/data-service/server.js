const express = require("express");

const SERVICE_NAME = "provider-first-data-service";
const PORT = process.env.PORT || 4105;

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.post("/data-access", (req, res) => {
  const {
    trace_id,
    request_id,
    action,
    resource
  } = req.body;

  res.json({
    service: SERVICE_NAME,
    trace_id,
    request_id,
    data_service_touched: true,
    action,
    resource,
    mock_data_access: "complete"
  });
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
