import os
import requests
import time
import toml

import obsws_python as obs

# Simple script to change the state of the tally light based on
# stream and scene statuses.

# Scene to bind tally light state to
TALLY_SCENE = "Camera"

class Observer:
    def __init__(self):
        self._client = obs.EventClient()
        self._client.callback.register(
            [
                self.on_current_program_scene_changed,
                self.on_stream_state_changed,
                self.on_exit_started,
            ]
        )
        self.running = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._client.disconnect()

    def on_stream_state_changed(self, data):
        updateLight()

    def on_current_program_scene_changed(self, data):
        updateLight()
        

    def on_exit_started(self, _):
        requests.get(f"http://localhost:8989/?action=light&green=0")
        self.running = False

def config_initialize():
    CONFIG="config.toml"
    if not os.path.isfile(CONFIG):
        
        print("No config present, initializing.")

        DEFAULT_DATA = {
            "connection": {
                "host": "localhost",
                "port": 4455,
                "password": "ChangeMe!"
            }
        }

        with open(CONFIG, "w") as f:
            toml.dump(DEFAULT_DATA, f)
        
        print("Config initialized, edit password value in config.toml before running again.")
        print("Exiting.")
        quit()

def light(action, color):
    url = f"http://localhost:8989/?action={action}&{color}=100"
    requests.get(url)

def updateLight():
    status= req_client.get_stream_status()
    scene = f"{req_client.get_scene_list().current_program_scene_name}"
    if status.output_reconnecting == True:
        if scene == f"{TALLY_SCENE}":
            light("blink", "yellow")
        else:
            light("light", "yellow")
    elif status.output_active == True:
        if scene == f"{TALLY_SCENE}":
            light('light', 'red')
        else:
            light('blink', 'green')
    else:
        light('light', 'green')


if __name__ == "__main__":
    config_initialize()
    with Observer() as  observer:
        with obs.ReqClient() as req_client:
            while observer.running:
                time.sleep(0.1)