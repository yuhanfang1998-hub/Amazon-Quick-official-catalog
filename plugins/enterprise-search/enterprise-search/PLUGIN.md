---
name: enterprise-search
display_name: Enterprise Search
description: "Ask questions about your work and get one sourced answer from your email, documents and chat -- plus a daily or weekly digest. Adapted from Anthropic's Enterprise Search plugin: https://github.com/anthropics/knowledge-work-plugins/tree/main/enterprise-search"
author: Anthropic
version: 0.1.0
kind: solution
icon: assets/icon.svg

# References into the shared pools, form <category>/<name>.
skills:
  - enterprise-search/enterprise-search
  - enterprise-search/enterprise-digest
  - enterprise-search/enterprise-search-strategy
  - enterprise-search/enterprise-knowledge-synthesis
  - enterprise-search/enterprise-source-management
agents:
  - enterprise-search/workplace-search-assistant

categories:
  - Enterprise Search

# Solution front door: the search agent, which drives the five skills above.
entrypoint:
  type: agent
  ref: enterprise-search/workplace-search-assistant
  goal: Give me my digest for today.

# Connector slots: a purpose plus the connector types that can fill it. All
# optional -- the agent searches whatever is connected.
connectors:
  - key: email
    label: Email
    description: Where to search your mail.
    types: [MICROSOFT_OUTLOOK, GMAIL]
    required: false
  - key: documents
    label: Documents
    description: Where to search your files.
    types: [MICROSOFT_SHAREPOINT, MICROSOFT_ONEDRIVE, GOOGLE_DRIVE, BOX]
    required: false
  - key: chat
    label: Chat
    description: Where to search your team conversations.
    types: [SLACK, MICROSOFT_TEAMS]
    required: false
---

# Enterprise Search

Ask a question the way you would ask a colleague -- "what did we decide about the
launch date?" -- and get one answer drawn from your email, documents and chat, with
a link to where each part came from. Or ask for a digest to catch up on the day.

## What's included

- **Workplace Search Assistant** (agent) — start here.
- **Workplace Search** — one question, every connected source.
- **Workplace Digest** — daily or weekly catch-up.
- **Search Strategy**, **Knowledge Synthesis**, **Source Management** — how the search is planned, merged and kept to the sources you have.

Adapted from Anthropic's open-source Enterprise Search plugin (Apache-2.0); see each skill's README.
