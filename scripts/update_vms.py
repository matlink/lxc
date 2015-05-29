#! /usr/bin/python3
import lxc
import sys

for container in lxc.list_containers(as_object=True):
    # Start the container (if not started)
    started=False
    if not container.running:
        if not container.start():
            continue
        started=True

    if not container.state == "RUNNING":
        continue

    # Wait for connectivity
    if not container.get_ips(timeout=30):
        continue

    # Run the updates
    container.attach_wait(lxc.attach_run_command,
                          ["apt-get", "update"])
    container.attach_wait(lxc.attach_run_command,
                          ["apt-get", "dist-upgrade", "-y"])

    # Shutdown the container
    if started:
        if not container.shutdown(30):
            container.stop()
