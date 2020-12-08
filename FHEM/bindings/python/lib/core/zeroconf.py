import asyncio
import socket
from zeroconf import Zeroconf, ServiceInfo


class zeroconf:

    instance = None

    def get_instance(logger):
        if zeroconf.instance is None:
            zeroconf.instance = zeroconf(logger)
        return zeroconf.instance

    def __init__(self, logger):
        self.logger = logger
        self.loop = asyncio.get_event_loop()
        self.zeroconf = Zeroconf()

    async def create_service(self, type, name, port, properties):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        info = ServiceInfo(
            type + "._tcp.local.",
            name + "." + type + "._tcp.local.",
            addresses=[socket.inet_aton(local_ip)],
            port=port,
            properties=properties,
            server=hostname + ".local.",
        )
        self.zeroconf.register_service(info)

    def get_zeroconf(self):
        return self.zeroconf

    def stop(self):
        self.zeroconf.close()