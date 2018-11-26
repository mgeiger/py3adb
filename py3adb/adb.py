import sys
import os
import subprocess


class ADB:
    PYADB_VERSION = "3.0.4"

    # reboot modes
    REBOOT_RECOVERY = 1
    REBOOT_BOOTLOADER = 2

    # default TCP/IP port
    DEFAULT_TCP_PORT = 5555
    # default TCP/IP host
    DEFAULT_TCP_HOST = "localhost"

    def pyadb_version(self):
        return self.PYADB_VERSION

    def __init__(self, adb_path=None):
        self._adb_path = adb_path
        self._output = None
        self._error = None
        self._return = 0
        self._devices = None
        self._target = None

    def _clean(self):
        self._output = None
        self._error = None
        self._return = 0

    def _parse_output(self, outstr):
        ret = None

        if len(outstr) > 0:
            ret = outstr.splitlines()

        return ret

    def _build_command(self, cmd):
        ret = None

        if (
            self._devices is not None
            and len(self._devices) > 1
            and self._target is None
            and "devices" not in cmd
        ):
            self._error = "Must set target device first"
            self._return = 1
            return ret

        # Modified function to directly return command set for Popen
        #
        # Unfortunately, there is something odd going on and the argument list is not being properly
        # converted to a string on the windows 7 test systems.  To accomodate, this block explitely
        # detects windows vs. non-windows and builds the OS dependent command output
        #
        # Command in 'list' format: Thanks to Gil Rozenberg for reporting the issue
        #
        if sys.platform.startswith("win"):
            ret = self._adb_path + " "
            if self._target is not None:
                ret += "-s " + self._target + " "
            if isinstance(cmd, type([])):
                ret += " ".join(cmd)
            else:
                ret += cmd
        else:
            ret = [self._adb_path]
            if self._target is not None:
                ret += ["-s", self._target]

            if isinstance(cmd, type([])):
                for i in cmd:
                    ret.append(i)
            else:
                ret += [cmd]

        return ret

    def get_output(self):
        return self._output

    def get_error(self):
        return self._error

    def get_return_code(self):
        return self._return

    def lastFailed(self):
        """
        Did the last command fail?
        """
        if self._output is None and self._error is not None and self._return:
            return True
        return False

    def run_cmd(self, cmd):
        """
        Runs a command by using adb tool ($ adb <cmd>)
        """
        self._clean()

        if not self._adb_path:
            self._error = "ADB path not set"
            self._return = 1
            return

        # For compat of windows
        cmd_list = self._build_command(cmd)

        try:
            adb_proc = subprocess.Popen(
                cmd_list,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
            )
            (self._output, self._error) = adb_proc.communicate()
            self._return = adb_proc.returncode
            self._output = self._output.decode("utf-8")
            self._error = self._error.decode("utf-8")

            if len(self._output) == 0:
                self._output = None
            else:
                self._output = [
                    x.strip() for x in self._output.split("\n") if len(x.strip()) > 0
                ]

            if len(self._error) == 0:
                self._error = None

        except:
            pass

        return self._error, self._output

    def get_version(self):
        """
        Returns ADB tool version
        adb version
        """
        self.run_cmd("version")
        try:
            ret = self._output[0].split()[-1:][0]
        except:
            ret = None
        return ret

    def check_path(self):
        """
        Intuitive way to verify the ADB path
        """
        if not self.get_version():
            return False
        return True

    def set_adb_path(self, adb_path):
        """
        Sets ADB tool absolute path
        """
        if not os.path.isfile(adb_path):
            return False
        self._adb_path = adb_path
        return True

    def get_adb_path(self):
        """
        Returns ADB tool path
        """
        return self._adb_path

    def start_server(self):
        """
        Starts ADB server
        adb start-server
        """
        self._clean()
        self.run_cmd("start-server")
        return self._output

    def kill_server(self):
        """
        Kills ADB server
        adb kill-server
        """
        self._clean()
        self.run_cmd("kill-server")

    def restart_server(self):
        """
        Restarts ADB server
        """
        self.kill_server()
        return self.start_server()

    def restore_file(self, file_name):
        """
        Restore device contents from the <file> backup archive
        adb restore <file>
        """
        self._clean()
        self.run_cmd(["restore", file_name])
        return self._output

    def wait_for_device(self):
        """
        Blocks until device is online
        adb wait-for-device
        """
        self._clean()
        self.run_cmd("wait-for-device")
        return self._output

    def get_help(self):
        """
        Returns ADB help
        adb help
        """
        self._clean()
        self.run_cmd("help")
        return self._output

    def get_devices(self):
        """
        Returns a list of connected devices
        adb devices
        mode serial/usb
        """
        error = 0
        self._devices = None
        self.run_cmd("devices")
        if self._error is not None:
            return 1, self._devices
        try:
            self._devices = [x.split()[0] for x in self._output[1:]]
        except Exception:
            self._devices = None
            error = 2

        return error, self._devices

    def set_target_device(self, device):
        """
        Select the device to work with
        """
        self._clean()
        if device is None or device not in self._devices:
            self._error = "Must get device list first"
            self._return = 1
            return False
        self._target = device
        return True

    def get_target_device(self):
        """
        Returns the selected device to work with
        """
        return self._target

    def get_state(self):
        """
        Get ADB state
        adb get-state
        """
        self._clean()
        self.run_cmd("get-state")
        return self._output

    def get_serialno(self):
        """
        Get serialno from target device
        adb get-serialno
        """
        self._clean()
        self.run_cmd("get-serialno")
        return self._output

    def reboot_device(self, mode):
        """
        Reboot the target device
        adb reboot recovery/bootloader
        """
        self._clean()
        if mode not in (self.REBOOT_RECOVERY, self.REBOOT_BOOTLOADER):
            self._error = "mode must be REBOOT_RECOVERY/REBOOT_BOOTLOADER"
            self._return = 1
            return self._output
        self.run_cmd(
            [
                "reboot",
                "%s" % "recovery" if mode == self.REBOOT_RECOVERY else "bootloader",
            ]
        )
        return self._output

    def set_adb_root(self):
        """
        restarts the adbd daemon with root permissions
        adb root
        """
        self._clean()
        self.run_cmd("root")
        return self._output

    def set_system_rw(self):
        """
        Mounts /system as rw
        adb remount
        """
        self._clean()
        self.run_cmd("remount")
        return self._output

    def get_remote_file(self, remote, local):
        """
        Pulls a remote file
        adb pull remote local
        """
        self._clean()
        self.run_cmd(["pull", remote, local])

        if self._error is not None and "bytes in" in self._error:
            self._output = self._error
            self._error = None

        return self._output

    def push_local_file(self, local, remote):
        """
        Push a local file
        adb push local remote
        """
        self._clean()
        self.run_cmd(["push", local, remote])
        return self._output

    def shell_command(self, cmd):
        """
        Executes a shell command
        adb shell <cmd>
        """
        self._clean()
        self.run_cmd(["shell", cmd])
        return self._output

    def listen_usb(self):
        """
        Restarts the adbd daemon listening on USB
        adb usb
        """
        self._clean()
        self.run_cmd("usb")
        return self._output

    def listen_tcp(self, port=DEFAULT_TCP_PORT):
        """
        Restarts the adbd daemon listening on the specified port
        adb tcpip <port>
        """
        self._clean()
        self.run_cmd(["tcpip", port])
        return self._output

    def get_bugreport(self):
        """
        Return all information from the device that should be included in a bug report
        adb bugreport
        """
        self._clean()
        self.run_cmd("bugreport")
        return self._output

    def get_jdwp(self):
        """
        List PIDs of processes hosting a JDWP transport
        adb jdwp
        """
        self._clean()
        self.run_cmd("jdwp")
        return self._output

    def get_logcat(self, lcfilter=""):
        """
        View device log
        adb logcat <filter>
        """
        self._clean()
        self.run_cmd(["logcat", lcfilter])
        return self._output

    def run_emulator(self, cmd=""):
        """
        Run emulator console command
        """
        self._clean()
        self.run_cmd(["emu", cmd])
        return self._output

    def connect_remote(self, host=DEFAULT_TCP_HOST, port=DEFAULT_TCP_PORT):
        """
        Connect to a device via TCP/IP
        adb connect host:port
        """
        self._clean()
        self.run_cmd(["connect", "%s:%s" % (host, port)])
        return self._output

    def disconnect_remote(self, host=DEFAULT_TCP_HOST, port=DEFAULT_TCP_PORT):
        """
        Disconnect from a TCP/IP device
        adb disconnect host:port
        """
        self._clean()
        self.run_cmd(["disconnect", "%s:%s" % (host, port)])
        return self._output

    def ppp_over_usb(self, tty=None, params=""):
        """
        Run PPP over USB
        adb ppp <tty> <params>
        """
        self._clean()
        if tty is None:
            return self._output

        cmd = ["ppp", tty]
        if params != "":
            cmd += params

        self.run_cmd(cmd)
        return self._output

    def sync_directory(self, directory=""):
        """
        Copy host->device only if changed (-l means list but don't copy)
        adb sync <dir>
        """
        self._clean()
        self.run_cmd(["sync", directory])
        return self._output

    def forward_socket(self, local=None, remote=None):
        """
        Forward socket connections
        adb forward <local> <remote>
        """
        self._clean()
        if local is None or remote is None:
            return self._output
        self.run_cmd(["forward", local, remote])
        return self._output

    def uninstall(self, package=None, keepdata=False):
        """
        Remove this app package from the device
        adb uninstall [-k] package
        """
        self._clean()
        if package is None:
            return self._output

        cmd = "uninstall "
        if keepdata:
            cmd += "-k "
        cmd += package
        self.run_cmd(cmd.split())
        return self._output

    def install(self, fwdlock=False, reinstall=False, sdcard=False, pkgapp=None):
        """
        Push this package file to the device and install it
        adb install [-l] [-r] [-s] <file>
        -l -> forward-lock the app
        -r -> reinstall the app, keeping its data
        -s -> install on sdcard instead of internal storage
        """
        self._clean()
        if pkgapp is None:
            return self._output

        cmd = "install "
        if fwdlock is True:
            cmd += "-l "
        if reinstall is True:
            cmd += "-r "
        if sdcard is True:
            cmd += "-s "

        cmd += pkgapp
        self.run_cmd(cmd.split())
        return self._output

    def find_binary(self, name=None):
        """
        Look for a binary file on the device
        """

        self.run_cmd(["shell", "which", name])

        if self._output is None:  # not found
            self._error = "'%s' was not found" % name
        elif self._output[0] == "which: not found":  # 'which' binary not available
            self._output = None
            self._error = "which binary not found"
