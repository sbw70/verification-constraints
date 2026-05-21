const express = require("express");

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

  res.json(boundary_event);
});

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on ${PORT}`);
});
