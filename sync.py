import subprocess


def sync_to_remote(remote_dirs, local_dir):
    for item in remote_dirs.split(","):
        rsynccmd = "rsync -av --progress --delete {} {}".format(local_dir, item)
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


def sync_to_local(remote_dir, local_dir):
    rsynccmd = "rsync -av --progress --delete {} {}".format(remote_dir, local_dir)
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
    print("This script is not intended to be used by itself, use manager.py!")
    exit(1)
