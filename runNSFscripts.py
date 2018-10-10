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

from dbmanager.CORDISmanager import CORDISmanager
from lemmatizer.ESlemmatizer import ESLemmatizer
from lemmatizer.ENlemmatizer import ENLemmatizer

def main(resetDB=False):
    """Genera la Base de Datos a partir de los ficheros Excel proporcionados por FECYT
    :param resetDB: If True, delete existing database and generate new one from zero
    """

    #########################
    # Configuration variables
    #
    dbUSER = 'PTLprojects'
    dbPASS = 'Kts93_u17a'
    dbNAME = 'db_Pr_NSF'
    dbSERVER = 'vanir.tsc.uc3m.es'
    #dbSERVER = 'localhost'
    #dbSERVER = 'jake.tsc.uc3m.es'
    #dbSERVER = '192.168.1.35' #Synology at home
    #dbPORT = 3307

    #########################
    # Datafiles
    #
    dir_projects = './data_Pr_CORDIS/data/ProjectData/Excel/'
    dir_organizations = './data_Pr_CORDIS/data/OrganizationData/Excel/'
    dir_researchers = './data_Pr_CORDIS/data/ResearcherProject/Excel/'
    file_countries = './data_Pr_CORDIS/data/Countries/Excel/cordisref-countries.xls'
    file_activities = './data_Pr_CORDIS/data/OrgActivity/Excel/cordisref-organizationActivityType.xls'
    file_fundingsch = './data_Pr_CORDIS/data/FundingScheme/Excel/cordisref-projectFundingSchemeCategory.xls'
    file_sicCodes = './data_Pr_CORDIS/data/sicCodes/Excel/cordisref-sicCode.xls'
    file_tpc2020 = './data_Pr_CORDIS/data/Topics/Excel/cordisref-H2020topics.xlsx'
    dir_programmes = './data_Pr_CORDIS/data/Programmes/Excel/'

    ####################################################
    #1. Database connection

    DB = CORDISmanager (db_name=dbNAME, db_connector='mysql', path2db=None,
                        db_server=dbSERVER, db_user=dbUSER, db_password=dbPASS)
    #                    db_port=dbPORT)

    ####################################################
    # #2. If activated, remove and create again database tables
    if resetDB:
        print('Regenerating the database. Existing data will be removed.')
        # The following method deletes all existing tables, and create them
        # again without data
    #     DB.deleteDBtables()
    #     DB.createDBtables(dir_projects, dir_organizations, dir_researchers,
    #         file_countries, file_activities, file_fundingsch,
    #         file_sicCodes, file_tpc2020, dir_programmes)


    # # ####################################################
    # # 3. Arregla los campos SIC en la tabla de projects
    # DB.SICconsolidate()


    # ####################################################
    # # 4. Lematización de textos en inglés
    enLM = ENLemmatizer()
    df = DB.readDBtable('total_projects',limit=None,selectOptions='ProjectID, Title, AbstractNarration')
    allprojects = df.values.tolist()

    lchunk = 1000
    nproyectos = len(allprojects)
    bar = Bar('Lemmatizing English Descriptions', max=1+nproyectos/lchunk)

    allLEMAS = []
    for index,x in enumerate(allprojects):
        if not (index+1)%lchunk:
            DB.setField('total_projects', 'ProjectID', 'LEMAS_UC3M_ENG', allLEMAS)
            allLEMAS = []
            bar.next()
        allLEMAS.append((x[0], enLM.processENstr(x[1]) + '*****' + enLM.processENstr(x[2])))
    bar.finish()
    DB.setField('proyectos', 'ProjectID', 'LEMAS_UC3M_ENG', allLEMAS)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='dbCORDIS')    
    parser.add_argument('--resetDB', action='store_true', help='If activated, the database will be reset and re-created')
    args = parser.parse_args()

    if args.resetDB:
        #The database will be erased and recreated from scratch, default excel files 
        #will be used as indicated in the configuration file
        main(resetDB=True)

    else:
        main(resetDB=False)
