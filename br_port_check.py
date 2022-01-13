import re
import sys

regExFind_bridge = r'name="([\w\W]+?)"'
regExFind_br_port = r'interface=([\w\W]+?)(?: \n +| )bridge=([\w\W]+?)(?:[\s]priority=| \n)'
regExFind_interface = r'interface=(.+?)(?: \n +| )actual-interface'

br_empty = set()
br_single = set()
br_inactive = set()
br_in_ipaddr = set()

bridge_param = dict([['--empty', ('empty bridges', br_empty)],
                     ['--single', ('bridges with single port', br_single)],
                     ['--inactive', ('bridges with inactive port', br_inactive)],
                     ['--inipaddr', ('bridges that are interfaces in "ip addresses"', br_in_ipaddr)]
                     ])


# Получаем список bridge port из текста с помощью регулярного выражения
def getbrportfromfile(br_file, br_port_file, ipfile=''):
    # global br_inactive#, br_in_ipaddr

    int_ip_addr = set()
    if ipfile != '':
        with open(ipfile, encoding='ANSI') as file:
            int_ip_addr.update(set(re.findall(regExFind_interface, file.read())))

    with open(br_file, encoding='ANSI') as file:
        all_bridges = set(re.findall(regExFind_bridge, file.read()))  # получаем список всех бриджей из файла
        br_in_ipaddr.update(all_bridges & int_ip_addr)  # находим пересечения с интерфейсами в "ip addresses"
        bridge_dict = dict([(bridge, []) for bridge in all_bridges  # формируем словарь из бриджей, пока без портов
                            if bridge not in br_in_ipaddr])

    with open(br_port_file, encoding='ANSI') as file:
        br_port_list = list(re.findall(regExFind_br_port, file.read()))
        for port, bridge in br_port_list:
            ports = bridge_dict.get(bridge, [])
            ports.append(port)
            if port[0] == '*':
                br_inactive.add(bridge)
            if bridge in bridge_dict:
                bridge_dict.update({bridge: ports})
            # else:
            #     print(f'The bridge="{bridge}" is not contained in main bridge list.')
        return bridge_dict


def print_bridge(param):
    print('\n', bridge_param[param][0].capitalize(),'-', len(bridge_param[param][1]), ':')
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

    print(f'Total bridges - {len(br_port_list)}.\n')
    for value in bridge_param.values():
        print(value[0].capitalize(),'-', len(value[1]))
    # print_bridge('--inactive')


    param = sys.argv & bridge_param.keys()
    if len(param) == 1:
        print_bridge(param.pop())
    else:
        for key in bridge_param:
            print_bridge(key)
