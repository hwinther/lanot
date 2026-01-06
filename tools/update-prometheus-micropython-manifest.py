#!/usr/bin/python
import os

root_path = '/mnt/Prosjekter/lanot/src/core/prometheus'
f = open(root_path + '/../../../tools/prometheus.micropython.manifest.py', 'w')
for root, dirs, files in os.walk(root_path, topdown=False):
   for name in files:
      if os.path.splitext(name)[1] != '.py':
        continue
      relative_root = root.replace(root_path.replace('prometheus', ''), '')
      relative_file_path = os.path.join(relative_root, name)
      # freeze('/mnt/Prosjekter/lanot/src/core', 'prometheus/__init__.py')
      frz = "freeze('/mnt/Prosjekter/lanot/src/core', '%s')" % relative_file_path
      print(frz)
      f.write(frz + '\n')
f.close()
