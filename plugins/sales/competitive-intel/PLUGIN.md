---
name: competitive-intel
display_name: Competitive Intel
description: Research competitors on the web and get a cited comparison, a SWOT and, when you need one, a business case -- no setup or connectors needed.
author: Amazon
version: 0.1.0
kind: solution
icon: assets/icon.svg

# References into the shared pools, form <category>/<name>.
skills:
  - sales/competitor-intel
  - leadership/swot-analysis-generator
  - leadership/business-case-builder
agents:
  - sales/market-analyst

categories:
  - Sales

# Solution front door: the analyst agent, which drives the three skills above.
entrypoint:
  type: agent
  ref: sales/market-analyst
  goal: Compare Notion and Confluence for a 50-person engineering team, then give me a SWOT.
---

# Competitive Intel

Name the products or companies you care about and get back research you can act on:
a side-by-side comparison with sources, a SWOT, and a business case when a decision
is on the table. Everything comes from the web -- no connectors to set up.

## What's included

- **Market Analyst** (agent) — start here; it chains the skills for you.
- **Competitor Intel** — researches positioning, pricing and features, with sources.
- **SWOT Analysis Generator** — strengths, weaknesses, opportunities, threats, and the strategies that follow.
- **Business Case Builder** — a decision-ready case for an initiative.
