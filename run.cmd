python excludeip.py ppp_secret_from_cm.txt ip_from_address_plan.txt > ppp_exclude_address_plan.txt
python excludeip.py ppp_exclude_address_plan.txt ppp_active_from_cm.txt > ppp_exclude_address_plan_and_active.txt
python excludeip.py ppp_exclude_address_plan_and_active.txt eoip.txt > 1_ppp_exclude_eoip.txt

python excludeip.py eoip.txt ip_addr_from_cm.txt --local > eoip_local_exclude_ip_addr_from_cm.txt
python excludeip.py eoip_local_exclude_ip_addr_from_cm.txt ip_from_address_plan.txt > 2_eoip_local_exclude_ip_in_cm_and_addr_plan.txt

python excludeip.py eoip.txt ip_from_address_plan.txt --remote > eoip_remote_exclude_ip_from_address_plan.txt
python excludeip.py eoip_remote_exclude_ip_from_address_plan.txt ppp_active_from_cm.txt > 3_eoip_remote_exclude_address_plan_and_active.txt

