# Traffic Patterns

This directory defines traffic distribution and request arrival behavior used throughout the benchmark environment.

Traffic patterns exist to simulate realistic workload conditions across both request paths.

Traffic definitions may include:
- steady-state traffic
- burst traffic
- sustained invalid traffic
- mixed valid/invalid traffic
- concurrent request waves
- randomized request intervals
- replay bursts
- denial-heavy traffic
- low-volume baseline traffic

The purpose of traffic pattern definitions is to evaluate how request ordering affects operational behavior under different workload conditions.

Both benchmark paths should receive equivalent traffic distributions whenever possible so timing and activation behavior remain directly comparable.
