# Checks performed during publication staging

This directory holds post-score publication checks, classified as preflight/reproduction rather than a new scored campaign. The portable nine-test suite and a full verifier replay are run from the staging root. Original preflight/scored evidence, source artifacts, frozen configs and verifier implementation remain unchanged.

publication_audit.json records copy/hash checks and the later replay result. These checks do not retroactively add new cases or claims to the original scored run.
