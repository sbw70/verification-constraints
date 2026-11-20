# Proposed rollback — no network changes made

Before STOP 2 approval, retain a dated cable/port map, complete OPNsense config export,
switch configuration backup, host network settings and service-unit snapshots, and
their hashes. Confirm local console access and an existing management path that does
not depend on the new test VLANs. Record exact physical NIC identities before editing.

If management is lost, application path fails, an existing deployment is affected, or
unexpected routing appears, stop MD001 traffic and preserve logs. Disconnect only
the newly added test cables and stop only MD001 services. Restore host dedicated-link
addresses/routes and previous service settings from snapshots. Do not delete evidence.

From preserved management/console access, remove only newly added MD001 rules,
aliases, interface assignments and VLAN objects in dependency order, then reapply.
If that cannot reliably recover the recorded baseline, restore the reviewed complete
OPNsense backup through System > Configuration > Backups; account for service restart
or reboot needs and verify interface mapping. OPNsense documents the restore workflow
and partial-restore dependencies in its
[backup documentation](https://docs.opnsense.org/manual/backups.html).

Restore switch configuration from its saved backup using the installed firmware's
documented restore workflow. Retain its original management addressing and cable map.
Factory reset is not the default rollback and would require its own approval. If the
UI is inaccessible, use the prearranged local management recovery connection before
considering a reset. Restore original cable placement and verify management access.

Recheck existing MP005/MH001 listener addresses, route selections and services against
the pre-change inventory without invoking their scored executions. Retain actual
rollback commands, UTC times, config hashes, outcomes and unresolved failures in a new
evidence directory. Do not resume MD001 deployment until the operator approves a
revised plan. The exact recovery NIC/address and backup locations remain STOP 2 inputs.
