# Activation Metrics

This directory defines infrastructure activation measurements used throughout the benchmark environment.

Activation metrics exist to measure how much infrastructure participates in request handling before provider-controlled admissibility decisions occur.

Measurements may include:
- systems activated before denial
- application activation events
- gateway activation events
- data-service interaction events
- downstream orchestration depth
- execution chain depth
- stateful infrastructure activation
- intermediary participation

The purpose of activation metrics is to observe how request ordering changes execution behavior before authorization outcomes are known.

These measurements are central to comparing:
- intermediary-first execution
- provider-first admissibility
- downstream activation scope
- execution confinement behavior
