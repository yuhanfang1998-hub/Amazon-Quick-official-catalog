---
name: agent-builder-kit
display_name: Agent Builder Kit
description: Turn an existing agent definition into a reusable Quick skill, with a ready-made test agent to try it on.
author: Amazon Quick
version: 0.1.0
kind: solution
skills:
  - skills/amazon-quick/agent-to-quick-skill
agents:
  - agents/amazon-quick/yhfang-test-agent
---

# Agent Builder Kit

A **solution** plugin: one install gives you a skill plus an agent that uses it.

## What's included

- **Agent to Quick Skill** (skill): converts an agent into a Quick skill.
- **Yhfang Test Agent** (agent): a sample agent wired to the skill above.
