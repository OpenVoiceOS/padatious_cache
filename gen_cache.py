import os.path
import time

from ovos_config.locale import setup_locale
from ovos_core.intent_services import IntentService
from ovos_core.skill_manager import SkillManager, on_error, on_stopping, on_ready, on_alive, on_started
from ovos_utils import wait_for_exit_signal
from ovos_utils.fakebus import FakeBus
from ovos_utils.log import LOG
from ovos_config import Configuration
from threading import Event

cache_created = Event()

# it is a singleton, so this applies globally within the process
Configuration()["secondary_langs"] =  ["gl-ES", "ca-ES", "pt-PT", "nl-NL",
                                       "it-IT", "fr-FR", "eu", "es-ES",
                                       "de-DE", "da-DK", "en-US"]
Configuration()["intents"]["padatious"]["intent_cache"] = f"{os.path.dirname(__file__)}/intent_cache"

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

#bus.on("mycroft.skills.trained", handle_done)
bus.on("mycroft.ready.check", handle_done) # only starts after last trained message

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

