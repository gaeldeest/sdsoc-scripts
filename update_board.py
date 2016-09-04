#!/usr/bin/env python

from os import path
import os, glob, sys
import pysftp
import paramiko
import time
from optparse import OptionParser

def copy_files(host, project_dir, timeout):
    cnopts = pysftp.CnOpts()
    cnopts.timeout = timeout
    cnopts.hostkeys = None

    print("Copying SD card content...")
    try:
        with pysftp.Connection(host, username='root', password='root', cnopts=cnopts) as sftp:
            sftp.put_r(path.join(project_dir, "sd_card"), "/mnt")
    except pysftp.ConnectionException:
        print("Error connecting to host.")
        sys.exit(-1)
    except KeyboardInterrupt:
        print("User interrupted connection..")
        sys.exit(-1)

def reboot(host, timeout):
    print("Rebooting the board...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='root', password='root', timeout=timeout)
    ssh.exec_command("/sbin/reboot -f > /dev/null 2>&1 &", timeout=timeout)
    ssh.close()

def wait_for_reboot_and_ssh(host, ntrials, wait, timeout):
    for i in range(ntrials):
        try:
            print("Trying to connect... (attempt: %d/%d)" %(i+1, ntrials))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username='root', password='root', timeout=timeout)
            print("Success !")
            return ssh
        except paramiko.ssh_exception.NoValidConnectionsError:
            print("FAILED ! Waiting %d seconds before retrying." % wait)
            time.sleep(wait)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--host", action="store", type="string", dest="host")
    parser.add_option("-d", "--project-dir", type="string", dest="project_dir", default=os.getcwd())
    parser.add_option("-t", "--timeout", type="int", dest="timeout", default=5)
    parser.add_option("-w", "--wait", type="int", dest="wait", default=5)
    parser.add_option("-n", "--trials", type="int", dest="ntrials", default=10)

    (options, args) = parser.parse_args(sys.argv)

    copy_files(options.host, options.project_dir, options.timeout)
    reboot(options.host, options.ntrials, options.wait, options.timeout)
    print(wait)

    print("Done.")
    time.sleep()

    wait_for_reboot_and_ssh(options.host, options.ntrials, options.wait, options.timeout)
