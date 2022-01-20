import re
import sys

int_ip_addr = set()

# Поиск бриджей
regExFind_bridge = r'name="([\w\W]+?)"'

# Поиск бридж портов
regExFind_br_port = r'interface=([\w\W]+?)(?: \n +| )bridge=([\w\W]+?)(?:[\s]priority=| \n)'

# Поиск интерфейсов в "ip addresses"
regExFind_interface = r'interface=(.+?)(?: \n +| )actual-interface'

br_empty = set()
br_single = set()
br_inactive = set()
br_in_ipaddr = set()
int_single = set()
vlans_free = set()
eoip_free = set()
ip_free = set()

bridge_param = dict([['--empty', ('bridges without ports', br_empty)],
                     ['--single', ('bridges with single port', br_single)],
                     ['--intsingle', ('interfaces included in the bridges one by one', int_single)],
                     ['--vlans_free', ('vlans that are not in bridges and ip addresses', vlans_free)],
                     ['--eoip_free', ('name of eoip that are not in bridges, vlans or ip addresses', eoip_free)],
                     ['---ip_free',
                      ('remote ip addresses from PPP and EOIP that are not in TU and not in active PPP', ip_free)]
                     ])


# Получаем список bridge port из текста с помощью регулярного выражения
def getbrportfromfile(br_file, br_port_file, ipfile=''):
    if ipfile != '':
        with open(ipfile, encoding='ANSI') as file:
            # получаем список всех # интерфейсов из "ip addresses"
            int_ip_addr.update(set(re.findall(regExFind_interface, file.read())))

    with open(br_file, encoding='ANSI') as file:
        all_bridges = set(re.findall(regExFind_bridge, file.read()))  # получаем список всех бриджей из файла
        br_in_ipaddr.update(all_bridges & int_ip_addr)  # находим пересечения с интерфейсами в "ip addresses"
        bridge_dict = dict([(bridge, []) for bridge in all_bridges  # формируем словарь из бриджей, пока без портов
                            if bridge not in br_in_ipaddr])

    with open(br_port_file, encoding='ANSI') as file:
        br_port_list = list(re.findall(regExFind_br_port, file.read()))  # получаем список всех бридж портов из файла
        for port, bridge in br_port_list:
            ports = bridge_dict.get(bridge, [])  # получаем текущий списко портов для каждого бриджа
            ports.append(port)  # добавляем новый порт к списку портов для бриджа
            if port[0] == '*':  # если порт неактивный, формируем список бриджей с неактивными портами
                br_inactive.add(bridge)
            if bridge in bridge_dict:  # добавляем только в том случае если бридж ранее не был ранее отфильтрован
                bridge_dict.update({bridge: ports})
            # else:
            #     print(f'The bridge="{bridge}" is not contained in main bridge list.')
        return bridge_dict


def print_bridge(param):
    print('\n', bridge_param[param][0].capitalize(), '-', len(bridge_param[param][1]), ':')
    print("\n".join(bridge_param[param][1]))


if __name__ == '__main__':

    key_param = ''
    for key, value in bridge_param.items():
        key_param += f'if use key "{key}"\t print only {value[0]}\n       '

    description = f'''
    1. args: br_file br_port_file [--empty|--single|--inactive|--inipaddr] [-ipfile ip_addr.txt]
        Print name of Bridge in terminal where contains one or zero or "*..." interface.
        "br_file" was generated command: "/interface bridge pr file=bridge"
        "br_port_file" was generated command: "/interface bridge port pr file=br_port detail"
    Ex.: python br_port_check.py bridge.txt br_port.txt > bridge_without_port.txt

    2. {key_param}
    Ex.: python br_port_check.py bridge.txt br_port.txt --empty
    
    Bridge found by regexp: "{regExFind_bridge}" 
    Bridge port found by regexp: "{regExFind_br_port}"   
    
    3. You can exclude bridges that contains in "ip addresses".
    For this use key -ipfile and specify file name
    "ipfile" was generated command: "/ip address pr file=ip_addr detail"
    Ex.: python br_port_check.py bridge.txt br_port.txt --empty -ipfile ip_addr.txt > bridge_without_port.txt
    
    Bridges that are interfaces in "ip addresses" found by regexp: "{regExFind_interface}"
    '''

    if len(sys.argv) < 3:
        print(description)
        exit()

    # br_file = 'bridge.txt'
    # br_port_file = 'br_port.txt'

    br_file = sys.argv[1]
    br_port_file = sys.argv[2]

    ipadr_file = ''
    # ipadr_file = 'ip_addr.txt'
    if '-ipfile' in sys.argv:
        ipadr_file = sys.argv[sys.argv.index('-ipfile') + 1]

    br_port_list = getbrportfromfile(br_file, br_port_file, ipfile=ipadr_file)

    for key, value in br_port_list.items():
        if value == []:
            br_empty.add(key)
        elif len(value) == 1:
            br_single.add(key)
            if value[0] not in int_ip_addr:  # исключаем интерфейсы которые есть в "ip addresss"
                int_single.add(value[0])

    print(f'Total bridges - {len(br_port_list)}.\n')
    for value in bridge_param.values():
        print(value[0].capitalize(), '-', len(value[1]))
    # print_bridge('--inactive')

    param = sys.argv & bridge_param.keys()
    if len(param) == 1:
        print_bridge(param.pop())
    else:
        for key in bridge_param:
            print_bridge(key)
