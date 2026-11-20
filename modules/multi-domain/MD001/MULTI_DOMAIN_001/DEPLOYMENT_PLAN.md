# Proposed network deployment — STOP 2, not authorized

No live interface, switch, Pi, or firewall inventory was performed. Addresses and
ports below are exact proposed values, conditional on conflict and capability checks.
They are not claims about existing assignments. `configs/deployment.PROPOSED.json`
is an unapplied design. Exact physical parent NIC names, management addresses,
firmware/UI versions, and available ports remain unresolved approval inputs.

## Inventory before proposing an applicable change

Under a later operator-controlled inspection, export OPNsense configuration and rule
tables; record version, interface names/MACs, current VLANs, assignments, routes,
management path, floating/group/automatic rules, NAT and existing states. Confirm one
unused dedicated trunk-capable NIC; do not repurpose MP005/MH001's active links.
Record GS308Ev4 hardware/firmware, current configuration, cable map, management IP,
802.1Q mode, port capabilities and management-access restrictions. Preserve backups.
On each Linux host record `ip -br address`, `ip -d link`, `ip route show table all`,
`ip -6 route`, `ss -lntup`, firewall configuration and service startup settings.
On Pi record `ls /sys/class/net`, `ip -d link`, `sysctl net.ipv4.ip_forward`,
`sysctl net.ipv6.conf.all.forwarding`, bridge/tunnel interfaces and Wi-Fi routes.
Identify existing deployments and all out-of-band paths before selecting test links.

Operator must retain console access to OPNsense and local switch recovery access.
Inspect address conflicts for 10.77.10/20/30.0/24, routes and VPNs. If any requirement
is unmet, revise this design and present concrete changes before approval.

## Proposed cabling and VLAN membership

Use advanced 802.1Q, not port-based VLAN mode. T = tagged, U = untagged, - = excluded.

| GS308Ev4 port | Connected device | VLAN 1 | VLAN 10 | VLAN 20 | VLAN 30 | PVID |
|---|---|---|---|---|---|---|
| 1 | dedicated OPNsense trunk NIC (name unresolved) | U | T | T | T | 1 |
| 2 | Dell Domain A dedicated Ethernet | - | U | - | - | 10 |
| 3 | Pi relay eth0, one routed subnet | - | - | - | U | 30 |
| 4 | HP Domain B dedicated Ethernet | - | - | U | - | 20 |
| 5 | operator management | U | - | - | - | 1 |
| 6–8 | unused; no cables | U | - | - | - | 1 |

Retain VLAN 1 management addressing after inspection; do not invent a replacement
management subnet. Unused ports remain physically controlled. Retain the existing
management path while staging. Confirm UI reachability only from the intended
operator management interface using supported access controls; do not assume switch
management isolation follows solely from this membership table. If the firmware cannot
provide the needed management boundary, resolve it before deployment. No firmware
upgrade, factory reset, or management renumbering is authorized by this document.

