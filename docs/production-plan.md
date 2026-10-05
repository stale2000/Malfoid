# Production plan

Malfoid's long-term goal is a complete anime-style reimagining of the first Harry Potter film. Production will begin by checking the existing short anime scene, then measure the work needed before committing to a full feature schedule. The public repository will grow through individually reviewed story, design, production-source, and media releases.

## Production parts

| Part | Deliverables |
|---|---|
| Story | Brief, feature outline, Malfoid's character arc, emotional beats |
| Script | Authoritative feature screenplay, dialogue, revisions |
| Continuity | Timeline, character knowledge, relationship and AU changes |
| Anime style | Shared design rules for line, color, lighting, framing, motion, and effects |
| Character art | Turnarounds, expressions, poses, costumes, scale and color references |
| Locations and props | Reusable layouts, backgrounds, objects, and continuity notes |
| Voice | Casting/direction, pronunciation, selected takes, edited dialogue |
| Music and sound | Score, ambience, effects, foley, stems and final mix |
| Scene planning | Stable scene/shot IDs, shot lists, boards, animatics |
| Animation | Layout, key poses, generated or animated shots, cleanup and compositing |
| Editorial | Picture assembly, transitions, titles, captions, credits and master exports |
| Pipeline | Versioned workflows, software/model requirements, asset manifests, backups |
| Review and release | Scene QC, provenance, licensing, credits, release inventory |

## Scene organization

Use [`films/scenes/`](../films/scenes/README.md) for scene packets and local scene renders. The folder documents stable scene IDs and keeps MP4/MOV/MKV/WebM renders out of Git; publish only a reviewed cut by linking a durable hosted release. Story seeds and working screenplay drafts live in [`creative/`](../creative/README.md), while downloaded third-party inspiration stays local in the ignored [`inspiration/downloads/`](../inspiration/README.md) library with tracked source links.


Each feature scene has a stable ID such as `MF01-SC010`; shots use `MF01-SC010-SH003`. IDs stay stable when scenes move in the edit. A scene packet links its script revision, shots, storyboards, designs, voice takes, sound cues, captions, production status, and review notes. Shared characters, locations, voices, and props each have one master asset record that scenes reference.

Track script, design, boards, animatic, voice, picture, sound, captions, provenance, and release readiness separately. A change to dialogue can affect voice, timing, lip sync, and captions. A costume change can affect the shots that use it. Mark dependent work for review when an input changes.

## Production order

1. Set the feature brief, story and continuity.
2. Lock a scene's dialogue and prepare its shot plan and boards.
3. Select final voice takes and update animatic timing.
4. Approve layouts and generate or animate each shot using the shared character and location designs.
5. Review visual consistency, acting, lip sync, effects and composites.
6. Assemble the feature; finish music, effects, mix, captions and credits after picture timing is stable.
7. Review the exact public files and their provenance before release.

Scenes can progress in parallel when they use approved script, style, and shared assets. Review the complete feature at rough assembly and final assembly so scene-level approvals do not hide pacing or continuity problems.

## Anime and production workflow

The current production archive uses ComfyUI workflows, generated or edited references, Python/FFmpeg assembly scripts, separate voice production, and compositing. Each workflow must identify its required inputs, software and node versions, model and service terms, and whether a clean public clone has the inputs needed to run it. Preserve approved outputs for stable playback and assembly; generated results may vary between model or service versions.

The proposed master format is 1920×1080, 24 fps, BT.709, with 48 kHz stereo audio. This is a target to validate against the benchmark, not a verified feature delivery spec. Keep native resolution, frame rate, and audio metadata for source and generated assets. Fit or crop deliberately; do not stretch footage or imply an upscale adds native detail.

## Current benchmark

The Mirror of Erised scene V5 is the current short anime benchmark. Existing records include an approved Harry voice direction and a selected Draconia voice direction. Review the entire scene for pronunciation, dialogue timing, lip sync, character consistency, and image-reference handling. Add another shot or short scene only to test a capability the existing scene does not cover.

Measure minutes, service/GPU cost, attempts, accepted duration, review and revision time, and storage per shot. Use those measurements to estimate the remaining feature; set per-shot retry/spend limits before larger generation batches. Keep scripts, selected designs/takes, editable project sources, manifests and chosen outputs backed up separately from the movie source.
