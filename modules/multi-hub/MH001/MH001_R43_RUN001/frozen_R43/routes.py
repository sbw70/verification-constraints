"""Strict, static MH001 topology. Loading never resolves names or contacts hosts."""
import ipaddress
import json
from pathlib import Path

DESTINATIONS = {"PROVIDER_A", "PROVIDER_B"}
EXPECTED = {"HUB_A": {"PROVIDER_A": "PROVIDER_A", "PROVIDER_B": "HUB_B"},
            "HUB_B": {"PROVIDER_A": "PROVIDER_A", "PROVIDER_B": "PROVIDER_B"}}


def unique(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("duplicate_configuration_key")
        result[name] = value
    return result


def endpoint(value):
    if not isinstance(value, dict) or set(value) != {"host", "port"}:
        raise ValueError("endpoint_fields")
    address = ipaddress.ip_address(value["host"])
    if address.is_unspecified or address.is_multicast or str(address) != value["host"]:
        raise ValueError("endpoint_requires_canonical_unicast_literal")
    if type(value["port"]) is not int or not 1 <= value["port"] <= 65535:
        raise ValueError("endpoint_port")
    return value


def load(path):
    config = json.loads(Path(path).read_bytes(), object_pairs_hook=unique,
                        parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite_json")))
    if not isinstance(config, dict) or set(config) != {"hub_id", "listen", "timeout_seconds", "routes"}:
        raise ValueError("configuration_fields")
    hub = config["hub_id"]
    if hub not in EXPECTED or type(config["timeout_seconds"]) is not int:
        raise ValueError("hub_identity_or_timeout")
    if config["timeout_seconds"] != {"HUB_A": 15, "HUB_B": 10}[hub]:
        raise ValueError("frozen_timeout")
    endpoint(config["listen"])
    if not isinstance(config["routes"], dict) or set(config["routes"]) != DESTINATIONS:
        raise ValueError("exact_routes_required")
    for destination, route in config["routes"].items():
        if not isinstance(route, dict) or set(route) != {"next_hop", "endpoint"}:
            raise ValueError("route_fields")
        if hub == "HUB_B" and route["next_hop"] == "HUB_A":
            raise ValueError("hub_b_to_hub_a_forbidden")
        if route["next_hop"] != EXPECTED[hub][destination]:
            raise ValueError("frozen_route_mismatch")
        if endpoint(route["endpoint"]) == config["listen"]:
            raise ValueError("self_route")
    return config


def validate_pair(a_path, b_path):
    a, b = load(a_path), load(b_path)
    if (a["hub_id"], b["hub_id"]) != ("HUB_A", "HUB_B"):
        raise ValueError("pair_identity")
    addresses = {"HUB_A": a["listen"], "HUB_B": b["listen"]}
    for config in (a, b):
        for route in config["routes"].values():
            name, address = route["next_hop"], route["endpoint"]
            if name in addresses and addresses[name] != address:
                raise ValueError("next_hop_endpoint_inconsistent")
            addresses[name] = address
    if len({(v["host"], v["port"]) for v in addresses.values()}) != 4:
        raise ValueError("node_endpoint_alias_or_loop")
    configs = {"HUB_A": a, "HUB_B": b}
    for start in configs:
        for destination in DESTINATIONS:
            seen, current = set(), start
            while current in configs:
                if current in seen:
                    raise ValueError("routing_loop")
                seen.add(current)
                current = configs[current]["routes"][destination]["next_hop"]
            if current != destination:
                raise ValueError("wrong_terminal_provider")
    return a, b


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("hub_a")
    parser.add_argument("hub_b")
    args = parser.parse_args()
    validate_pair(args.hub_a, args.hub_b)
    print("MH001_ROUTE_PAIR_VALID")
