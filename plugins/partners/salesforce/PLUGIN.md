---
name: salesforce
display_name: Salesforce
description: Pipeline and deal-management workflows for teams that run sales in Salesforce.
author: Salesforce
version: 0.1.0
kind: partner
icon: assets/icon.svg

# References into the shared skill pool, form <category>/<name>.
skills:
  - sales/deal-pipeline-manager
  - sales/competitor-intel
agents: []

categories:
  - Sales

connectors:
  - key: crm
    label: CRM
    description: The Salesforce org your pipeline lives in.
    types: [SALESFORCE_CRM]
    required: true
---

# Salesforce

Pipeline and deal-management workflows for teams that run their sales in
Salesforce, published by Salesforce.

## What's included

- **Deal Pipeline Manager** — keep your pipeline current and moving.
- **Competitor Intel** — pull together competitive intelligence for a deal.
