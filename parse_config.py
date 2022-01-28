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

output_file = 'output_file.txt'

br_empty = set()
br_single = set()
br_inactive = set()
br_in_ipaddr = set()
# int_single = set()
int_single_dict = dict()
vlans_free = set()
eoip_free = set()
ip_free = set()

general_param = dict([['--empty', ('Бриджы без портов', br_empty,
                                   '/interface bridge port print where bridge="{0}"\t'
                                   '/interface bridge disable [find where name="{0}"]')],
                      ['--single', ('Бриджы с одним портом', br_single,
                                    '/interface bridge port print where bridge="{0}"\t'
                                    '/interface bridge disable [find where name="{0}"]')],
                      ['--intsingle', ('Одиночные интерфейсы в бриджах', int_single_dict,
                                       '/interface {1} print where name="{0}"\t'
                                       '/interface {1} disable [find where name="{0}"]')],
                      ['--vlans_free', ('Вланы, которых нет ни в бриджах, ни в IP адресах, ни в bonding', vlans_free,
                                        '/interface vlan print where name="{0}"\t'
                                        '/interface vlan disable [find where name="{0}"]')],
                      ['--eoip_free', ('EOIP, которых нет ни в бриджах, ни во вланах, ни в bonding', eoip_free,
                                       '/interface eoip print where name="{0}"\t'
                                       '/interface eoip disable [find where name="{0}"]')],
                      ['--ip_free',
                       ('Remote ip адреса из PPP and EOIP которых нет в ТУ и нет в активных PPP', ip_free,
                        '/interface eoip print where remote-address={0}\t'
                        '/interface eoip disable [find where remote-address={0}]')]
                      ])

key_param = ''
for key, value in general_param.items():
    key_param += f'if use key "{key}"\t - {value[0]}\n   '

description = f''' 
parse_config.exe export_compact.rsc [-tu ip_from_address_plan.txt] [-active ip_ppp_active_from_cm.txt] 
[{'|'.join(general_param)}] [-out {output_file}]

export_compact.rsc - файл с конфигурацией, полученный командой /export compact file=export_compact
-tu file_name - файл с ip адересами из ТУ КРУС
-active file_name - файл с активными сессиями PPP на, получен командой /ppp active pr file=ip_ppp_active_from_cm

-out file_name - файл для вывода результата, по-умолчанию {output_file}

2. {key_param}
Если ни один ключ не указан выводятся все!

Пример: parse_config.exe export_compact.rsc -tu ip_from_address_plan.txt -active ip_ppp_active_from_cm.txt -out file.txt
'''

config = ''
ip_from_tu = set()
ip_active_ppp = set()
int_ip_addr = set()
port_in_bridges = set()
vlans = set()


def exclude_int_in_bonding(int_list, slaves_list):
    res = set(int_list)
    for int in int_list:
        for slaves in slaves_list:
            if int in slaves:
                res.remove(int)
                break
    return res


def print_interface(params):
    res = ''
    sum = 0
    for param in params:  # Формирование шапки
        count = len(general_param[param][1])
        stroka = f"{general_param[param][0].capitalize()} - {count}\n"
        sum += count
        res += stroka
        print(stroka)
    stroka = 'Итого: '+str(sum)+'\n'
    res += stroka
    print(stroka)

    for param in params:
        variable_for_print = general_param[param][1]
        template_for_print = general_param[param][2]
        s = f"\n---{general_param[param][0].capitalize()} - {len(variable_for_print)}:\n"
        if template_for_print:  # Проверка наличия шаблона для печати
            if type(variable_for_print) is dict:  # Если значения хранятся в словаре, значит есть доп параметр для печати
                for int_name, int_type in variable_for_print.items():
                    s += f"{int_name}\t{template_for_print.format(int_name, int_type)}\n"
            else:
                for int_name in variable_for_print:
                    s += f"{int_name}\t{template_for_print.format(int_name)}\n"
        else:
            s += '\n'.join(variable_for_print) + '\n'
        res += s
        # print(s)
    print(f'---Подробная информация в файле "{output_file}"---')
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

    int_vlans = set(parse_section(regex_section.interface_vlan, config, 2))
    eoip_int = name_eoip - port_in_bridges - int_ip_addr - int_vlans
    eoip_free.update(exclude_int_in_bonding(eoip_int, bonding))
    # DONE TODO переписать вычитание bonding с учетом проверки на вхождение
    return eoip_free


def get_bridges():
    """
4. DONE! ToDo: Исключить бриджы которые участвуют в "ip addresses"
            Вывести бриджы без портов
            Вывести бриджы с одним портом и эти одиночные порты
    """

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
            if ports[0] not in int_ip_addr:
                # исключаем интерфейсы которые есть в "ip addresss" и в bonding
                # DONE! TODO переписать вычитание bonding с учетом проверки на вхождение
                # int_single.update(exclude_int_in_bonding([ports[0]], bonding))
                # int = ''.join(exclude_int_in_bonding([ports[0]], bonding))
                if int := ''.join(exclude_int_in_bonding([ports[0]], bonding)):
                    type_int = ''
                    if int in name_eoip:
                        type_int = 'eoip'
                    elif int in vlans:
                        type_int = 'vlan'
                    int_single_dict.update({int:type_int})

    return [br_empty, br_single, int_single_dict]


def get_vlans_free():
    """
5. DONE! ToDo: Вывести вланы, не участвующие в бриджах и в "ip addresses"
    """
    vlans_free.update(exclude_int_in_bonding(vlans - int_ip_addr - port_in_bridges - int_vlans, bonding))
    # DONE! TODO переписать вычитание bonding с учетом проверки на вхождение
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

    if '-out' in argv:
        output_file = argv[argv.index('-out') + 1]

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
    bonding.update(set(s))
    all_bridges = set(parse_section(regex_section.interface_bridge, config))  # получаем все бриджи из конфига
    name_eoip = set(parse_section(regex_section.interface_eoip, config))

    int_ip_addr = set(parse_section(regex_section.ip_address, config))
    port_in_bridges = set(parse_section(regex_section.interface_bridge_port, config, reg_id=2))
    vlans = set(parse_section(regex_section.interface_vlan, config))  # получаем список всех влан
    int_vlans = set(parse_section(regex_section.interface_vlan, config, reg_id=2))  # список портов на которых есть влан

    get_bridges()
    get_vlans_free()
    get_eoip_free()
    if file_tu:
        get_ip_free()

    param = argv & general_param.keys()

    output_msg = f'''--- Результат анализа конфигурации из файла "{config_file}"
Исключены remote ip находящиеся в файлах "{file_tu}" и "{file_active}" 
Всего проанализировано: вланов - {len(vlans)}, еоип - {len(name_eoip)}, бриджей - {len(all_bridges)}, \
порт бриджей - {len(port_in_bridges)}, бондингов - {len(bonding)} 
'''
    print(output_msg)

    if param:
        to_file = print_interface(param)
    else:
        to_file = print_interface(general_param.keys())

    print('\nThe End!')

    with open(output_file, 'w', encoding='ANSI', ) as file:
        file.write(output_msg + to_file)

    # input('For exit press ENTER...', )
    # os.system('pause')
