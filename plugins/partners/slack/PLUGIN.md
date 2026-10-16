---
name: slack
display_name: Slack
description: Search your Slack workspace and write clear, well-formatted Slack messages.
author: Slack
version: 0.1.0
kind: partner
icon: assets/icon.svg

# References into the shared skill pool, form <category>/<name>.
skills:
  - partners/slack-messaging
  - partners/slack-search
agents: []

categories:
  - Partners

connectors:
  - key: workspace
    label: Slack workspace
    description: The Slack workspace to search and post in.
    types: [SLACK]
    required: true
---

# Slack

Search your Slack workspace and write messages people actually read, published by Slack.

## What's included

- **Slack Search** — find messages, files, channels, and people.
- **Slack Messaging** — write clear, well-formatted messages, announcements, and canvases.
