# -*- coding: utf-8 -*-
import json
import codecs
import datetime
import traceback
from tool import client, account
from tool.Criterion import Criterion
from tool.Operator import Operator
import cx_Oracle

jsonpath = '/usr/local/lib/python2.7/site-packages/flask/GD/gs_conf.json'


def get(table, id):
    conn = _get_conn()
    try:
        cur = conn.cursor()
        sql = "SELECT * FROM {table} WHERE domain = '{id}'".format(table=table, id=id)
        # print("sql: %s" % sql)
        cur.execute(sql)
        row = cur.fetchone()
        column_names = _get_column_names(cur)
        return {column_names[i]: column_value for i, column_value in enumerate(row)}
    except:
        traceback.print_exc()
    finally:
        _close_conn(conn)


def search(table, where='', order='', select='*', size=None):
    conn = _get_conn()
    try:
        cur = conn.cursor()
        if where:
            where = 'WHERE ' + where
        if order:
            order = 'ORDER BY ' + order
        sql = "SELECT %s FROM %s t %s %s" % (select, table, where, order)
        # print("sql: %s" % sql)
        cur.execute(sql)
        if size is None:
            rows = cur.fetchall()
        else:
            rows = cur.fetchmany(size=size)
        column_names = _get_column_names(cur)
        dict_results = []
        for row in rows:
            dict_result = {}
            for i, column_value in enumerate(row):
                column_name = column_names[i]
                if isinstance(column_value, datetime.datetime):
                    column_value = column_value.strftime('%Y-%m-%d %H:%M:%S')
                dict_result[column_name] = column_value
            dict_results.append(dict_result)
        return dict_results
    except:
        traceback.print_exc()
    finally:
        _close_conn(conn)


def one_search(table, criterions, field, orders=[], size=None):
    tmp_results = and_search(table, criterions, orders, [field], size)
    return [tmp_result[field] for tmp_result in tmp_results]


def and_search(table, criterions, orders=[], fields=[], size=None):
    select = ','.join(fields) or '*'
    where = _to_where(criterions, True)
    order = _to_order(orders)
    return search(table, where, order, select, size)


def or_search(table, criterions, orders=[], fields=[], size=None):
    select = ','.join(fields) or '*'
    where = _to_where(criterions, False)
    order = _to_order(orders)
    return search(table, where, order, select, size)


def count(table, criterions=[]):
    """
    查询满足条件的记录数
    :param table: 表名
    :param criterions: Criterion对象列表
    :return: 记录数
    """
    sql = 'SELECT count(*) FROM {table}'.format(table=table)
    where = _to_where(criterions, True)
    if where:
        sql += ' WHERE ' + where
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        return row[0]
    except:
        traceback.print_exc()
        return -1
    finally:
        _close_conn(conn)


def insert(table, record, connection=None):
    """
    插入一条记录到指定表
    :param table: 要插入的表名
    :param record: 行记录dict
    :return: True: 成功，False：失败
    :param connection: 数据库连接，用于调用者自己控制事务的场景
    """
    return batch_insert(table, [record], connection)


def batch_insert(table, dict_list, connection=None):
    """
    批量插入指定记录到指定表
    :param table: 要插入的表
    :param dict_list: 记录字典列表
    :return: True: 成功，False：失败
    :param connection: 数据库连接，用于调用者自己控制事务的场景
    """
    conn = connection or _get_conn()
    try:
        cur = conn.cursor()
        for dict in dict_list:
            columns = ''
            values = ''
            for (column, value) in dict.items():
                columns += column + ","
                if isinstance(value, str):
                    value = "'" + value.replace("'", "''") + "'"
                    values += value + ","
                elif value is None:
                    values += "null,"
                elif isinstance(value, datetime.datetime):
                    values += "TIMESTAMP '" + str(value) + "',"
                else:
                    values += "'" + str(value) + "',"
            sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, columns[:-1], values[:-1])
            # print("sql: %s" % sql)
            cur.execute(sql)
        connection or conn.commit()
    except:
        traceback.print_exc()
        return False
    finally:
        connection or _close_conn(conn)
    return True


