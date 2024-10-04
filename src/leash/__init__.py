__version__ = '0.3.2'

CMD_NAME = 'leash'  # Lower case command and module name
APP_NAME = 'Leash'  # Application name in texts meant to be human readable
APP_URL = 'https://github.com/opulo-inc/'

import numpy as np
import pyvista as pv

def main():
    
    from .lumen import Lumen

    lumen = Lumen()

    try:
        lumen.connect()
        lumen.home(x=True, y=False, z=False)
        lumen.home()


        positions = np.array()

        xBase = 231.5
        yBase = 252.5

        lumen.goto(x=xBase, y=yBase)

        for i in range(2):
            for j in range(2):

                lumen.goto(z=8)
                lumen.goto(x=xBase + (i), y = yBase + (j))
                try:
                    positions.append(lumen.probe("LEFT", startZ = 8))
                except:
                    pass

        print(positions)
    except KeyboardInterrupt:
        lumen.idle()
    
if __name__ == '__main__':
    main()
