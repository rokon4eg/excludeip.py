На ЦМ в консоле выполнить две команды:
/export compact file=export_compact
/ppp active pr file=ip_ppp_active_from_cm
Полученные два файла скопировать в папку рядом parse_config.exe

Из ТУ КРУС отчетом выгрузить IP адреса.
"Конструктор отчетов -> Устройства -> Устройства с данными для мониторинга"
Отфильтровать записи по нужному городу. Сохранить в текстовый файл с именем "ip_from_address_plan.txt"
Форматирование файла не важно, главное чтоб в IP адресах не было пробелов и прочих символов кроме точек.

Имена файлов могут быть любыми, но тогда их надо будет явно указать при запуске parse_config.exe

Пример: 
parse_config.exe export_compact.rsc [-tu ip_from_address_plan.txt] [-active ip_ppp_active_from_cm.txt]
[--empty|--single|--intsingle|--vlans_free|--eoip_free|--ip_free]

export_compact.rsc - config_file_name - всегда первый аргумент - файл с конфигурацией, полученный командой /export compact file=export_compact
-tu file_name - файл с ip адересами из ТУ КРУС
-active file_name - файл с активными сессиями PPP на, получен командой /ppp active pr file=ip_ppp_active_from_cm

Можно ограничить вывод комбинируя ключи из списка ниже:
2. if use key "--empty"  - Бриджы без портов
   if use key "--single"         - Бриджы с одним портом
   if use key "--intsingle"      - Одиночные интерфейсы в бриджах
   if use key "--vlans_free"     - Вланы, которых нет ни в бриджах, ни в IP адресах
   if use key "--eoip_free"      - EOIP, которых нет ни в бриджах, ни во вланах, ни в IP адресах
   if use key "--ip_free"        - Remote ip адреса из PPP and EOIP которых нет в ТУ и нет в активных PPP
Если ни один ключ не указан выводятся все!