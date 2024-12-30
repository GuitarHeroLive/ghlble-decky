import os
import decky
import asyncio
import subprocess
import signal
import psutil

class Plugin:
    async def startDBus(self):
        try:
            result = subprocess.run(
                ["dbus-launch", "--sh-syntax"],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.splitlines():
                if line.startswith("DBUS_SESSION_BUS_ADDRESS") or line.startswith("DBUS_SESSION_BUS_PID"):
                    key, value = line.split("=", 1)
                    value = value.rstrip(";")
                    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
                        value = value[1:-1]
                    os.environ[key] = value
        except Exception as e:
            decky.logger.error(f"DBus couldn't be started: {str(e)}")

    async def stopDBus(self):
        dbus_pid = os.environ.get("DBUS_SESSION_BUS_PID")
        if dbus_pid:
            try:
                dbus_pid = int(dbus_pid)
                proc = psutil.Process(dbus_pid)
                proc.terminate()
                proc.wait()
            except Exception as e:
                pass

    async def daemonStop(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == 'ghlble':
                    proc.terminate()
            except Exception as e:
                continue
        await self.stopDBus()

    async def daemonStart(self):
        try:
            await self.daemonStop()
            await self.startDBus()
            self.daemon = await asyncio.create_subprocess_exec(os.path.join(os.path.dirname(__file__), "bin/ghlble"), "--daemon", env=os.environ.copy())
        except Exception as e:
            decky.logger.error(f"Daemon couldn't be started: {str(e)}")

    async def daemonSetScan(self, enabled: bool):
        if enabled:
            await self.daemonStart()
        else:
            try:
                await asyncio.create_subprocess_exec(os.path.join(os.path.dirname(__file__), "bin/ghlble"), "--scan=off", env=os.environ.copy())
            except Exception as e:
                decky.logger.warning(f"Scan couldn't be stopped: {str(e)}")

    async def daemonGetScan(self):
        try:
            process = await asyncio.create_subprocess_exec(os.path.join(os.path.dirname(__file__), "bin/ghlble"), "--scan", env=os.environ.copy(), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                return False
            output = stdout.decode().strip()
            if output == "Scan status: Scanning":
                return True
            elif output == "Scan status: Not scanning":
                return False
            else:
                return False
        except Exception as e:
            return False

    async def _migration(self):
        pass

    async def _main(self):
        pass

    async def _unload(self):
        await self.daemonStop()

    async def _uninstall(self):
        pass