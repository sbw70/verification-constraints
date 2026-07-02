# Labs

Experimental testbeds, comparison harnesses, and validation environments for provider-controlled verification constraint architectures.

This directory is separate from the core NUVL reference implementation.

The labs are used to evaluate where denial occurs, what activates before denial, and whether provider-controlled authority remains inside the provider boundary.

## Lab Types

Labs may include:

- comparison harnesses
- simulated enterprise request paths
- provider-first benchmark environments
- measurement dashboards
- repeatable test scenarios
- control-plane validation environments

## Provider-First Comparison

The provider-first comparison evaluates request ordering.

The comparison is not about blocking more requests. It is about where denial happens and what activates before denial.

Measured observations may include:

- earlier denial in the provider-first path
- reduced downstream activation before denial
- zero database touches before denial in the provider-first design
- lower latency under the tested path
- lower CPU load under the tested path

Exact values belong in dated reports, screenshots, dashboards, or specific lab notes rather than this top-level README.

## Scope

Labs are experimental validation environments.

They are not production deployment instructions, formal benchmarks, or claims that every implementation will produce the same measurements.
