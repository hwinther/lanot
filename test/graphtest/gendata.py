# coding=utf-8
import os
import json
import dateutil.parser

path = '/srv/nodedata/data'
d = dict()
for folder in os.listdir(path):
    folder_path = os.path.join(path, folder)
    # records = list()
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        for line in open(file_path, 'r').read().replace('\r', '').split('\n'):
            if line == '':
                continue
            jobject = json.loads(line)
            # records.append(jobject)
            dt = dateutil.parser.parse(jobject['timestamp'])
            key = dt.strftime('%Y.%m.%d-%H:%M:%S')
            if key not in d:
                d[key] = list()
            d[key].append(jobject)

lst = list()
keys = d.keys()
keys.sort()
for key in keys:
    values = d[key]
    # print(values)
    d3 = dict()
    d3['timestamp'] = values[0]['timestamp']
    for value in values:
        name = value['node'] + '_' + value['sensor']
        # print(repr(name))
        d3[name] = float(value['value'])
    lst.append(d3)

js_filepath = '/srv/nodedata/html/sensors.js'
print('writing %d records to %s' % (len(keys), js_filepath))
open(js_filepath, 'w').write('window.sensor_data = ' + json.dumps(lst) + '\r\n')
