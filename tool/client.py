#!/usr/bin/python
# -*- coding:UTF-8 -*-
import logging
import sys
import requests

__all__ = ['Client']


class Client(object):
    """
    使用Godaddy的API执行操作
    """

    def __init__(self, account, log_level=None):
        """
        创建godaddy.Client
        """
        self.logger = logging.getLogger('GoDaddyPy.Client')
        if log_level is not None:
            self.logger.setLevel(log_level)
        self.API_TEMPLATE = 'https://api.godaddy.com/v1'
        self.DOMAINS = u'/domains'
        self.DOMAIN_INFO = u'/domains/{domain}'
        self.RECORDS = u'/domains/{domain}/records'
        self.RECORDS_TYPE = u'/domains/{domain}/records/{type}'
        self.RECORDS_TYPE_NAME = u'/domains/{domain}/records/{type}/{name}'
        self.account = account

    def build_record_url(self, domain, record_type=None, name=None):
        url = self.API_TEMPLATE
        if name is None and record_type is None:
            url += self.RECORDS.format(domain=domain)
        elif name is None and record_type is not None:
            url += self.RECORDS_TYPE.format(domain=domain, type=record_type)
        elif name is not None and record_type is None:
            raise ValueError("DNS记录必须与类型匹配")
        else:
            url += self.RECORDS_TYPE_NAME.format(domain=domain, type=record_type, name=name)
        return url

    def get_headers(self):  # 获取头部信息
        return self.account.get_headers()

    def get_json_from_response(self, url, json=None, **kwargs):  # 返回字典列表
        return self.request_submit(requests.get, url=url, json=json, **kwargs).json()

    def log_response_from_method(self, req_type, resp):
        self.logger.debug('[{req_type}] response: {resp}'.format(resp=resp, req_type=req_type.upper()))
        self.logger.debug('Response data: {}'.format(resp.content))

    def patch(self, url, json=None, **kwargs):  # 选择requests模块
        return self.request_submit(requests.patch, url=url, json=json, **kwargs)

    def put(self, url, json=None, **kwargs):  # 选择requests模块
        return self.request_submit(requests.put, url=url, json=json, **kwargs)

    @staticmethod
    def remove_key_from_dict(dictionary, key_to_remove):
        return dict((key, value) for key, value in dictionary.items() if key != key_to_remove)

    def request_submit(self, func, **kwargs):
        """
        应对任何请求
        :param func: 调用url请求的形式,data,json,params等
        :type func: (url: Any, data: Any, json: Any, kwargs: Dict)
        """
        resp = func(headers=self.get_headers(), **kwargs)
        self.log_response_from_method(func.__name__, resp)
        self.validate_response_success(resp)
        return resp

    def scope_control_account(self, account):
        if account is None:
            return self.account
        else:
            return account

    @staticmethod
    def validate_response_success(response):
        """
         抛出4xx和5xx异常
         """
        try:
            response.raise_for_status()
        except Exception as e:
            raise BadResponse(response.json())

    def add_record(self, domain, record):
        """
        添加域名DNS记录
        :param domain: 域名
        :param record: 详细信息记录，为字典类型
        """
        self.add_records(domain, [record])

        # If we didn't get any exceptions, return True to let the user know
        return True

    def add_records(self, domain, records):
        """
        批量添加域名DNS记录
        :param domain: 域名
        :param records: 详细信息记录，为字典列表类型
        """
        url = self.API_TEMPLATE + self.RECORDS.format(domain=domain)
        self.patch(url, json=records)
        self.logger.debug('Added records @ {}'.format(records))
        return True

    def get_domain_info(self, domain):
        """
        获取域名信息
        :param domain: 域名
        :return json格式
        """
        url = self.API_TEMPLATE + self.DOMAIN_INFO.format(domain=domain)
        return self.get_json_from_response(url)

    def get_domains(self):
        """
        获取账号内所有域名列表
        """
        url = self.API_TEMPLATE + self.DOMAINS
        data = self.get_json_from_response(url)
        domains = list()
        for item in data:
            domain = item['domain']
            domains.append(domain)
            self.logger.debug('Discovered domains: {}'.format(domain))
        return domains

    def update_domain(self, domain, **kwargs):
        """
        """
        update = {}
        for k, v in kwargs.items():
            update[k] = v
        url = self.API_TEMPLATE + self.DOMAIN_INFO.format(domain=domain)
        self.patch(url, json=update)
        self.logger.info("Updated domain {} with {}".format(domain, update))

    def get_records(self, domain, record_type=None, name=None):
        """
        获取域名DNS记录信息
        """
        url = self.build_record_url(domain, record_type=record_type, name=name)
        data = self.get_json_from_response(url)
        self.logger.debug('Retrieved {} record(s) from {}.'.format(len(data), domain))
        return data

    def replace_records(self, domain, records, record_type=None, name=None):
        """
        替换域名记录，如果选定record_type或者name，则替换相应的记录
        """
        url = self.build_record_url(domain, name=name, record_type=record_type)
        self.put(url, json=records)
        return True

    def update_ip(self, ip, record_type='A', domains=None, subdomains=None):
        """Update the IP address in all records, specified by type, to the value of ip.  Returns True if no
        exceptions occurred during the update.  If no domains are provided, all domains returned from
        self.get_domains() will be updated.  By default, only A records are updated.

        :param record_type: The type of records to update (eg. 'A')
        :param ip: The new IP address (eg. '123.1.2.255')
        :param domains: A list of the domains you want to update (eg. ['123.com','abc.net'])
        :param subdomains: A list of the subdomains you want to update (eg. ['www','dev'])

        :type record_type: str
        :type ip: str
        :type domains: str, list of str
        :type subdomains: str, list of str
        :return: True if no exceptions occurred
        """

        if domains is None:
            domains = self.get_domains()
        elif sys.version_info < (3, 0):
            if type(domains) == str:
                domains = [domains]
        elif sys.version_info >= (3, 0) and type(domains) == str:
            domains = [domains]
        elif type(domains) == list:
            pass
        else:
            raise SystemError("Domains must be type 'list' or type 'str'")

        for domain in domains:
            a_records = self.get_records(domain, record_type=record_type)
            for record in a_records:
                r_name = str(record['name'])
                r_ip = str(record['data'])
                if not r_ip == ip:
                    if ((subdomains is None) or
                            (type(subdomains) == list and subdomains.count(r_name)) or
                            (type(subdomains) == str and subdomains == r_name)):
                        record.update(data=str(ip))
                        self.update_record(domain, record)
        return True

    def delete_records(self, domain, name, record_type=None, data=None):
        records = self.get_records(domain)
        if records is None:
            return False
        save = list()
        deleted = 0
        for record in records:
            if (record_type == str(record['type']) or record_type is None) and name == str(record['name']) and (
                    data == str(record['data']) or data is None):
                deleted += 1
            else:
                save.append(record)

        self.replace_records(domain, records=save)
        self.logger.info("Deleted {} records @ {}".format(deleted, domain))
        return True

    def update_record(self, domain, record, record_type=None, name=None):
        if record_type is None:
            record_type = record['type']
        if name is None:
            name = record['name']
        url = self.API_TEMPLATE + self.RECORDS_TYPE_NAME.format(domain=domain, type=record_type, name=name)
        self.put(url, json=record)
        return True

    def update_record_ip(self, ip, domain, name, record_type):
        """
        更新域名
        :param ip: the new IP for the DNS record (ex. '123.1.2.255')
        :param domain: the domain where the DNS belongs to (ex. 'example.com')
        :param name: the DNS record name to be updated (ex. 'dynamic')
        :param record_type: Record type (ex. 'CNAME', 'A'...)

        :return: True if no exceptions occurred
        """
        records = self.get_records(domain, name=name, record_type=record_type)
        data = {'data': str(ip)}
        for _rec in records:
            _rec.update(data)
            self.update_record(domain, _rec)
        return True


class BadResponse(Exception):
    def __init__(self, message, *args, **kwargs):
        self._message = message
        super(BadResponse, *args, **kwargs)

    def __str__(self, *args, **kwargs):
        return 'Response Data: {}'.format(self._message)
