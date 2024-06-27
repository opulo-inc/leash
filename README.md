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

`pip install git+https://github.com/opulo-inc/leash.git`

It can help to include the `--force-reinstall` flag in this command to make sure you're getting the latest version.

From here, it's easy to connect to a Lumen:

```python
from leash.lumen import Lumen

lumen = Lumen()

if lumen.connect():

    lumen.home()

    # .goto() sends a move command with any optional arguments x, y, z, a, and b
    lumen.goto(x=10 y=10)
    lumen.goto(z=20)

    # Waits until all sent commands to the Lumen are complete
    # helpful for letting delays in code also delay the Lumen
    lumen.finishMoves()
    # Causes Lumen to pause for a second because we just called finishMoves()
    time.sleep(1)

    lumen.safeZ()

    # Pumps

    lumen.leftPump.toggle(True)
    time.sleep(1)
    print(lumen.leftPump.read())
    lumen.leftPump.toggle(False)

    lumen.rightPump.toggle(True)
    time.sleep(1)
    print(lumen.rightPump.read())
    lumen.rightPump.toggle(False)

    # Ring Lights

    lumen.topLight.on(140, 60, 90)
    lumen.finishMoves()
    time.sleep(1)
    lumen.topLight.off()

    lumen.botLight.on(140, 60, 90)
    lumen.finishMoves()
    time.sleep(1)
    lumen.botLight.off()

    # Feeders

    myLumen.photon.scan()
    print(myLumen.photon.activeFeeders)


```

TODO

- uvc support https://github.com/jtfrey/uvc-util/tree/master
- 