def update(table, dict_list, fields=None, criterions=None, connection=None):
    """
    更新指定表的多条记录
    :param table: 要更新的表名
    :param dict_list: 行记录dict的list, 注意：dict中必须要有id的key
    :param fields: 要更新的字段列表
    :param connection: 数据库连接，用于调用者自己控制事务的场景
    :param criterions: 默认使用id做查询条件,也可传入criterions列表座位查询条件
    :return: True: 成功，False：失败
    """
    conn = connection or _get_conn()
    try:
        cur = conn.cursor()
        for d in dict_list:
            column_value = ''
            for (column, value) in d.items():
                if column == 'id':
                    id = value
                if fields and column not in fields:
                    continue
                elif not column.startswith('_') and not column.endswith('_'):
                    if isinstance(value, str):
                        value = "'" + value.replace("'", "''") + "'"
                    elif value is None:
                        value = "null"
                    elif isinstance(value, datetime.datetime):
                        value = "TIMESTAMP '" + str(value) + "'"
                    else:
                        value = "'" + str(value) + "'"
                    column_value += column + '=' + value + ','
            if criterions is None:
                sql = "UPDATE %s SET %s WHERE id = '%s'" % (table, column_value[:-1], id)
            else:
                where = _to_where(criterions, True)
                sql = "UPDATE %s SET %s WHERE %s" % (table, column_value[:-1], where)
            print("sql: %s" % sql)
            cur.execute(sql)
        connection or conn.commit()
    except:
        traceback.print_exc()
        return False
    finally:
        connection or _close_conn(conn)
    return True


def batch_delete(table, criterions, connection=None):
    """
    批量删除
    :param connection: 数据库连接，用于调用者自己控制事务的场景
    :param table:  要删除的表名
    :param criterions: Criterion对象列表
    :return: True: 成功，False：失败
    """
    where = _to_where(criterions, True)
    conn = connection or _get_conn()
    try:
        cur = conn.cursor()
        sql = "DELETE from %s WHERE %s" % (table, where)
        # print("sql: %s" % sql)
        cur.execute(sql)
        connection or conn.commit()
    except:
        traceback.print_exc()
        return False
    finally:
        connection or _close_conn(conn)
    return True


def delete(table, id, connection=None):
    """
    从指定表中删除指定id的记录
    :param connection: 数据库连接，用于调用者自己控制事务的场景
    :param table: 要删除的表名
    :param id: 主键
    :return: True: 成功，False：失败
    """
    return delete_all(table, [id], connection)


def delete_all(table, ids, connection=None):
    """
    从指定表中删除指定id列表的记录
    :param connection: 数据库连接，用于调用者自己控制事务的场景
    :param table: 要删除的表名
    :param ids: 主键列表
    :return: True: 成功，False：失败
    """
    conn = connection or _get_conn()
    try:
        cur = conn.cursor()
        for id in ids:
            sql = "DELETE from %s WHERE id = '%s'" % (table, id)
            # print("sql: %s" % sql)
            cur.execute(sql)
        connection or conn.commit()
    except:
        traceback.print_exc()
        return False
    finally:
        connection or _close_conn(conn)
    return True


def _to_order(orders):
    if not orders:
        return ''
    order_strs = [order.field + ' ' + order.direction.name for order in orders]
    return ','.join(order_strs)


def _to_where(criterions, is_and):
    if not criterions:
        return ''
    items = []
    for criterion in criterions:
        if isinstance(criterion, list):
            if is_and:
                or_where = _to_where(criterion, False)
                if or_where:
                    items.append("(" + or_where + ")")  # 内层(第二层)or
            else:
                and_where = _to_where(criterion, True)
                if and_where:
                    items.append("(" + and_where + ")")  # 第三层(and)
        else:
            if criterion.value is not None and criterion.value != '' and criterion.value != []:
                items.append(_to_where_item(criterion))
    if is_and:
        return ' AND '.join(items)
    return ' OR '.join(items)


