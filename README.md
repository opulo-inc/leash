# leash

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

From here, it's easy to connect to a Lumen:

```python
from leash.hardware.lumen import Lumen

myLumen = Lumen()

if myLumen.connect():
    myLumen.photon.scan()
    print(myLumen.photon.activeFeeders)

```