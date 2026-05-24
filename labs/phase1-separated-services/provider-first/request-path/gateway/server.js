const express = require("express");
const axios = require("axios");

let requestCounter = 0;

const SERVICE_NAME = "provider-first-gateway";
const PORT = process.env.PORT || 4103;

const BOUNDARY_URL =
  process.env.BOUNDARY_URL ||
  "http://provider-first-boundary:4101/boundary-check";

const APP_URL =
  process.env.APP_URL ||
  "http://provider-first-app:4104/execute";

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok",
    requests_seen: requestCounter
  });
});

app.post("/gateway", async (req, res) => {
  requestCounter++;

  const gateway_received_at_ms = Date.now();

  const {
    trace_id,
    request_id,
    token,
    action,
    resource
  } = req.body;

  const trace = [SERVICE_NAME];

  try {
    const gateway_forwarded_at_ms = Date.now();

    const boundaryResponse = await axios.post(BOUNDARY_URL, {
      trace_id,
      request_id,
      token,
      action,
      resource,
      trace
    });

    const verifierDecision =
      boundaryResponse.data.verifier_response;

    if (!verifierDecision.allowed) {
      const gateway_responded_at_ms = Date.now();

      return res.status(403).json({
        service: SERVICE_NAME,
        path: "provider-first",

        trace_id,
        request_id,

        allowed: false,
        denied: true,
        reason: verifierDecision.reason,

        token_type: verifierDecision.token_type,

        forwarded_to_boundary: true,
        downstream_execution: false,
        denied_before_app: true,
        provider_decision_seen: true,

        gateway_received_at_ms,
        gateway_forwarded_at_ms,
        gateway_responded_at_ms,
        gateway_elapsed_ms:
          gateway_responded_at_ms - gateway_received_at_ms,

        total_requests_seen: requestCounter,

        activated_components:
          boundaryResponse.data.activated_components,

        boundary_response: boundaryResponse.data,
        app_response: null
      });
    }

    const appResponse = await axios.post(APP_URL, {
      trace_id,
      request_id,
      token,
      token_type: verifierDecision.token_type,
      action,
      resource,
      trace: boundaryResponse.data.activated_components
    });

    const gateway_responded_at_ms = Date.now();

    res.status(200).json({
      service: SERVICE_NAME,
      path: "provider-first",

      trace_id,
      request_id,

      allowed: true,
      denied: false,
      reason: verifierDecision.reason,

      token_type: verifierDecision.token_type,

      forwarded_to_boundary: true,
      downstream_execution: true,
      denied_before_app: false,
      provider_decision_seen: true,

      gateway_received_at_ms,
      gateway_forwarded_at_ms,
      gateway_responded_at_ms,
      gateway_elapsed_ms:
        gateway_responded_at_ms - gateway_received_at_ms,

      total_requests_seen: requestCounter,

      activated_components:
        appResponse.data.activated_components,

      boundary_response: boundaryResponse.data,
      app_response: appResponse.data
    });
  } catch (err) {
    res.status(500).json({
      service: SERVICE_NAME,
      path: "provider-first",
      error: "gateway failed",
      details: err.message,
      total_requests_seen: requestCounter
    });
  }
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
