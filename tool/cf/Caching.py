# -*- coding: utf-8 -*-
"""
cloudflare缓存相关操作的封装
"""

import requests


class Caching:
    def __init__(self, domain):
        self.domain = domain

    def purge_all_cache(self):
        """
        清除当前域名的所有静态资源缓存
        :return: True：成功，False：失败
        """
        data = '{"purge_everything":true}'
        url = self.domain.account.zone_url + self.domain.zone_id + "/purge_cache"
        response = requests.delete(url, data=data, headers=self.domain.account.headers)
        if response.status_code == 200:
            return True
        else:
            print('清除域名%s的缓存失败：%s' % (self.domain.name, response.text))
            return False
