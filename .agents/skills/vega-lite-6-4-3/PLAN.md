# ☑ Plan ➖ Vega-Lite 6.4.3 Skill: Valid Reference Files
- Depends On: NONE
- Created: 2026-06-14T21:21:17Z
- Updated: 2026-06-14T21:38:18Z
- Current Phase: NONE
- Current Task: NONE

## ☑ Phase 1 ➖ Setup Validator and Analyze Examples
- ☑ Task 1.1 ➖ Create validation script (validate_vl.py) using jsonschema + vega-lite-schema.json
- ☑ Task 1.2 ➖ Validate all 810 examples/specs/*.vl.json from vega-lite repo against schema ⚓ Task 1.1
- ☑ Task 1.3 ➖ Analyze example categories and pick representative charts for reference files ⚓ Task 1.2

## ☑ Phase 2 ➖ Create Vega-Lite Skill Skeleton
- ☑ Task 2.1 ➖ Scaffold vega-lite-6-4-3 skill with skman.sh create --with-references
- ☑ Task 2.2 ➖ Write SKILL.md with frontmatter, Overview, Usage sections ⚓ Task 2.1
- ☑ Task 2.3 ➖ Create validation helper script scripts/validate_vl.py and wrapper scripts/vega-lite.sh ⚓ Task 2.2

## ☑ Phase 3 ➖ Write Reference Files with Valid Chart Examples
- ☑ Task 3.1 ➖ Write 01-bar-charts.md with valid bar chart examples ⚓ Phase 2 - Task 2.3
- ☑ Task 3.2 ➖ Write 02-area-line-charts.md with valid area/line chart examples ⚓ Phase 2 - Task 2.3
- ☑ Task 3.3 ➖ Write 03-scatter-circle-plots.md with valid scatter/circle plot examples ⚓ Phase 2 - Task 2.3
- ☑ Task 3.4 ➖ Write 04-geo-maps.md with valid geographic map examples ⚓ Phase 2 - Task 2.3
- ☑ Task 3.5 ➖ Write 05-layered-charts.md with valid layered chart examples ⚓ Phase 2 - Task 2.3
- ☑ Task 3.6 ➖ Write 06-facet-repeat.md with valid faceted/repeated chart examples ⚓ Phase 2 - Task 2.3
- ☑ Task 3.7 ➖ Write 07-interactive-selection.md with valid interactive/selection examples ⚓ Phase 2 - Task 2.3
- ☑ Task 3.8 ➖ Write 08-advanced-patterns.md with valid advanced pattern examples ⚓ Phase 2 - Task 2.3

## ☑ Phase 4 ➖ Validate All Reference File Examples
- ☑ Task 4.1 ➖ Extract and validate all JSON specs from reference files against vega-lite schema ⚓ Phase 3 - Task 3.8
- ☑ Task 4.2 ➖ Fix any invalid examples until all pass validation ⚓ Task 4.1
- ☑ Task 4.3 ➖ Run skman.sh validate on the skill directory ⚓ Task 4.2

## ☑ Phase 5 ➖ Final Review and Cleanup
- ☑ Task 5.1 ➖ Run skman.sh info on the skill
- ☑ Task 5.2 ➖ Verify SKILL.md references all reference files ⚓ Task 5.1
- ☑ Task 5.3 ➖ Final validation pass — all examples valid, skill structure compliant ⚓ Task 5.2
<!-- checksum: 3f5f26c48ba9e9d6 -->
