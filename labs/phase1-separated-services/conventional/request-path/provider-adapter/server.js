const express = require("express");

let requestCounter = 0;

const SERVICE_NAME = "conventional-provider-adapter";
const PORT = process.env.PORT || 3104;

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok",
    requests_seen: requestCounter
  });
});

app.post("/provider-check", (req, res) => {
  requestCounter++;

  const received_at_ms = Date.now();

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

  let allowed = false;
  let reason = "not allowed";

  if (token_type === "valid_admin" && action === "admin:access") {
    allowed = true;
    reason = "admin access allowed";
  }

  if (token_type === "valid_user" && action === "profile:read") {
    allowed = true;
    reason = "user profile read allowed";
  }

  const responded_at_ms = Date.now();

  res.json({
    service: SERVICE_NAME,
    trace_id,
    request_id,

    provider_decision_seen: true,

    token_type,
    token_valid,
    subject,
    role,

    allowed,
    denied: !allowed,
    reason,

    action,
    resource,

    trace: [
      ...trace,
      SERVICE_NAME
    ],

    received_at_ms,
    responded_at_ms,
    elapsed_ms:
      responded_at_ms - received_at_ms,

    total_requests_seen: requestCounter
  });
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
