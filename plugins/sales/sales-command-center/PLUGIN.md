---
name: sales-command-center
display_name: Sales Command Center
description: Keeps a seller's pipeline current and their follow-ups on time.
author: Amazon
version: 0.1.0
kind: solution
icon: assets/icon.svg

# References into the shared skill pool, form <category>/<name>.
skills:
  - sales/deal-pipeline-manager
  - sales/follow-up-cadence
  - sales/lead-prospector
agents:
  - sales/sales-assistant

categories:
  - Sales

# Solution front door; must be one of this plugin's own children.
entrypoint:
  type: agent
  ref: sales/sales-assistant
  goal: Review my pipeline and draft the follow-ups I owe.

# Connector slots: a purpose plus the connector types that can fill it.
connectors:
  - key: crm
    label: CRM
    description: Where your opportunities, accounts and contacts live.
    types: [SALESFORCE_CRM, SALESFORCE]
    required: false
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
