import subprocess


def sync_to_remote(remote_dirs, local_dir):
    printed_stats = False
    for item in remote_dirs.split(","):
        rsynccmd = "rsync -av --progress --delete --itemize-changes {} {}".format(local_dir, item)
        rsyncproc = subprocess.Popen(rsynccmd,
                                     shell=True,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE)

        while True:
            if printed_stats:
                break
            next_line = rsyncproc.stdout.readline().decode("utf-8")
            if not next_line:
                break
            elif next_line.find("<f+++++++++") != -1:
                print("New wallpaper: {}".format(next_line.split()[1]))
            elif next_line.find("*deleting") != -1:
                print("Deleting: {}".format(next_line.split()[1]))

        exitcode = rsyncproc.wait()

        if exitcode == 0:
            printed_stats = True
            print("Success!")


def sync_to_local(remote_dir, local_dir):
    rsynccmd = "rsync -av --progress --delete --itemize-changes {} {}".format(remote_dir, local_dir)
    rsyncproc = subprocess.Popen(rsynccmd,
                                 shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)

    while True:
        next_line = rsyncproc.stdout.readline().decode("utf-8")
        if not next_line:
            break
        elif next_line.find("<f+++++++++") != -1:
            print("New wallpaper: {}".format(next_line.split()[1]))
        elif next_line.find("*deleting") != -1:
            print("Deleting: {}".format(next_line.split()[1]))

    exitcode = rsyncproc.wait()

    if exitcode == 0:
        print("Success!")


if __name__ == '__main__':
    print("This script is not intended to be used by itself, use manager.py!")
    exit(1)