After STOP 2 approval: preserve backups, create VLANs 10/20/30, set trunk membership,
then access-port membership and matching PVIDs; remove access ports from VLAN 1.
Apply one reviewed change at a time and verify management after each. Port 1 carries
untagged VLAN 1 and tagged test VLANs; Linux access ports use untagged Ethernet.
Pi needs only its existing wired interface for the proposed single relay subnet;
it must not bridge or route packets between A and B. Alternate Wi-Fi, USB Ethernet,
VPN and IPv6 paths must be inspected and excluded from test conveyance.
NETGEAR documents advanced 802.1Q membership and PVID configuration in its
[GS308Ev4 manual](https://www.downloads.netgear.com/files/GDC/GS308Ev4/GS308Ev4_UM_EN.pdf).

## OPNsense interfaces, addresses, and rules

On the inspected dedicated trunk parent, propose VLAN10 `MD001_A` 10.77.10.1/24,
VLAN20 `MD001_B` 10.77.20.1/24, VLAN30 `MD001_RELAY` 10.77.30.1/24.
No DHCP or inter-domain NAT is needed. A = 10.77.10.10/24, gateway 10.77.10.1;
B = 10.77.20.10/24, gateway 10.77.20.1; Pi = 10.77.30.10/24, gateway 10.77.30.1.
Provision these only on dedicated approved host links. Preserve existing management.

Create host aliases MD001_A_HOST, MD001_B_HOST, MD001_PI with those /32 addresses.
Proposed inbound interface rules, logged, with unique labels:

| Interface | Action / family / protocol | Source | Destination / port | Label |
|---|---|---|---|---|
| MD001_A | block quick / IPv4 / any | A host | B host / any | MD001_DENY_DIRECT_A_B |
| MD001_A | pass quick / IPv4 / TCP | A host | Pi / 18081 | MD001_ALLOW_A_RELAY |
| MD001_A | block quick / IPv4+IPv6 / any | any | any | MD001_A_DEFAULT_DENY |
| MD001_RELAY | pass quick / IPv4 / TCP | Pi | B / 18443 | MD001_ALLOW_RELAY_B |
| MD001_RELAY | block quick / IPv4+IPv6 / any | any | any | MD001_RELAY_DEFAULT_DENY |
| MD001_B | block quick / IPv4+IPv6 / any | any | any | MD001_B_DEFAULT_DENY |

Return traffic uses firewall connection state; this state is unrelated to artifact
verification state. Preserve existing management rules, add no general A/B internet
access, and enable no ESP path for the baseline. Audit floating/group/automatic rules
that can precede interface rules and check effective order. Remove only matching
MD001 test states before preflight, after review; do not clear unrelated states.
OPNsense's [rule documentation](https://docs.opnsense.org/manual/firewall.html)
describes rule precedence and state behavior. No rule interprets an artifact or verdict.

## Application endpoints and unresolved deployment adapter

Proposed relay `10.77.30.10:18081`: frozen HUB_B implementation. Route selector
PROVIDER_B -> 10.77.20.10:18443. B listens on `/verify`, HTTP/1.1 POST with explicit
Content-Length. Port 18443 is an arbitrary TCP port here, not a TLS claim. The baseline
is isolated lab plaintext to permit external byte reconstruction; adding TLS would
require a revised observation plan. No TLS termination at OPNsense is proposed.

The desktop service binds only loopback. A later reviewed physical adapter must
validate config, bind these exact approved interfaces, restrict routes/methods, retain
public trust provisioning, and assign an unreachable/blocked unused PROVIDER_A route.
Do not use an inapplicable two-hub CLI or modify frozen forwarder source to do this.
There are no deployable live startup commands in this desktop package.

For physical N01, every original artifact must still enter Pi's relay first. Only
after forwarding may a separate downstream B-side test adapter modify outcome and
submit locally to the verifier. It must bind only the approved endpoint and offer no
A-accessible bypass. Its activation/configuration and port placement require STOP 2
review. Preserve the normal B01 path and record any case-specific adapter change.

## Preflight and capture plan, for later approval

Preflight is separate from scored B01/B02/N01. Export effective rules and static
route/config hashes. Once approved listeners and permitted paths exist, use these
connectivity probes with UTC console transcripts:

```sh
# On A: must fail; correlate source/destination/time with the named firewall deny.
nc -vz -w 3 10.77.20.10 18443
# On A: approved relay listener must accept TCP.
nc -vz -w 3 10.77.30.10 18081
# On Pi: approved B listener must accept TCP.
nc -vz -w 3 10.77.20.10 18443
```

TCP probes alone do not establish the application relay path. Send a separately
labeled non-scored verification fixture via the relay; correlate its exact saved body
at producer, external Pi ingress, external Pi egress and B ingress with the two flows.
A failed connection alone does not prove a firewall denial: retain the named rule's
actual denial log including matching tuple and time. Inspect B's listening status so
a closed service cannot masquerade as path enforcement. Retain full console output,
source addresses, rule export and firewall log, and permit-list observations.

On Pi, after confirming its actual interface name, external capture proposal:

```sh
sudo tcpdump -i eth0 -s 0 -U -w MD001_UNIQUE_PREFLIGHT.pcap 'tcp port 18081 or tcp port 18443'
```

Single-interface ingress and egress are distinguished by source/destination/port
tuples. Use a new filename per capture. Account for TCP sequence reassembly,
retransmissions, segmentation and HTTP Content-Length; extract request bodies from
each complete stream, retaining extraction method/tool version, stream IDs, raw body
files, and hashes. Do not hash entire packets or HTTP messages and call them artifact
hashes. If capture offloads, missing segments, encryption or framing prevent reliable
reconstruction, record that limitation and do not award physical B01 PASS. Frozen
relay egress diagnostics alone cannot close this gap. Capture does not alter the relay.

After successful physical network preflight, STOP 3 still requires explicit approval
before scored tests. ESP actuation requires separate approval. No configuration or
probe in this document has been executed on the physical network.
