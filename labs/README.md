# Labs

Experimental testbeds, comparison harnesses, and validation environments for provider-controlled verification constraint architectures.

This directory is separate from the core NUVL reference implementation.

The labs are used to test how the constraint model behaves under different request paths, load profiles, deployment shapes, and operating conditions.

## Lab Types

Labs may include:

- provider-first comparison environments
- simulated request paths
- benchmark and load-mix harnesses
- measurement dashboards
- repeatable validation scenarios
- live control-plane tests
- hardware or endpoint trials
- deferred, delayed, or disconnected-client tests
- local-network experiments
- future research and development testbeds

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

Labs are research and development environments.

They are not production deployment instructions, formal benchmarks, certifications, or claims that every implementation will produce the same measurements.
