# -*- coding: utf-8 -*-
"""
cloudflare dns记录相关操作的封装
"""
import requests


class Record:
    def __init__(self, domain, type=None, name=None, content=None, proxied=False, orig_result=None):
        self.domain = domain
        if orig_result:
            self.id = orig_result.get("id")
            self.type = orig_result.get("type")
            self.name = orig_result.get("name")
            self.content = orig_result.get("content")
            self.proxied = orig_result.get("proxied")
        else:
            self.type = type
            self.name = name
            self.content = content
            self.proxied = proxied

    def open_cdn(self):
        """
        开启当前记录的CDN代理
        :return: True：成功，False：失败
        """
        return self._update("proxied", True)

    def close_cdn(self):
        """
        关闭当前记录的CDN代理
        :return: True：成功，False：失败
        """
        return self._update("proxied", False)

    def update_content(self):
        """
        更新当前记录的值
        :return: True：成功，False：失败
        """
        return self._update("content", self.content)

    def delete(self):
        """
        将当前记录删除
        :return: True：成功，False：失败
        """
        return self.domain.del_record_by_id(self.id)

    def _update(self, name, value):
        if isinstance(value, str):
            value = '"' + value + '"'
        data = '{"%s":%s}' % (name, value)
        url = self.domain.account.zone_url + self.domain.zone_id + '/dns_records/' + self.id
        hs = self.domain.account.headers
        response = requests.patch(url, data, headers=hs)
        if response.status_code == 200:
            return True
        else:
            print('更新域名%s的dns记录(%s, %s)失败：%s' % (self.domain.name, name, value, response.text))
            return False
