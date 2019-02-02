"""
Created on Dec 20 2016
@author: Jerónimo Arenas García

Work with MySQL Database. Run scripts for:

    * Creating database
    * Adding content to database
"""

import argparse
import configparser
from progress.bar import Bar

from dbmanager.CORDISmanager import CORDISmanager
from lemmatizer.ENlemmatizer import ENLemmatizer

def main(resetDB=False, lemmatize=False, projects=False, organizations=False, researchers=False, meta=False):
    """
        :param resetDB: If True, delete existing database and generate new one from zero
        :param lemmatize: If True lemmatize projects table
        :param projects: If True, regenerate projects table
        :param organizations: If True, regenerate organizations table
        :param researchers: If True, regenerate researchers table
        :param meta: If True, regenerate metadata Tables
    """

    cf = configparser.ConfigParser()
    cf.read('config.cf')

    #########################
    # Configuration variables
    #
    dbUSER = cf.get('DB', 'dbUSER')
    dbPASS = cf.get('DB', 'dbPASS')
    dbSERVER = cf.get('DB', 'dbSERVER')
    #db_port =

    #########################
    # Datafiles
    #
    dbNAME = cf.get('CORDIS', 'dbNAME')
    dir_projects = cf.get('CORDIS', 'dir_projects')
    dir_organizations = cf.get('CORDIS', 'dir_organizations')
    dir_researchers = cf.get('CORDIS', 'dir_researchers')
    file_countries = cf.get('CORDIS', 'file_countries')
    file_activities = cf.get('CORDIS', 'file_activities')
    file_fundingsch = cf.get('CORDIS', 'file_fundingsch')
    file_sicCodes = cf.get('CORDIS', 'file_sicCodes')
    file_tpc2020 = cf.get('CORDIS', 'file_tpc2020')
    dir_programmes = cf.get('CORDIS', 'dir_programmes')
    dir_reports_FP7 = cf.get('CORDIS', 'dir_reports_FP7')
    dir_reports_H2020 = cf.get('CORDIS', 'dir_reports_H2020')

    generic_stw = cf.get('CORDIS', 'generic_stw')
    specific_stw = cf.get('CORDIS', 'specific_stw')

    ####################################################
    #1. Database connection

    DB = CORDISmanager (db_name=dbNAME, db_connector='mysql', path2db=None,
                        db_server=dbSERVER, db_user=dbUSER, db_password=dbPASS)
    #                    db_port=dbPORT)

    ##################################################
    #2. If activated, remove and create again database tables
    if resetDB:
        print('Regenerating the database. Existing data will be removed.')
        # The following method deletes all existing tables, and create them
        # again without data
        DB.deleteDBtables()
        DB.createProjectsTable(dir_projects, dir_reports_FP7, dir_reports_H2020)
        DB.createOrganizationsTable(dir_organizations)
        DB.createResearchersTable(dir_researchers)
        DB.createMetatables(file_countries, file_activities, file_fundingsch,
            file_sicCodes, file_tpc2020, dir_programmes)
        DB.SICconsolidate()

    else:
        if projects:
            DB.createProjectsTable(dir_projects, dir_reports_FP7, dir_reports_H2020)
            DB.SICconsolidate()
        if organizations:
            DB.createOrganizationsTable(dir_organizations)
        if researchers:
            DB.createResearchersTable(dir_researchers)
        if meta:
            DB.createMetatables(file_countries, file_activities, file_fundingsch,
                                file_sicCodes, file_tpc2020, dir_programmes)

    # ####################################################
    # 3. Lematización de textos en inglés
    if lemmatize:
        enLM = ENLemmatizer(generic_stw, specific_stw)
        df = DB.readDBtable('projects',limit=None,selectOptions='rcn, title, objective, report')
        allprojects = df.values.tolist()

        #Chunks for monitoring progress and writing in the database
        lchunk = 100
        nproyectos = len(allprojects)
        bar = Bar('Lemmatizing English Descriptions', max=1+nproyectos/lchunk)

        allLEMAS = []
        for index,x in enumerate(allprojects):
            if not (index+1)%lchunk:
                DB.setField('projects', 'rcn', 'LEMAS_UC3M_ENG', allLEMAS)
                allLEMAS = []
                bar.next()
            allLEMAS.append((x[0], enLM.processENstr(x[1]) + ' ***** ' + enLM.processENstr(x[2]) + \
                             ' ***** ' + enLM.processENstr(x[3]) ))
        bar.finish()
        DB.setField('proyectos', 'rcn', 'LEMAS_UC3M_ENG', allLEMAS)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='dbCORDIS')    
    parser.add_argument('--resetDB', action='store_true', help='If activated, the database will be reset and re-created')
    parser.add_argument('--lemmatize', action='store_true', help='If activated, lemmatize the corpus')
    parser.add_argument('--projects', action='store_true', help='If activated, regenerate projects table')
    parser.add_argument('--organizations', action='store_true', help='If activated, regenerate organizations table')
    parser.add_argument('--researchers', action='store_true', help='If activated, regenerate researchers table')
    parser.add_argument('--meta', action='store_true', help='If activated, regenerate metadata tables')
    args = parser.parse_args()

    main(resetDB=args.resetDB, lemmatize=args.lemmatize, projects=args.projects, organizations=args.organizations,
         researchers=args.researchers, meta=args.meta)