def _to_where_item(criterion):
    op = criterion.operator
    field = criterion.field
    value = criterion.value
    if isinstance(value, datetime.datetime):
        value = "TIMESTAMP '" + str(value) + "'"
    if isinstance(criterion.value, str):
        value = value.replace("'", "''")
    if op == Operator.EQ:
        if isinstance(criterion.value, str):
            return "%s='%s'" % (field, value)
        return "%s=%s" % (field, value)
    elif op == Operator.NE:
        if isinstance(criterion.value, str):
            return "%s<>'%s'" % (field, value)
        return "%s<>%s" % (field, value)
    elif op == Operator.ILIKE:
        return "LOWER(%s) like '%%%s%%'" % (field, value.lower())
    elif op == Operator.ILIKE_S:
        return "LOWER(%s) like '%s%%'" % (field, value.lower())
    elif op == Operator.ILIKE_E:
        return "LOWER(%s) like '%%%s'" % (field, value.lower())
    elif op == Operator.GT:
        return "%s>%s" % (field, value)
    elif op == Operator.GE:
        if isinstance(criterion.value, str):
            return "%s>='%s'" % (field, value)
        return "%s>=%s" % (field, value)
    elif op == Operator.LT:
        return "%s<%s" % (field, value)
    elif op == Operator.LE:
        if isinstance(criterion.value, str):
            return "%s<='%s'" % (field, value)
        return "%s<=%s" % (field, value)
    elif op == Operator.EXISTS:
        value = value.replace("''", "'")
        return "EXISTS (%s)" % (value)
    elif op == Operator.IN:
        return "%s in %s" % (field, _in(value))
    elif op == Operator.NOT_IN:
        return "%s not in %s" % (field, _in(value))
    elif op == Operator.IS_NULL:
        return "%s is null" % field
    elif op == Operator.IS_NOT_NULL:
        return "%s is not null" % field


def _in(value):
    in_str = '('
    for item in value:  # list
        if item:
            in_str += "'" + str(item) + "',"
    return in_str[:-1] + ")"


def judgment_json(jsonpath):  # 读取json文件
    with codecs.open(jsonpath, 'r', encoding='utf-8') as j:
        return json.load(j)


def _get_conn():
    """
    获取数据库连接
    :return: 返回连接对象，使用完请自行关闭
    """
    gs_conf = judgment_json()
    hps = gs_conf['db']['db_host'] + ':' + gs_conf['db']['db_port'] + '/' + gs_conf['db']['db_scheme']
    return cx_Oracle.connect(gs_conf['db']['db_user'], gs_conf['db']['db_psd'], hps)


def _close_conn(conn):
    """
    关闭数据库连接
    """
    conn and conn.close()


def _get_column_names(cur):
    """
    获取列名
    :param cur:  cursor
    :return: 列名列表
    """
    return [e[0] for e in cur.description]


def get_next_seq_no(seq_name):
    """
    获取序列的下一个值
    :param seq_name: 序列名称
    :return: 序列值
    """
    conn = _get_conn()
    try:
        cur = conn.cursor()
        sql = "select nextval('%s')" % seq_name
        cur.execute(sql)
        return cur.fetchone()[0]
    except:
        traceback.print_exc()
    finally:
        _close_conn(conn)


def writejson(dictwrite):
    with codecs.open(jsonpath, 'w') as w:  # 写入json文件
        json.dump(dictwrite, w, indent=4)


def judgment_json():  # 读取json文件
    with codecs.open(jsonpath, 'r') as j:
        return json.load(j)


def update_account(manage):
    gs_conf = judgment_json()
    if manage in gs_conf['account'].keys():
        userAccount = account.Account(gs_conf["account"][manage]['api_key'], gs_conf["account"][manage]['api_secret'])
        userClient = client.Client(userAccount)
        gs_conf['account'][manage]['domain'] = userClient.get_domains()
        writejson(gs_conf)
        return True


def add_account(manage, key, secret):
    gs_conf = judgment_json()
    gs_conf['account'][manage] = {'domain': [], 'api_key': key, 'api_secret': secret}
    writejson(gs_conf)
    update_account(manage)


def get_domain_account(domain):
    gs_conf = judgment_json()
    manage = ''
    for account in gs_conf['account']:
        if domain in gs_conf['account'][account]['domain']:
            manage = account
    return manage


def get_user_client(manage):
    gs_conf = judgment_json()
    if manage in gs_conf['account'].keys():
        userAccount = account.Account(gs_conf["account"][manage]['api_key'], gs_conf["account"][manage]['api_secret'])
        return client.Client(userAccount)
    else:
        return 'Account not exist'


def get_account_domain(manage):
    gs_conf = judgment_json()
    if manage in gs_conf['account'].keys():
        return gs_conf['account'][manage]['domain']
    else:
        return 'Account not exist'


def get_accounts():
    gs_conf = judgment_json()
    return gs_conf['account'].keys()
