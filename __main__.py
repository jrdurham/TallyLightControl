import os
import time
import rpyc
import toml
import stacklight
import signal
import obsws_python as obs

from rpyc.utils.server import ThreadedServer

# Simple script to change the state of the tally light based on
# stream and scene statuses.

# Scene to bind tally light state to
TALLY_SCENE = "Camera"
TALLY_SCENE_AUDIO="STBY2"

# Transition used for tally light. This turns the light red as soon as the transition to the camera is begun.
# Requires a unique transition name set for the TALLY_SCENE's transition override.
TALLY_TRANSITION = "CamWipe"

lights = {}
lights["red"] = "off"
lights["yellow"] = "off"  # Self test leaves the light flashing yellow.
lights["green"] = "off"


class Observer:
    def __init__(self):
        self._client = obs.EventClient()
        self._client.callback.register(
            [
                self.on_current_program_scene_changed,
                self.on_stream_state_changed,
                self.on_exit_started,
                self.on_scene_transition_started,
            ]
        )
        self.running = True
        signal.signal(signal.SIGINT, self.graceful_exit)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._client.disconnect()

    def on_stream_state_changed(self, data):
        print(f"{data.output_state}")
        if f"{data.output_state}" in (
            "OBS_WEBSOCKET_OUTPUT_STARTING",
            "OBS_WEBSOCKET_OUTPUT_RECONNECTING",
            "OBS_WEBSOCKET_OUTPUT_PAUSED",
            "OBS_WEBSOCKET_OUTPUT_UNKNOWN",
        ):
            self.updateLight(override={"green": "flash"})
        elif f"{data.output_state}" in (
            "OBS_WEBSOCKET_OUTPUT_STARTED",
            "OBS_WEBSOCKET_OUTPUT_RESUMED",
            "OBS_WEBSOCKET_OUTPUT_RECONNECTED",
        ):
            self.updateLight(override={"green": "on"})
            time.sleep(1)
            self.updateLight()
        elif f"{data.output_state}" in ("OBS_WEBSOCKET_OUTPUT_STOPPING"):
            self.updateLight(override={"red": "off", "green": "flash"})
        elif f"{data.output_state}" in ("OBS_WEBSOCKET_OUTPUT_STOPPED"):
            time.sleep(2)
            self.updateLight(override={"green": "off", "red": "off", "yellow": "off"})
        elif f"{data.output_active}" == False:
            self.updateLight("green", "off")

    def on_current_program_scene_changed(self, data):
        self.updateLight(data.scene_name)
    
    def on_scene_transition_started(self, data):
        if f"{data.transition_name}" == f"{TALLY_TRANSITION}" and lights["green"] in ("on","flash"):
            self.updateLight(override={"red": "on"})

    def on_exit_started(self, data):
        self.graceful_exit()

    def light(self, color: str, status: str):
        if lights[f"{color}"] != f"{status}":
            lights[f"{color}"] = f"{status}"
            stacklight.cmd_light(color, status)
            print(f"Commanded: {color} {status}")
        else:
            print(f"Already set: {color} {status}")

    def updateLight(self, init=False, override=None, scene=None):
        light = self.light

        if override is not None:
            if len(override) > 1:
                for key in override:
                    light(key, override[key])
                    time.sleep(1)
            else:
                for key in override:
                    light(key, override[key])
            return

        stream = req_client.get_stream_status().output_active

        if init is True:
            if stream == True:
                light("green", "on")
                if (
                    f"{req_client.get_scene_list().current_program_scene_name}"
                    == f"{TALLY_SCENE}"
                ):
                    light("red", "on")
                elif (
                    f"{req_client.get_scene_list().current_program_scene_name}"
                    == f"{TALLY_SCENE_AUDIO}"
                ):
                    light("red", "flash")
            print("Stacklight initialized.")
            return

        scene = f"{req_client.get_scene_list().current_program_scene_name}"

        if stream == True:
            if scene == f"{TALLY_SCENE}":
                light("red", "on")
            elif scene == f"{TALLY_SCENE_AUDIO}":
                light("red", "flash")
            else:
                light("red", "off")

    def graceful_exit(self, *args):
        print("Exiting...")
        stacklight.clr_light()
        os._exit(0)
        server.close


class StacklightService(rpyc.Service):
    def exposed_light_override(self, override=None):
        print("Client command received!")
        if override is not None:
            observer.updateLight(override=override)
        else:
            return "Error: No override values given!"

    def exposed_init(self):
        stacklight.init()
    
    def exposed_clr(self):
        stacklight.clr_light()


def config_initialize():
    CONFIG = "config.toml"
    if not os.path.isfile(CONFIG):

        print("No config present, initializing.")

        DEFAULT_DATA = {
            "connection": {"host": "localhost", "port": 4455, "password": "ChangeMe!"}
        }

        with open(CONFIG, "w") as f:
            toml.dump(DEFAULT_DATA, f)

        print(
            "Config initialized, edit password value in config.toml before running again."
        )
        print("Exiting.")
        quit()


if __name__ == "__main__":
    config_initialize()
    with Observer() as observer:
        with obs.ReqClient() as req_client:
            print(stacklight.init())
            observer.updateLight(init=True)
            server = ThreadedServer(StacklightService, port=11152, hostname="localhost")
            server.start()
            while observer.running:
                time.sleep(0.1)
