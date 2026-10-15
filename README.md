# Amazon Quick Official Catalog

The Amazon Quick Official Catalog provides reusable agent skills for [Amazon Quick](https://aws.amazon.com/quick/) on desktop. Each skill packages instructions, validation steps, and supporting files for a specific task, so you can install an existing workflow instead of explaining or rebuilding it in every conversation.

Learn more about the [Amazon Quick skill catalog](https://amazon-quick.github.io/Amazon-Quick-official-catalog) where you can find skills for productivity, sales, marketing, legal work, financial services, healthcare and life sciences, energy and utilities, and other areas.

## Documentation

The documentation explains how skills work, how to install them, and how to build skills that other people can use.

- [What are skills in Amazon Quick?](https://amazon-quick.github.io/Amazon-Quick-official-catalog/getting-started/)
- [Install skills in Amazon Quick on desktop](https://amazon-quick.github.io/Amazon-Quick-official-catalog/install/)
- [Browse the Amazon Quick skill catalog](https://amazon-quick.github.io/Amazon-Quick-official-catalog/skill-catalog/)
- [Build skills with software engineering practices](https://amazon-quick.github.io/Amazon-Quick-official-catalog/build-skills/)

[![License](https://img.shields.io/badge/license-MIT--0-blue.svg)](LICENSE)

## Contributing

To report a problem or request a skill, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Official agents

Alongside skills, the catalog can ship ready-to-use **agents**. An official
agent is a local, read-only agent (the same install model as official skills):
installing one writes the agent definition into the user's directory and nothing
is created server-side, so it stays maintained by us and is not editable by the
customer.

### Layout

One directory per agent:

```
agents/{category}/{name}/
  agent.json          # required — the agent definition
  assets/icon.svg     # optional — the agent icon (SVG only, <= 5 KB)
```

`agent.json` is the app's **Agent Export JSON** plus three catalog-only fields
(`schema_version`, `author`, `icon`). Its shape and limits are defined by
[`agent.schema.json`](agent.schema.json):

| Field | Rule |
|---|---|
| `schema_version` | must be `1` |
| `name` | 1–50 chars |
| `description` | 1–1000 chars |
| `system_prompt` | 5–50,000 chars |
| `welcome_message` | ≤ 300 chars |
| `starter_prompts` | ≤ 3, each ≤ 100 chars |
| `capabilities` | e.g. `["WEB_SEARCH"]` |
| `skills` | official skills from this catalog, by `{category}/{name}` path (no ids) |
| `author` / `icon` | optional; `icon` is a path to an SVG under `assets/` |
| `connectors` / `spaces` / `files` | must be `[]` in v1 |

### Adding an agent

1. **Build and export.** Build the agent in Amazon Quick, then export it as JSON.
2. **Clean the exported fields.** Remove every environment-specific id — the
   export's `connectors`, `spaces` and `files` hold account-specific ARNs/ids
   and must be emptied (`[]`) for v1. No field may contain an ARN or a UUID.
3. **Reference skills by path, not id.** List each required skill in `skills`
   by its catalog path, e.g. `"amazon-quick/agent-to-quick-skill"`. The skill
   must already be published in this catalog.
4. **Add the three catalog fields.** Set `schema_version: 1`, an `author`, and
   (optionally) an `icon` pointing to `assets/icon.svg`.
5. **Register it in `catalog.json`.** Add an asset entry under the right
   category: `{ "path": "agents/{category}/{name}", "type": "agent",
   "checksum": "sha256:..." }`.
6. **Regenerate checksums and validate:**

   ```bash
   uv run python -m scripts.skills_checksum          # fills in the checksum
   uv run python -m scripts.agents_validate          # validates the agent
   uv run python -m scripts.skills_checksum --check   # verifies checksums
   ```

CI runs the same checks (plus the schema and the validator tests) on every
change — see [`.github/workflows/validate.yml`](.github/workflows/validate.yml).

## License

This repository is licensed under MIT-0. For details, see the [LICENSE](LICENSE) file.
