# Claude Internal Skills Workspace

## Project Intent
This workspace is designed to transform legacy project documentation into 
reusable "Skills" for the team. 

## Operating Principles
1. **Security First**: Never move files out of `docs/raw/` unless they are anonymized.
2. **Evidence-Based**: All AI responses must cite a specific project document from the archive.
3. **Skill-Based Logic**: Use the specialized definitions in `.claude/skills/` for specific tasks.

## Local Workflow
- Use `scripts/parse_docs.py` to prepare raw text for Claude.
- Reference `.claude/skills/` when initializing a new session.