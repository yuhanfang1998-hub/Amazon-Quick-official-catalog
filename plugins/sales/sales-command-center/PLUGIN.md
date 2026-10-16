---
# ── existing keys, unchanged ───────────────────────────────────────────
name: sales-command-center
display_name: Sales Command Center
description: Keeps a seller's pipeline current and their follow-ups on time.
author: Amazon Quick
version: 0.1.0
kind: solution                 # solution | package | partner
icon: assets/icon.svg

# Children are REFERENCES into the shared pools. Never copies -- a plugin
# directory holds a manifest and its icon, nothing else.
# Form is <category>/<name>; the key already says the type.
skills:
  - sales/deal-pipeline-manager
  - sales/follow-up-cadence
  - sales/lead-prospector
agents:
  - amazon-quick/yhfang-test-agent

# ── NEW: subject shelves ──────────────────────────────────────────────
# A list, from catalog.json's category names. Validated against that set.
# Distinct from `kind`, which is a publisher tier, not a subject.
categories:
  - Sales

# ── NEW: the front door ───────────────────────────────────────────────
# Required when kind: solution. Forbidden on package and partner.
# `ref` MUST be one of this plugin's own children, above.
entrypoint:
  type: agent                  # agent | skill
  ref: amazon-quick/yhfang-test-agent
  goal: Review my pipeline and draft the follow-ups I owe.

# ── NEW: what the customer must answer before this plugin can exist ──
# A slot names a PURPOSE and the connector types that satisfy it --
# never a specific connector, which only the customer's account knows.
connectors:
  - key: communication
    label: Communication
    description: Where follow-ups are sent from.
    types: [GMAIL, MICROSOFT_OUTLOOK, SLACK]
    required: true
---

# Sales Command Center

Keeps your pipeline current and your follow-ups on time.

## What's included

- **Deal Pipeline Manager** — review deal stages and spot stalled opportunities.
- **Follow-up Cadence** — plan and track outreach follow-ups.
- **Lead Prospector** — find and qualify new leads.
