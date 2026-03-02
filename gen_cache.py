import os.path
import time
from threading import Event

from ovos_config import Configuration
from ovos_config.locale import setup_locale
from ovos_core.intent_services import IntentService
from ovos_core.skill_manager import SkillManager
from ovos_utils.fakebus import FakeBus
from ovos_utils.log import LOG

cache_created = Event()

# it is a singleton, config changes apply globally within the process

# load all target languages
Configuration()["secondary_langs"] = ["eu", "es-ES", "gl-ES", "ca-ES", "pt-PT", "pt-BR", "nl-NL", "de-DE", "it-IT",
                                      "fr-FR", "da-DK", "en-US"]
Configuration()["intents"]["padatious"]["intent_cache"] = f"{os.path.dirname(__file__)}/intent_cache"
Configuration()["intents"]["pipelines"] = ["ovos-padacioso-pipeline-plugin-high"]

setup_locale()

bus = FakeBus()

done = False


def print_m(m):
    print(m)


def handle_done(m):
    global done
    done = True


def handle_notdone(m):
    global done
    done = False


bus.on("message", print_m)

bus.on("padatious:register_intent", handle_notdone)
bus.on("register_intent", handle_notdone)
bus.on("register_vocab", handle_notdone)
bus.on("mycroft.skills.train", handle_notdone)

# bus.on("mycroft.skills.trained", handle_done)
bus.on("mycroft.ready.check", handle_done)  # only starts after last trained message

intents = IntentService(bus)
skill_manager = SkillManager(bus)
skill_manager.start()

while not done:
    time.sleep(10)

print("DONE!! finished cache")

time.sleep(5)

intents.shutdown()
skill_manager.stop()

LOG.info('Skills service shutdown complete!')
