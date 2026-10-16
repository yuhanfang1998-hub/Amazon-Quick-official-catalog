---
name: engineering
display_name: Engineering
description: "A senior-engineer partner for everyday work -- system design, architecture decisions, debugging, incident response and test plans -- that can draft your status email. Adapted from Anthropic's Engineering plugin: https://github.com/anthropics/knowledge-work-plugins/tree/main/engineering"
author: Anthropic
version: 0.1.0
kind: solution
icon: assets/icon.svg

# References into the shared pools, form <category>/<name>.
skills:
  - software-engineering/engineering-system-design
  - software-engineering/engineering-architecture-decision
  - software-engineering/engineering-debug
  - software-engineering/engineering-incident-response
  - software-engineering/engineering-testing-strategy
agents:
  - software-engineering/engineering-assistant

categories:
  - Software Engineering

# Solution front door: the engineering agent, which drives the five skills above.
entrypoint:
  type: agent
  ref: software-engineering/engineering-assistant
  goal: "We have an incident: checkout latency jumped to 5s after today's deploy. Help me triage it."

# Connector slots: a purpose plus the connector types that can fill it.
connectors:
  - key: status-email
    label: Status updates by email
    description: Drafts incident and status update emails for you to review and send.
    types: [MICROSOFT_OUTLOOK, GMAIL]
    required: false
---

# Engineering

A senior-engineer partner for the work you do every day. Describe the problem in
the chat; no files or setup needed.

## What's included

- **Engineering Assistant** (agent) — start here; it picks the right skill for the request.
- **System Design** — requirements, architecture, components and trade-offs.
- **Architecture Decision** — compare options and write the ADR.
- **Structured Debugging** — reproduce, isolate, diagnose, fix.
- **Incident Response** — triage, status updates, blameless postmortem.
- **Testing Strategy** — what to test at each level.

With an Outlook or Gmail connector, the assistant drafts status emails for you to
review and send; it never sends on its own.

Adapted from Anthropic's open-source Engineering plugin (Apache-2.0); see each skill's README.
