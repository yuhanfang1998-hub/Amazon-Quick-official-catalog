---
name: prior-auth-desk
display_name: Prior Authorization Desk
description: Helps payer and provider teams review prior authorization requests against clinical policy and spot denial patterns.
author: Amazon
version: 0.1.0
kind: solution
icon: assets/icon.svg

# References into the shared skill pool, form <category>/<name>.
skills:
  - healthcare/prior-authorization-clinical-policy
  - healthcare/prior-authorization-decision-automation
  - healthcare/healthcare-claims-analytics
agents:
  - healthcare/prior-auth-reviewer

categories:
  - Healthcare & Life Sciences

# Solution front door: the reviewer agent, which drives the three skills above.
entrypoint:
  type: agent
  ref: healthcare/prior-auth-reviewer
  goal: Check this prior authorization request against our clinical policy and tell me what is missing.

# Connector slots: a purpose plus the connector types that can fill it.
connectors:
  - key: policy-documents
    label: Clinical policy documents
    description: Where your medical policies and coverage criteria are stored.
    types: [MICROSOFT_SHAREPOINT, GOOGLE_DRIVE, BOX, MICROSOFT_ONEDRIVE]
    required: true
  - key: communication
    label: Communication
    description: Where review summaries and appeal letters are sent from.
    types: [MICROSOFT_OUTLOOK, GMAIL, MICROSOFT_TEAMS, SLACK]
    required: false
---

# Prior Authorization Desk

Review prior authorization requests against your clinical policy, find what a
request is missing, and see where denials cluster.

## What's included

- **Prior Auth Reviewer** (agent) — reviews a request end to end and tells you what is missing; start here.
- **Prior Authorization Clinical Policy Reasoning** — check a request against coverage criteria, step therapy and appeal options.
- **Prior Authorization Decision Automation** — turn PA rules into a repeatable review workflow and explain denials.
- **Healthcare Claims Analytics** — screen claims for billing issues and outliers.
