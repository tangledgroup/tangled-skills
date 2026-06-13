# Templates

## Contents
- SKILL.md Template (Simple)
- SKILL.md Template (Complex)
- Reference File Template
- Optional Sections

---

## SKILL.md Template (Simple)

Use when the topic is conceptual, single-domain, or has no natural subtopic split.

```markdown
---
name: <skill-name>
description: <specific description with WHAT and WHEN>
---

# <Project Name> <Version>

## Overview

Brief description of what the project/tool does and its primary use cases.

## When to Use

Clear guidance on when this skill should be invoked. Include specific scenarios.

## Core Concepts

Key concepts, terminology, and fundamental ideas related to the topic.
```

## SKILL.md Template (Complex)

Use when content has 2+ distinct subtopics and an agent would only need 1–2 reference files per task.

```markdown
---
name: <skill-name>
description: <specific description with WHAT and WHEN>
---

# <Project Name> <Version>

## Overview

Brief description of what the project/tool does and its primary use cases.

## When to Use

Clear guidance on when this skill should be invoked. Include specific scenarios.

## Core Concepts

Key concepts, terminology, and fundamental ideas related to the topic.

## Advanced Topics

**<Topic 1>**: Brief description → [Topic 1](reference/01-topic-one.md)
**<Topic 2>**: Brief description → [Topic 2](reference/02-topic-two.md)
```

## Reference File Template

Place in `reference/NN-<topic>.md`. Keep under 200 lines — split if longer.

```markdown
# <Topic Name>

## Contents
- Subsection 1
- Subsection 2
- Subsection 3

## Subsection 1
Content here...

## Subsection 2
Content here...

## Subsection 3
Content here...
```

For files over 100 lines, the table of contents at the top lets the agent see full scope even when previewing.

## Optional Sections

Include only when applicable.

### `## Installation / Setup`

Include when the tool/library requires installation, configuration, or environment setup. Skip for conceptual, guideline, or meta-skills.

### `## Usage Examples`

Include when practical code examples are relevant. Provide copy-pasteable code blocks with language tags. Skip for conceptual or meta-skills where code doesn't apply.

### `## Advanced Topics`

Include **only** when the skill has companion reference files in `reference/`. Use as navigation hub linking to them (see Complex template above).
