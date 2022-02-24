"""
Created on Feb25 2019
@author: Jerónimo Arenas García

Import Semantic Scholar Database to Mongo DB

    * Creating database from downloaded gzip files

"""

import argparse
import configparser
from progress.bar import Bar
import pymongo
import os
import gzip
import json
import ipdb
from tika import parser as tikaparser
from bs4 import BeautifulSoup

from lemmatizer.ENlemmatizer import ENLemmatizer

def main(import_mongoDB=False, ACL_mongoDB=False):
    """
    """

    cf = configparser.ConfigParser()
    cf.read('config.cf')

    #########################
    # Configuration variables
    #
    dbUSER = cf.get('DB', 'dbUSER')
    dbPASS = cf.get('DB', 'dbPASS')
    dbSERVER = cf.get('DB', 'dbSERVER')
    MONGOdbSERVER = cf.get('MONGODB', 'MONGOdbSERVER')
    MONGOdbPORT = cf.get('MONGODB', 'MONGOdbPORT')
    MONGOdbNAME = cf.get('SemanticScholar', 'MONGOdbNAME')
    MONGOdbCollection = cf.get('SemanticScholar', 'MONGOdbCollection')

    mongo_connector = pymongo.MongoClient('mongodb://' + MONGOdbSERVER + ':' + MONGOdbPORT + '/')
    Scholar_mongodb = mongo_connector[MONGOdbNAME]
    Scholar_col = Scholar_mongodb[MONGOdbCollection]

    #########################
    # Datafiles
    #
    data_files = cf.get('SemanticScholar', 'data_files')

    ####################################################
    #1. Create Mongo DB from data files

    if import_mongoDB:

        #If collection exists we drop any content
        if MONGOdbCollection in Scholar_mongodb.list_collection_names():
            Scholar_col.drop()

        #Now, we start popullating the collection with data
        gz_files = [data_files+el for el in os.listdir(data_files) if el.startswith('s2-corpus')]
        bar = Bar('Inserting papers in Mongo Database', max=len(gz_files))
        for gzf in gz_files:
            bar.next()
            with gzip.open(gzf, 'rt') as f:
                papers_infile = f.read().replace('}\n{','},{')
                papers_infile = json.loads('['+papers_infile+']')
                Scholar_col.insert_many(papers_infile)
        bar.finish()

        print('Creating Title Index ...')
        Scholar_col.create_index([("title", pymongo.DESCENDING)])
        print('Creating Year Index ...')
        Scholar_col.create_index([('year', pymongo.DESCENDING)])
        print('Creating DOI Index ...')
        Scholar_col.create_index([('doi', pymongo.DESCENDING)])
        print('Creating journal Index ...')
        Scholar_col.create_index([('journalName', pymongo.DESCENDING)])
        print('Creating id Index ...')
        Scholar_col.create_index([('id', pymongo.DESCENDING)])
        print('Creating venue Index ...')
        Scholar_col.create_index([('venue', pymongo.DESCENDING)])

    if ACL_mongoDB:
        ACL_col = Scholar_mongodb['ACL_papers']

        #If collection exists we drop any content
        if 'ACL_papers' in Scholar_mongodb.list_collection_names():
            ACL_col.drop()

        #Next we insert all ACL recognizable papers in database
        bar = Bar('Inserting ACL papers in Mongo Database', max=4300)
        for idx,paper in enumerate(Scholar_col.find()):
            paper['lowertitle'] = paper['title'].lower()
            if not idx%10000:
                bar.next()
            counts1 = [1 for item in paper['pdfUrls'] if 'http://www.aclweb.org/anthology' in item]
            counts2 = [1 for item in paper['pdfUrls'] if 'http://www.lrec-conf.org' in item]
            if len(counts1+counts2):
                ACL_col.insert_one(paper)
        bar.finish()

        print('Creating Title Index ...')
        ACL_col.create_index([("title", pymongo.DESCENDING)])
        print('Creating Year Index ...')
        ACL_col.create_index([('year', pymongo.DESCENDING)])
        print('Creating DOI Index ...')
        ACL_col.create_index([('doi', pymongo.DESCENDING)])
        print('Creating journal Index ...')
        ACL_col.create_index([('journalName', pymongo.DESCENDING)])
        print('Creating id Index ...')
        ACL_col.create_index([('id', pymongo.DESCENDING)])
        print('Creating venue Index ...')
        ACL_col.create_index([('venue', pymongo.DESCENDING)])

    # # ####################################################
    # # 3. Lematización de textos en inglés
    # if lemmatize:
    #     enLM = ENLemmatizer(generic_stw, specific_stw)
    #     df = DB.readDBtable('projects',limit=None,selectOptions='rcn, title, objective, report')
    #     allprojects = df.values.tolist()

    #     #Chunks for monitoring progress and writing in the database
    #     lchunk = 10
    #     nproyectos = len(allprojects)
    #     bar = Bar('Lemmatizing English Descriptions', max=1+nproyectos/lchunk)

    #     allLEMAS = []
    #     for index,x in enumerate(allprojects):
    #         if not (index+1)%lchunk:
    #             DB.setField('projects', 'rcn', 'LEMAS_UC3M_ENG', allLEMAS)
    #             allLEMAS = []
    #             bar.next()
    #         allLEMAS.append((x[0], enLM.processENstr(x[1]) + ' ***** ' + enLM.processENstr(x[2]) + \
    #                          ' ***** ' + enLM.processENstr(x[3]) ))
    #     bar.finish()
    #     DB.setField('proyectos', 'rcn', 'LEMAS_UC3M_ENG', allLEMAS)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='dbCORDIS')    
    parser.add_argument('--import_mongoDB', action='store_true', help='If activated, mongoDB database will be created')
    parser.add_argument('--ACL_mongoDB', action='store_true', help='If activated, create ACL mongoDB database')
    args = parser.parse_args()

    main(import_mongoDB=args.import_mongoDB, ACL_mongoDB=args.ACL_mongoDB)
