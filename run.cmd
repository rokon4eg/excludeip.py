python excludeip.py ppp_secret_from_cm.txt ip_from_address_plan.txt > 1_ip_exclude_address_plan.txt
python excludeip.py 1_ip_exclude_address_plan.txt ppp_active_from_cm.txt > 2_ip_exclude_active.txt
python excludeip.py 2_ip_exclude_active.txt eoip.txt > 3_ip_exclude_eoip.txt
python excludeip.py eoip.txt ip_addr_from_cm.txt > eoip_exclude_ip_addr.txt
python excludeip.py eoip_exclude_ip_addr.txt ppp_secret_from_cm.txt > 4_eoip_exclude_ip+secret.txt
