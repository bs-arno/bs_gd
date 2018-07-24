# -*- coding: utf-8 -*-
"""
cloudflare防火墙相关操作的封装
"""
from tool.cf.FirewallRule import FirewallRule
import requests


class Firewall:
    def __init__(self, domain, sec_lvl=None):
        self.domain = domain
        self.sec_lvl = sec_lvl  # 安全级别：essentially_off, low, medium, high, under_attack
        self.rules_url = domain.account.zone_url + domain.zone_id + '/firewall/access_rules/rules'

    def set_medium_lvl(self):
        """
            设置当前域名的安全级别为“中级”
            :return: True：成功，False：失败
        """
        return self.set_sec_lvl('medium')

    def set_under_attack_lvl(self):
        """
            设置当前域名的安全级别为“正在被攻击”
            :return: True：成功，False：失败
        """
        return self.set_sec_lvl('under_attack')

    def is_under_attack_lvl(self):
        """
        是否当前安全级别为“正在被攻击”
        :return: True：是，False：否
        """
        return self.get_sec_lvl() == 'under_attack'

    def is_medium_lvl(self):
        """
        是否当前安全级别为“中级”
        :return: True：是，False：否
        """
        return self.get_sec_lvl() == 'medium'

    def get_sec_lvl(self):
        """
        获取当前域名的安全级别
        :return: 安全级别：essentially_off, low, medium, high, under_attack，失败返回None
        """
        response = requests.get(self.domain.account.zone_url + self.domain.zone_id + '/settings/security_level', headers=self.domain.account.headers)
        if response.status_code == 200:
            return response.json().get('result').get("value")
        else:
            print('获取域名%s的安全级别失败：%s' % (self.domain.name, response.text))

    def set_sec_lvl(self, sec_lvl):
        """
        设置当前域名的安全级别
        :param sec_lvl: 安全级别
        :return: True：成功，False：失败
        """
        data = '{"value":"' + sec_lvl + '"}'
        response = requests.patch(self.domain.account.zone_url + self.domain.zone_id + '/settings/security_level', data, headers=self.domain.account.headers)
        if response.status_code == 200:
            return True
        else:
            print('设置域名%s的安全级别为%s失败：%s' % (self.domain.name, sec_lvl, response.text))
            return False

    def block_ips(self, ips):
        """
        阻止指定ip访问该域名
        :param ips 单个ip或ip列表
        :return: True: 成功, False: 失败
        """
        if isinstance(ips, str):
            ips = [ips]

        for ip in ips:
            success = self.add_rule('block', 'ip', ip)
            if not success:
                return False
        return True

    def add_rule(self, mode, target, value):
        """
        添加防火墙访问规则
        :param mode: 规则模式: block, challenge, whitelist, js_challenge
        :param target: 规则目标: ip, ip_range, country
        :param value: 规则的值
        :return: True: 成功, False: 失败
        """
        data = '{"mode":"%s","configuration":{"target":"%s","value":"%s"},"notes":""}' % (mode, target, value)
        response = requests.post(self.rules_url, data=data, headers=self.domain.account.headers)
        if response.status_code == 200:
            return True
        else:
            print('添加防火墙规则失败！mode：%s, target：%s, value：%s。%s' % (mode, target, value, response.text))
            return False

    def delete_rule(self, id=None, value=None, mode='block', target='ip'):
        """
        删除满足条件的防火墙访问规则
        :param id: 规则id
        :param value: 规则的值
        :param mode:  规则模式: block, challenge, whitelist, js_challenge
        :param target: 规则目标: ip, ip_range, country
        :return: True: 成功, False: 失败
        """
        data = '{"cascade":"none"}'
        if id:
            response = requests.delete(self.rules_url + "/" + id, data=data, headers=self.domain.account.headers)
            if response.status_code == 200:
                return True
            else:
                print('通过id：%s删除防火墙规则失败：%s' % (id, response.text))
        else:
            rules = self.search_rule(value=value, mode=mode, target=target)
            if rules:
                for rule in rules:
                    success = self.delete_rule(id=rule.id)
                    if not success:
                        return False
                return True
            else:
                return False

    def search_rule(self, value, mode='block', target='ip'):
        """
        查询访问规则
        :param value: 规则的值
        :param mode:  规则模式: block, challenge, whitelist, js_challenge
        :param target: 规则目标: ip, ip_range, country
        :return: FirewallRule对象列表，失败返回None
        """
        params = 'scope_type=zone&page=1&per_page=1000'
        if mode:
            params += '&mode=' + mode
        if target:
            params += '&configuration_target=' + target
        if value:
            params += '&configuration_value=' + value
        url = self.rules_url + '?' + params
        response = requests.get(url, headers=self.domain.account.headers)
        rules = []
        if response.status_code == 200:
            results = response.json().get("result")
            for result in results:
                rules.append(FirewallRule(self, result))
            return rules
        else:
            print('查询防火墙规则失败！mode：%s, target：%s, value：%s。%s' % (mode, target, value, response.text))
