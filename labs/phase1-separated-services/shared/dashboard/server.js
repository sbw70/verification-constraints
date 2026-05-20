const express = require("express");

const SERVICE_NAME = "shared-dashboard";
const PORT = process.env.PORT || 5101;

const app = express();

app.use(express.json());

app.get("/health", (req, res) => {
  res.json({
    service: SERVICE_NAME,
    status: "ok"
  });
});

app.get("/dashboard", (req, res) => {
  res.json({
    service: SERVICE_NAME,

    benchmark: {
      name: "Provider-First vs Conventional",
      phase: "Phase 1"
    },

    paths: {
      conventional: {
        status: "online"
      },

      provider_first: {
        status: "online"
      }
    },

    metrics: {
      latency_ms: {},
      provider_timing_ms: {},
      activation_depth: {},
      requests_per_second: {}
    }
  });
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
