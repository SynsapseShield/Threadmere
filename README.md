# Threadmere

Threadmere is a local-first AI observability, provenance, and conversational security simulation engine.

It teaches how AI systems inherit trust, drift through interaction, and become influenced by hidden or contaminated context.
It also teaches basic prompting literacy: prompts are instructions plus context, and copied prompts or documents from the internet can carry unsafe assumptions into an AI workflow.

## Philosophy

- Make hidden influence visible.
- Preserve replayability.
- Use fictional or synthetic data only.
- Stay local-first and inspectable.
- Use calm ASCII terminal UI.
- Do not build offensive tooling.

Core trust reminders:

- Imported != trusted.
- Indexed != safe.
- Local != safe.
- Visible != complete.

## Build Stack

- Python 3.12+
- Rich
- Pydantic
- PyYAML
- Standard library only

Not used in this MVP:

- Flask
- FastAPI
- React
- SQLite or databases
- Live LLM APIs
- Vector databases
- Networking
- Autonomous agents

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 threadmere.py
```

## Commands

- help
- briefing
- promptlab
- orchard
- profiles
- profile <profile_id>
- inspect <artifact_id>
- chat <message>
- replay
- debrief
- export
- reset
- quit

## Main Scenario

`q1_sharepoint_poisoned_deck`

A vendor Q1 summary deck appears in Aster Vale Municipal Services. It looks normal in the visible layer, but the system layer includes hidden instruction-like text and weak provenance. The learner must inspect provenance before trusting or summarizing it.

The scenario also includes `internet_prompt_snippet`, a copied public prompt that demonstrates why prompt provenance matters. Learners can run `promptlab`, inspect the prompt, and observe how the security lenses keep untrusted instructions out of retrieval, tools, and memory.

## Project Structure

```text
Threadmere/
├── README.md
├── requirements.txt
├── threadmere.py
├── models.py
├── loader.py
├── lenses.py
├── profiles.py
├── trace.py
├── ui.py
├── canon/
│   ├── architecture.md
│   ├── metaphors.md
│   ├── profiles.md
│   ├── roadmap.md
│   └── terminology.md
├── domain_packs/
│   └── aster_vale_municipal/
│       ├── world.yaml
│       ├── policies.yaml
│       ├── assistant_profiles.yaml
│       ├── artifacts/
│       │   ├── internet_prompt_snippet.yaml
│       │   ├── vendor_q1_summary.yaml
│       │   └── verified_policy_record.yaml
│       └── scenarios/
│           └── q1_sharepoint_poisoned_deck.yaml
├── traces/
├── exports/
└── devlogs/
    └── DEVLOG.md
```

## Educational Scope

Threadmere is an educational simulation environment. It is for observability, provenance literacy, and safer workflow design.

It does not test third-party systems, harvest secrets, or automate offensive actions.

The air gap can fail at the human layer.

A poisoned apple does not need network access if people carry slices between orchards.

## Weaver Logs

Weaver Logs preserve development provenance: why decisions were made, what tradeoffs were accepted, and what thread should be picked up next.

See `devlogs/DEVLOG.md`.

## Ethical-Use Boundaries

- Fictional data only by default.
- No private or production system testing.
- No credential harvesting or exploit-chain generation.
- No offensive red-team automation features.
- Prompt examples are fictional and designed to teach defensive recognition, not bypass behavior.

## Trace Privacy

- Do not enter credentials, private records, or production secrets into a lesson.
- Common credential patterns are redacted and trace text is length-limited before storage.
- Trace and export files are written with owner-only permissions.
- Generated session traces are ignored by Git by default.

## License

This project is distributed under the terms in `LICENSE`.
