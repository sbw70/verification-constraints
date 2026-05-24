const express = require("express");

let requestCounter = 0;

const SERVICE_NAME = "provider-first-verifier";
const PORT = process.env.PORT || 4102;

const app = express();
app.use(express.json());

function classifyToken(token) {
  if (token === "admin-token") return "valid_admin";
  if (token === "user-token") return "valid_user";
  if (token === "expired-token") return "expired_token";
  return "invalid_token";
}

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok",
    requests_seen: requestCounter
  });
});

app.post("/verify", (req, res) => {
  requestCounter++;

  const received_at_ms = Date.now();

  const {
    trace_id,
    request_id,
    token,
    action,
    resource,
    trace = []
  } = req.body;

  const token_type = classifyToken(token);

  let allowed = false;
  let reason = "not allowed";

  if (token_type === "valid_user" && action === "profile:read") {
    allowed = true;
    reason = "user profile read allowed";
  }

  if (token_type === "valid_admin" && action === "admin:access") {
    allowed = true;
    reason = "admin access allowed";
  }

  if (token_type === "expired_token") {
    reason = "token expired";
  }

  if (token_type === "invalid_token") {
    reason = "invalid token";
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
