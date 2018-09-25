import configparser
import subprocess

config = configparser.ConfigParser()
config.read("config.ini")


def sync_to_remote():
    rsync_dirs = config["DEST"]["RSYNC_DIRS"]
    source = config["SOURCE"]["DIR"]
    for item in rsync_dirs.split(","):
        rsynccmd = "rsync -av --progress {} {}".format(source, item)
        rsyncproc = subprocess.Popen(rsynccmd,
                                     shell=True,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE)

        while True:
            next_line = rsyncproc.stdout.readline().decode("utf-8")
            if not next_line:
                break
            print(next_line)

        exitcode = rsyncproc.wait()

        if exitcode == 0:
            print("Success!")


if __name__ == '__main__':
    sync_to_remote()
