#!/usr/bin/env python3
# Copyright 2026 Seth Brian Wells
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Artist hub config validator.

Checks a config file for completeness and correctness before the artist
goes live. Run manually or as a pre-live gate.

Usage:
    python validate_config.py configs/my-act.json
    python validate_config.py --all          # validate every file in configs/
"""

import json
import os
import sys

CONFIGS_DIR = os.path.join(os.path.dirname(__file__), "configs")
EXPECTED_SCHEMA = "artist-hub-v1"


# ------------------------------------------------------------------
# Rules
# ------------------------------------------------------------------

def _check(errors, condition, message):
    if not condition:
        errors.append(message)


def validate(config: dict) -> list[str]:
    """Return a list of error strings. Empty list means valid."""
    errors = []

    # Schema
    _check(errors, config.get("_schema") == EXPECTED_SCHEMA,
           f"_schema must be '{EXPECTED_SCHEMA}'")

    # Identity
    _check(errors, bool(config.get("artist_name", "").strip()),
           "artist_name is required")
    _check(errors, bool(config.get("act_name", "").strip()),
           "act_name is required")

    # Contact
    email = config.get("contact_email", "")
    _check(errors, "@" in email and "." in email.split("@")[-1],
           "contact_email is missing or invalid")

    # URLs
    music_url = config.get("music_url", "")
    _check(errors,
           music_url.startswith("http://") or music_url.startswith("https://"),
           "music_url must be a full URL starting with http:// or https://")

    # Tickets
    price = config.get("ticket_price_usd")
    _check(errors, isinstance(price, (int, float)) and price >= 0,
           "ticket_price_usd must be a non-negative number")

    qty = config.get("ticket_quantity")
    _check(errors, isinstance(qty, int) and qty >= 1,
           "ticket_quantity must be an integer >= 1")

    limit = config.get("purchase_limit_per_fan")
    _check(errors, isinstance(limit, int) and limit >= 1,
           "purchase_limit_per_fan must be an integer >= 1")

    if isinstance(qty, int) and isinstance(limit, int) and qty >= 1 and limit >= 1:
        _check(errors, limit <= qty,
               "purchase_limit_per_fan cannot exceed ticket_quantity")

    # Refund policy
    _check(errors, bool(config.get("refund_policy", "").strip()),
           "refund_policy is required")

    # Payments — required before going live
    stripe = config.get("stripe_account_id", "")
    _check(errors, stripe.startswith("acct_"),
           "stripe_account_id is missing or invalid (must start with 'acct_')")

    # Fee sanity
    fee = config.get("platform_fee_pct")
    _check(errors, isinstance(fee, (int, float)) and 0 <= fee <= 100,
           "platform_fee_pct must be a number between 0 and 100")

    # Hub ID
    hub_id = config.get("hub_id", "")
    _check(errors, hub_id.startswith("HUB_") and len(hub_id) > 4,
           "hub_id is missing or malformed (assigned by bot at registration)")

    return errors


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def validate_file(path: str) -> bool:
    """Validate one file. Print results. Return True if valid."""
    try:
        with open(path) as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"  FAIL  {path}")
        print(f"        Could not read file: {e}")
        return False

    errors = validate(config)
    act = config.get("act_name") or os.path.basename(path)

    if errors:
        print(f"  FAIL  {act}  ({path})")
        for err in errors:
            print(f"        - {err}")
        return False
    else:
        active = config.get("active", False)
        status = "live" if active else "ready (not yet live)"
        print(f"  OK    {act}  [{status}]")
        return True


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    if args == ["--all"]:
        if not os.path.isdir(CONFIGS_DIR):
            print(f"No configs/ directory found at {CONFIGS_DIR}")
            sys.exit(1)
        files = [
            os.path.join(CONFIGS_DIR, f)
            for f in sorted(os.listdir(CONFIGS_DIR))
            if f.endswith(".json")
        ]
        if not files:
            print("No config files found.")
            sys.exit(0)
    else:
        files = args

    print()
    results = [validate_file(p) for p in files]
    print()

    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"All {total} config(s) valid.")
        sys.exit(0)
    else:
        print(f"{total - passed} of {total} config(s) failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
