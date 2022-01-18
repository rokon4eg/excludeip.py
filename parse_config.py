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
    """1. Сравнить IP адреса из PPP secrets с адресами в ТУ (ip_from_address_plan.txt)
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
2. Исключить те EOIP для которых local-addresses участвуют в "ip addresses"

3. Исключить те EOIP для которых remote-addresses есть в ТУ (ip_from_address_plan.txt)
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

def get_bridges(config, file_tu):
    """
4. Исключить бриджы которые участвуют в "ip addresses"
Вывести бриджы без портов
Вывести бриджы с одним портом и эти одиночные порты
    """
    res = set()
    return res

def get_vlans(config):
    """
5. Вывести вланы, не участвующие в бриджах и в "ip addresses"
    """
    vlans = parse_section(regex_section.interface_vlan, config)  # получаем список всех влан
    int_ip_addr = parse_section(regex_section.ip_address, config)  # получаем список интерфейсов на которых есть ip
    res = set(vlans) - set(int_ip_addr)
    # ToDo: исключить вланы, участвующие в бриджах
    return res

if __name__ == '__main__':
    ipfile = 'export_compact.txt.rsc'
    with open(ipfile, encoding='ANSI') as file:
        config = file.read()

    vlans = get_vlans(config)
    print('Count vlans:', len(vlans))
    pprint(vlans)