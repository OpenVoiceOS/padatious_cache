# Padatious Cache

pre trained padatious intents to make first boot faster

padatious was created with only a few sentences in mind for each intent training data

today the reality is a bit different, with the number of intents and languages growing we are getting some cases that take a long time to train

The issue is particularly noticeable in languages like catalan and galician that contain lots of alternative/optional words in the utterance examples to account for verb tenses and grammatical gender

```
2025-02-26 23:55:10.009 - skills - ovos_padatious.simple_intent:train:121 - DEBUG - Training ask.intent with 79 inputs and samples: 23414 positive + 10130 negative
2025-02-27 00:04:01.166 - skills - ovos_padatious.simple_intent:train:128 - DEBUG - Training ask.intent finished!
```

```
2025-02-27 01:04:51.904 - skills - ovos_padatious.simple_intent:train:124 - DEBUG - Training ask.intent with 93 inputs and samples: 110784 positive + 20212 negative
```

This repository bootstraps the whole process allowing padatious to skip training intents unless training data changes

## Usage

place the `intent_cache` folder in `~/.local/share/mycroft`

