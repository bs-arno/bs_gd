#!/usr/bin/python
from flask.GD import Account, Client


type_list = ['A', 'CNAME']
api_key = 'dLYgnspmfKRp_YWTu6vjFWaBYHribTwYnsM'
api_secret = 'YWTzg6n6Z3ECPiQVP6wMZd'
userAccount = Account(api_key, api_secret)
userClient = Client(userAccount)
userClient.add_record('jyw186.com', {'data': '100.100.100.100', 'type': 'A', 'name': 'T'})
