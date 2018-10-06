"""
This class provides functionality for:

* importing project data provided by FECYT

Created on Jul 5 2018

@author: Jerónimo Arenas García

"""

import os
import ipdb
import pandas as pd
import numpy as np
from progress.bar import Bar
from datetime import datetime
import time

from dbmanager.base_dm_sql import BaseDMsql

SCI_diccio = {'Materials Technology': 'MAT',
 'Resources of the Sea, Fisheries': 'SEA',
 'Life Sciences': 'LIF',
 'Fossil Fuels': 'FFU',
 'Electronics, Microelectronics': 'ELM',
 'Education, Training' : 'EDU',
 'Telecommunications': 'TEL',
 'Policies': 'POL',
 'Information Processing, Information Systems': 'IPS',
 'Information Processing, Informa': 'IPS',
 'Economic Aspects': 'ECO',
 'Earth Sciences': 'EAR',
 'Energy Storage, Energy Transport': 'EST',
 'Transport': 'TRA',
 'Reference Materials': 'REF',
 'Radiation Protection': 'RAD',
 'Meteorology': 'MET',
 'Food': 'FOO',
 'Standards': 'STA',
 'Radioactive Waste': 'RWA',
 'Industrial Manufacture': 'IND',
 'Innovation, Technology Transfer': 'ITT',
 'Regional Development': 'REG',
 'Scientific Research': 'SCI',
 'Safety': 'SAF',
 'Agriculture': 'AGR',
 'Energy Saving': 'ESV',
 'Telecommunication': 'TEL',
 'Legislation, Regulations': 'LEG',
 'Aerospace Technology': 'AER',
 'Nuclear Fission': 'FUS',
 'Evaluation': 'EVA',
 'Coordination, Cooperation': 'COO',
 'Information, Media': 'INF',
 'Other Energy Topics': 'OET',
 'Biotechnology': 'BIO',
 'Social Aspects': 'SOC',
 'Mathematics, Statistics': 'MST',
 'Other Technology': 'TEC',
 'Waste Management': 'WAS',
 'Telecommunicatio': 'TEL',
 'Medicine, Health': 'MED',
 'Environmental Protection': 'ENV',
 'Measurement Methods': 'MEA',
 'Construction Technology': 'CON',
 'Forecasting': 'FOR',
 'Nuclear Fusion': 'FUS',
 'Renewable Sources of Energy': 'RSE'}

def replace_SIC(input_array):
    for descr, code in SCI_diccio.items():
        input_array = input_array.replace(descr, code)
    input_array = input_array.replace(' ','')
    return input_array


