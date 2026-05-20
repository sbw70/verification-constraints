const express = require("express");

const SERVICE_NAME = "shared-load-generator";
const PORT = process.env.PORT || 5201;

const app = express();

app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.post("/generate", (req, res) => {

  const request = {
    trace_id: `trace_${Date.now()}`,
    request_id: `req_${Date.now()}`,

    token: "user-token",
    token_type: "valid_user",

    action: "profile:read",
    resource: "acct_001",

    payload: {
      message: "generated request"
    }
  };

  res.json({
    service: SERVICE_NAME,
    generated: true,
    request
  });
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
