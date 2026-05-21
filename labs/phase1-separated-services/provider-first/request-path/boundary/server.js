const express = require("express");
const axios = require("axios");

const SERVICE_NAME = "provider-first-boundary";
const PORT = process.env.PORT || 4101;

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.post("/boundary-check", async (req, res) => {

  const started_at_ms = Date.now();

  const trace = [
    "provider-first-boundary"
  ];

  const {
    trace_id,
    request_id,
    token,
    action,
    resource
  } = req.body;

  const boundary_event = {
    service: SERVICE_NAME,
    trace_id,
    request_id,
    boundary_checked: true,
    token_present: !!token,
    action,
    resource
  };

  try {

    const verifierResponse = await axios.post(
      "http://provider-first-verifier:4102/verify",
      {
        trace_id,
        request_id,
        token_type:
          token === "admin-token"
            ? "valid_admin"
            : token === "user-token"
              ? "valid_user"
              : "invalid_token",

        action,
        resource
      }
    );

    const verifier_returned_at_ms = Date.now();

    trace.push("provider-first-verifier");

    res.json({
      boundary_event,
      verifier_response: verifierResponse.data,
      trace,
      started_at_ms,
      verifier_returned_at_ms,
      total_elapsed_ms:
        verifier_returned_at_ms - started_at_ms
    });

  } catch (err) {

    res.status(500).json({
      service: SERVICE_NAME,
      error: "verifier_forward_failed",
      details: err.message
    });

  }

});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
