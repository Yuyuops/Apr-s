# Architecture MVP

## Pipeline

`Official source -> ingestion -> atomic measures -> Policy Compiler -> validation -> capability audit -> simulation`

The compiler does not predict outcomes by itself. It produces typed policy objects and identifies which simulation capabilities are required.

## Layers

1. **Source layer** — immutable source metadata and excerpts.
2. **Policy layer** — normalized action, target, value, timing and prerequisites.
3. **Institutional graph** — institutions, competences, treaties and transfers.
4. **Simulation layer** — public finance, households, macroeconomy, environment and sector modules.
5. **Scenario layer** — uncertain or externally dependent consequences.
6. **Presentation layer** — time slider and uncertainty ranges.

## Core rule

A missing causal model is a capability gap, not permission to invent a coefficient.
