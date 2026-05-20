const express = require("express");

const SERVICE_NAME = "conventional-provider-adapter";
const PORT = process.env.PORT || 3104;

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.post("/provider-check", (req, res) => {
  const {
    trace_id,
    request_id,
    token_type,
    action,
    resource
  } = req.body;

  let allowed = false;
  let reason = "not allowed";

  if (token_type === "valid_admin") {
    allowed = true;
    reason = "admin token allowed";
  }

  if (token_type === "valid_user" && action === "profile:read") {
    allowed = true;
    reason = "user profile read allowed";
  }

  res.json({
    service: SERVICE_NAME,
    trace_id,
    request_id,
    provider_decision_seen: true,
    allowed,
    denied: !allowed,
    reason,
    action,
    resource
  });
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
