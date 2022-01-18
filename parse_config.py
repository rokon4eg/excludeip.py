from br_port_check import bridge_param
f'''
1. Сравнить адреса из PPP secrets с адресами в ТУ (ip_from_address_plan.txt)
2. Исключить активные PPP (ppp_active_from_cm.txt)

3. Исключить те EOIP для которых local-addresses участвуют в "ip addresses"

4.  Исключить те EOIP для которых remote-addresses есть в ТУ (ip_from_address_plan.txt)
5.  Исключить активные PPP (ppp_active_from_cm.txt)


Исключить бриджы которые участвуют в "ip addresses"
Вывести бриджы без портов
Вывести бриджы с одним портом и эти одиночные порты

Вывести вланы, не участвующие в бриджах и в "ip addresses"

Ex.: python parse_config.py export_compact.txt.rsc [-tu ip_from_address_plan.txt] [-active ppp_active_from_cm.txt] 
[{'|'.join(bridge_param)}]
'''
