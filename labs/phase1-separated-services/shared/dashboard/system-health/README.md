# System Health

This directory contains infrastructure health and operational status visualization components for the benchmark environment.

System health monitoring exists to provide visibility into the operational state of benchmark services during execution.

Displayed information may include:
- service availability
- process status
- connectivity state
- request failures
- timeout frequency
- CPU utilization
- memory utilization
- service restart events
- load conditions

The purpose of the system health layer is to distinguish benchmark behavior from infrastructure instability during testing.

This layer is shared so both request paths are evaluated under the same operational monitoring conditions.
