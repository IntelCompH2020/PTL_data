"""
This class provides functionality for:

* importing ACL anthology data

Created on Feb 27 2019

@author: Jerónimo Arenas García

"""

import os
import pandas as pd
import numpy as np
import ipdb
from progress.bar import Bar
import time
from collections import Counter
import itertools

from dbmanager.base_dm_sql import BaseDMsql

class ACLmanager(BaseDMsql):
    """
    Specific functions for FECYT database creation
    """

    def __init__(self, db_name, db_connector, path2db=None,
                 db_server=None, db_user=None, db_password=None, db_port=None):
        """
        Initializes the FECYT Manager object

        Args:
            db_name      :Name of the DB
            db_connector :Connector. Available options are mysql or sqlite
            path2db :Path to the project folder (sqlite only)
            db_server    :Server (mysql only)
            db_user      :User (mysql only)
            db_password  :Password (mysql only)
        """
        super(ACLmanager, self).__init__(
            db_name, db_connector, path2db, db_server, db_user,
            db_password, db_port)

    def createDBtables(self):
        """
        Create DB table structure
        """
        if 'ACLpapers' in self.getTableNames():
            sql_cmd = """DROP TABLE ACLpapers"""
            self._c.execute(sql_cmd)

        sql_cmd = """CREATE TABLE ACLpapers(

                        ACLid VARCHAR(8) PRIMARY KEY,
                        SSid VARCHAR(40) NOT NULL,

                        year SMALLINT UNSIGNED,
                        doi TINYTEXT,
                        booktitle TINYTEXT,
                        publisher TINYTEXT,

                        title TEXT,
                        abstract TEXT,
                        entities TEXT,
                        paper MEDIUMTEXT,

                        LEMAS_title TEXT,
                        LEMAS_abstract TEXT,
                        LEMAS_entities TEXT,
                        LEMAS_paper MEDIUMTEXT,

                        LEMAS2_title TEXT,
                        LEMAS2_abstract TEXT,
                        LEMAS2_entities TEXT,
                        LEMAS2_paper MEDIUMTEXT

                        ) DEFAULT CHARSET=utf8mb4"""
        self._c.execute(sql_cmd)

        sql_cmd = """CREATE UNIQUE INDEX SSid ON ACLpapers(SSid)"""
        self._c.execute(sql_cmd)

        if 'outCitations_graph' in self.getTableNames():
            sql_cmd = """DROP TABLE outCitations_graph"""
            self._c.execute(sql_cmd)

        sql_cmd = """CREATE TABLE outCitations_graph(

                        ACLid1 VARCHAR(8) NOT NULL,
                        ACLid2 VARCHAR(8) NOT NULL,
                        comon_cit SMALLINT UNSIGNED NOT NULL,
                        comon_cit_noself SMALLINT UNSIGNED NOT NULL,
                        weight FLOAT NOT NULL,
                        weight_noself FLOAT NOT NULL

                        ) DEFAULT CHARSET=utf8mb4"""
        self._c.execute(sql_cmd)

        sql_cmd = """CREATE INDEX ACLid1 ON outCitations_graph(ACLid1)"""
        self._c.execute(sql_cmd)
        sql_cmd = """CREATE INDEX ACLid2 ON outCitations_graph(ACLid2)"""
        self._c.execute(sql_cmd)

        #Commit changes to database
        self._conn.commit()

