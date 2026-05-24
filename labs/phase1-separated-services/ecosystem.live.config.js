module.exports = {
  apps: [
    {
      name: "phase1-live-comparison",
      script: "./scripts/start-live-comparison.sh",
      cwd: __dirname,
      interpreter: "bash",
      autorestart: true,
      watch: false,
      max_restarts: 20,
      restart_delay: 5000,
      env: {
        NODE_ENV: "production",
        SLEEP_SECONDS: "2",
        SERVICE_WAIT_SECONDS: "5"
      }
    }
  ]
};
