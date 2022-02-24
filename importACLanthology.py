"""
Created on Dec 20 2016
@author: Jerónimo Arenas García

Create ACL anthology MySQL Database. Run scripts for:

    * Creating database
    * Adding content to database

    We have cleaned some of the fields, but on the way we have also learned a lot
    Now, I would do things differently, I write stuff down here in case in the
    future I want to rewrite this routine

    1/ Extracting ACL papers from SScholar_mongo to ACL_mongo is a good idea
       Filtering is done in importSScholar.py by URL. We should check the list
       of ACL-related domains
    2/ This is not done yet, but should be: There are many papers that could simply
       be removed from the database. They appear mostly in the ACL anthology repository
       but also in the SScholar database. Some examples are:
           - Brief Notes: ...
           - Author Index: ...
           - Proceedings of: ...
           - 
           - Quizá también "Book Review:" aunque esto puede matizarse supongo
        Creo que la eliminación de estos artículos debería ser lo primero que se hace
        en esta rutina
    3/ A veces no es fácil encontrar esos "papers basura", por lo que otro criterio sería 
       limpiar por número de páginas en el pdf
    4/ Como resultado de esta rutina se están matcheando *** 38871 papers, y quedan sin matchear 9216. ***
       También tenemos 2071 papers en Semantic Scholar que no se les encuentra pareja
    5/ Convendría revisar la parte de búsqueda por URL en la MongoDB

    6/ Más opciones para ampliar la cobertura:
           - Buscar los títulos no encontrados contra Semantic Scholar, Google Scholar, ... 
           - Algo de limpieza manual
           - Llevar registro de dónde se pierden qué registros, porque en general supongo que
             se perderá más de años antiguos
           - Normalizar el criterio para quedarnos con uno u otro paper de SScholar, porque hay duplicados
             por ejemplo, para eliminar duplicados podríamos usar también el nombre de los autores
           - Incluir en la importación de google scholar un campo 'lowertitle'

    7/ Se debería volcar la información de autores, en caso que se quiera utilizar. Esa información 
       está disponible tanto para ACL_anthology como para Semantic Scholar, pero no la he volcado de momento
       Sería bueno, entre otras cosas, para crear una tabla de nodos excluyendo las autocitas

    8/ En outgraph=True, hay que borrar la tabla de citas antes de volver a insertarlas

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
import numpy as np
import distance

from dbmanager.ACLmanager import ACLmanager
from lemmatizer.ENlemmatizer import ENLemmatizer

def main(matchDB=False, resetDB=False, outgraph=False, lemmatize=False):
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
    dbNAME = cf.get('ACL', 'dbNAME')
    MONGOdbSERVER = cf.get('MONGODB', 'MONGOdbSERVER')
    MONGOdbPORT = cf.get('MONGODB', 'MONGOdbPORT')
    MONGOdbNAME = cf.get('SemanticScholar', 'MONGOdbNAME')
    MONGOdbCollection = cf.get('SemanticScholar', 'MONGOdbCollection')

    #########################
    # Datafiles
    #
    data_files = cf.get('ACL', 'data_files')
    pdf_files = cf.get('ACL', 'pdf_files')
    generic_stw = cf.get('ACL', 'generic_stw')
    specific_stw = cf.get('ACL', 'specific_stw')

    ####################################################
    #1. Connect to mongoDB

    mongo_connector = pymongo.MongoClient('mongodb://' + MONGOdbSERVER + ':' + MONGOdbPORT + '/')
    Scholar_mongodb = mongo_connector[MONGOdbNAME]
    Scholar_col = Scholar_mongodb[MONGOdbCollection]
    ACL_col = Scholar_mongodb['ACL_papers']

    if matchDB:

        ####################################################
        #2. We match papers in the ACL directories with papers in mongoDB
        allACLpapers = [el for el in os.listdir(data_files) 
                            if os.path.isdir(os.path.join(data_files, el))]
        allyears = sorted(list(set([el[1:3] for el in allACLpapers])))

        match_dictio = {}
        not_found = []

        allmongoACLpapers = [el for el in ACL_col.find({}, {'id':1, 'lowertitle':1, 'paperAbstract':1, 'pdfUrls':1})]
        allmongoACLpapers_id = [el['id'] for el in allmongoACLpapers]
        allmongoACLpapers_title = [el['lowertitle'] for el in allmongoACLpapers]
        allmongoACLpapers_abstract = [el['paperAbstract'] for el in allmongoACLpapers]
        allmongoACLpapers_urls = [' '.join(el['pdfUrls']) for el in allmongoACLpapers]

        def remove_from_all(SSid):
            idx_SSid = allmongoACLpapers_id.index(SSid)
            allmongoACLpapers_id.pop(idx_SSid)
            allmongoACLpapers_title.pop(idx_SSid)
            allmongoACLpapers_abstract.pop(idx_SSid)
            allmongoACLpapers_urls.pop(idx_SSid)

        url_list = []
        url_list2 = []

        for thisyear in allyears:

            #Variable initialization
            thisyearpapers = [el for el in allACLpapers if el[1:3]==thisyear]

            lchunk = 1+int(len(thisyearpapers)/100)
            bar = Bar('Searching projects for year ' + thisyear + ' in Semantic Scholar', max=100)

            for idx,el in enumerate(thisyearpapers):
                found = 0
                if not idx%lchunk:
                    bar.next()
                try:
                    with open(os.path.join(data_files,el,el.lower()+'.bib'), 'r') as fin:
                        lines = fin.readlines()
                        ####################
                        #Search match by doi
                        doi_line = [el2 for el2 in lines if ' doi =' in el2]
                        if len(doi_line):
                            doi = doi_line[0].split('"')[-2]
                            query_res = [el2 for el2 in Scholar_col.find({'doi': doi})]
                            #Remove all from list of papers in mongoDB
                            for item in query_res:
                                remove_from_all(item['id'])

                            if len(query_res)==1:
                                match_dictio[el] = query_res[0]
                                found = 1
                            if len(query_res)>1:
                                #We keep the one with longer abstract
                                keep = np.argmax([len(item['paperAbstract']) for item in query_res])
                                match_dictio[el] = query_res[keep]
                                found = 1

                        ####################################
                        #If not found, search match by title in ACL MongoDB collection
                        if not found:
                            title_line = [el2 for el2 in lines if ' title =' in el2]
                            if len(title_line):
                                title = title_line[0].split('"')[-2].lower()
                                query_res = [el2 for el2 in ACL_col.find({'lowertitle': title})]
                                #Remove all from list of papers in mongoDB
                                for item in query_res:
                                    remove_from_all(item['id'])

                                if (len(query_res)==2) or (len(query_res)==3):
                                    #If two or three results, keep only the ones with abstract
                                    query_res = [item for item in query_res if len(item['paperAbstract'])]
                                    found = 1
                                if (len(query_res)==2) or (len(query_res)==3):
                                    #If still two or three, keep only those with a valid URL
                                    query_res = [item for item in query_res 
                                        if sum([1 for item2 in item['pdfUrls'] if el in item2])]
                                    found = 1
                                if len(query_res)==1:
                                    match_dictio[el] = query_res[0]
                                    found = 1
                                if (len(query_res)==2) or (len(query_res)==3):
                                    #We keep the one with more outCitations
                                    idx2 = np.argmax([len(item['outCitations']) for item in query_res])
                                    match_dictio[el] = query_res[idx2]
                                    found = 1
                                if len(query_res)>3:
                                    #These are compilations, bios, indexes, etc, we skip them
                                    found = 1
                                    
                        ####################################
                        #If not found, search match by URL in ACL MongoDB collection
                        #Esta sección habría que revisarla
                        if not found:
                            url_line = [el2 for el2 in lines if ' url =' in el2]
                            if len(url_line):
                                url = url_line[0].split('"')[-2]
                                pos_list = [idx2 for idx2,item in enumerate(allmongoACLpapers_urls) if url in item]
                                if len(pos_list):
                                    #Hemos comprobado que no hay matches multiples, con lo que simplemente
                                    #verificamos si ha encontrado un match, y nos quedamos con la primera posicion
                                    searchid = allmongoACLpapers_id[pos_list[0]]
                                    query_res = [el2 for el2 in ACL_col.find({'id': searchid})]
                                    if ((distance.nlevenshtein(query_res[0]['lowertitle'], title)<0.25)
                                        or
                                        (len(query_res[0]['lowertitle'])>10 and query_res[0]['lowertitle'] in title)):
                                        match_dictio[el] = query_res[0]
                                        remove_from_all(searchid)
                                        found = 1

                        ####################################
                        #If not found, search match by dirname in url in ACL MongoDB collection
                        #Esta sección habría que revisarla
                        if not found:
                            pos_list = [idx2 for idx2,item in enumerate(allmongoACLpapers_urls) if el in item]
                            if len(pos_list)==1:
                                searchid = allmongoACLpapers_id[pos_list[0]]
                                query_res = [el2 for el2 in ACL_col.find({'id': searchid})]
                                if ((distance.nlevenshtein(query_res[0]['lowertitle'], title)<0.25)
                                        or
                                    (len(query_res[0]['lowertitle'])>10 and query_res[0]['lowertitle'] in title)):
                                    match_dictio[el] = query_res[0]
                                    remove_from_all(searchid)
                                    found = 1

                            elif len(pos_list)>1:
                                if title.startswith('proceedings of'):
                                    #we do not keep this record, but mark it as found
                                    found=1
                                else:
                                    dss = [distance.nlevenshtein(title, allmongoACLpapers_title[kk]) for kk in pos_list]
                                    if min(dss)<0.25:
                                        pos_min = np.argmin(dss)
                                        searchid = allmongoACLpapers_id[pos_list[pos_min]]
                                        query_res = [el2 for el2 in ACL_col.find({'id': searchid})]
                                        match_dictio[el] = query_res[0]
                                        remove_from_all(searchid)
                                        found = 1

                        ####################################
                        #If not found, search match by title in Big SScholar collection

                        if not found:
                            title_line = [el2 for el2 in lines if ' title =' in el2]
                            if len(title_line):
                                title = title_line[0].split('"')[-2]
                                query_res = [el2 for el2 in Scholar_col.find({'title': title})]

                                #No hay campo lower en Scholar_col, así que probamos alternativas:
                                if len(query_res)==0:
                                    query_res = [el2 for el2 in Scholar_col.find({'title': title.title()})]
                                if len(query_res)==0:
                                    query_res = [el2 for el2 in Scholar_col.find({'title': title.upper()})]
                                if len(query_res)==0:
                                    query_res = [el2 for el2 in Scholar_col.find({'title': title.capitalize()})]

                            #Si hay 1 entrada, la damos por buena; si hay más no seleccionamos. Esto se
                            #podría mejorar, obviamente
                            if len(query_res)==1:
                                match_dictio[el] = query_res[0]
                                remove_from_all(query_res[0]['id'])
                                found = 1

                        if not found:
                            not_found.append(el)

                except:
                    not_found.append(el)
            bar.finish()

        print('Total matched:', len(match_dictio))
        print('Not found:', len(not_found))
        print('Not identified in Mongo list:', len(allmongoACLpapers_id))

        with open('match_ACL_SScholar.txt','w') as fout:
            for key in match_dictio.keys():
                fout.write(key+':'+match_dictio[key]['id']+'\n')

    if resetDB:
        print('Generating MySQL database')
    
        DB = ACLmanager (db_name=dbNAME, db_connector='mysql', path2db=None,
                            db_server=dbSERVER, db_user=dbUSER, db_password=dbPASS)

        DB.createDBtables()

        bar = Bar('Inserting project data', max=400)

        #Insert data
        with open('match_ACL_SScholar.txt','r') as fin:
            for idx,line in enumerate(fin.readlines()):

                if not idx%100:
                    bar.next()
                
                ACLid = line.split(':')[0]
                SSid = line.split(':')[-1].strip()

                columns = ['ACLid', 'SSid']
                arguments = [ACLid, SSid]

                #Read .bib file
                with open(os.path.join(data_files,ACLid,ACLid.lower()+'.bib'), 'r') as fACL:
                    lines = fACL.readlines()

                #Read record from Mongo DB
                SSinfo = ACL_col.find_one({'id': SSid})
                if SSinfo is None:
                    SSinfo = Scholar_col.find_one({'id': SSid}, {})

                #Leemos year
                if 'year' in SSinfo.keys():
                    year = SSinfo['year']
                    columns.append('year')
                    arguments.append(year)
                else:
                    year_line = [el for el in lines if ' year =' in el]
                    if len(year_line):
                        year = year_line[0].split('"')[-2]
                        columns.append('year')
                        arguments.append(year)

                #Leemos doi
                if 'doi' in SSinfo.keys():
                    doi = SSinfo['doi']
                    columns.append('doi')
                    arguments.append(doi)
                else:
                    doi_line = [el for el in lines if ' doi =' in el]
                    if len(doi_line):
                        doi = doi_line[0].split('"')[-2]
                        columns.append('doi')
                        arguments.append(doi)

                #Leemos booktitle
                booktitle_line = [el for el in lines if ' booktitle =' in el]
                if len(booktitle_line):
                    booktitle = booktitle_line[0].split('"')[-2]
                    columns.append('booktitle')
                    arguments.append(booktitle)

                #Leemos publisher
                publisher_line = [el for el in lines if ' publisher =' in el]
                if len(publisher_line):
                    publisher = publisher_line[0].split('"')[-2]
                    columns.append('publisher')
                    arguments.append(publisher)

                #Leemos título
                if 'title' in SSinfo.keys():
                    title = SSinfo['title']
                    columns.append('title')
                    arguments.append(title)
                else:
                    title_line = [el for el in lines if ' title =' in el]
                    if len(title_line):
                        title = title_line[0].split('"')[-2]
                        columns.append('title')
                        arguments.append(title)

                #Leemos abstract
                if 'paperAbstract' in SSinfo.keys():
                    abstract = SSinfo['paperAbstract']
                    columns.append('abstract')
                    arguments.append(abstract)

                #Leemos entities
                if 'entities' in SSinfo.keys():
                    entities = ', '.join(SSinfo['entities'])
                    columns.append('entities')
                    arguments.append(entities)

                #Extraemos texto del pdf
                pdf_to_parse = os.path.join(pdf_files, ACLid+'.pdf')
                if os.path.isfile(pdf_to_parse):
                    try:
                        raw = tikaparser.from_file(pdf_to_parse)
                        if raw['status']==200:
                            columns.append('paper')
                            arguments.append(raw['content'])
                    except:
                        pass
                else:
                    print('Falta el pdf para el paper con ACLid', ACLid)

                #Insert in DATABASE
                try:
                    DB.insertInTable('ACLpapers', columns, [tuple(arguments)])
                except:
                    print('Error al insertar en la BD el paper con ACLid', ACLid)
        bar.finish()
        del DB

    if outgraph:
        print('calculating output citation graph')
    
        DB = ACLmanager (db_name=dbNAME, db_connector='mysql', path2db=None,
                            db_server=dbSERVER, db_user=dbUSER, db_password=dbPASS)

        bar = Bar('Reading all citations from Scholar database', max=400)

        ACLids = []
        SSids = []
        outCit = []
        authorids = [] 
        noselfoutCit = []

        #Insert data
        with open('match_ACL_SScholar.txt','r') as fin:
            for idx,line in enumerate(fin.readlines()):

                if not idx%100:
                    bar.next()
                
                ACLid = line.split(':')[0]
                SSid = line.split(':')[-1].strip()

                ACLids.append(ACLid)
                SSids.append(SSid)

                #Read record from Mongo DB
                SSinfo = ACL_col.find_one({'id': SSid})
                if SSinfo is None:
                    SSinfo = Scholar_col.find_one({'id': SSid})

                #Leemos autores para eliminar autocitas
                if 'authors' in SSinfo.keys():
                    SSauth = [item for item in SSinfo['authors'] if len(item['ids'])]
                    try:
                        authorids.append([item['ids'][0] for item in SSauth])
                    except:
                        pass
                else:
                    authorids.append([])

                #Leemos outputCitations
                if 'outCitations' in SSinfo.keys():
                    outCit.append(SSinfo['outCitations'])
                    #Ahora eliminamos las autocitas
                    #ids de los autores del paper
                    self_authors = set(authorids[-1])
                    noselfcitations = []
                    for citedpaper in SSinfo['outCitations']:
                        #Read record from Mongo DB
                        SSinfo2 = ACL_col.find_one({'id': citedpaper}, {'authors':1})
                        if SSinfo2 is None:
                            SSinfo2 = Scholar_col.find_one({'id': citedpaper}, {'authors':1})
                        if 'authors' in SSinfo2.keys():
                            ref_authors = [item['ids'][0] for item in SSinfo2['authors'] if len(item['ids'])]
                        if len([el for el in ref_authors if el in self_authors])==0:
                            noselfcitations.append(citedpaper)
                    noselfoutCit.append(noselfcitations)
                else:
                    outCit.append([])
                    noselfoutCit.append([])

        bar.finish()

        bar = Bar('Calculating links and storing in database', max=400)
        for idx,ACLid in enumerate(ACLids):

            if not idx%100:
                bar.next()

            #Citations of current paper
            out_set = set(outCit[idx])
            #Citations of current paper excluding self_citations
            out_set_noself = set(noselfoutCit[idx])

            #Stores links for this paper
            links_idx = []

            for idx2 in range(idx+1,len(ACLids)):

                ACLid2 = ACLids[idx2]

                cit_paper2 = outCit[idx2]
                comon_cit = [cit for cit in cit_paper2 if cit in out_set]

                cit_paper2_noself = noselfoutCit[idx2]
                comon_cit_noself = [cit for cit in cit_paper2_noself if cit in out_set_noself]

                if len(comon_cit_noself):
                    similitud_noself = float(len(comon_cit_noself))/np.sqrt(len(out_set_noself)*len(cit_paper2_noself))
                else:
                    similitud_noself = 0

                if len(comon_cit):
                    similitud = float(len(comon_cit))/np.sqrt(len(out_set)*len(cit_paper2))
                    links_idx.append((ACLid, ACLid2, len(comon_cit), len(comon_cit_noself),
                                                                 similitud, similitud_noself))

            #Insert in DATABASE
            if len(links_idx):
                DB.insertInTable('outCitations_graph', ['ACLid1','ACLid2','comon_cit','comon_cit_noself',
                                                                        'weight','weight_noself'], links_idx)
        
        bar.finish()
        del DB

    # ####################################################
    # 3. Lematización de textos en inglés
    if lemmatize:
        print('Lemmatizing database')
    
        DB = ACLmanager (db_name=dbNAME, db_connector='mysql', path2db=None,
                            db_server=dbSERVER, db_user=dbUSER, db_password=dbPASS)

        enLM = ENLemmatizer(generic_stw, specific_stw)

        df = DB.readDBtable('ACLpapers',limit=None,selectOptions='ACLid, paper',
                                        filterOptions='LEMAS_paper is NULL')
        allpapers = df.values.tolist()

        #Chunks for monitoring progress and writing in the database
        lchunk = 10
        npapers = len(allpapers)
        bar = Bar('Lemmatizing Papers', max=1+npapers/lchunk)

        titleLEMAS = []
        entityLEMAS = []
        abstractLEMAS = []
        paperLEMAS = [] 
        for index,x in enumerate(allpapers):
            if not (index+1)%lchunk:
                #DB.setField('ACLpapers', 'ACLid', 'LEMAS2_title', titleLEMAS)
                #DB.setField('ACLpapers', 'ACLid', 'LEMAS2_entities', entityLEMAS)
                #DB.setField('ACLpapers', 'ACLid', 'LEMAS2_abstract', abstractLEMAS)
                DB.setField('ACLpapers', 'ACLid', 'LEMAS_paper', paperLEMAS)

                titleLEMAS = []
                entityLEMAS = []
                abstractLEMAS = []
                paperLEMAS = [] 
                bar.next()
            #titleLEMAS.append((x[0], enLM.processENstr(x[1])))
            #entityLEMAS.append((x[0], enLM.processENstr(x[2])))
            #abstractLEMAS.append((x[0], enLM.processENstr(x[3])))
            paperLEMAS.append((x[0], enLM.processENstr(x[1])))
        bar.finish()
        #DB.setField('ACLpapers', 'ACLid', 'LEMAS2_title', titleLEMAS)
        #DB.setField('ACLpapers', 'ACLid', 'LEMAS2_entities', entityLEMAS)
        #DB.setField('ACLpapers', 'ACLid', 'LEMAS2_abstract', abstractLEMAS)
        DB.setField('ACLpapers', 'ACLid', 'LEMAS_paper', paperLEMAS)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='importACLanthology')    
    parser.add_argument('--matchDB', action='store_true', help='If activated, match ACL_anthology and SScholar')
    parser.add_argument('--resetDB', action='store_true', help='If activated, database will be regenerated')
    parser.add_argument('--outgraph', action='store_true', help='If activated, the output citations graph will be calculated')
    parser.add_argument('--lemmatize', action='store_true', help='If activated, the output citations graph will be calculated')
    args = parser.parse_args()

    main(matchDB=args.matchDB, resetDB=args.resetDB, outgraph=args.outgraph, lemmatize=args.lemmatize)
