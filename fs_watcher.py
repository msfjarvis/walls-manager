import threading

import pyinotify


class FSWatcher(object):
    """ Threaded class that implements a filesystem watcher
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, directory_to_watch: str):
        """
        Constructor for file system watcher thread
        :param directory_to_watch: Self-explanatory
        """
        wm = pyinotify.WatchManager()
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE
        self.handler = EventHandler()
        self.notifier = pyinotify.Notifier(wm, self.handler)
        self.wdd = wm.add_watch(directory_to_watch, mask, rec=True)

        thread = threading.Thread(target=self.notifier.loop, args=())
        thread.daemon = True
        thread.start()


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print(event.pathname)

    def process_IN_DELETE(self, event):
        print(event.pathname)
