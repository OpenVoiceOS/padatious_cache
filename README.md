# Padatious Intent Cache

Pre-trained Padatious intent classifiers to significantly accelerate the first boot and skill loading of OpenVoiceOS.

## The Problem

Padatious was originally designed for small datasets with a few sentences per intent. However, as the number of intents
and languages grows, training times have increased drastically.

> ⚠️ Depending on the number of skills installed padatious intent training can slow down a raspberri pi to a crawl!

This is particularly noticeable in languages like **Catalan** and **Galician**, where utterance examples include many
alternatives/optionals to account for verb tenses and grammatical gender. Large datasets can lead to training times
exceeding 10 minutes for a single intent:

```text
DEBUG - Training ask.intent with 110,784 positive + 20,212 negative samples...
... a few minutes later ...
DEBUG - Training ask.intent finished!
```

## The Solution

This repository uses an automated utility (`gen_cache.py`) to bootstrap the training process. By simulating a complete
`ovos-core` environment, we generate binary intent models for every supported language and configuration variation.

When these pre-trained models are present, Padatious skips the expensive training phase unless the local training data (
`.intent` files) has changed.

## Technical Details

The `gen_cache.py` utility generates a matrix of **8 different configuration profiles** to ensure compatibility with
various user setups:

| Feature                 | Variations                                      |
|-------------------------|-------------------------------------------------|
| **Languages**           | 12 (en, es, pt, fr, de, it, nl, da, ca, gl, eu) |
| **Domain Engine**       | Enabled / Disabled (Two-stage classification)   |
| **Stemming**            | Enabled / Disabled                              |
| **ASCII Normalization** | Enabled / Disabled                              |

### How it works

1. **Mock Environment:** Uses `FakeBus` and `SkillManager` to load skills without a running messagebus.
2. **Pipeline Injection:** Forces the `ovos-padatious-pipeline-plugin-high` pipeline.
3. **Lifecycle Monitoring:** Listens for `mycroft.ready.check` to verify all Padatious threads have finished writing to
   disk before cycling to the next config profile.

## Usage

1. Download the `intent_cache` directories from the latest release/build.
2. Place the folder in your XDG data directory (usually `~/.local/share/mycroft`).

```bash
# Example structure
~/.local/share/mycroft/intent_cache/
├── en-us/
├── es-es/
└── ...

~/.local/share/mycroft/intent_cache_domain/
├── en-us/
├── es-es/
└── ...
```
