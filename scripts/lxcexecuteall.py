#! /usr/bin/python3
import lxc, sys

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def execute(container,command):
    print(OKGREEN+container.name+ENDC)
    # Start the container (if not started)
    started=False
    if not container.running:
        if not container.start():
            return
        started=True

    if not container.state == "RUNNING":
        return

    # Wait for connectivity
    if not container.get_ips(timeout=30):
        return

    # Run the updates
    container.attach_wait(lxc.attach_run_command,command)
    # Shutdown the container
    if started:
        if not container.shutdown(30):
            container.stop()

def main():
    command = list()
    for arg in sys.argv[1:]:
        command.append(arg)
    for container in lxc.list_containers(as_object=True):
        execute(container,command)

if __name__=='__main__':
    main()
