# Leash

Leash is a control API for the LumenPnP written in Python. It is meant to be used as an easy way to automate actions with the LumenPnP.

It contains:

- Machine axis control
- Pump and valve control
- Ring light control
- Vacuum sensor reading
- Full Photon bus control
- Image capture from both cameras

## Usage

To install (ideally in a virtual environment), use:

```bash
pip install git+https://github.com/opulo-inc/leash.git
```

It can help to include the `--force-reinstall` flag in this command to make sure you're getting the latest version.

From here, it's easy to connect to a Lumen:

```python
from leash.lumen import Lumen

lumen = Lumen()

if lumen.connect():
    try:
        lumen.home()

        # .goto() sends a move command with any optional arguments x, y, z, a, and b
        lumen.goto(x=10 y=10)
        lumen.goto(z=20)

        lumen.safeZ()

        # To make sure Lumen actions align with your code timing, use lumen.sleep()
        # This just makes sure all commands are complete before delaying
        lumen.sleep(2)

        # If you need more control, you can use lumen.finishMoves() which blocks until
        # the Lumen's command queue is empty
        lumen.finishMoves()
        # You can then use any other delays or timing functions afterwards
        time.sleep(1)

        # Pumps

        lumen.leftPump.on()
        lumen.sleep(1)
        print(lumen.leftPump.read())
        lumen.leftPump.off()

        lumen.rightPump.on()
        lumen.sleep(1)
        print(lumen.rightPump.read())
        lumen.rightPump.off()

        # Ring Lights

        lumen.topLight.on(140, 60, 90, 255)
        lumen.sleep(1)
        lumen.topLight.off()

        lumen.botLight.on(140, 60, 90, 255)
        lumen.sleep(1)
        lumen.botLight.off()

        # Feeders

        myLumen.photon.scan()
        print(myLumen.photon.activeFeeders)
    
    except KeyboardInterrupt:
        lumen.idle()


```

TODO

- uvc exposure support https://github.com/jtfrey/uvc-util/tree/master
- A few more simple vision commands (fid and rect position)