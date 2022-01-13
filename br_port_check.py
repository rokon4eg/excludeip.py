import re
import sys

regExFind_bridge = r'name="([\w\W]+?)"'
regExFind_br_port = r'interface=([\w\W]+?)(?: \n +| )bridge=([\w\W]+?)(?:[\s]priority=| \n)'


# Получаем список bridge port из текста с помощью регулярного выражения
def getbrportfromfile(br_file, br_port_file):
    with open(br_file, encoding='ANSI') as file:
        bridge_dict = dict([(bridge, []) for bridge in re.findall(regExFind_bridge, file.read())])
    with open(br_port_file, encoding='ANSI') as file:
        br_port_list = list(re.findall(regExFind_br_port, file.read()))
        for port, bridge in br_port_list:
            ports=bridge_dict.get(bridge, [])
            ports.append(port)
            if bridge not in bridge_dict:
                print(f'The bridge="{bridge}" is not contained in main bridge list')
            bridge_dict.update({bridge: ports})
        print(len(bridge_dict))
        return bridge_dict


if __name__ == '__main__':
    description = f'''
    args: br_file br_port_file
        Print name of Bridge in terminal where containse one or zerro or "*~~" interface.
        "br_file" was generated command: "/interface bridge pr file=bridge"
        "br_port_file" was generated command: "/interface bridge port pr file=br_port detail"
    Ex.: python br_port_check.py br_port.txt > bridge_without_port.txt
    Bridge found by regexp: "{regExFind_bridge}" 
    Bridge port found by regexp: "{regExFind_br_port}"   
    '''

    # if len(sys.argv) < 2:
    #     print(description)
    #     exit()

    br_file = 'bridge.txt'
    br_port_file = 'br_port.txt'
    # br_file = sys.argv[1]
    # br_port_file = sys.argv[2]
    br_port_list = getbrportfromfile(br_file, br_port_file)

    print(br_port_list)
