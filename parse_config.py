from pprint import pprint

from br_port_check import bridge_param
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

Ex.: python parse_config.py export_compact.txt.rsc [-tu ip_from_address_plan.txt] [-active ppp_active_from_cm.txt] 
[{'|'.join(bridge_param)}]
'''


def get_ip_secrets(config, file_tu, file_active=None):
    """
ToDo: Сравнить IP адреса из PPP secrets с адресами в ТУ (ip_from_address_plan.txt)
      Исключить активные PPP (ppp_active_from_cm.txt)
    """
    res = set()

    def exclude_ip_from_tu():
        pass

    def exclude_ip_from_active():
        pass

    return res


def get_ip_eoip(config, file_tu, file_active=None):
    """
2. ToDo: Исключить те EOIP для которых local-addresses участвуют в "ip addresses"

3. ToDo : Исключить те EOIP для которых remote-addresses есть в ТУ (ip_from_address_plan.txt)
    Исключить активные PPP (ppp_active_from_cm.txt)
    """
    res = set()

    def exclude_local_eoip_from_tu():
        pass

    def exclude_remote_eoip_from_tu():
        pass

    def exclude_active():
        pass

    return res


def get_bridges(config):
    """
4. ToDo: Исключить бриджы которые участвуют в "ip addresses"
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

    br_empty = set()
    br_single = set()
    int_single = set()

    all_bridges = set(parse_section(regex_section.interface_bridge,config)) # получаем все бриджи из конфига
    int_ip_addr = set(parse_section(regex_section.ip_address, config)) # получаем все порты на которых есть ip
    br_without_ipaddr = all_bridges - int_ip_addr # исключаем бриджы на которых есть ip
    bridge_dict = dict([(bridge, []) for bridge in br_without_ipaddr])  # формируем словарь из бриджей, пока без портов
    bridge_ports = parse_section(regex_section.interface_bridge_port,config)  # получаем бриджы и порты из конфига
    for bridge, port in bridge_ports:
        if bridge in bridge_dict:
            bridge_dict[bridge] += [port]

    for bridge, ports in bridge_dict.items():
        if not ports:
            br_empty.add(bridge)
        elif len(ports) == 1:
            br_single.add(bridge)
            if ports[0] not in int_ip_addr: # исключаем интерфейсы которые есть в "ip addresss"
                int_single.add(ports[0])


    # res = set()
    # return Res(res)
    return Res([br_empty,br_single,int_single])

def get_free_vlans(config):
    """
5. DONE! ToDo: Вывести вланы, не участвующие в бриджах и в "ip addresses"
    """
    class Res(list):
        def __str__(self):
            res = f'Total vlans:{self[1]}. Vlans in ip addresses: {self[2]}. Vlans in bridges: {self[3]}.\n' \
                  f'Count free vlans: {len(self[0])}\n'
            res += "\n".join(self[0])
            return res

    vlans = parse_section(regex_section.interface_vlan, config)  # получаем список всех влан
    int_ip_addr = parse_section(regex_section.ip_address, config)  # получаем список интерфейсов на которых есть ip
    port_in_bridges = parse_section(regex_section.interface_bridge_port, config, reg_id=2)
    # Done: исключить вланы, участвующие в бриджах

    free_vlans = set(vlans) - set(int_ip_addr) - set(port_in_bridges)
    return Res([free_vlans, len(vlans), len(int_ip_addr), len(port_in_bridges)])


if __name__ == '__main__':
    ipfile = 'export_compact.txt.rsc'
    file_tu = 'ip_from_address_plan.txt'
    with open(ipfile, encoding='ANSI') as file:
        config = file.read()

    # vlans = get_free_vlans(config)
    # print(vlans)

    bridge = get_bridges(config)
    print(bridge)
