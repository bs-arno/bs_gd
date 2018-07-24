#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import codecs
import os
import urllib
json_path = '/var/log_in.json'


class send_msg:
    def judgment_json(self):
        try:
            with codecs.open(json_path, 'r', encoding='utf-8') as j:
                return json.load(j), True
        except Exception as e:
            return str(e), False

    def user_login_mail(self):
        user_dict, bool = self.judgment_json()
        if bool:
            for user_log_in in user_dict["user_login"]:
                log_msg = '\"%s\"' % user_log_in
                title = '\"User login\"'
                os.popen('echo %s | mail -s %s arno@bsnetworks.net' % (log_msg.encode('utf-8'), title))
                user_dict["user_login"].remove(user_log_in)
            with codecs.open(json_path, 'w', encoding='utf-8') as w:
                json.dump(user_dict, w, ensure_ascii=False, indent=4)

    def user_login_telegram(self):
        user_dict, bool = self.judgment_json()
        if bool:
            for user_log_in in user_dict["user_login"]:
                telegram_url = "\"https://api.telegram.org/bot601361780:AAFvNBM42Z5V7RJb5ge9Y0n0XuvijbMVp5Q/sendMessage\""
                log_msg = '%s' % user_log_in
                target = '\"chat_id=525853532&text=%s\"' % log_msg.encode('utf-8')
                po = 'curl -X POST %s -d %s &>/dev/null' % (telegram_url, target)
                os.popen(po)
                user_dict["user_login"].remove(user_log_in)
                with codecs.open(json_path, 'w', encoding='utf-8') as w:
                    json.dump(user_dict, w, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    send_msg().user_login_mail()
