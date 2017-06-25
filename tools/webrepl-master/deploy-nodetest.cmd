rem python webrepl_cli.py ..\..\src\devices\mp-esp8266-test\boot.py 192.168.1.188:/boot.py

python webrepl_cli.py ..\..\src\devices\mp-esp8266-test\nodetest.py 192.168.1.188:/nodetest.py

python webrepl_cli.py ..\..\src\core\python\prometheus.py 192.168.1.188:/prometheus.py
python webrepl_cli.py ..\..\src\core\python\prometheus_esp8266.py 192.168.1.188:/prometheus_esp8266.py

rem python webrepl_cli.py ..\..\build\core\python\prometheus.mpy 192.168.1.188:/prometheus.mpy
rem python webrepl_cli.py ..\..\build\core\python\prometheus_esp8266.mpy 192.168.1.188:/prometheus_esp8266.mpy
