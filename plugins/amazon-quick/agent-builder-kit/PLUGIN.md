---
name: agent-builder-kit
display_name: Agent Builder Kit
description: Turn an existing agent definition into a reusable Quick skill, with a ready-made test agent to try it on.
author: Amazon Quick
version: 0.1.0
kind: solution
icon: assets/icon.svg

# References into the shared pools, form <category>/<name>.
skills:
  - amazon-quick/agent-to-quick-skill
agents:
  - amazon-quick/yhfang-test-agent

categories:
  - Amazon Quick

# Solution front door; must be one of this plugin's own children.
entrypoint:
  type: agent
  ref: amazon-quick/yhfang-test-agent
  goal: Turn my agent definition into a reusable Quick skill.
---

# Agent Builder Kit

Everything you need to turn an existing agent definition into a reusable Amazon
Quick skill — plus a ready-made agent to try it on.

## What's included

- **Agent to Quick Skill** — converts an agent definition into a Quick skill you
  can run and share.
- **Yhfang Test Agent** — a sample agent wired to the skill above, so you can see
  the conversion end to end right after installing.
