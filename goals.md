# Teaching Module App — Design Context Dump

This file summarizes a design discussion for a gamified teaching app, intended as
a handoff brief for continuing the build in Claude Code.

## Goal

Build a small web app to support teaching a university module. The app should
feel similar to Duolingo in structure — short units of content, clear
progression, gamified feel — but the content is academic papers, not language
learning.

Deployment requirement: must be **freely and openly deployable**, ideally as a
single link that can be sent to students with no install and no login.

## Chosen approach: Streamlit

Decided on **Streamlit**, deployed via **Streamlit Community Cloud** (free tier),
for these reasons:

- Python-based, which matches the author's existing skillset (academic/research
  background, comfortable in Python/R, HPC environments).
- Free hosting with a real public URL — "send people a link" requirement is met
  directly.
- Fast to build relative to a custom React/Next.js + backend approach.
- Good fit for the simple, mostly-linear flows described below (audio, buttons,
  progress bars, embedded content).

### Streamlit Community Cloud free-tier facts gathered (for reference)

- Up to ~3 apps per free personal workspace (approximate — verify in dashboard).
- Each app gets ~1 GB memory, shared/limited CPU. Apps that exceed this throttle
  or show a "gone over its resource limits" error.
- Apps with no traffic for 12 hours go to sleep; anyone visiting a sleeping app
  can wake it (not just the developer) — ~30 second wake-up delay.
- Free tier requires the app to be linked to a **public GitHub repo**. This
  matters if any content (e.g. exam-adjacent material, non-open-access papers)
  shouldn't be fully public — host that content outside the repo (e.g. a
  separate private store / direct links) rather than committing it directly.
- Streamlit offers **increased resources for educational/nonprofit/open-source
  use cases** via an application form. As a university lecturer building this
  for actual students, this is very likely to apply and is worth doing once the
  app is close to launch-ready, to remove resource-limit risk.

### Alternatives considered and rejected (for context, not pursued further)

- **Anki** — excellent spaced repetition, free, shareable decks, but doesn't
  support podcasts/quizzes natively and doesn't have a "Duolingo" feel.
- **H5P** — open-source interactive content (quizzes, flashcards), can embed in
  Reading's VLE (Blackboard/Moodle) if supported — worth a quick look
  separately, but doesn't give Duolingo-style streaks/XP out of the box.
- **Full custom build** (React/Next.js + Vercel + Supabase/Firebase) — would
  give the most polished "real app" feel but is a much bigger project (weeks,
  not days) and wasn't judged worth it for a single module's content.

## Content structure (the core design)

### Unit of content: one "Week"

Each week of the module = **two papers**. Each paper goes through the same
three-stage sequence:

1. **Podcast** — a short audio clip (currently AI-generated via TTS,
   may move to human-recorded/the author's own voice later) that orients the
   student to **both papers for the week**: why these papers, what are the core
   claims, what to watch for. Intended as a "trailer," not a substitute for
   reading — should deliberately not give away everything (e.g. leave at least
   one "nugget" per paper only discoverable by actually reading), so the
   comprehension questions can't be answered from the podcast alone.
2. **Papers** — the actual readings. Hosted as PDFs or linked via DOI/publisher
   links. Copyright matters here: don't put non-open-access PDFs in the public
   GitHub repo Streamlit Cloud needs; link out instead, or host separately.
3. **Comprehension questions** (per paper) — a mix of:
   - **Multiple choice** — auto-graded, instant feedback.
   - **Short answer** — **self-assessed**: student writes an answer, then
     clicks to reveal a model answer, and self-marks "got it" / "missed it."
     No AI grading, no rubric-based backend grading — deliberately kept simple
     for v1.

### Full week sequence

```
Podcast (covers both papers) → Paper 1 questions → Paper 2 questions → week complete
```

### Gating

**Strict sequential gating** — Paper 2's questions stay locked until Paper 1's
questions are completed. Chosen specifically because it's simpler to implement
than free navigation (progress is a single pointer/integer, not a graph of
unlocked states) — not purely a pedagogical choice, though it does also enforce
"listen → read → prove it" discipline.

### State model

Progress per student per week reduces to a single integer / stage marker, e.g.:

```
stage 0 = not started
stage 1 = podcast done (covers both papers)
stage 2 = paper 1 questions done
stage 3 = paper 2 questions done / week complete
```

### No persistence, no login — explicit decision

- **No student IDs, no accounts, no database.** This was an explicit, deliberate
  choice — the author does not want to track who is doing the reading or
  collect any identifying data. Low-stakes, anonymous, self-paced tool.
- Progress lives entirely in Streamlit's `session_state` and resets on
  refresh/new browser/device. This is accepted as a tradeoff, not an oversight.
- **Implication for gamification**: true multi-day streak tracking (the core
  Duolingo habit-loop mechanic) requires persistence across sessions, which this
  app deliberately doesn't have. So v1 gamification will have the *feel* of
  progress (progress bars, unlock animations, completion checkmarks, an
  in-session XP/points counter) but not real cross-day streaks. This is a known,
  accepted limitation for v1 — could be revisited later with an optional
  "save my code to resume" feature if students want to pause partway through a
  week, but that is **not** part of the current scope.

## Architecture sketch (not yet built)

```
Week (hardcoded or loaded from a simple config file / Python dict — content,
      not yet decided whether to externalize into JSON/YAML for easier
      non-technical editing later)
 └─ Podcast (single audio covering both papers — file path/URL; should NOT
     assume AI vs. human-recorded, just "a podcast" with a file path, so
     swapping AI clips for the author's own recordings later is a content
     change, not a code change)
 └─ Paper 1
     ├─ paper (PDF path or external link)
     ├─ MCQs (auto-graded)
     └─ short answer (self-assessed: input box → reveal model answer → 
         self-mark button)
 └─ Paper 2
     └─ ... same structure (paper + questions)
 └─ "Week complete" screen
```

Single Streamlit app serves all students from one public URL; each visitor gets
an independent session.

## Open / not-yet-decided items

- Whether to externalize week/paper content into a config file (JSON/YAML) vs.
  hardcoding in Python — not decided yet, worth deciding once there's a working
  skeleton, since it affects how easy it is to add new weeks later.
- TTS provider/licensing for AI-generated audio — flagged as "worth checking
  terms allow educational use" but not yet investigated in detail.
- Whether content should be split across multiple small apps (per-week?) or one
  app covering the whole module — not yet discussed; current assumption is one
  app, but worth revisiting given the free-tier "~3 apps" limit doesn't
  obviously map onto "one app per week" if the module runs many weeks.

## Immediate next step (in progress when this was written)

Building a working Streamlit skeleton: one week, two dummy/placeholder papers,
the full podcast → read → MCQ → short-answer → unlock flow, with a simple
progress bar, using placeholder audio/content so the mechanics can be clicked
through before real papers/podcasts are substituted in.