class OpenVpn:
    id = None
    host_name = None
    ip = None
    current_connection = None
    max_connection = None
    city = None
    country = None
    vpn_type = None
    cpu = None
    ram = None
    lastTimeSync = None
    online = None
    source = None
    config = None

    def __init__(self, idVpn, host_name, ip, current_connection, max_connection, city, country, vpn_type, cpu, ram,
                 lastTimeSync, online, source, config):
        self.id = idVpn
        self.host_name = host_name
        self.ip = ip
        self.current_connection = current_connection
        self.max_connection = max_connection
        self.city = city
        self.country = country
        self.vpn_type = vpn_type
        self.cpu = cpu
        self.ram = ram
        self.lastTimeSync = lastTimeSync
        self.online = online
        self.source = source
        self.config = config
