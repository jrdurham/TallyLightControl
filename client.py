import rpyc
import sys

c = rpyc.connect("localhost", 11152)
#c.root.light_override({"yellow":"flash"})

def send_cmd(color: str, state: str):
    c.root.light_override({color:state})

if __name__ == "__main__":
    color = str(sys.argv[1])
    state = str(sys.argv[2])
    send_cmd(color, state)