import serial
import os
import time
import queue
import threading
import signal

import serial.tools
import serial.tools.list_ports

MIN_DELAY = 0.5  # Minimum delay in seconds between commands
COMMANDS = {
    "green": {
        "on": b"\xa0\x02\x01\xa3",
        "flash": b"\xa0\x02\x01\xb4",
        "off": b"\xa0\x02\x00\xa2",
    },
    "yellow": {
        "on": b"\xa0\x03\x01\xa4",
        "flash": b"\xa0\x03\x01\xb5",
        "off": b"\xa0\x03\x00\xa3",
    },
    "red": {
        "on": b"\xa0\x01\x01\xa2",
        "flash": b"\xa0\x01\x01\xb3",
        "off": b"\xa0\x01\x00\xa1",
    },
}


def init():
    # This is just for testing function of lights by the user.
    print("Performing test, verify visual function of all lights.")
    OLD_MIN_DELAY = MIN_DELAY
    chg_min(0.2)
    for i in range(2):
        for cmd in COMMANDS:
            cmd_light(cmd, "on")
        for cmd in COMMANDS:
            cmd_light(cmd, "off")
    chg_min(0.04)
    for i in range(3):
        for cmd in COMMANDS:
            cmd_light(cmd, "on")
        for cmd in COMMANDS:
            cmd_light(cmd, "off")
    time.sleep(1.8)
    chg_min(0.01)
    for cmd in COMMANDS:
        cmd_light(cmd, "on")
    chg_min(0.02)
    time.sleep(3.5)
    cmd_light("red", "off")
    cmd_light("yellow", "off")
    cmd_light("green", "off")
    time.sleep(1)
    chg_min(OLD_MIN_DELAY)
    return "Test complete."


def clr_light():
    for color in ["red", "yellow", "green"]:
        command_queue.put(COMMANDS[color]["off"])
        time.sleep(1)


def chg_min(interval):
    command_queue.put(interval)


def cmd_light(color: str, state: str):
    color = color.lower()
    state = state.lower()

    if color not in COMMANDS:
        raise ValueError(
            f"Invalid color '{color}'. Valid options are: {list(COMMANDS.keys())}"
        )
    if state not in COMMANDS[color]:
        raise ValueError(
            f"Invalid state '{state}' for color '{color}'. Valid options are: {list(COMMANDS[color].keys())}"
        )
    command = COMMANDS[color][state]

    command_queue.put(command)
    return f"Color: {color}, state: {state}"


def get_port(description):
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if description in port.description:
            return port.device


def process_queue():
    """Continuously process commands from the queue with a delay."""
    global MIN_DELAY
    while True:
        ser.reset_output_buffer
        command = command_queue.get()  # Get the next command from the queue
        if command is None:  # Exit signal
            break
        if isinstance(command, float):
            MIN_DELAY = command
        else:
            ser.write(command)
        time.sleep(MIN_DELAY)  # Ensure delay between commands
        command_queue.task_done()  # Mark this task as done


command_queue = queue.Queue()
queue_thread = threading.Thread(target=process_queue, daemon=True)

ser = serial.Serial(
    port=get_port("USB-SERIAL CH340"), baudrate=9600, bytesize=8, stopbits=1
)
ser.reset_input_buffer()
ser.reset_output_buffer()
queue_thread.start()
