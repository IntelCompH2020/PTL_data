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

from dbmanager.FECYTmanager import FECYTmanager
from lemmatizer.ESlemmatizer import ESLemmatizer

def main(resetDB=False):
    """Genera la Base de Datos a partir de los ficheros Excel proporcionados por FECYT
    :param resetDB: If True, delete existing database and generate new one from zero
    """

    #########################
    # Configuration variables
    #
    dbUSER = 'PTLprojects'
    dbPASS = 'Kts93_u17a'
    dbNAME = 'db_Pr_FECYT'
    dbSERVER = 'vanir.tsc.uc3m.es'
    #dbSERVER = 'localhost'
    #dbSERVER = 'jake.tsc.uc3m.es'
    #dbSERVER = '192.168.1.35' #Synology at home
    #dbPORT = 3307

    #########################
    # Datafiles
    #
    file_convocatorias = './data_Pr_FECYT/Titulo_Convocatoria.xlsx'    
    PAIDdir = './data_Pr_FECYT/PAID_data'
    file_allprojects = './data_Pr_FECYT/All_Projects.xlsx'
    file_allprojects_ESP = './data_Pr_FECYT/All_Projects_ESP.xlsx'
    file_allprojects_ENG = './data_Pr_FECYT/All_Projects_ENG.xlsx'
    file_allprojects_LEMAS = './data_Pr_FECYT/All_Projects_LEMAS.xlsx'
    file_allresearchers = './data_Pr_FECYT/All_Researchers.xlsx'
    file_allorganizations = './data_Pr_FECYT/All_Organizations.xlsx'
    file_coordinados = './data_Pr_FECYT/cordinated.xlsx'

    ####################################################
    #1. Database connection

    DB = FECYTmanager (db_name=dbNAME, db_connector='mysql', path2db=None,
                        db_server=dbSERVER, db_user=dbUSER, db_password=dbPASS)
    #                    db_port=dbPORT)


    # ####################################################
    # #2. If activated, remove and create again database tables
    # if resetDB:
    #     print('Regenerating the database. Existing data will be removed.')
    #     # The following method deletes all existing tables, and create them
    #     # again without data
    #     DB.deleteDBtables()
    #     DB.createDBtables(file_convocatorias)

    # # ####################################################
    # # #3. Processing PAID datafiles

    # DB.addPAIDdir(PAIDdir)

    # ####################################################
    # #4. Processing excel files with project information by reference
    # DB.updateprojectdata(file_allprojects)
    # DB.updateprojectdata(file_allprojects_ESP)
    # DB.updateprojectdata(file_allprojects_ENG)
    # DB.updateprojectdata(file_allprojects_LEMAS)

    # ####################################################
    # #5. Processing excel files with organization information by CIF
    # DB.updateorgdata(file_allorganizations)

    # ####################################################
    # #6. Processing excel files with researchers information by NIF
    # DB.updateresearcherdata(file_allresearchers)
    #
    # Additionally, consolidate tables investigadores and investigadorproyecto
    # DB.cleanResearcherTable()

    # ####################################################
    # #7. Run translation if necessary and save results to excel file
    # #so that it is not necessary to rerun this code for already translated projects
    # DB.run_translator()
    # writer = pd.ExcelWriter(file_allprojects_ESP[:-5]+'_new.xlsx')
    # for fld in ['TITULO_ESP', 'RESUMEN_ESP', 'PALABRAS_ESP']:
    #     df = DB.readDBtable('proyectos', limit=None,
    #                     selectOptions='REFERENCIA, '+fld,
    #                     filterOptions=fld +' IS NOT NULL AND LENGTH('+fld+')',
    #                     orderOptions=None)
    #     df.to_excel(writer, sheet_name=fld, index=False)
    # writer.save()

    # for cc in ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016']:
    DB.run_translator_ENG('2007')
    # writer = pd.ExcelWriter(file_allprojects_ENG[:-5]+'_new.xlsx')
    # for fld in ['TITULO_ENG', 'RESUMEN_ENG', 'PALABRAS_ENG']:
    #     df = DB.readDBtable('proyectos', limit=None,
    #                     selectOptions='REFERENCIA, '+fld,
    #                     filterOptions=fld +' IS NOT NULL AND LENGTH('+fld+')',
    #                     orderOptions=None)
    #     df.to_excel(writer, sheet_name=fld, index=False)
    # writer.save()

    # ####################################################
    # #8. Detection of coordinated projects

    # # This line generates a file with all coordinated files information
    # # It is advisable to manually edit the file before saveing to database
    # #DB.detecta_coord(file_coordinados)

    # #Save coordinated projects information to database
    # df = pd.read_excel(file_coordinados)
    # df = df[['REF', 'Num coordinados', 'Lista coordinados']]
    # df = df[df['Num coordinados']>0]
    # valores = df.values.tolist()

    # DB.setField('proyectos', 'REFERENCIA', 'NCOORDINADOS', [(el[0], el[1]) for el in valores])
    # DB.setField('proyectos', 'REFERENCIA', 'PCOORDINADOS', [(el[0], el[2]) for el in valores])

    # ####################################################
    # #9. Lematización de textos en castellano
    # esLM = ESLemmatizer()
    # df = DB.readDBtable('proyectos',limit=None,selectOptions='REFERENCIA, TITULO_ESP, PALABRAS_ESP, RESUMEN_ESP',
    #                     filterOptions='TITULO_ESP IS NOT NULL')
    # allprojects = df.values.tolist()

    # lchunk = 100
    # nproyectos = len(allprojects)
    # bar = Bar('Lemmatizing Spanish Descriptions', max=1+nproyectos/lchunk)

    # allLEMAS = []
    # for index,x in enumerate(allprojects):
    #     if not index%lchunk:
    #         bar.next()
    #     allLEMAS.append((x[0], esLM.processESstr(x[1]) + '*****' + esLM.processESstr(x[2]) + \
    #              '*****' + esLM.processESstr(x[3])))
    # bar.finish()
    # DB.setField('proyectos', 'REFERENCIA', 'LEMAS_UC3M', allLEMAS)

    # ####################################################
    # #9. Lematización de textos en inglés



if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='dbFECYT')    
    parser.add_argument('--resetDB', action='store_true', help='If activated, the database will be reset and re-created')
    args = parser.parse_args()

    if args.resetDB:
        #The database will be erased and recreated from scratch, default excel files 
        #will be used as indicated in the configuration file
        main(resetDB=True)

    else:
        main(resetDB=False)
