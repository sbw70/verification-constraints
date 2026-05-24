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

    allowed,
    denied: !allowed,
    reason,

    token_type,
    action,
    resource,

    received_at_ms,
    responded_at_ms,
    elapsed_ms:
      responded_at_ms - received_at_ms,

    total_requests_seen: requestCounter,

    activated_components: [
      ...trace,
      SERVICE_NAME
    ]
  });
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
