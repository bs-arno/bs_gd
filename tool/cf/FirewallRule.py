# -*- coding: utf-8 -*-
"""
cloudflare防火墙访问规则的封装
"""


class FirewallRule:
    def __init__(self, firewall, origResult=None, mode=None, target=None, value=None):
        self.firewall = firewall
        if origResult:
            self.id = origResult.get('id')
            self.mode = origResult.get('mode')  # block, challenge, whitelist, js_challenge
            self.target = origResult.get('configuration').get('target')  # ip, ip_range, country
            self.value = origResult.get('configuration').get('value')
            self.status = origResult.get('status')
            self.notes = origResult.get('notes')
            self.created_on = origResult.get('created_on')
            self.modified_on = origResult.get('modified_on')
        else:
            self.mode = mode
            self.target = target
            self.value = value
