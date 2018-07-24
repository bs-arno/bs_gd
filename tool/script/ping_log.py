#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import re
import time
import threading
# cd /home/oracle/scripts/;nohup python ping_log.py >/dev/null 2>&1 &
ip_list = ['43.226.45.239', '43.228.76.70', '124.232.137.197', '43.227.64.30', '61.136.166.230', '211.149.241.154',
           '183.57.41.119', '117.23.59.201', '114.118.18.133', '222.132.16.214', '112.73.90.89', '112.73.85.248',
           '121.201.125.199', '103.45.109.241']

lock = threading.Lock()


def ping_ip(ip):
    popen = subprocess.Popen('ping -c4 -w1 %s' % ip, stdout=subprocess.PIPE, shell=True)
    results = popen.stdout.read()
    matchs_log = re.findall(r'(100% packet loss)', results)
    if matchs_log:
        lock.acquire()
        try:
            matchs_log = "'" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' ping:' + ip + ' ' + matchs_log[
                0] + "'"
            subprocess.Popen('echo %s >> /var/ping.log' % matchs_log, stdout=subprocess.PIPE, shell=True)
        finally:
            lock.release()


if __name__ == '__main__':
    while True:
        for ip in ip_list:
            threading.Thread(target=ping_ip, args=(ip,)).start()
        time.sleep(10)
