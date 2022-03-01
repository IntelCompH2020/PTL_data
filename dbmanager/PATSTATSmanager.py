"""
This class provides functionality for:

* importing project data provided by FECYT

Created on Jul 5 2018

@author: Jerónimo Arenas García

"""

from __future__ import print_function    # For python 2 copmatibility
import os
import pandas as pd
import numpy as np
import copy
import ipdb
from progress.bar import Bar
import time


from dbmanager.base_dm_sql import BaseDMsql


class PATSTATSmanager(BaseDMsql):
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

        super(PATSTATSmanager, self).__init__(
            db_name, db_connector, path2db, db_server, db_user,
            db_password, db_port)

        #Change character set. 4 Bytes are necessary
        self._conn.set_character_set('utf8mb4')


    def createDBtables(self):
        """
        Create DB table structure
        """

        sql_cmd = """CREATE TABLE tls203_appln_abstr (
                        appln_id int(11) NOT NULL DEFAULT '0',
                        appln_abstract_lg char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
                        appln_abstract text COLLATE utf8mb4_unicode_ci,
                        appln_lemas text COLLATE utf8mb4_unicode_ci,
                        PRIMARY KEY (appln_id)
                        ) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  AVG_ROW_LENGTH=1500;"""
        self._c.execute(sql_cmd)

        #Commit changes to database
        self._conn.commit()

