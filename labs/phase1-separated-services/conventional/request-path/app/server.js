const express = require("express");

const SERVICE_NAME = "conventional-app";
const PORT = process.env.PORT || 3102;

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.post("/execute", (req, res) => {
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
    application_activated: true,
    action,
    resource
  });
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
