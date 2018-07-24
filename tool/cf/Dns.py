# -*- coding: utf-8 -*-
"""
cloudflare缓存相关操作的封装
"""
from tool.cf.Record import Record

import requests


class Dns:
    def __init__(self, domain):
        self.domain = domain
        self.account = domain.account

    def get_all_records(self):
        """
        获取该域名的所有DNS记录
        :return: DNS记录对象列表，失败时返回None
        """
        response = requests.get(self.account.zone_url + self.domain.zone_id + '/dns_records' + '?per_page=1000', headers=self.account.headers)
        if response.status_code == 200:
            return [Record(domain=self.domain, orig_result=item) for item in response.json().get("result")]
        else:
            print('取该域名%s所有DNS记录失败：%s' % (self.domain.name, response.text))

    def add_record(self, record):
        """
        为该域名添加DNS记录
        :param record: DNS记录对象
        :return: 成功返回记录id，失败返回None
        """
        data = '{"type":"%s","name":"%s","content":"%s","proxied":%s}' % (record.type, record.name, record.content, record.proxied)
        response = requests.post(self.account.zone_url + self.domain.zone_id + '/dns_records', data, headers=self.account.headers)
        if response.status_code == 200:
            r = response.json()
            return Record(self, orig_result=r.get('result'))
        else:
            if 'record already exists' in response.text:
                print('域名%s下已经存在dns记录%s，忽略之' % (self.domain.name, record.content))
                records = self.search_records(record)
                if records and len(records) > 0:
                    return records[0]
                return record
            print('为域名%s添加DNS记录失败：%s' % (self.domain.name, response.text))

    def search_records(self, record):
        """
        查找符合条件的dns记录对象
        :param record: dns记录对象
        :return: dns记录对象列表，找不到返回空列表，失败返回None
        """
        results = []
        records = self.get_all_records()
        if records:
            for r in records:
                if r.content == record.content and r.name == record.name and r.type == record.type:
                    results.append(r)
                elif r.name == record.name and r.type == record.type:
                    results.append(r)
                elif r.type == record.type:
                    results.append(r)
        if len(records) == 0:
            print('没有找到符合条件的dns记录！')
        return results

    def del_record(self, record):
        """
        删除该域名指定的DNS记录
        :param record: DNS记录id或对象，删除条件的优先顺序为: content, name, type
        :return: True：成功，False：失败
        """
        success = True
        if isinstance(record, Record):
            if record.id:
                success = self.del_record_by_id(record.id)
            else:
                delete = False
                for r in self.get_all_records():
                    if r.content == record.content and r.name == record.name and r.type == record.type:
                        delete = True
                    elif r.name == record.name and r.type == record.type:
                        delete = True
                    elif r.type == record.type:
                        delete = True

                    if delete:
                        success = self.del_record_by_id(record.id) and success
        else:
            success = self.del_record_by_id(record.id)
        return success

    def del_record_by_id(self, record_id):
        """
        删除指定id的DNS记录
        :param record_id: DNS记录id
        :return: True：成功，False：失败
        """
        response = requests.delete(self.account.zone_url + self.domain.zone_id + '/dns_records/' + record_id, headers=self.account.headers)
        if response.status_code == 200:
            return True
        else:
            print('删除域名%s中id为%s的DNS记录失败：%s' % (self.domain.name, record_id, response.text))
            return False

    def close_all_cdn(self):
        """
        关闭该域名所有记录的CDN
        :return: True：成功，False：失败
        """
        success = True
        for record in self.get_all_records():
            success = record.close_cdn() and success
        return success

    def open_all_cdn(self):
        """
        开启该域名所有记录的CDN
        :return: True：成功，False：失败
        """
        success = True
        for record in self.get_all_records():
            success = record.open_cdn() and success
        return success
