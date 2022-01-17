# Поиск IP адреса
from collections import namedtuple

regExFindIP = r'\d+\.\d+\.\d+\.\d+'

# Поиск ip адресов в EOIP
regExFindEOIP = r'local-address=(\d+\.\d+\.\d+\.\d+)[.\s]+remote-address=(\d+\.\d+\.\d+\.\d+)'

# Поиск LocalIP адреса в EOIP
regExFindLocalIPfromEOIP = r'local-address=(\d+\.\d+\.\d+\.\d+)\b'

# Поиск RemoteIP адреса в EOIP
regExFindRemoteIPfromEOIP = r'remote-address=(\d+\.\d+\.\d+\.\d+)\b'

# Поиск бриджей
regExFind_bridge = r'name="([\w\W]+?)"'

# Поиск бридж портов
regExFind_br_port = r'interface=([\w\W]+?)(?: \n +| )bridge=([\w\W]+?)(?:[\s]priority=| \n)'

# Поиск интерфейсов в "ip addresses"
regExFind_interface = r'interface=(.+?)(?: \n +| )actual-interface'


# формирование регулярного выражения для заданной секции для выборки из "export_compact"
def new_regex_section(section):
    return rf'\{section}\n([\s\S]+?)\n\/'

# Выбор одноименной секции из export_compact
sections=dict([
    ('interface_bridge', ['regex field for interface bridge']),
    ('interface_eoip', ['regex field for interface eoip']),
    ('interface_vlan',[]),
    ('interface_bridge_port',[]),
    ('ppp_secret',[]),
    ('ip_address',[])
])

Regex_sections = namedtuple('Regex_sections', sections)

regex_section = Regex_sections._make([
    [new_regex_section('/'+section.replace('_',' '))] + sections[section] for section in Regex_sections._fields
])

regex_section = regex_section._replace(interface_eoip=regex_section.interface_eoip+[
    'regex field for interface eoip'
])
regex_section = regex_section._replace(interface_bridge=regex_section.interface_bridge+[
    'regex field for interface bridge'
])
