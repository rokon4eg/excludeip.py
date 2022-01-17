# Поиск IP адреса
regExFindIP = r'\d+\.\d+\.\d+\.\d+'

# Поиск ip адресов в EOIP
regExFindEOIP = r'local-address=(\d+\.\d+\.\d+\.\d+)[.\s]+remote-address=(\d+\.\d+\.\d+\.\d+)'

# Поиск LocalIP адреса в EOIP
regExFindLocalIPfromEOIP = r'local-address=(\d+\.\d+\.\d+\.\d+)\b'

# Поиск RemoteIP адреса в EOIP
regExFindRemoteIPfromEOIP = r'remote-address=(\d+\.\d+\.\d+\.\d+)\b'

# Поиск бриджей
regExFind_bridge = r'name="([\w\W]+?)"'

# Поиск бридж портов
regExFind_br_port = r'interface=([\w\W]+?)(?: \n +| )bridge=([\w\W]+?)(?:[\s]priority=| \n)'

# Поиск интерфейсов в "ip addresses"
regExFind_interface = r'interface=(.+?)(?: \n +| )actual-interface'


# Выбор всей секции /interface bridge из export_compact
regEx_interface_bridge = r'\/interface bridge\n([\s\S]+?)\n\/'