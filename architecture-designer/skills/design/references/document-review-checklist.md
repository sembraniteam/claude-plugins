# Document Review Checklist (F1-F7, C1-C9)

The canonical catalog of format (F) and content (C) checks for architecture documents. `document-reviewer` audits every item below as PASS/FAIL; `document-fixer` corrects every FAIL item. Both agents implement the full catalog — this file is the single source of truth for the item list and the literal formats both must produce identically. If an item is added, renamed, or renumbered, update both agent files to match; neither agent file should duplicate the item catalog itself, only its own role's criteria or fix procedure.

## Item catalog

| ID  | Name                                                      |
|-----|-----------------------------------------------------------|
| F1  | Metadata table is the first content                       |
| F2  | Date format in metadata table                             |
| F3  | Version number                                            |
| F4  | Status value                                              |
| F5  | Reason and Previous Document                              |
| F6  | File naming                                               |
| F7  | Mermaid code blocks                                       |
| C1  | Requirements summary present                              |
| C2  | Constraints and feasibility present                       |
| C3  | Capacity planning present                                 |
| C4  | Technology decisions with justifications                  |
| C5  | All diagrams included                                     |
| C5a | ERD index plan table present                              |
| C6  | Content accuracy                                          |
| C7  | Infrastructure as Code section present                    |
| C8  | CI/CD Pipeline section present                            |
| C9  | Decentralized Architecture Considerations section present |

## Literal formats (must match exactly in both agents)

**Metadata table header** (F1):
```
| Date | Version | Status | Reason | Previous Document |
|------|---------|--------|--------|-------------------|
```

**Date format** (F2): `dd-mmm-y` — day zero-padded two digits; month three-letter abbreviation with uppercase first letter (`Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`); year four digits. Example: `05-Jul-2026`.

**Filename pattern** (F6): `{yyyymmdd}-{topic}.md` — `{yyyymmdd}` is 8 digits in ISO order (year, month, day; e.g. `20260705` for 5 July 2026); `{topic}` is kebab-case (lowercase letters, numbers, hyphens only).

**Valid Mermaid diagram type keywords** (F7): `flowchart`, `graph`, `erDiagram`, `sequenceDiagram`, `classDiagram`, `stateDiagram-v2`, `stateDiagram`, `C4Context`, `C4Container`, `architecture-beta`, `gitGraph`, `mindmap`, `timeline`, `gantt`, `pie`, `quadrantChart`, `xychart-beta`.

**ERD index plan table header** (C5a):
```
| Index Name | Table | Column(s) | Type | Reason |
```
