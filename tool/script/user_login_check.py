#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import time
import codecs
import os


class user_log:
    def get_new_user(self):
        users = os.popen("who|grep -v tty")
        flag = False
        user_login = ""
        user = []
        for user_line in users.read().splitlines():
            user_list = user_line.split()
            date_time = user_list[2] + ' ' + user_list[3]
            if time.time() - time.mktime(time.strptime(date_time, "%Y-%m-%d %H:%M")) < 60:
                user_dict = {user_list[0]: user_list[4]}
                if user_dict not in user:
                    user.append(user_dict)
                    login = '%s 用户(%s)于 %s 登陆服务器：%s' % (user_list[0], user_list[4], date_time, self.get_host_ip())
                    user_login = user_login + login + '\n'
                    flag = True
        if flag:
            print(user_login.rstrip())
        else:
            # print("No user login!")
            print("0")

    def get_host_ip(self):
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
