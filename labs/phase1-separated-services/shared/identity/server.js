const express = require("express");

const SERVICE_NAME = "shared-identity";
const PORT = process.env.PORT || 3101;

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.post("/validate-token", (req, res) => {
  const { token } = req.body;

  let result = {
    valid: false,
    token_type: "invalid_token",
    subject: null,
    role: null,
    reason: "unrecognized token"
  };

  if (token === "user-token") {
    result = {
      valid: true,
      token_type: "valid_user",
      subject: "user_001",
      role: "user",
      reason: "valid user token"
    };
  }

  if (token === "admin-token") {
    result = {
      valid: true,
      token_type: "valid_admin",
      subject: "admin_001",
      role: "admin",
      reason: "valid admin token"
    };
  }

  if (token === "expired-token") {
    result = {
      valid: false,
      token_type: "expired_token",
      subject: null,
      role: null,
      reason: "token expired"
    };
  }

  res.json({
    service: SERVICE_NAME,
    ...result
  });
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
