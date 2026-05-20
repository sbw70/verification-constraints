# Workloads

This directory defines the benchmark workload types used throughout the comparison environment.

Workloads exist to ensure both request paths receive equivalent request intent, traffic composition, and execution pressure during testing.

Workload definitions may include:
- valid user requests
- valid administrative requests
- invalid token requests
- expired session requests
- replay attempts
- wrong-scope requests
- wrong-account requests
- mixed valid/invalid traffic
- sustained request streams
- burst traffic scenarios

The purpose of workload definitions is to normalize benchmark traffic so operational differences can be attributed to request ordering rather than inconsistent request behavior.

Both benchmark paths should process equivalent workload patterns whenever possible.
