const express = require("express");

const SERVICE_NAME = "provider-first-verifier";
const PORT = process.env.PORT || 4102;

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.post("/verify", (req, res) => {

  const received_at_ms = Date.now();

  const {
    trace_id,
    request_id,
    token_type,
    action,
    resource,
    trace = []
  } = req.body;

  const updated_trace = [
    ...trace,
    SERVICE_NAME
  ];

  let allowed = false;
  let denied = true;
  let reason = "not allowed";

  if (
    token_type === "valid_user" &&
    action === "profile:read"
  ) {
    allowed = true;
    denied = false;
    reason = "user profile read allowed";
  }

  if (
    token_type === "valid_admin" &&
    action === "admin:access"
  ) {
    allowed = true;
    denied = false;
    reason = "admin access allowed";
  }

  const responded_at_ms = Date.now();

  res.json({
    service: SERVICE_NAME,
    trace_id,
    request_id,

    provider_decision_seen: true,

    allowed,
    denied,
    reason,

    action,
    resource,

    trace: updated_trace,

    received_at_ms,
    responded_at_ms,

    elapsed_ms:
      responded_at_ms - received_at_ms
  });

});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
