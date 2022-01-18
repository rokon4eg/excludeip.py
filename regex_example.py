import re

from collections import namedtuple
from pprint import pprint

regex_flash = r'\\\n *'  # удаление переносов из конфигурационного файла

# формирование регулярного выражения для заданной секции для выборки из "export_compact"
def new_regex_section(section):
    return rf'\{section}\n([\s\S]+?)\n\/'


def parse_section(section, config):
    # pass
    config = re.sub(regex_flash, '', config)  # удаление переносов из конфигурационного файла
    section_config = re.findall(section[0], config)[0]
    res = re.findall(section[1], section_config)
    return res


# Выбор одноименной секции из export_compact
sections = dict([
    ('interface_bridge', [r'add(?:.+)name=(.+?)(?: protocol-mode|\n)']),  # возвращает имя bridge
    ('interface_eoip', [r'add\b(?:.+?)local-address=((?:\d+\.){3}\d+)(?:.+?)remote-address=((?:\d+\.){3}\d+)']),
    # возвращает local-address, remote-address
     # [r'add\b(?:.+?)local-address=((?:\d+\.){3}\d+)(?:.+?)name=(.+?) remote-address=((?:\d+\.){3}\d+)']),
    ('interface_vlan', [r'add(?:.+)name=(.+?)(?: vlan-id|\n)']),  # возвращает имя vlan
    ('interface_bridge_port', [r'add\b(?:.+?)bridge=(.+)(?:.+?)interface=(.+?)\n']),  # возвращает bridge и interface
    ('ppp_secret', [r'add(?:.+)remote-address=((?:\d+\.){3}\d+)(?: service|\n| )']), # возвращает remote-address
    ('ip_address', [r'add(?:.+)interface=(.+?)(?: network|\n)']) # возвращает interface
])

Regex_sections = namedtuple('Regex_sections', sections)

regex_section = Regex_sections._make([
    [new_regex_section('/' + section.replace('_', ' '))] + sections[section] for section in Regex_sections._fields
])

if __name__ == '__main__':
    ipfile = 'export_compact.txt.rsc'
    with open(ipfile, encoding='ANSI') as file:
        config = file.read()

    # print(parse_section(regex_section.interface_bridge, config))
    pprint(parse_section(regex_section.interface_eoip, config))
    # pprint(parse_section(regex_section.interface_vlan, config))
    # pprint(parse_section(regex_section.interface_bridge_port, config))
    # pprint(parse_section(regex_section.ppp_secret, config))
    # pprint(set(parse_section(regex_section.ip_address, config)))