"""
OVOS Padatious Intent Pre-Training & Cache Generation Utility.

This script simulates a complete 'ovos-core' environment to trigger skill
loading and intent training. It is designed to run via GitHub Actions to
generate binary intent classifiers.

Workflow:
1. Mocks a system-wide install by starting the SkillManager and IntentService.
2. Iterates through various Padatious engine configurations (stemming, ascii, etc.).
3. Captures the trained intent cache for all installed skills and all languages.
4. The resulting 'intent_cache' directory is then uploaded to GitHub and
   downloaded during user installation to significantly speed up first boot.

Note: In 'domain_engine' mode, the system performs a two-stage classification:
first identifying the Skill (domain), then the specific Intent within that skill.
"""

import os.path
import time
from threading import Event

from ovos_config import Configuration
from ovos_core.intent_services import IntentService
from ovos_core.skill_manager import SkillManager
from ovos_utils.fakebus import FakeBus
from ovos_utils.log import LOG


# --- Global Configuration Setup ---
# The Configuration object is a singleton; these settings mimic a production mycroft.conf

# 1. Ensure all supported languages are processed to build a multi-lingual cache
Configuration()["secondary_langs"] = [
    "eu", "es-ES", "gl-ES", "ca-ES", "pt-PT", "pt-BR", "nl-NL", "de-DE", "it-IT",
    "fr-FR", "da-DK", "en-US"
]

# 2. Pipeline Hack: Force the use of the Padatious high-priority pipeline plugin
Configuration()["intents"]["pipelines"] = ["ovos-padatious-pipeline-plugin-high"]

# 3. Pathing: Set the destination for the generated cache files
cfg = Configuration()["intents"]["padatious"]
cfg["intent_cache"] = f"{os.path.dirname(__file__)}/intent_cache"

# Define the matrix of Padatious engine config variations.
# We generate caches for every combination to support different user configs.
opts = [
    {"domain_engine": False, "stem": False, "cast_to_ascii": False}, # Standard
    {"domain_engine": True, "stem": False, "cast_to_ascii": False},  # Domain-based
    {"domain_engine": False, "stem": True, "cast_to_ascii": False},  # Stemming enabled
    {"domain_engine": True, "stem": True, "cast_to_ascii": False},
    {"domain_engine": False, "stem": False, "cast_to_ascii": True},  # ASCII normalization
    {"domain_engine": True, "stem": False, "cast_to_ascii": True},
    {"domain_engine": False, "stem": True, "cast_to_ascii": True},
    {"domain_engine": True, "stem": True, "cast_to_ascii": True},
]

# --- Main Training Loop ---
for opt in opts:
    print(f"--- Training Profile: {opt} ---")

    # Inject specific engine options into the global configuration
    new_conf = {**cfg, **opt}
    Configuration()["intents"]["ovos-padatious-pipeline-plugin"] = new_conf

    # Use FakeBus to avoid requiring a running messagebus-service (dbus/websocket)
    bus = FakeBus()
    done = False

    def print_m(m):
        """Debug helper to log bus traffic during the training phase."""
        print(m)

    def handle_done(m):
        """Success callback: System is ready and all intents are trained."""
        global done
        done = True

    def handle_notdone(m):
        """Reset callback: Triggered if new registration activity is detected."""
        global done
        done = False

    # Attach listeners to monitor the skill lifecycle and training status
    bus.on("message", print_m)
    bus.on("padatious:register_intent", handle_notdone)
    bus.on("register_intent", handle_notdone)
    bus.on("register_vocab", handle_notdone)
    bus.on("mycroft.skills.train", handle_notdone)

    # 'mycroft.ready.check' is the signal that all skills have finished their
    # internal setup and the SkillManager has completed its loading sequence.
    # SkillManager emits this to check if all other components are also ready
    bus.on("mycroft.ready.check", handle_done)

    # Instantiate services to trigger automatic skill loading and training
    intents = IntentService(bus)
    skill_manager = SkillManager(bus)
    skill_manager.start()

    # Block until training is complete. This allows Padatious threads
    # to write the compiled models to the disk.
    while not done:
        time.sleep(10)

    print("CACHE COMPLETED: Intent models have been written to disk.")

    # Grace period for file I/O to finalize
    time.sleep(5)

    # Clean shutdown of simulated core services
    intents.shutdown()
    skill_manager.stop()

    LOG.info('Virtual environment teardown complete!')

    # Remove references to prepare for the next configuration iteration
    del bus
    del intents
    del skill_manager