class CORDISmanager(BaseDMsql):
    """
    Specific functions for CORDIS database creation
    """

    def __init__(self, db_name, db_connector, path2db=None,
                 db_server=None, db_user=None, db_password=None, db_port=None):
        """
        Initializes the CORDIS Manager object

        Args:
            db_name      :Name of the DB
            db_connector :Connector. Available options are mysql or sqlite
            path2db :Path to the project folder (sqlite only)
            db_server    :Server (mysql only)
            db_user      :User (mysql only)
            db_password  :Password (mysql only)
        """

        super(CORDISmanager, self).__init__(
            db_name, db_connector, path2db, db_server, db_user,
            db_password, db_port)

    def createDBtables(self, prj_dir, org_dir, rsr_dir,
            ctr_file, act_file, fs_file, sic_file, tpc2020_file, prg_dir):
        """
        Create DB table structure and fill in with some data

            * prj_dir: Relative path to directory with project Excel files
            * org_dir: Relative path to directory with organization Excel files
            * rsr_dir: Relative path to directory with researcher Excel files
            * ctr_file: Relative path to excel file with country information
            * act_file: Relative path to excel file with organization activities
            * fs_file: Relative path to excel file with funding scheme information
            * sic_file: Relative path to excel file with SIC Codes information
            * tpc2020_file: Relative path to excel file with H2020 Topics Information
            * prg_dir: Relative path to directory with programme information

        """

        if 'projects' not in self.getTableNames():
            ####create projects table
            sql_cmd = """CREATE TABLE projects(
                            frame_programme VARCHAR(5) DEFAULT NULL,
                            rcn int(11) NOT NULL PRIMARY KEY,
                            reference VARCHAR(45) DEFAULT NULL,
                            acronym VARCHAR(45) DEFAULT NULL,
                            status VARCHAR(255) DEFAULT NULL,
                            programme VARCHAR(255) DEFAULT NULL,
                            topics VARCHAR(255) DEFAULT NULL,
                            frameworkProgramme VARCHAR(45) DEFAULT NULL,
                            title TEXT DEFAULT NULL,
                            startDate datetime DEFAULT NULL,
                            endDate datetime DEFAULT NULL,
                            projectUrl VARCHAR(255) DEFAULT NULL,
                            objective TEXT DEFAULT NULL,
                            totalCost VARCHAR(255) DEFAULT NULL,
                            ecMaxContribution VARCHAR(255) DEFAULT NULL,
                            `call` VARCHAR(45) DEFAULT NULL,
                            fundingScheme VARCHAR(255) DEFAULT NULL,
                            coordinator VARCHAR(255) DEFAULT NULL,
                            coordinatorCountry VARCHAR(5) DEFAULT NULL,
                            participants TEXT,
                            participantCountries VARCHAR(255) DEFAULT NULL,
                            subjects VARCHAR(255) DEFAULT NULL,
                            LEMAS_UC3M_ENG TEXT
                            ) DEFAULT CHARSET=utf8"""
            self._c.execute(sql_cmd)

            fieldnames = self.getColumnNames('projects')

            #Fill table with project data
            #We process all excel files in the indicated directory
            for root, dirs, files in os.walk(prj_dir):
                for file in files:
                    if file.endswith('.xls') or file.endswith('.xlsx'):
                        if not file.startswith('~'):
                            print('Importing project file:', os.path.join(root,file))
                            df = pd.read_excel(os.path.join(root,file))
                            #We add an identifier of the FP
                            df['frame_programme'] = file.split('_')[0]
                            #Keep only columns in SQL Table
                            df_fld = [fld for fld in fieldnames
                                            if fld in df.columns.tolist()]
                            df = df[df_fld]
                            #Fill nan in date columns to a predefined value for later setting it to NULL
                            df['startDate'].fillna(datetime(2100,1,1), inplace=True)
                            df['startDate'] = pd.to_datetime(df['startDate'])
                            df['endDate'].fillna(datetime(2100,1,1), inplace=True)
                            df['endDate'] = pd.to_datetime(df['endDate'])
                            #Fill nan in numeric columns to a predefined value for later setting it to NULL
                            df['totalCost'] = df['totalCost'].astype(float).fillna(0.0)
                            df['ecMaxContribution'] = df['ecMaxContribution'].astype(float).fillna(0.0)
                            #Fill all other nans with empty strings
                            df = df.replace(np.nan, '', regex=True)
                            #Store data in SQL table
                            self.insertInTable('projects', df_fld, df.values.tolist())

            #Set to NULL missing date values (String columns are left as empty strings)
            sql_cmd = 'UPDATE projects set startDate=NULL where startDate="2100-01-01"'
            self._c.execute(sql_cmd)
            sql_cmd = 'UPDATE projects set endDate=NULL where endDate="2100-01-01"'
            self._c.execute(sql_cmd)
            sql_cmd = 'UPDATE projects set totalCost=NULL where totalCost=0'
            self._c.execute(sql_cmd)
            sql_cmd = 'UPDATE projects set ecMaxContribution=NULL where ecMaxContribution=0'
            self._c.execute(sql_cmd)

        if 'organizations' not in self.getTableNames():
            ####create organizations table
            sql_cmd = """CREATE TABLE organizations(
                            id INT(11),
                            name VARCHAR(255) NOT NULL PRIMARY KEY,
                            shortName VARCHAR(45) DEFAULT NULL,
                            activityType VARCHAR(45) DEFAULT NULL,
                            country VARCHAR(5) DEFAULT NULL,
                            street VARCHAR(255) DEFAULT NULL,
                            city VARCHAR(45) DEFAULT NULL,
                            postCode VARCHAR(45) DEFAULT NULL,
                            organizationUrl VARCHAR(255) DEFAULT NULL,
                            vatNumber VARCHAR(45) DEFAULT NULL
                            ) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""
            self._c.execute(sql_cmd)

            sql_cmd = """CREATE TABLE orgzproject(
                            name VARCHAR(255) NOT NULL,
                            projectRcn INT(11) NOT NULL,
                            role VARCHAR(45),
                            ecContribution FLOAT,
                            endOfParticipation VARCHAR(45),
                            activityType VARCHAR(45) DEFAULT NULL,
                            country VARCHAR(5) DEFAULT NULL
                            ) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""
            self._c.execute(sql_cmd)

            # #Fill table with organization data
            # #We process all excel files in the indicated directory
            # #and concatenate all available information in one dataframe
            # flds = ['projectRcn', 'role', 'id', 'name', 'shortName', 'activityType',
            #          'endOfParticipation', 'ecContribution', 'country', 'street',
            #          'city', 'postCode', 'organizationUrl', 'vatNumber']
            # df_all = pd.DataFrame(columns=flds)

            # for root, dirs, files in os.walk(org_dir):
            #     for file in files:
            #         if file.endswith('.xls') or file.endswith('.xlsx'):
            #             if not file.startswith('~'):
            #                 print('Importing organization file:', os.path.join(root,file))
            #                 df = pd.read_excel(os.path.join(root,file))
            #                 df_fld = [fld for fld in flds if fld in df.columns.tolist()]
            #                 df = df[df_fld]
            #                 df_all = df_all.append(df, ignore_index=True)

            # #Fill nan in numeric columns to a predefined value for later setting it to NULL
            # df_all['ecContribution'] = df_all['ecContribution'].astype(float).fillna(0.0)
            # #Fill all other nans with empty strings
            # df_all = df_all.replace(np.nan, '', regex=True)
            # #In field ActivityType the acronym is sometimes preceded by slash
            # df_all['activityType'] = df_all['activityType'].apply(lambda x: x[-3:])

            # #Capitalize string fields
            # df_all['name'] = df_all['name'].str.upper()
            # df_all['shortName'] = df_all['shortName'].str.upper()
            # df_all['activityType'] = df_all['activityType'].str.upper()
            # df_all['country'] = df_all['country'].str.upper()
            # df_all['city'] = df_all['city'].str.upper()
            # df_all['postCode'] = df_all['postCode'].str.upper()
            # df_all['organizationUrl'] = df_all['organizationUrl'].str.upper()

            # #Next, we are going to collapse names, etc of institutions having the same URL
            # diccionames = {}
            # URLS = list(set(df_all['organizationUrl'].dropna().values.tolist()))
            # URLS = [x for x in URLS if x!='']

            # for i,k in enumerate(URLS):
            #     if not i%1000:
            #         print(i)
            #     df_small = df_all[df_all['organizationUrl']==k]
            #     diccionames[k] = list(set(df_small['name'].values.tolist()))

            # #Collapse names, shortname and activityType
            # for i,k in enumerate(URLS):
            #     if not i%1000:
            #         print(i)

            #     #Obtain all names associated with URL    
            #     existingnames = [ x for x in diccionames[k] if x !='']

            #     #Extract relevant dataframe and preferred values for certain fields
            #     dfaux = df_all.loc[df_all['name'].isin(existingnames)]
            #     if len(dfaux):
            #         preferredname = dfaux['name'].mode()[0]
            #         preferredshort = dfaux['shortName'].mode()[0]
            #         preferredUrl = dfaux['organizationUrl'].mode()[0]
            #         preferredactivity = dfaux['activityType'].mode()[0]

            #         #Finally, make replacements
            #         df_all.loc[df_all['name'].isin(existingnames), 'shortName'] = preferredshort
            #         df_all.loc[df_all['name'].isin(existingnames), 'organizationUrl'] = preferredUrl
            #         df_all.loc[df_all['name'].isin(existingnames), 'activityType'] = preferredactivity
            #         df_all.loc[df_all['name'].isin(existingnames), 'name'] = preferredname

            # #Next, we are going to collapse names, etc of institutions having the same VATNumber
            # diccionames = {}
            # VATS = list(set(df_all['vatNumber'].dropna().values.tolist()))
            # VATS = [x for x in VATS if x!='']
            # VATS = [x for x in VATS if x!='NOTAPPLICABLE']

            # for i,k in enumerate(VATS):
            #     if not i%1000:
            #         print(i)
            #     df_small = df_all[df_all['vatNumber']==k]
            #     diccionames[k] = list(set(df_small['name'].values.tolist()))

            # #Collapse names, shortname and activityType
            # for i,k in enumerate(VATS):
            #     if not i%1000:
            #         print(i)

            #     #Obtain all names associated with URL    
            #     existingnames = [ x for x in diccionames[k] if x !='']

            #     #Extract relevant dataframe and preferred values for certain fields
            #     dfaux = df_all.loc[df_all['name'].isin(existingnames)]
            #     if len(dfaux):
            #         preferredname = dfaux['name'].mode()[0]
            #         preferredshort = dfaux['shortName'].mode()[0]
            #         preferredUrl = dfaux['organizationUrl'].mode()[0]
            #         preferredactivity = dfaux['activityType'].mode()[0]

            #         #Finally, make replacements
            #         df_all.loc[df_all['name'].isin(existingnames), 'shortName'] = preferredshort
            #         df_all.loc[df_all['name'].isin(existingnames), 'organizationUrl'] = preferredUrl
            #         df_all.loc[df_all['name'].isin(existingnames), 'activityType'] = preferredactivity
            #         df_all.loc[df_all['name'].isin(existingnames), 'name'] = preferredname
            #         df_all.loc[df_all['name'].isin(existingnames), 'vatNumber'] = k

            # #Next, we are going to collapse names, etc of institutions having the same id
            # diccionames = {}
            # IDS = list(set(df_all['id'].dropna().values.tolist()))
            # IDS = [x for x in IDS if x!='']

            # for i,k in enumerate(IDS):
            #     if not i%1000:
            #         print(i)
            #     df_small = df_all[df_all['id']==k]
            #     diccionames[k] = list(set(df_small['name'].values.tolist()))

            # #Collapse names, shortname and activityType
            # for i,k in enumerate(IDS):
            #     if not i%1000:
            #         print(i)

            #     #Obtain all names associated with URL    
            #     existingnames = [ x for x in diccionames[k] if x !='']

            #     #Extract relevant dataframe and preferred values for certain fields
            #     dfaux = df_all.loc[df_all['name'].isin(existingnames)]
            #     if len(dfaux):
            #         preferredname = dfaux['name'].mode()[0]
            #         preferredshort = dfaux['shortName'].mode()[0]
            #         preferredUrl = dfaux['organizationUrl'].mode()[0]
            #         preferredactivity = dfaux['activityType'].mode()[0]

            #         #Finally, make replacements
            #         df_all.loc[df_all['name'].isin(existingnames), 'shortName'] = preferredshort
            #         df_all.loc[df_all['name'].isin(existingnames), 'organizationUrl'] = preferredUrl
            #         df_all.loc[df_all['name'].isin(existingnames), 'activityType'] = preferredactivity
            #         df_all.loc[df_all['name'].isin(existingnames), 'name'] = preferredname
            #         df_all.loc[df_all['name'].isin(existingnames), 'id'] = k

            # #Remove elements without a name (barely 350)
            # df_all = df_all.loc[df_all['name']!='']

            df_all = pd.read_excel('df_all.xlsx')
            #We are going to use the name as index. We concatenate with the country
            #in case a company can be registered in two different countries
            df_all['name'] = df_all['name'] + '_' + df_all['country']


            df_fld = ['id', 'name', 'shortName', 'activityType', 'country', 'street',
                                 'city', 'postCode', 'organizationUrl', 'vatNumber']
            df_all_org = df_all[df_fld]
            df_all_org = df_all_org.replace(np.nan, '', regex=True)
            df_all_org = df_all_org.drop_duplicates(subset=['name'])

            df_all_org_values = df_all_org.values.tolist()

            #Store data in SQL table
            for record in df_all_org_values:
                try:
                    self.insertInTable('organizations', df_fld, [record])
                except:
                    print(record[1])

            df_fld = ['name', 'projectRcn', 'role', 'ecContribution', 'endOfParticipation',
                        'activityType', 'country']
            df_all_orgprj = df_all[df_fld]
            df_all_orgprj = df_all_orgprj.replace(np.nan, '', regex=True)
            df_all_orgprj = df_all_orgprj.drop_duplicates()

            self.insertInTable('orgzproject', df_fld, df_all_orgprj.values.tolist())

        if 'countries' not in self.getTableNames():
            ####create Countries table
            sql_cmd = """CREATE TABLE countries(
                            euCode VARCHAR(2) CHARACTER SET utf8 NOT NULL,
                            isoCode VARCHAR(40) CHARACTER SET utf8,
                            name VARCHAR(50) CHARACTER SET utf8,
                            language VARCHAR(2) CHARACTER SET utf8
                            )"""
            self._c.execute(sql_cmd)

            #Fill table with data from ctr_file
            df = pd.read_excel(ctr_file)
            df = df.replace(np.nan, '', regex=True)
            fieldnames = df.columns.tolist()
            fieldvalues = df.values.tolist()
            self.insertInTable('countries', fieldnames, fieldvalues)

        if 'orgactivities' not in self.getTableNames():
            ####create orgactivities table
            sql_cmd = """CREATE TABLE orgactivities(
                            code VARCHAR(3) CHARACTER SET utf8 NOT NULL,
                            activityType VARCHAR(100) CHARACTER SET utf8
                            )"""
            self._c.execute(sql_cmd)

            #Fill table with data from act_file
            df = pd.read_excel(act_file)
            df = df.replace(np.nan, '', regex=True)
            fieldnames = ['code', 'activityType']
            fieldvalues = df[['Code','Title']].values.tolist()
            self.insertInTable('orgactivities', fieldnames, fieldvalues)

        if 'fundingschemes' not in self.getTableNames():
            ####create fundingschemes table
            sql_cmd = """CREATE TABLE fundingschemes(
                            code VARCHAR(20) CHARACTER SET utf8 NOT NULL,
                            fundingScheme VARCHAR(150) CHARACTER SET utf8
                            )"""
            self._c.execute(sql_cmd)

            #Fill table with data from fs_file
            df = pd.read_excel(fs_file)
            df = df.replace(np.nan, '', regex=True)
            df = df.applymap(str)
            fieldnames = ['code', 'fundingScheme']
            fieldvalues = df[['code','title']].values.tolist()
            self.insertInTable('fundingschemes', fieldnames, fieldvalues)

        if 'sicCodes' not in self.getTableNames():
            ####create sicCodes table
            sql_cmd = """CREATE TABLE sicCodes(
                            code VARCHAR(3) CHARACTER SET utf8 NOT NULL,
                            SICtitle VARCHAR(100) CHARACTER SET utf8,
                            description VARCHAR(300) CHARACTER SET utf8,
                            language VARCHAR(2) CHARACTER SET utf8
                            )"""
            self._c.execute(sql_cmd)

            #Fill table with data from sic_file
            df = pd.read_excel(sic_file)
            df = df.replace(np.nan, '', regex=True)
            fieldnames = ['code', 'SICtitle', 'description', 'language']
            fieldvalues = df.values.tolist()
            self.insertInTable('sicCodes', fieldnames, fieldvalues)

        if 'topics2020' not in self.getTableNames():
            ####create sicCodes table
            sql_cmd = """CREATE TABLE topics2020(
                            topicRCN INT(11) NOT NULL PRIMARY KEY,
                            topicCODE VARCHAR(100) CHARACTER SET utf8 NOT NULL,
                            title VARCHAR(255) CHARACTER SET utf8,
                            language VARCHAR(2) CHARACTER SET utf8
                            )"""
            self._c.execute(sql_cmd)

            #Fill table with data from tpc2020_file
            df = pd.read_excel(tpc2020_file)
            df = df.replace(np.nan, '', regex=True)
            fieldnames = ['topicRCN', 'topicCODE', 'title', 'language']
            fieldvalues = df.values.tolist()
            self.insertInTable('topics2020', fieldnames, fieldvalues)

        if 'programmes' not in self.getTableNames():
            ####create sicCodes table
            sql_cmd = """CREATE TABLE programmes(
                            prgRCN INT(11) NOT NULL,
                            prgCODE VARCHAR(45) CHARACTER SET utf8,
                            title VARCHAR(400) CHARACTER SET utf8,
                            shortTitle VARCHAR(100) CHARACTER SET utf8,
                            language VARCHAR(2) CHARACTER SET utf8
                            )"""
            self._c.execute(sql_cmd)

            #Fill table with programmes data
            #We process all excel files in the indicated directory
            #and concatenate all available information in one dataframe
            flds = ['rcn', 'code', 'title', 'shortTitle', 'language']
            df_all = pd.DataFrame(columns=flds)

            for root, dirs, files in os.walk(prg_dir):
                for file in files:
                    if file.endswith('.xls') or file.endswith('.xlsx'):
                        if not file.startswith('~'):
                            print('Importing programmes file:', os.path.join(root,file))
                            df = pd.read_excel(os.path.join(root,file))
                            df_all = df_all.append(df, ignore_index=True)

            #Fill table with data from sic_file
            df_all = df_all.replace(np.nan, '', regex=True)
            fieldvalues = df_all.values.tolist()
            fieldnames = ['prgRCN', 'prgCODE', 'title', 'shortTitle', 'language']
            self.insertInTable('programmes', fieldnames, fieldvalues)

        if 'researchers' not in self.getTableNames():
            ####create sicCodes table
            sql_cmd = """CREATE TABLE researchers(
                            researcherID int(11) NOT NULL PRIMARY KEY,
                            title VARCHAR(5) CHARACTER SET utf8,
                            firstName VARCHAR(40) CHARACTER SET utf8,
                            lastName VARCHAR(60) CHARACTER SET utf8
                            )"""
            self._c.execute(sql_cmd)

            sql_cmd = """CREATE TABLE rschprojects(
                            researcherID INT(11) NOT NULL,
                            projectRcn INT(11) NOT NULL
                            )"""
            self._c.execute(sql_cmd)

            #Fill table with researchers data
            #We process all excel files in the indicated directory
            #and concatenate all available information in one dataframe
            flds = ['projectId', 'projectAcronym', 'fundingScheme', 'title',
                     'firstName', 'lastName', 'organisationId']
            df_all = pd.DataFrame(columns=flds)

            for root, dirs, files in os.walk(rsr_dir):
                for file in files:
                    if file.endswith('.xls') or file.endswith('.xlsx'):
                        if not file.startswith('~'):
                            print('Importing researchers file:', os.path.join(root,file))
                            df = pd.read_excel(os.path.join(root,file))
                            df_all = df_all.append(df, ignore_index=True)

            #Fill table with data from sic_file
            df_all = df_all.replace(np.nan, '', regex=True)

            #Obtain a list of unique researchers, and assign them a unique identifier
            df_researchers = df_all[['title', 'firstName', 'lastName']].drop_duplicates().reset_index()
            df_researchers['researcherID'] = df_researchers.index

            #Save them to database
            fieldnames = ['researcherID', 'title', 'firstName', 'lastName']
            df_researchers = df_researchers[fieldnames]
            self.insertInTable('researchers', fieldnames, df_researchers.values.tolist())

            #Next, we need to obtain the pairs researcher - project_rcn
            #However, a mapping is necessary because df_all contain the references for projects
            #and not the rcns

            #Read from dataset pairs of project_rcn vs project_reference to map references
            #in the researcher files with project rcns
            df_prj = self.readDBtable('projects', selectOptions='rcn, reference')
            #And Map rcns in the big dataframe
            df_all['projectId'] = df_all['projectId'].map(str)
            df_all = df_all.join(df_prj.set_index('reference'), on='projectId')

            # We also need to add a column with the referenceID for the researchers
            # We compute for that a new field for the join operation
            df_researchers['uniquename'] = df_researchers['title'] + \
                    df_researchers['firstName']+df_researchers['lastName']
            df_all['uniquename'] = df_all['title'] + \
                    df_all['firstName']+df_all['lastName']

            df_researchers = df_researchers[['uniquename', 'researcherID']]
            df_all = df_all.join(df_researchers.set_index('uniquename'), on='uniquename')

            #Save to DB pairs with a valid rcn
            df_all = df_all[['researcherID', 'rcn']]
            df_all = df_all.dropna()

            fieldnames = ['researcherID', 'projectRcn']
            self.insertInTable('rschprojects', fieldnames, df_all.values.tolist())

        #Commit changes to database
        self._conn.commit()
        
    def SICconsolidate(self):
        df = self.readDBtable('projects', limit=None, selectOptions='rcn, subjects')
        df['subjects'] = df['subjects'].apply(replace_SIC)

        values = [tuple(el) for el in df.values.tolist() if el[1]!='']
        self.setField('projects', 'rcn', 'subjects', values)

        return



