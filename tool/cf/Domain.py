# -*- coding: utf-8 -*-

"""
cloudflare域名相关操作的封装
"""
from tool.cf.Caching import Caching
from tool.cf.Dns import Dns
from tool.cf.Firewall import Firewall
from tool.cf.Speed import Speed


class Domain:
    def __init__(self, account, orig_result, name='', jump_start=False, status='active', paused=False):
        self.account = account
        if orig_result:
            self.name = orig_result.get('name')
            self.zone_id = orig_result.get('id')
            self.status = orig_result.get("status")
            self.paused = bool(orig_result.get("paused"))
            self.created_on = orig_result.get("created_on")
            self.modified_on = orig_result.get("modified_on")
            self.name_servers = orig_result.get("name_servers")
        else:
            self.name = name
            self.jump_start = jump_start
            self.status = status
            self.paused = paused
        self.dns = Dns(self)
        self.firewall = Firewall(self)
        self.speed = Speed(self)
        self.caching = Caching(self)
