# IVADO Labs: A/B Test Analyst Skill

This repository contains an executable "Skill" for Claude (VSC Extension or Claude Code) designed to standardize A/B test analysis according to internal IVADO Labs statistical methodologies.

## Overview
The **A/B Test Analyst Skill** automates the analysis of experiment data.

## Project Structure
- `.claude/skills/`: Contains the core behavioral instructions for the AI.
- `docs/templates/`: The Source of Truth (Methodology) sourced from Confluence.
- `docs/raw/test_fixtures/`: Standardized datasets for validation and benchmarking.
- `output/`: The default directory for AI-generated Markdown reports.

## How to Use
To activate the skill in a fresh VS Code Claude session:

1. **Initialize the Context:**
   Mention the skill and methodology files to prime the AI:
   > "Initialize your role using `@ab_test_specialist.md` and adhere to `@ab_analysis_methodology.md`."

2. **Provide Data:**
   Upload or mention your CSV file:
   > "Perform a full analysis on `@your_data.csv`."

3. **Retrieve Report:**
   The Skill will automatically calculate ATE, P-values, and CIs, and save a formatted report to the `/output` folder.
