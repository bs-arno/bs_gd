# -*- coding: utf-8 -*-
"""
cloudflare速度相关操作的封装
"""
import requests


class Speed:
    def __init__(self, domain, min_js=True, min_css=True, min_html=True):
        self.domain = domain
        self.min_js = min_js
        self.min_css = min_css
        self.min_html = min_html

    def active_min_js(self):
        """
            开启js的最小化
            :return: True：成功，False：失败
            """
        self.toggle_min_status(True, 'js')

    def active_min_css(self):
        """
            开启css的最小化
            :return: True：成功，False：失败
            """
        self.toggle_min_status(True, 'css')

    def active_min_html(self):
        """
            开启html的最小化
            :return: True：成功，False：失败
        """
        self.toggle_min_status(True, 'html')

    def inactive_min_js(self):
        """
            关闭js的最小化
            :return: True：成功，False：失败
            """
        self.toggle_min_status(False, 'js')

    def inactive_min_css(self):
        """
            关闭css的最小化
            :return: True：成功，False：失败
            """
        self.toggle_min_status(False, 'css')

    def inactive_min_html(self):
        """
        关闭html的最小化
        :return: True：成功，False：失败
        """
        self.toggle_min_status(False, 'html')

    def toggle_min_status(self, on, suffix=None):
        """
        切换最小化开启状态
        :param suffix: css或js或html, 为None时作用于css和js和html
        :param on: True: 开启， False: 关闭
        :return: True：成功，False：失败
        """
        if suffix:
            status = "on" if on else "off"
            data = '{"value":{"' + suffix + '":"' + status + '"}}'
            response = requests.patch(self.domain.account.zone_url + self.domain.zone_id + '/settings/minify', data=data, headers=self.domain.account.headers)
            if response.status_code == 200:
                return True
            else:
                print('切换域名%s静态资源文件%s最小化开启状态为%s失败：%s' % (self.domain.name, suffix, status, response.text))
                return False
        else:
            return self.toggle_min_status(on, 'js') and self.toggle_min_status(on, 'css') and self.toggle_min_status(on, 'html')

    def get_min_status(self, suffix):
        """
        获取静态资源最小化的开启状态
        :param suffix: css或js或html
        :return: True: 开启， False: 关闭，失败返回None
        """
        response = requests.get(self.domain.account.zone_url + self.domain.zone_id + '/settings/minify', headers=self.domain.account.headers)
        if response.status_code == 200:
            return response.json().get('result').get("value").get(suffix) == 'on'
        else:
            print('获取域名%s静态资源文件%s最小化开启状态失败：%s' % (self.domain.name, suffix, response.text))
