import re
import os.path
from sys import exit, argv
from regex_example import parse_section, regex_section, regExFindIP

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

br_empty = set()
br_single = set()
br_inactive = set()
br_in_ipaddr = set()
int_single = set()
vlans_free = set()
eoip_free = set()
ip_free = set()

general_param = dict([['--empty', ('Бриджы без портов', br_empty)],
                      ['--single', ('Бриджы с одним портом', br_single)],
                      ['--intsingle', ('Одиночные интерфейсы в бриджах', int_single)],
                      ['--vlans_free', ('Вланы, которых нет ни в бриджах, ни в IP адресах, ни в bonding', vlans_free)],
                      ['--eoip_free', ('EOIP, которых нет ни в бриджах, ни во вланах, ни в bonding', eoip_free)],
                      ['--ip_free',
                       ('Remote ip адреса из PPP and EOIP которых нет в ТУ и нет в активных PPP', ip_free)]
                      ])

key_param = ''
for key, value in general_param.items():
    key_param += f'if use key "{key}"\t - {value[0]}\n   '

description = f''' 
parse_config.exe export_compact.rsc [-tu ip_from_address_plan.txt] [-active ip_ppp_active_from_cm.txt] 
[{'|'.join(general_param)}]

export_compact.rsc - файл с конфигурацией, полученный командой /export compact file=export_compact
-tu file_name - файл с ip адересами из ТУ КРУС
-active file_name - файл с активными сессиями PPP на, получен командой /ppp active pr file=ip_ppp_active_from_cm

2. {key_param}
Если ни один ключ не указан выводятся все!

Для записи данных в файл в конце команды допишите " > output_file_name.txt"

Пример: parse_config.exe export_compact.rsc -tu ip_from_address_plan.txt -active ip_ppp_active_from_cm.txt > out_file.txt
'''

config = ''
ip_from_tu = set()
ip_active_ppp = set()
int_ip_addr = set()
port_in_bridges = set()
vlans = set()


def print_bridge(params):
    res = ''
    for param in params:
        s = f"{general_param[param][0].capitalize()} - {len(general_param[param][1])}.\n"
        res += s
        print(s)
    for param in params:
        s = f"\n---{general_param[param][0].capitalize()} - {len(general_param[param][1])}:\n"
        s += '\n'.join(general_param[param][1])+'\n'
        res += s
        print(s)
    return res

# Получаем список IP адресов из текста с помощью регулярного выражения
def getipfromfile(filename, regex):
    with open(filename, encoding='ANSI') as file:
        return list(re.findall(regex, file.read()))


def get_ip_free():
    """
DONE! ToDo: Сравнить IP адреса из PPP secrets и remote address из EOIP с адресами в ТУ (ip_from_address_plan.txt)
       Исключить активные PPP (ppp_active_from_cm.txt)
    """
    ip_ppp = set(parse_section(regex_section.ppp_secret, config))
    ip_eoip = set(parse_section(regex_section.interface_eoip, config, 3))
    ip_free.update((ip_ppp | ip_eoip) - ip_from_tu - ip_active_ppp)
    return ip_free


def get_eoip_free():
    """
2. DONE! ToDo: Исключить те EOIP которых нет в бридж портах, вланах, bonding
    """
    name_eoip = set(parse_section(regex_section.interface_eoip, config))
    int_vlans = set(parse_section(regex_section.interface_vlan, config, 2))
    eoip_free.update(name_eoip - port_in_bridges - set(int_ip_addr) - int_vlans - bonding)
    return eoip_free


def get_bridges():
    """
4. DONE! ToDo: Исключить бриджы которые участвуют в "ip addresses"
            Вывести бриджы без портов
            Вывести бриджы с одним портом и эти одиночные порты
    """
    all_bridges = set(parse_section(regex_section.interface_bridge, config))  # получаем все бриджи из конфига
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
            if ports[0] not in (int_ip_addr|bonding):  # исключаем интерфейсы которые есть в "ip addresss" и в bonding
                int_single.add(ports[0])

    return [br_empty, br_single, int_single]


def get_vlans_free():
    """
5. DONE! ToDo: Вывести вланы, не участвующие в бриджах и в "ip addresses"
    """
    vlans_free.update(set(vlans) - set(int_ip_addr) - set(port_in_bridges) - bonding - int_vlans)
    return vlans_free


if __name__ == '__main__':
    print(description)

    if len(argv) > 1:
        config_file = argv[1]
    else:
        config_file = 'export_compact.rsc'

    if '-tu' in argv:
        file_tu = argv[argv.index('-tu') + 1]
    else:
        file_tu = 'ip_from_address_plan.txt'

    if '-active' in argv:
        file_active = argv[argv.index('-active') + 1]
    else:
        file_active = 'ip_ppp_active_from_cm.txt'

    if not os.path.exists(config_file):
        print(f'! Error: Конфигурационный файл "{config_file}" не указан или не существует.')
        input('Для выхода нажмите ENTER...', )
        exit()
    if not os.path.exists(file_active):
        print(f'! Warning: Файл с IP адресами из PPP active "{file_active}" не указан или не существует.')
        file_active = ''
    if not os.path.exists(file_tu):
        print(f'! Warning: Файл с IP адресами из ТУ "{file_tu}" не указан или не существует.')
        file_tu = ''

    # file_tu = ''
    # file_active = ''
    if file_tu:
        ip_from_tu.update(set(getipfromfile(file_tu, regExFindIP)))

    if file_active:
        ip_active_ppp.update(set(getipfromfile(file_active, regExFindIP)))

    with open(config_file, encoding='ANSI') as file:
        config = file.read()

    bonding = set()
    s = parse_section(regex_section.interface_bonding, config)
    [bonding.update(set(i)) for i in s]



    int_ip_addr = set(parse_section(regex_section.ip_address, config))
    port_in_bridges = set(parse_section(regex_section.interface_bridge_port, config, reg_id=2))
    vlans = set(parse_section(regex_section.interface_vlan, config))  # получаем список всех влан
    int_vlans = set(parse_section(regex_section.interface_vlan, config, reg_id=2))  # список портов на которых есть влан

    get_bridges()
    get_vlans_free()
    get_eoip_free()
    get_ip_free()

    param = argv & general_param.keys()

    output_msg = f'''--- Результат анализа конфигурации из файла "{config_file}"
Исключены remote ip находящиеся в файлах "{file_tu}" и "{file_active}" 
'''
    print(output_msg)

    if param:
        to_file = print_bridge(param)
    else:
        to_file = print_bridge(general_param.keys())

    print('\nThe End!')

    with open('output_file.txt','w', encoding='ANSI',) as file:
        file.write(output_msg + to_file)

    input('For exit press ENTER...', )
    # os.system('pause')
