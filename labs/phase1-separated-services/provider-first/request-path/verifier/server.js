const express = require("express");
const axios = require("axios");

let requestCounter = 0;

const SERVICE_NAME = "provider-first-verifier";
const PORT = process.env.PORT || 4102;

const IDENTITY_URL =
  process.env.IDENTITY_URL ||
  "http://shared-identity:3101/validate-token";

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok",
    requests_seen: requestCounter
  });
});

app.post("/verify", async (req, res) => {
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

  const updated_trace = [
    ...trace,
    SERVICE_NAME
  ];

  try {
    const identityResponse = await axios.post(IDENTITY_URL, {
      token
    });

    const identity = identityResponse.data;

    let allowed = false;
    let denied = true;
    let reason = "not allowed";

    if (!identity.valid) {
      reason = identity.reason || "identity rejected token";
    }

    if (
      identity.token_type === "valid_user" &&
      action === "profile:read"
    ) {
      allowed = true;
      denied = false;
      reason = "user profile read allowed";
    }

    if (
      identity.token_type === "valid_admin" &&
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
      identity_checked: true,

      token_valid: identity.valid,
      token_type: identity.token_type,
      subject: identity.subject,
      role: identity.role,

      allowed,
      denied,
      reason,

      action,
      resource,

      trace: updated_trace,

      received_at_ms,
      responded_at_ms,
      elapsed_ms: responded_at_ms - received_at_ms,

      total_requests_seen: requestCounter
    });
  } catch (err) {
    const responded_at_ms = Date.now();

    res.status(500).json({
      service: SERVICE_NAME,
      trace_id,
      request_id,
      error: "verifier failed to reach identity service",
      details: err.message,
      received_at_ms,
      responded_at_ms,
      elapsed_ms: responded_at_ms - received_at_ms,
      total_requests_seen: requestCounter
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
