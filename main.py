# PhotoBooth source file
# Program entry point for launching the PhotoBooth desktop application.

from photobooth.app import PhotoBoothApp


def main():
    # This is the program entry point. It creates the application controller and starts Kivy's
    # event loop, which keeps the window responsive until the user closes it.
    app = PhotoBoothApp()
    app.run()


if __name__ == "__main__":
    main()
