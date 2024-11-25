# Tally Light Control for OBS Studio

Tally Light Control is an incredibly plain and simple Python script that utilizes the OBS Websocket Server and the obsws-python module to control a Kuando Busylight.

## Installation

This script was built to work with `OBS 29.1.3` and `Python 3.12.3`.

```bash
git clone https://github.com/jrdurham/TallyLightControl.git && pushd TallyLightControl
pip install -r requirements.txt
```

## Configure

1. Open `__main.py__` with your favorite text editor and change the TALLY_SCENE value from `Camera` to match the name of whichever scene you want the light's tally state to be tied to.
1. Upon first run, the script generates a config file, so run it:
    ```bash
    python .
    ```
1. Next, change the password value inside config.toml from `ChangeMe!` to whatever your OBS Websocket Server password is.
1. Ensure the Websocket Server is enabled in OBS Studio.
1. Ensure the HTTP API program is running locally for the Kuando Busylight.

## Run
As in configuration step 2, running the script is as simple as:
```bash
python .
```

## Test
If you want to test the script without running the HTTP API for the light, run ```api-listener.py```, which is a simple Flask app that replicates the incredibly basic functionality of the API within the scope of the tally light script's expected interaction with the API.

## Automation
I intend on adding the execution of this script to the already complex workflows I have set up to automate my semi-weekly streams via my Elgato Stream Deck. In my use case, this script will be launched by the Stream Deck with a multi-action after launching the OBS process. The script closes automatically when the Websocket server indicates OBS is closing.

## Future Plans
I also intend on using a raspi and an LED status light tower stack to eventually replace the Busylight, which would allow me to use multiple colors at once for more options. If and when that happens, I'll be updating this script to better match that system, however I'd like for this to be more easily configurable to allow for other APIs.