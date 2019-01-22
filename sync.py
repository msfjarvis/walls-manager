# pylint: disable=missing-docstring

import subprocess


def sync_to_remote(remote_dirs, local_dir, markdown_output, remote_url):
    printed_stats = False
    for item in remote_dirs.split(","):
        rsynccmd = "rsync -av --progress --delete --itemize-changes {} {}".format(local_dir, item)
        rsyncproc = subprocess.Popen(rsynccmd,
                                     shell=True,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE)

        if not remote_url:
            markdown_output = False

        while True:
            if printed_stats:
                break
            next_line = rsyncproc.stdout.readline().decode("utf-8")
            if not next_line:
                break
            elif next_line.find("<f+++++++++") != -1:
                print("New wallpaper: {}".format(print_names(remote_url,
                                                             extract_pretty_name(next_line),
                                                             markdown_output)))
            elif next_line.find("*deleting") != -1:
                print("Deleting: {}".format(extract_pretty_name(next_line)))
            elif next_line.find("<f.st......") != -1:
                print("Updating: {}".format(print_names(remote_url,
                                                        extract_pretty_name(next_line),
                                                        markdown_output)))

        exitcode = rsyncproc.wait()

        if exitcode == 0:
            printed_stats = True


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
        elif next_line.find(">f+++++++++") != -1:
            print("New wallpaper: {}".format(extract_pretty_name(next_line)))
        elif next_line.find("*deleting") != -1:
            print("Deleting: {}".format(extract_pretty_name(next_line)))
        elif next_line.find(">f.st......") != -1:
            print("Updating: {}".format(extract_pretty_name(next_line)))

    rsyncproc.wait()


def print_names(base_url, file_name, is_markdown):
    if is_markdown:
        return "[{}]({})".format(file_name, base_url + (file_name.replace(" ", "_")) + ".jpg")
    return file_name


def extract_pretty_name(rsync_output_line):
    return rsync_output_line.split()[1].replace("_", " ").replace(".jpg", "")


if __name__ == '__main__':
    print("This script is not intended to be used by itself, use manager.py!")
    exit(1)
