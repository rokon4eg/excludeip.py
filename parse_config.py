import sys
from pprint import pprint

# from br_port_check import general_param, \
#     int_ip_addr, br_empty, br_single, int_single, vlans_free, eoip_free, \
#     print_bridge, ip_free
from br_port_check import *
from excludeip import getipfromfile, regExFindIP
from regex_example import parse_section, regex_section

f'''
1. Сравнить IP адреса из PPP secrets с адресами в ТУ (ip_from_address_plan.txt)
Исключить активные PPP (ppp_active_from_cm.txt)

2. Исключить те EOIP для которых local-addresses участвуют в "ip addresses"

3. Исключить те EOIP для которых remote-addresses есть в ТУ (ip_from_address_plan.txt)
Исключить активные PPP (ppp_active_from_cm.txt)

4. Исключить бриджы которые участвуют в "ip addresses"
Вывести бриджы без портов
Вывести бриджы с одним портом и эти одиночные порты

5. Вывести вланы, не участвующие в бриджах и в "ip addresses"
'''

description = f''' 
Ex.: python parse_config.py export_compact.txt.rsc [-tu ip_from_address_plan.txt] [-active ppp_active_from_cm.txt] 
[{'|'.join(general_param)}]
export_compact.txt.rsc - файл с конфигурацией полученый командой /export compact file=export_compact.txt
-tu file_name - файл с ip адересами из ТУ КРУС
-active file_name - файл с активными сессиями ppp на микротике
'''

config = ''
ip_from_tu = set()
ip_active_ppp = set()
int_ip_addr = set()
port_in_bridges = set()
vlans = set()


def get_ip_free():
    """
DONE! ToDo: Сравнить IP адреса из PPP secrets и remote address из EOIP с адресами в ТУ (ip_from_address_plan.txt)
       Исключить активные PPP (ppp_active_from_cm.txt)
    """
    ip_ppp = set(parse_section(regex_section.ppp_secret, config))
    ip_eoip = set(parse_section(regex_section.interface_eoip, config, 3))
    # ip_from_tu = set(getipfromfile(file_tu, regExFindIP))
    # ip_active = set()
    # if file_active:
    #     ip_active = set(getipfromfile(file_active, regExFindIP))
    ip_free.update((ip_ppp | ip_eoip) - ip_from_tu - ip_active_ppp)
    return ip_free


def get_ip_eoip():
    """
2. DONE! ToDo: Исключить те EOIP которых нет в бридж портах, вланах, ip addresses
    """
    name_eoip = set(parse_section(regex_section.interface_eoip, config))
    eoip_free.update(name_eoip - port_in_bridges - vlans - ip_from_tu)
    return eoip_free

def get_bridges():
    """
4. DONE! ToDo: Исключить бриджы которые участвуют в "ip addresses"
            Вывести бриджы без портов
            Вывести бриджы с одним портом и эти одиночные порты
    """

    class Res(list):
        def __str__(self):
            res = f'Empty bridges: {len(self[0])}. Bridges with single port: {len(self[1])}. Count free vlans: {len(self[2])}\n'
            res += f'Empty bridges: {len(self[0])}\n'
            res += "\n".join(self[0])

            res += f'\n\nSingle bridges: {len(self[1])}\n'
            res += "\n".join(self[1])

            res += f'\n\nFree vlans: {len(self[2])}\n'
            res += "\n".join(self[2])
            return res

    all_bridges = set(parse_section(regex_section.interface_bridge, config))  # получаем все бриджи из конфига
    # int_ip_addr = set(parse_section(regex_section.ip_address, config)) # получаем все порты на которых есть ip
    br_without_ipaddr = all_bridges - int_ip_addr  # исключаем бриджы на которых есть ip
    bridge_dict = dict([(bridge, []) for bridge in br_without_ipaddr])  # формируем словарь из бриджей, пока без портов
    bridge_ports = parse_section(regex_section.interface_bridge_port, config)  # получаем бриджы и порты из конфига
    for bridge, port in bridge_ports:
        if bridge in bridge_dict:
            bridge_dict[bridge] += [port]

    for bridge, ports in bridge_dict.items():
        if not ports:
            br_empty.add(bridge)
        elif len(ports) == 1:
            br_single.add(bridge)
            if ports[0] not in int_ip_addr:  # исключаем интерфейсы которые есть в "ip addresss"
                int_single.add(ports[0])

    # res = set()
    # return Res(res)
    return Res([br_empty, br_single, int_single])


def get_free_vlans():
    """
5. DONE! ToDo: Вывести вланы, не участвующие в бриджах и в "ip addresses"
    """

    class Res(list):
        def __str__(self):
            res = f'Total vlans:{self[1]}. Vlans in ip addresses: {self[2]}. Vlans in bridges: {self[3]}.\n' \
                  f'Count free vlans: {len(self[0])}\n'
            res += "\n".join(self[0])
            return res

    # vlans = parse_section(regex_section.interface_vlan, config)  # получаем список всех влан
    # int_ip_addr = parse_section(regex_section.ip_address, config)  # получаем список интерфейсов на которых есть ip
    # port_in_bridges = parse_section(regex_section.interface_bridge_port, config, reg_id=2)

    # Done: исключить вланы, участвующие в бриджах
    vlans_free.update(set(vlans) - set(int_ip_addr) - set(port_in_bridges))
    return Res([vlans_free, len(vlans), len(int_ip_addr), len(port_in_bridges)])


if __name__ == '__main__':
    config_file = 'export_compact.txt.rsc'
    ip_from_tu = set(getipfromfile('ip_from_address_plan.txt', regExFindIP))
    ip_active_ppp = set(getipfromfile('ppp_active_from_cm.txt', regExFindIP))

    # if len(sys.argv) < 2:
    #     print(description)
    #     exit()
    # else:
    #     config_file = sys.argv[1]
    # file_tu = ''
    # file_active = ''
    # if '-tu' in sys.argv:
    #     file_tu = sys.argv[sys.argv.index('-tu') + 1]
    #     ip_from_tu.update(set(getipfromfile(file_tu, regExFindIP)))
    # if '-active' in sys.argv:
    #     ip_active_ppp = sys.argv[sys.argv.index('-active') + 1]
    #     ip_active_ppp.update(set(getipfromfile(file_active, regExFindIP)))

    with open(config_file, encoding='ANSI') as file:
        config = file.read()

    int_ip_addr = set(parse_section(regex_section.ip_address, config))
    port_in_bridges = set(parse_section(regex_section.interface_bridge_port, config, reg_id=2))
    vlans = set(parse_section(regex_section.interface_vlan, config))  # получаем список всех влан

    get_bridges()
    get_free_vlans()
    get_ip_eoip()
    get_ip_free()

    param = sys.argv & general_param.keys()
    if not param:
        for key in general_param:
            print_bridge(key)
    else:
        while param:
            print_bridge(param.pop())

    print('The End!')
