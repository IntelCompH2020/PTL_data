# -*- coding: utf-8 -*-
"""
Created on Dec 20 2016
@author: Jerónimo Arenas García

Work with MySQL Database. Run scripts for:

    * Creating database
    * Adding content to database
    * ... 

"""

import argparse
import pandas as pd
import ipdb
from progress.bar import Bar
import os

from dbmanager.base_dm_sql import BaseDMsql

def main(resetDB=False):
    """Genera la Base de Datos a partir de los ficheros Excel proporcionados por FECYT
    :param resetDB: If True, delete existing database and generate new one from zero
    """

    #########################
    # Configuration variables
    #
    dbUSER = 'PTLprojects'
    #dbUSER = 'jero_admin'
    dbPASS = 'Kts93_u17a'
    #dbPASS = 'Ae7Kithi,se9'
    dbNAME = 'db_Pa_PATSTATS'
    dbSERVER = 'vanir.tsc.uc3m.es'
    #dbSERVER = 'localhost'
    #dbSERVER = 'jake.tsc.uc3m.es'
    #dbSERVER = '192.168.1.35' #Synology at home
    #dbPORT = 3307

    path_tozipfiles = './data_Pa_PATSTAT/data'
    path_tobow = './data_Pa_PATSTAT/bows.csv'
    tmpdir = './data_Pa_PATSTAT/tmp'

    ####################################################
    #1. Database connection

    DB = BaseDMsql (db_name=dbNAME, db_connector='mysql', path2db=None,
                        db_server=dbSERVER, db_user=dbUSER, db_password=dbPASS)
    #                    db_port=dbPORT)


    ####################################################
    #2. If activated, remove and create again database tables
    if resetDB:
        print('Regenerating the database. Existing data will be removed.')
        # The following method deletes all existing tables, and create them
        # again without data

        # cmd = './load_patstat.sh -v -u ' + dbUSER + ' -p ' + dbPASS + ' -h ' + dbSERVER + \
        #       ' -z ' + path_tozipfiles + ' -e '+ tmpdir + ' -d ' + dbNAME
        # print(cmd)

        # os.system(cmd)
        
        #Importamos el BOW de politecnica
        print('Volcando los bow proporcionados por UPM')
        lines = []
        with open(path_tobow, 'r') as fin:
            for i, ln in enumerate(fin.readlines()):
                if not i%1000000:
                    print('Numero de registros leidos:', i)
                lines.append(ln.split(';;'))
        lines = list(map(lambda x: (x[0], x[-1].strip()), lines))
        lines = list(filter(lambda x: x[0]!='appln_id', lines))
        #Escribimos en la base de datos por chunks para no saturar
        print('Escribiendo en la Base de Datos')
        def chunks(l, n):
            """ Yield successive n-sized chunks from l. """
            for i in range(0, len(l), n):
                yield l[i: i + n]
        chunksize = 100000
        chunksresult = list(chunks(lines, chunksize))
        bar = Bar('Saving Bow to database:', max=len(chunksresult))
        bar.next()
        for data in chunksresult:
            DB.insertInTable('tls203_appln_abstr',
                ['appln_id', 'appln_abstract_bow'], data)
            bar.next()

        bar.finish()



if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='dbPATSTATS')    
    parser.add_argument('--resetDB', action='store_true', help='If activated, the database will be reset and re-created')
    args = parser.parse_args()

    if args.resetDB:
        #The database will be erased and recreated from scratch, default excel files 
        #will be used as indicated in the configuration file
        main(resetDB=True)

    else:
        main(resetDB=False)
