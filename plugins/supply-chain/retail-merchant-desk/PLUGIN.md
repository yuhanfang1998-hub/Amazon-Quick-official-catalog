---
name: retail-merchant-desk
display_name: Retail Merchant Desk
description: Runs a retail merchant's week from one place -- the Monday performance briefing, daily supply chain exceptions, and answers from sales data.
author: Amazon
version: 0.1.0
kind: solution
icon: assets/icon.svg

# References into the shared pools, form <category>/<name>.
skills:
  - data-analytics/retail-merchant-briefing
  - supply-chain/retail-supply-chain-pulse
  - supply-chain/demand-forecast-explainer
  - data-analytics/retail-analytics-concierge
agents:
  - supply-chain/retail-merchant-assistant

categories:
  - Supply Chain & Logistics

# Solution front door: the merchant agent, which drives the four skills above.
entrypoint:
  type: agent
  ref: supply-chain/retail-merchant-assistant
  goal: Give me my Monday briefing.

# Connector slots: a purpose plus the connector types that can fill it.
connectors:
  - key: sales-data
    label: Sales and inventory data
    description: Where your sales, inventory and forecast tables live.
    types: [SNOWFLAKE, AMAZON_REDSHIFT, AMAZON_S3]
    required: true
  - key: team-channel
    label: Team channel
    description: Where the briefing and exception digest are posted.
    types: [SLACK, MICROSOFT_TEAMS]
    required: false
---

# Retail Merchant Desk

Run the merchandising week from one place: a Monday briefing that says what needs a
decision, a daily digest of supply chain exceptions, and plain-English answers from
your sales data.

## What's included

- **Retail Merchant Assistant** (agent) — start here; it picks the right skill for the question.
- **Merchant Monday Briefing** — weekly performance with recommended actions.
- **Supply Chain Morning Pulse** — daily exceptions by severity, with root cause.
- **Demand Forecast Explainer** — why a forecast moved, in plain English.
- **Self-Service Analytics Concierge** — ask a question, get the query and the chart.
