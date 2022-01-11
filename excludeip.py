import re
import sys

# regExFindIP = r'(((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))'
regExFindIP = r'\d+\.\d+\.\d+\.\d+'
regExFindEOIP = r'name=\"([- \.\s\W\d\w]+?)\"[\d\D]*?local-address=(\d+\.\d+\.\d+\.\d+)[.\s]+remote-address=(\d+\.\d+\.\d+\.\d+)'
regExFindLocalIPfromEOIP = r'local-address=(\d+\.\d+\.\d+\.\d+)\b'
regExFindRemoteIPfromEOIP = r'remote-address=(\d+\.\d+\.\d+\.\d+)\b'


# Получаем список IP адресов из текста с помощью регулярного выражения
def getipfromfile(filename, regex):
    with open(filename, encoding='ANSI') as file:
        return list(re.findall(regex, file.read()))


# Сравниваем два списка IP адресов на совпадения
# если isinclude = True, то возвращаем список IP содержащийся в обеих списках
# если isinclude = False, то возвращаем список IP содержащийся в ipListMain, и не вхоящий в subipList
def compareIPlist(iplistmain, subiplist, isinclude=False):
    res = []
    for ip in iplistmain:
        if not (ip in subiplist):
            res.append(ip)
    return res


if __name__ == '__main__':

    description = f'''
    1. args: base_file exclude_ip_list_file [--local|--remote]
        Print in terminal IP address list from base_file exclude ip in exclude_ip_list_file
        IP found by regexp = "{regExFindIP}"
    Ex.: python excludeip.py ppp_secret_from_cm.txt ip_from_address_plan.txt > 1_ip_exclude_address_plan.txt
    
    2. if use key [--local|--remote]:
        Print in terminal EOIP Local or Remote IP address list from base_file exclude ip in exclude_ip_list_file
        Local IP found by regexp = "{regExFindLocalIPfromEOIP}"
        Remote IP found by regexp = "{regExFindRemoteIPfromEOIP}"
    Ex.: python excludeip.py eoip1.txt ip_from_address_plan.txt --remote  > 5_remote_eoip_exclude_addrpan.txt
    '''

    if len(sys.argv) < 3:
        print(description)
        exit()

    # filebase = 'ppp_secret_from_cm.txt'
    filebase = sys.argv[1]
    # subfile = 'ip_from_address_plan.txt'
    subfile = sys.argv[2]
    subiplist = getipfromfile(subfile, regExFindIP)
    # iplist = compareIPlist(iplistmain, subiplist)
    if len(sys.argv) == 4:
        if sys.argv[3] == '--local':
            eoipLocalIPlist = compareIPlist(getipfromfile(filebase, regExFindLocalIPfromEOIP), subiplist)
            print('Local IP addresses from EOIP in file: "{}" exclude ip in file: "{}"'.format(filebase, subfile),
                  '\nCount:',
                  len(eoipLocalIPlist))
            for ip in eoipLocalIPlist:
                print(ip)
        elif sys.argv[3] == '--remote':
            eoipRemoteIPlist = compareIPlist(getipfromfile(filebase, regExFindRemoteIPfromEOIP), subiplist)
            print('Remote IP addresses from EOIP in file: "{}" exclude ip in file: "{}"'.format(filebase, subfile),
                  '\nCount:',
                  len(eoipRemoteIPlist))
            for ip in eoipRemoteIPlist:
                print(ip)
    elif len(sys.argv) == 3:
        iplistmain = getipfromfile(filebase, regExFindIP)
        iplist = compareIPlist(iplistmain, subiplist)
        print('IP addresses from file: "{}" exclude ip in file: "{}"'.format(filebase, subfile), '\nCount:',
              len(iplist))
        for ip in iplist:
            print(ip)
    else:
        print(description)

    # print('IP addresses from file: "{}" exclude ip in file: "{}"'.format(filebase, subfile), '\nCount:', len(iplist))
    # print(sys.argv.__len__())
