import rpyc
import sys

c = rpyc.connect("localhost", 11152)

sys.argv.pop(0)

if __name__ == "__main__":
    if sys.argv[0] in "init":
        c.root.init()
    elif sys.argv[0] in ("clr","clear"):
        c.root.clr()
    elif sys.argv[0] in ("red","yellow","green") and sys.argv[1] in ("on", "off", "flash"):
        c.root.light_override({sys.argv[0]:sys.argv[1]})