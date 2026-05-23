module.exports = {
  apps: [
    {
      name: "phase1-live-comparison-load",
      script: "./scripts/live/run-continuous-comparison.sh",
      interpreter: "bash",
      cwd: "/root/verification-constraints/labs/phase1-separated-services",
      env: {
        BASE_URL: "http://localhost",
        RPS: "20",
        BURST_RPS: "80",
        BURST_SECONDS: "5",
        BURST_EVERY_SECONDS: "60",
        VALID_TOKEN: "admin-token",
        INVALID_TOKEN: "user-token"
      },
      autorestart: true,
      max_restarts: 20,
      restart_delay: 3000
    }
  ]
};
