# import scipy.misc
import io
# from PIL import Image
import json
# import numpy
import os
import pickle
import codecs
import time
import mysql.connector

DBErrorNotification = 'DBErrorNotification'
DBConnectErrorNotification = 'DBConnectErrorNotification'


class Database(object):
    dbapi = None

    def __init__(self, *args, **kwargs):
        super(Database, self).__init__()
        self.conn_kwargs = dict(kwargs)
        self.conn_args = args
        self.connected = False
        self.conn_pool_args = dict(pool_name='default_pool', pool_reset_session=False)
        # self.ch_tx_isolvl = None

        for k in list(kwargs.keys()):
            if k.startswith('pool_'):
                self.conn_pool_args[k] = self.conn_kwargs.pop(k, None)

    @staticmethod
    def from_config(db_params):
        return Database(**db_params)

    def connection(self, readonly=False, **kwargs):
        if not self.connected:
            print('Connecting to MySQL Database @{}'.format(self.conn_kwargs['host']))

        if kwargs:
            try:
                _conf = dict(self.conn_kwargs)
                _conf.update(kwargs)
                mysql_con = mysql.connector.connect(**_conf)
            except Exception as e:
                self._on_connect_error(e)
                return None
        else:
            try:
                mysql_con = mysql.connector.connect(**self.conn_pool_args, **self.conn_kwargs)
                self.connected = True
            except Exception as e:
                print(e)
                try:
                    mysql_con = mysql.connector.connect(**self.conn_kwargs)
                    self.connected = True
                except Exception:
                    self._on_connect_error(e)
                    return None

        conn = Connection(mysql_con)

        # if self.ch_tx_isolvl is None:
        #    self.ch_tx_isolvl = True
        #    c = conn.execute('SHOW SESSION VARIABLES LIKE "tx_isolation"')
        #    if c and c.rowcount :
        #        _row = c.fetchone()
        #        if _row[0] == 'READ-COMMITTED':
        #            self.ch_tx_isolvl = False

        # if self.ch_tx_isolvl:
        #    # https://stackoverflow.com/questions/21974627/mysql-connector-not-showing-inserted-results
        #    conn.execute('SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED')
        #    conn.commit()
        #    #https://mariadb.com/kb/en/library/sql-statements-that-cause-an-implicit-commit/

        # https://stackoverflow.com/questions/21974627/mysql-connector-not-showing-inserted-results
        conn.execute('SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED')
        conn.commit()
        # https://mariadb.com/kb/en/library/sql-statements-that-cause-an-implicit-commit/

        if readonly:
            conn.set_dirty(False)

        return conn

    def _on_connect_error(self, e):
        # get_logger().error('Database connection error', e)
        raise e

    ###
    # Utilities
    #
    @classmethod
    def to_sql(cls, obj):
        if obj is None:
            return None
        # if isinstance(obj, numpy.ndarray):
        #     """
        #     http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
        #     """
        #     out = io.BytesIO()
        #     im = Image.fromarray(obj)
        #     im.save(out, format='JPEG')
        #     out.seek(0)
        #     return cls.dbapi.Binary(out.read())  # buffer
        if isinstance(obj, (list, tuple)):
            # to json
            return json.dumps(obj)
        if isinstance(obj, dict):
            return pickle.dumps(obj)
        return obj

    # @staticmethod
    # def image_from_sql(data):
    #     if not data:
    #         return None
    #
    #     out = io.BytesIO(data)
    #     out.seek(0)
    #     pil = Image.open(out)
    #     return numpy.array(pil)


class Connection(object):
    def __init__(self, mycon):
        self.mycon = mycon
        self.dirty = True

    def set_dirty(self, dirty=True):
        self.dirty = dirty

    def is_connected(self):
        if self.mycon:
            return self.mycon.is_connected()
        return False

    def cursor(self, **kwargs):
        return self.mycon.cursor(**kwargs)

    def execute(self, sql, *args, **kwargs):
        try:
            c = self.mycon.cursor(**kwargs)
            c.execute(sql, args)
            return c
        except Exception as e:
            self._on_execute_error(e)
            return None

    def executemany(self, sql, args, **kwargs):
        try:
            c = self.mycon.cursor(**kwargs)
            c.executemany(sql, args)
            return c
        except Exception as e:
            self._on_execute_error(e)
            return None

    def commit(self):
        self.mycon.commit()

    def execute_file(self, file_path, *args):
        with codecs.open(file_path, 'r', 'utf-8') as f:
            SQLS = f.read()
        if args:
            SQLS = SQLS.format(*args)

        c = self.mycon.cursor()
        rs = c.execute(SQLS, multi=True)
        for r in rs:
            pass
        return c

    def execute_file_with_delimiters(self, file_path):
        queries = []
        delimiter = ';'
        query = ''
        with codecs.open(file_path, 'r', 'utf-8') as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith('--'):
                    continue
                if line.startswith('DELIMITER'):
                    delimiter = line[10:]
                else:
                    query += line + '\n'
                    if line.endswith(delimiter):
                        # Get rid of the delimiter, remove any blank lines and add this query to our list
                        queries.append(query.strip().strip(delimiter))
                        query = ''

        c = self.mycon.cursor()
        # print(queries)
        for query in queries:
            if not query.strip():
                continue
            rs = c.execute(query)
            # for r in rs:
            #     pass
        return c

    def get_connection_id(self):
        return self.mycon.connection_id if self.mycon else 0

    def close(self):
        if self.mycon:
            if self.is_connected():
                if self.dirty:
                    self.commit()
            try:
                self.mycon.close()
            except Exception as e:
                print("Exception on Closing %s", str(e))
            self.mycon = None

    def _on_execute_error(self, e):
        print('Database execute error', exc_info=e)
        self.close()
        # NotificationCenter.default.post_notification(self, DBErrorNotification, e)
        raise e

    def __del__(self):
        self.close()



