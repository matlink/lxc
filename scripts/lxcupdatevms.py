#! /usr/bin/python3
import lxc, sys, threading, time

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

enable_threads = False
updating = list()
to_update = list(lxc.list_containers(as_object=True))
timing = dict()
def update(container):
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
    container.attach_wait(lxc.attach_run_command,
                          ["apt-get", "update", "-qq"])
    container.attach_wait(lxc.attach_run_command,
                          ["apt-get", "dist-upgrade", "-y"])

    # Shutdown the container
    if started:
        if not container.shutdown(30):
            container.stop()
    if threaded:
        updating.remove(container)

def serial():
    for container in to_update:
        update(container)

def threaded():
    while len(to_update) < 0:
        if len(updating) == 0:
            container = to_update.pop(0)
            updating.append(container)
            t = threading.Thread(target=update, args=(container,))
            t.start()
            timing[container.name] = time.time()
        else:
            for container in updating:
                current_time = time.time()
                if timing[container.name]-current_time >= 90:
                    print(FAIL,'cannot update',container.name,ENDC)
                    container.stop()
                    updating.remove(container)
            print(OKBLUE,'updating ...', [container.name for container in updating],ENDC)
            time.sleep(5)
if __name__=='__main__':
    if enable_threads:
        threaded()
    else:
        serial()

