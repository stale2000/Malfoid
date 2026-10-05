# Harry voice profile — approved direction v1

**Status:** The user approved the Harry voice in the Mirror scene as a great version and asked that it be documented (October 5, 2026).

## Character direction

Youthful and boyish; gentle and sincere; natural British English; clear, conversational delivery with some softness. Avoid an adult-sounding performance, broad theatricality, or aggressive drama. This records the user’s preference for this parody character; it is not a claim that the voice is an original, unrelated voice.

## Internal reference take

The approved take is in the local V5 production archive: `production/trailer/outputs/mirror-erised-audio-v1/harry-approved/27b3ba2e_001.flac`. The scene workflow is `production/trailer/blueprints/qwen3-harry-mirror-approved-voice-v1.json`. Those paths are intentionally excluded from this public repository; no voice recording, clone sample, or source-film audio is included here.

The native Comfy workflow uses Qwen3 TTS 1.7B, English, `bf16`, and a fixed seed of `20261005`. The voice-clone prompt was conditioned on two earlier approved synthetic Harry takes. The local synthesis node’s remaining recorded widget values are `auto`, empty style text, `2048`, `0.8`, `20`, `0.7`, `1.05`, `false`, `auto`, `false`, and empty trailing text. Exact parameter meanings can depend on the installed node version; the private workflow is the authoritative internal record.

The approved reference chain originated from user-supplied film dialogue and generated audition takes. The reference media and the generated voice takes remain local-only. This public note records direction and provenance, not a distributable voice model or permission to reuse any actor’s performance.

## Review note

The user approved the voice quality and character fit. The generated take’s pronunciation of “Mirror of Erised” was not reliably recognized by the transcript check (“a rise”); listen to the isolated take before using it as the pronunciation target or releasing a final audio mix.

## Scene use

The voice is used in the working [Mirror of Erised draft](../../creative/drafts/mirror-of-erised-crush-v1.md). The existing public preview is silent and does not contain the cloned voice.
