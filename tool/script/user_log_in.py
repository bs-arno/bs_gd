#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import time
import json
import codecs
import os
import re

json_path = '/var/log_in.json'


class user_log:
    def get_new_user(self):
        self.create_file()
        user_dict = self.judgment_json()[0]
        users = os.popen("who|grep -v tty")
        flag = False
        for user_line in users.read().splitlines():
            user_list = user_line.split()
            date_time = user_list[2] + ' ' + user_list[3]
            if time.time() - time.mktime(time.strptime(date_time, "%Y-%m-%d %H:%M")) < 60:
                login_in = u'%s 用户(%s)于 %s 登陆 服务器：%s' % (user_list[0], user_list[4], date_time, self.get_ip())
                user_dict["user_login"].append(login_in)
                flag = True
        self.write_json(user_dict)
        if flag:
            print('0')
        else:
            print('1')

    def write_json(self, dict_json):
        with codecs.open(json_path, 'w', encoding='utf-8') as w:
            json.dump(dict_json, w, ensure_ascii=False, indent=4)

    def get_ip(self):
        host_info = os.popen("ip a ").read()
        reip = re.compile(r'\d+\.\d+\.\d+\.\d+')
        host_ip_list = reip.findall(host_info)
        return host_ip_list[0]

    def judgment_json(self):
        try:
            with codecs.open(json_path, 'r', encoding='utf-8') as j:
                return json.load(j), True
        except Exception as e:
            return str(e), False

    def create_file(self):  # 判断文件是否存在，不存在即创建文件
        if not os.path.exists(json_path):
            dict_json = {"user_login": []}
            self.write_json(dict_json)


def get_host_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


if __name__ == '__main__':
    user_log().get_new_user()
