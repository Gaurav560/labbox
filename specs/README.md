# Lab specs

A spec is the short form of a lab: the story, chapters, tasks, hints and cover scene.
`scripts/labbox new-lab --from-spec specs/<lab>.yaml` turns it into `labs/<lab>/` from a template
(`python`, `java`, `node`, `go`, `service-incident`, `preview-app`), with chapter skeletons full of
`TODO(author)` markers and an `AUTHORING.md` checklist. A lab is done when
`scripts/labbox validate <lab> --strict` and `scripts/labbox test-lab <lab>` both pass.

```yaml
id: python-collections
template: python
title: "Python collections"
subtitle: One line on what the learner builds.
track: languages            # languages | frameworks | databases | devops | system-design | ai | interview
tags: [python]
level: beginner             # beginner | intermediate | advanced
story:
  company: Dabba Express
  character: { name: Priya, role: "Founder, Dabba Express" }
  pitch: One line of story for the lab card.
cover_scene: "One line: what the cover diorama shows."
chapters:
  - id: 01-lists
    title: Lists that keep order
    minutes: 15
    goal: One line, what the learner can do after this chapter.
    tasks:
      - id: top_orders
        title: "orders.py: the three biggest orders"
        hints: ["A nudge", "A direction", "Almost there (never the answer)"]
```
