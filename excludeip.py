import re
import sys

# regExFindIP = r'(((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))'
regExFindIP = r'\d+\.\d+\.\d+\.\d+'
regExFindEOIP = r'local-address=(\d+\.\d+\.\d+\.\d+)[.\s]+remote-address=(\d+\.\d+\.\d+\.\d+)'
regExFindLocalIPfromEOIP = r'local-address=(\d+\.\d+\.\d+\.\d+)\b'
regExFindRemoteIPfromEOIP = r'remote-address=(\d+\.\d+\.\d+\.\d+)\b'

eoip_param = dict([['--local',(0,'Local')],
                  ['--remote',(1, 'Remote')]])


# Получаем список IP адресов из текста с помощью регулярного выражения
def getipfromfile(filename, regex):
    with open(filename, encoding='ANSI') as file:
        return list(re.findall(regex, file.read()))


# Сравниваем два списка IP адресов на совпадения
# если isinclude = True, то возвращаем список IP содержащийся в обеих списках
# если isinclude = False, то возвращаем список IP содержащийся в ipListMain, и не вхоящий в subipList
def compareIPlist(iplistmain, subiplist, eoip=None):
    """
    :param iplistmain: Список IP для проверки вхождений из :param subiplist:
    :param eoip: Определяет какой список проверять если анализиурем ЕОИП
    eoip = 0 - Проверяем в LocalAddress
    eoip = 1 - Проверяем в RemoteAddress
    :return: возвращаем список IP. В случае ЕОИП это всегда RemoteAddress
    """
    res = set()
    for ip in iplistmain:
        if eoip is None:
            check_ip = return_ip = ip
        else:
            check_ip = ip[eoip]  # Формирует список в котором проверяем вхождения
            return_ip = ip[1]
        if not (check_ip in subiplist):
            res.add(return_ip)
    return res


if __name__ == '__main__':

    description = f'''
    1. args: base_file exclude_ip_list_file [--local|--remote]
        Print in terminal IP address list from base_file exclude ip in exclude_ip_list_file
        IP found by regexp = "{regExFindIP}"
    Ex.: python excludeip.py ppp_secret_from_cm.txt ip_from_address_plan.txt > 1_ip_exclude_address_plan.txt
    
    2. if use key [--local|--remote]:
        Print in terminal EOIP Local or Remote IP address list from base_file exclude ip in exclude_ip_list_file
        Local and Remote IP found by regexp = "{regExFindEOIP}"
    Ex.: python excludeip.py eoip1.txt ip_from_address_plan.txt --remote  > 5_remote_eoip_exclude_addrpan.txt
    '''

    if len(sys.argv) < 3:
        print(description)
        exit()

    # filebase = 'eoip.txt'
    filebase = sys.argv[1]
    # subfile = 'ip_addr_from_cm.txt'
    subfile = sys.argv[2]
    subiplist = getipfromfile(subfile, regExFindIP)
    # baseiplist=getipfromfile(filebase, regExFindEOIP)
    # iplist = compareIPlist(iplistmain, subiplist)
    if len(sys.argv) == 4:
        eoip_arg = sys.argv[3]
        if eoip_arg in eoip_param:
            eoipIPlist = compareIPlist(getipfromfile(filebase, regExFindEOIP), subiplist, eoip_param.get(eoip_arg)[0])
            print(f'''
Checked {eoip_param.get(eoip_arg)[1]} IP addresses from EOIP in "{filebase}" 
Excluding IP containsed in "{subfile}"
Return Remote IP address list from EOIP tunnel.
Count:{len(eoipIPlist)}
''')
            print("\n".join(eoipIPlist))
    elif len(sys.argv) == 3:
        iplist = compareIPlist(getipfromfile(filebase, regExFindIP), subiplist)
        print('IP addresses from file: "{}" exclude ip in file: "{}"'.format(filebase, subfile), '\nCount:',
              len(iplist))
        print("\n".join(iplist))
    else:
        print(description)

    # print('IP addresses from file: "{}" exclude ip in file: "{}"'.format(filebase, subfile), '\nCount:', len(iplist))
    # print(sys.argv.__len__())
