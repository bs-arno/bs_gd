# -*- coding: utf-8 -*-
"""
cloudflare帐号相关操作的封装
"""

import requests

from tool.cf.Domain import Domain


class Account:
    url = 'https://api.cloudflare.com/client/v4/'
    zone_url = url + 'zones/'

    def __init__(self, email, token):
        self.email = email
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'X-Auth-Key': self.token,
            'X-Auth-Email': self.email
        }

    def get_all_domains(self):
        """
        获取该账号下的所有域名
        :return: dict(域名名称, 域名对象), 失败返回None
        """
        i = 1
        records = []
        while True:
            response = requests.get(self.zone_url + '?page=' + str(i) + '&per_page=1000', headers=self.headers)
            if response.status_code == 200:
                domains = response.json().get('result')
                count = len(domains)
                if count == 0:
                    break
                elif count <= 1000:
                    for origResult in domains:
                        domain_obj = Domain(self, origResult)
                        records.append((domain_obj.name, domain_obj))
                    if count == 1000:
                        i += 1
                    else:
                        break
            else:
                print('分页获取帐号%s下第%s分页(每页1000个)的域名时失败：%s' % (self.email, i, response.text))
                return
        return dict(records)

    def get_domain_by_name(self, domain_name):
        """
        根据域名名称获取域名对象
        :rtype: object
        :param domain_name: 域名名称
        :return: 域名对象，不存在或失败返回None
        """
        response = requests.get(self.zone_url + '?name=' + domain_name, headers=self.headers)
        if response.status_code == 200:
            domains = response.json().get('result')
            if len(domains) == 0:
                print('账号%s下不存在这个域名%s' % (self.email, domain_name))
            else:
                return Domain(account=self, orig_result=domains[0])
        else:
            print('根据域名%s获取其详细信息失败：%s' % (domain_name, response.text))

    def add_domain(self, domain):
        """
        添加域名
        :param domain: 域名名称或对象
        :return: Domain对象，失败返回None
        """
        jump_start = 'false'
        status = 'active'
        paused = 'false'
        if isinstance(domain, Domain):
            name = domain.name
            jump_start = domain.jump_start
            status = domain.status
            paused = domain.paused
        else:
            name = domain
        domain_data = '{"name":"' + name + '","jump_start":' + jump_start + ',"status":"' + status + '","paused":' + paused + '}'
        response = requests.post(self.zone_url, data=domain_data, headers=self.headers)
        if response.status_code == 200:
            return Domain(self, response.json().get('result'))
        else:
            if ':1061,' in response.text: # domain already exists
                # print('账号%s下已经存在域名%s，忽略之' % (self.email, name))
                return self.get_domain_by_name(name)
            print('添加域名%s失败：%s' % (name, response.text))

    def del_domain(self, domain_name):
        """
        删除域名
        :param domain_name: 域名名称
        :return: 是否删除成功
        """
        domain = self.get_domain_by_name(domain_name)
        if domain:
            zone_id = domain.zone_id
            response = requests.delete(self.zone_url + zone_id, headers=self.headers)
            if response.status_code == 200:
                return domain_name
            else:
                print('删除域名%s失败：%s' % (domain_name, response.text))
                return domain_name
        else:
            return False

    def get_name_servers(self):
        """
        获取name server地址
        :return: name server地址列表，失败返回None
        """
        response = requests.get(self.zone_url + '?per_page=1', headers=self.headers)
        if response.status_code == 200:
            r = response.json()
            results = r.get('result')
            if len(results) == 0:
                return []
            else:
                return results[0].get("name_servers")
        else:
            print('获取帐号%s的name server地址失败：%s' % (self.email, response.text))

    def get_domain_count(self):
        """
        获取域名总数
        :return: 域名总数，失败返回None
        """
        i = 1
        while True:
            response = requests.get(self.zone_url + '?page=' + str(i) + '&per_page=1000', headers=self.headers)
            if response.status_code == 200:
                r = response.json()
                count = len(r.get('result'))
                if count == 0:
                    return (i - 1) * 1000
                elif count < 1000:
                    return (i - 1) * 1000 + count
                else:
                    i += 1
            else:
                print('获取帐号%s的域名总数失败：%s' % (self.email, response.text))
                break

    def find_ip(self, ips):
        """
        查看指定ip的上下文信息
        :param ips: 单个ip或ip列表
        :return: Record对象列表
        """
        if isinstance(ips, str):
            ips = [ips]
        rs = []
        for (name, domain) in self.get_all_domains().items():
            for record in domain.get_all_records():
                if record.content in ips:
                    rs.append(record)
        return rs

    def block_ips(self, ips):
        """
        阻止指定ip访问该帐号下的所有域名
        :param ips 单个ip或ip列表
        :return: True: 成功, False: 失败
        """
        domains = self.get_all_domains();
        for domain in domains.values():
            success = domain.firewall.block_ips(ips)
            if not success:
                return False
            else:
                print('禁止ip：%s访问%s' % (ips, domain.name))
        return True

    def purge_cache(self):
        """
        清除该账号下所有域名的静态资源缓存
        :return: True: 成功, False: 失败
        """
        domains = self.get_all_domains();
        for domain in domains.values():
            success = domain.caching.purge_all_cache()
            if not success:
                return False
            else:
                print('清除%s的静态资源缓存成功' % domain.name)
        return True

    def delete_firewall_rule(self, value, mode='block', target='ip'):
        """
        为该账号下所有域名删除满足条件的防火墙访问规则
        :param value: 规则的值
        :param mode:  规则模式: block, challenge, whitelist, js_challenge
        :param target: 规则目标: ip, ip_range, country
        :return: True: 成功, False: 失败
        """
        domains = self.get_all_domains();
        for domain in domains.values():
            success = domain.firewall.delete_rule(value=value, mode=mode, target=target)
            if not success:
                return False
        return True

    def add_firewall_rule(self, mode, target, value):
        """
        为该账号下所有域名添加防火墙访问规则
        :param mode: 规则模式: block, challenge, whitelist, js_challenge
        :param target: 规则目标: ip, ip_range, country
        :param value: 规则的值
        :return: True: 成功, False: 失败
        """
        domains = self.get_all_domains();
        for domain in domains.values():
            success = domain.firewall.add_rule(mode, target, value)
            if not success:
                return False
            else:
                print('为%s添加防火墙规则：%s %s %s' % (domain.name, mode, target, value))
        return True

    def search_firewall_rule(self, value, mode='block', target='ip'):
        """
        查询该账号下所有满足条件的防火墙访问规则
        :param value: 规则的值
        :param mode:  规则模式: block, challenge, whitelist, js_challenge
        :param target: 规则目标: ip, ip_range, country
        :return: FirewallRule对象列表，失败返回None
        """
        results = []
        domains = self.get_all_domains();
        for domain in domains.values():
            rules = domain.firewall.search_rule(value=value, mode=mode, target=target)
            if rules:
                results.append(rules)
            else:
                return None
        return results

    def open_cdn(self):
        """
        开启该账号下所有域名所有dns记录的cdn
        :return: True: 成功, False: 失败
        """
        domains = self.get_all_domains();
        for domain in domains.values():
            success = domain.dns.open_all_cdn()
            if not success:
                return False
            else:
                print('开启%s所有dns记录的cdn' % domain.name)
        return True

    def close_cdn(self):
        """
        关闭该账号下所有域名所有dns记录的cdn
        :return: True: 成功, False: 失败
        """
        domains = self.get_all_domains();
        for domain in domains.values():
            success = domain.dns.close_all_cdn()
            if not success:
                return False
            else:
                print('关闭%s所有dns记录的cdn' % domain.name)
        return True

    def set_sec_lvl(self, sec_lvl):
        """
        设置该账号下所有域名的安全级别
        :param sec_lvl: 安全级别
        :return: True：成功，False：失败
        """
        domains = self.get_all_domains();
        for domain in domains.values():
            success = domain.firewall.set_sec_lvl(sec_lvl)
            if not success:
                return False
            else:
                print('设置%s的安全级别为%s成功' % (domain.name, sec_lvl))
        return True

    def toggle_min_status(self, on, suffix=None):
        """
        切换该账号下所有域名静态资源最小化(压缩)开启状态
        :param suffix: css或js或html, 为None时作用于css和js和html
        :param on: True: 开启， False: 关闭
        :return: True：成功，False：失败
        """
        domains = self.get_all_domains();
        for domain in domains.values():
            success = domain.speed.toggle_min_status(on)
            if not success:
                return False
            else:
                print('设置完成%s的JavaScript,CSS,HTML压缩' % (domain.name))
        return True
