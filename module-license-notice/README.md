# Licensing Structure and Scope

This repository contains components subject to different licensing terms.

The Apache License, Version 2.0 located at the repository root applies **only** to:

- The `nuvl-core/` directory; and
- Any file that explicitly includes an Apache 2.0 license header.

No other directories, modules, demonstrations, extensions, or bundled builds are covered by the Apache License unless an Apache 2.0 header is explicitly present in the file.

---

## Proprietary Modules

All modules not explicitly marked with an Apache 2.0 header — including, but not limited to, directories under `/modules/` and designated demo or extension builds — are proprietary works.

These components are not released under the Apache License.

No license is granted for:

- Commercial use  
- Redistribution  
- Modification or derivative works  
- Production deployment  
- Patent rights  

except pursuant to a separate written commercial agreement.

---

## Research Evaluation

Limited, non-commercial research evaluation licenses may be available upon request.

No rights are granted by default.

---

## Controlling Terms

License scope is determined exclusively by the presence of an explicit license header within an individual file.

A file is licensed under Apache 2.0 only if it carries a full, unqualified Apache 2.0 grant — for example, an `SPDX-License-Identifier: Apache-2.0` line, or the complete Apache 2.0 header with no added restrictions.

A file carrying a mixed or qualified notice — for example, one stating that certain components are Apache-licensed while the remaining logic is proprietary — is governed by the specific terms written in that file, not by Apache 2.0 as a whole.

A file with no license header grants no license.

For commercial licensing inquiries or evaluation requests, contact the repository owner.

## Challenge Demonstration Evaluation

This section is an exception to the proprietary and research-evaluation
restrictions above. It applies only to these files when they carry a header
expressly referring to this section:

- `nuvl-demos/nuvl-challenge/provider/provider.py`
- `nuvl-demos/nuvl-challenge/client/client.py`
- `nuvl-demos/nuvl-challenge/mint_token.py`
- `nuvl-demos/nuvl-challenge/attacker/attacker.py`

Individuals and organizations may copy, run, and modify these files solely for
local, noncommercial evaluation in test environments they control. No separate
research license is required for that evaluation. Internal technical evaluation
to decide whether to obtain a commercial license is permitted; production use,
commercial deployment, and providing the software as a service are not.

This permission includes only such patent rights controlled by the repository
owner as are necessary for that permitted evaluation of the listed files. It
does not grant patent rights for commercial implementation, production use, or
implementation of other proprietary modules.

Redistribution of these files or modified versions, and uses outside this
evaluation permission, require a separate written agreement. This permission
does not authorize testing systems controlled by others or replace any
separately agreed live-challenge permissions.

These files remain proprietary and are not released under Apache 2.0. They are
provided as is, without warranties, to the extent permitted by applicable law.
This permission creates no obligation to provide support, integration, or updates.

The core's Apache 2.0 license and the terms for all other components are unchanged.
