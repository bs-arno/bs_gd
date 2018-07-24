#!/usr/bin/python
# -*- coding: utf-8 -*-
import cx_Oracle
import random
import requests
import os

log_name_list = {"华北": ["北京", "天津", "河北", "山西", "内蒙古"], "东北": ["黑龙江", "辽宁", "吉林"],
                 "华东": ["浙江", "江苏", "上海", "山东", "安徽", "江西"], "中南": ["广东", "湖南", "湖北", "河南", "广西", "海南"],
                 "西北": ["陕西", "甘肃", "青海", "宁夏", "新疆"], "西南": ["四川", "云南", "重庆", "贵州", "西藏"]}


class domain_push:
    def get_conn(self):
        return cx_Oracle.connect("")

    def get_areas(self):
        conn = self.get_conn()
        cur = conn.cursor()
        ip_dict = {}
        for province in log_name_list:
            # sql = "select begin_ip from domain_ip_location where loc_name=:loc_name order by rand() limit 1"
            sql = "select begin_ip from domain_ip_location where loc_name=:loc_name"
            # sql = "select DISTINCT loc_name from domain_ip_location"
            cur.execute(sql, loc_name=random.sample(log_name_list[province], 1)[0])
            rows = cur.fetchmany()
            for row in random.sample(rows, 1):
                ip_dict[province] = row[0]
        return ip_dict

    def get_url(self, ip):
        return 'http://dmapi.yhzcs.org/domain_push?ip=%s&type=p' % ip

    def status_code(self, url):
        result = requests.get(url)
        if result.status_code == 200 and len(eval(result.text)) != 6:
            return 200
        else:
            return '%s错误, 获取域名信息为：%s' % (result.status_code, result.text)

    def check_domain_push(self):
        ip_dict = self.get_areas()
        for province in ip_dict:
            re = self.status_code(self.get_url(ip_dict[province]))
            if re != 200:
                self.domain_push_telegram(re)

    def domain_push_telegram(self, msg):
        telegram_url = "\"https://api.telegram.org/bot601361780:AAFvNBM42Z5V7RJb5ge9Y0n0XuvijbMVp5Q/sendMessage\""
        target = '\"chat_id=525853532&text=%s\"' % msg.encode('utf-8')
        po = 'curl -X POST %s -d %s' % (telegram_url, target)
        os.popen(po)


if __name__ == "__main__":
    domain_push().check_domain_push()
