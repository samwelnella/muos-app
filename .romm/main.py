from romm import RomM
import time

def main():

    romm = RomM()
    romm.start()

    while True:
        romm.update()
        # Add a small sleep to prevent 100% CPU usage
        time.sleep(0.01)

if __name__ == "__main__":
    main()
