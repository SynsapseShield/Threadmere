# Architecture

Core loop:

Scenario -> Artifact -> Lens Rule -> Event -> Trace -> Replayframe -> Debrief -> Export

Threadmere is local-first and deterministic. It loads fictional fixtures from YAML, runs rule-grounded lenses, stores trace events in memory, and exports JSON locally.

Design constraints:
- Imported != trusted.
- Indexed != safe.
- Local != safe.
- Visible != complete.
