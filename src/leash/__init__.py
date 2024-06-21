__version__ = '0.3.2'

CMD_NAME = 'leash'  # Lower case command and module name
APP_NAME = 'Leash'  # Application name in texts meant to be human readable
APP_URL = 'https://github.com/opulo-inc/'


from .hardware.lumen import Lumen

def main():

    lumen = Lumen()
    print(lumen.connect())


if __name__ == '__main__':
    main()
