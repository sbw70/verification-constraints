# Deliberately altered laboratory copies

N01_record.json changes record 4's signed boundary value while retaining its signature. N02_record.json changes one signature bit. N03_wrong_anchor.json specifies the original A event and the B trust anchor. N04_summary.json is an unsigned, deliberately false C02 execution summary. N05a_record.json changes only recorder classifications of the valid package. N05b_record.json combines N01's altered package with recorder fields claiming validity.

The fixtures are intentionally invalid or misleading test inputs, not canonical MP003 evidence. Each run's fixture_manifest.json identifies recipes, source record/hash and exact output hashes. The verifier checks or generates these deterministic fixture bytes before evaluating negatives. N03 and N04 have fixed descriptor/summary semantics implemented by the harness; they are not a general-purpose summary-analysis interface.
