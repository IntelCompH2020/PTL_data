
# -*- coding: utf-8 -*-


'''

Gestión de proyectos coordinados:

    Para saber si un proyecto se encuentra coordinado con otro (o con varios) debemos tener varias cosas en cuenta. A saber:
        - Existe un campo tipo que nos dice si es coordinado, multicéntrico o individual. Ahora bien, este campo, en muy pocos casos, no parece bien etiquetado.
        - En ciertas convocatorias se sabe que dos proyectos se encuentran coordinados porque tienen títulos muy muy parecidos (a veces tienen menos palabras o tienen un 1,2)
        - En otras convocatorias es la referencia del proyecto quien nos da la pista. Son referencias del tipo XXXX-YYYY-ZZZZ-AAAA, debemos comprobar si las n primeras tuplas 
            son iguales (n puede ser 3 o 4 en función de la convocatoria)


Con todos estos datos se ha creado una clase que analiza en función de cada convocatoria si se unen por la referencia o por el parecido (similitud) de los títulos.

Vamos con ello:

'''

import sys 
import csv
import argparse
import os
import json
import datetime
import numpy as np
import math
import pandas as pd

# My fucking magic fucntion
from difflib import SequenceMatcher
from progress.bar import Bar


class Tambourine ( object ):


    __myDfProjects__         =     None
    __coodProjectsDf__         =     None
    __similarProjectsDf__     =     None
    __listConvocatorias__     =     None
    __listAnios__            =     None
    __listaSimilares__         =     None
    __contDf__                 =     None
    __contDf2__             =     None
    __umbralSim__            =     None

    __indicadores__            = None
    __verbose__ = None

    def __init__ (self, df_projects, verbose=False):    

        self.__myDfProjects__        = df_projects
        self.__listConvocatorias__    = self.__myDfProjects__['TITULO CONVOCATORIA'].unique()
        self.__listAnios__             = self.__myDfProjects__['CONVOCATORIA'].unique()

        # To save similar projects. 
        columns = ['Titulo1', 'Titulo2', 'REF1', 'REF2', 'Estado1', 'Estado2', 'Tipo 1', 'Tipo 2', 'Titulo convocatoria', 'Anio', 'Similitud', 'MatchingRef']
        self.__similarProjectsDf__ = pd.DataFrame(columns=columns)
        

        columns = ['Titulo', 'REF', 'Estado',  'Tipo', 'Titulo convocatoria', 'Anio', 'Num coordinados', 'Lista coordinados']
        self.__coodProjectsDf__ = pd.DataFrame(columns=columns)
        
        # Incremental parameters
        self.__listaSimilares__     = []
        self.__contDf__             = 0
        self.__contDf2__             = 0

        # Other parameters
        self.__umbralSim__            = 0.8
        self.__verbose__            = verbose

    ''''
        Devuelve las similitudes entgre dos cadenas pasadas como parametro:
    '''
    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def remove_tildes(self, s):
        """Remove tildes from the input string
        :Param s: Input string (en utf-8)
        :Return: String without tildes (en utf-8)
        """
        list1 = ['á','é','í','ó','ú','Á','É','Í','Ó','Ú','à','è','ì','ò',
                     'ù','ü','â','ê','î','ô','û','ç','Ç']
        list2 = ['a','e','i','o','u','A','E','I','O','U','a','e','i','o',
                     'u','u','a','e','i','o','u','c','C']
        try:
            for i,letra in enumerate(list1):
                s = s.replace(letra,list2[i])
        except:
            s = ''

        return s
  
    '''
        Devuelve la lista de proyectos que tengan la misma referencia.
        Las referencias tienen un formato del tipo: XXXX-YYYY-ZZZZ-AAAA y podemos comparar las n primers bloques.
    '''      
    def matchReference(self, myDf, id1,id2,nFields,convocatoria, anio):
        if (myDf['TIPO DE PROYECTO'][id1] == 'Coordinado' and myDf['TIPO DE PROYECTO'][id2] == 'Coordinado') or (myDf['TIPO DE PROYECTO'][id1] == 'Multicéntrico' and myDf['TIPO DE PROYECTO'][id2] == 'Multicéntrico'):
            REF1 = ''.join(myDf['REFERENCIA'][id1].split('-')[:nFields])
            REF2 = ''.join(myDf['REFERENCIA'][id2].split('-')[:nFields])
            if REF1 == REF2:
                mySim = self.similar(self.remove_tildes(myDf['TITULO'][id1].lower()), self.remove_tildes(myDf['TITULO'][id2].lower()))
                self.__contDf__ += 1
                self. __similarProjectsDf__.loc[self.__contDf__] = [myDf['TITULO'][id1], myDf['TITULO'][id2], 
                                                   myDf['REFERENCIA'][id1], myDf['REFERENCIA'][id2],
                                                   myDf['STATUS'][id1], myDf['STATUS'][id2],
                                                   myDf['TIPO DE PROYECTO'][id1], myDf['TIPO DE PROYECTO'][id2],
                                                   convocatoria, anio, mySim, 1]
                self.__listaSimilares__.append(myDf['REFERENCIA'][id2]) 

    
    '''
         Devuelve la lista de proyectos con un titulo similar para proyectos que no sean indivduales.
    '''
    def matchTitle(self, myDf, id1,id2,convocatoria, anio):
        if (myDf['TIPO DE PROYECTO'][id1] == 'Coordinado' and myDf['TIPO DE PROYECTO'][id2] == 'Coordinado') or (myDf['TIPO DE PROYECTO'][id1] == 'Multicéntrico' and myDf['TIPO DE PROYECTO'][id2] == 'Multicéntrico'):
            mySim = self.similar(self.remove_tildes(myDf['TITULO'][id1].lower()), self.remove_tildes(myDf['TITULO'][id2].lower()))
            if (mySim>self.__umbralSim__):
                self.__contDf__ += 1
                self. __similarProjectsDf__.loc[self.__contDf__] = [myDf['TITULO'][id1], myDf['TITULO'][id2], 
                                                   myDf['REFERENCIA'][id1], myDf['REFERENCIA'][id2],
                                                   myDf['STATUS'][id1], myDf['STATUS'][id2],
                                                   myDf['TIPO DE PROYECTO'][id1], myDf['TIPO DE PROYECTO'][id2],
                                                   convocatoria, anio, mySim, 0]
                self.__listaSimilares__.append(myDf['REFERENCIA'][id2])

    '''
         Devuelve la lista de proyectos con un titulo similar.
    '''
    def matchTitleGeneral(self, myDf, id1,id2,convocatoria, anio):
        mySim = self.similar(self.remove_tildes(myDf['TITULO'][id1].lower()), self.remove_tildes(myDf['TITULO'][id2].lower()))
        if (mySim>self.__umbralSim__):
            self.__contDf__ += 1
            self. __similarProjectsDf__.loc[self.__contDf__] = [myDf['TITULO'][id1], myDf['TITULO'][id2], 
                                               myDf['REFERENCIA'][id1], myDf['REFERENCIA'][id2],
                                               myDf['STATUS'][id1], myDf['STATUS'][id2],
                                               myDf['TIPO DE PROYECTO'][id1], myDf['TIPO DE PROYECTO'][id2],
                                               convocatoria, anio, mySim, 0]
            self.__listaSimilares__.append(myDf['REFERENCIA'][id2])

        return mySim

    
    '''
        Rellena el dataframe con los proyectos coordinados que se han encontrado. Se guarda más información de la que se guardará 
        en la base de datos finalmente. 
    '''
    def calculaCoordinados (self):

        convocatoriasReferenciaType2 = ['SEIDI_RETOS_INVESTIGACION', 'SEIDI_PIFNO', 'SEIDI_PROYECTOS_EXCELENCIA','CDTI_EUROSTARS']
        convocatoriasReferenciaType3 = ['INIA']
        convocatoriasTitulo = ['ISCIII_PI', 'ISCIII_DTS', 'ISCIII_ICI']
        convocatoriasIndividual = ['SEIDI_EXPLORA', 'SEIDI_JOVENES', 'SEIDI_EUROPA_EXCELENCIA', 'CDTI_INTERNACIONALIZA', 'CDT_NEOTEC', 'CDTI_LIG_LIDERAZGO', 'ISCIII_PMP', 'SEIDI_REDES_EXCELENCIA', 'SEIDI_EUROPA_INVESTIGACION', 'CDTI_NEOTEC', 'CDTI_PROMOCION_TECNOLOGICA']
        for convocatoria in self.__listConvocatorias__:
            if not(convocatoria in convocatoriasIndividual):
                numProy = 0            

                for anio in self.__listAnios__:
                    
                    myDf = self.__myDfProjects__.loc[self.__myDfProjects__['TITULO CONVOCATORIA'] == convocatoria].loc[self.__myDfProjects__['CONVOCATORIA'] == anio]

                    if convocatoria in convocatoriasReferenciaType2+convocatoriasReferenciaType3:
                        myDf = myDf.loc[myDf['TIPO DE PROYECTO']!='Individual']

                    numProy += myDf.shape[0]
                    ids = myDf.index.values
                    barId = Bar(convocatoria + '/' + str(anio) + ':', max=len (ids))

                    for i, id1 in enumerate(ids):
                        self.__listaSimilares__=[]
                        barId.next()

                        for id2 in ids: 
                            if id1 != id2:
                                if convocatoria in convocatoriasReferenciaType2:
                                    self.matchReference(myDf, id1,id2,2,convocatoria, anio) 

                                elif convocatoria in convocatoriasReferenciaType3:
                                    self.matchReference(myDf, id1,id2,3,convocatoria, anio) 
                                                                                        
                                elif convocatoria in convocatoriasTitulo:
                                    self.matchTitle(myDf, id1,id2,convocatoria, anio)
                                else:
                                    mySim = self.matchTitleGeneral(myDf, id1,id2,convocatoria, anio)
                                    if (mySim <= self.__umbralSim__) and (convocatoria == 'SEIDI_APCI'): 
                                        if anio == 2013:
                                            self.matchReference(myDf, id1,id2,3,convocatoria, anio)
                                        else:
                                            self.matchReference(myDf, id1,id2,4,convocatoria, anio)
                                       
                        if (len(self.__listaSimilares__)>0 or myDf['TIPO DE PROYECTO'][id1] == 'Coordinado' 
                            or myDf['TIPO DE PROYECTO'][id1] == 'Multicéntrico'):
                            self.__contDf2__ += 1
                            listaStr = ', '.join(self.__listaSimilares__)
                            self.__coodProjectsDf__.loc[self.__contDf2__]  =  [myDf['TITULO'][id1], myDf['REFERENCIA'][id1], myDf['STATUS'][id1],
                                                myDf['TIPO DE PROYECTO'][id1], convocatoria, anio, len(self.__listaSimilares__),
                                                listaStr]
                        
                    barId.finish()                                       

            else:
                if self.__verbose__:
                    print ('Convocatoria sin coordinados: ' + convocatoria )
            #Los proyectos que se han marcado como similares de forma manual:
            self.__setManual__ ()

            if self.__verbose__:
                print ('Total de proyectos en esta convocatoria:')
                print (numProy)
                print ('Total de proyectos coordinados detectados:')
                print (self.__coodProjectsDf__.loc[self.__coodProjectsDf__['Titulo convocatoria'] == convocatoria].shape[0])
                print ('Total de falsas alarmas (detectados coordinados y etiquetados individual):')
                print (self.__coodProjectsDf__.loc[self.__coodProjectsDf__['Titulo convocatoria'] == convocatoria].loc[self.__coodProjectsDf__['Tipo'] == 'Individual'].shape[0])
                print ('Total de perdidas (no detectados coordinados y etiquetados como coordinados):')
                print (self.__coodProjectsDf__.loc[self.__coodProjectsDf__['Titulo convocatoria'] == convocatoria].loc[self.__coodProjectsDf__['Num coordinados'] ==0].shape[0])
            
        

    '''
        Algunos proyectos son un poco temperamentales y no se pueden clasificar ni por la referencia ni por el título. Algunos son sencillos de localizar y se ponen a mano.
        Otros se pierden como lágrimas en la lluvia.
    '''
    def __setManual__ ( self ):

        # Casos que detectamos manualmente
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PIE15/00037','Lista coordinados'] = '[PIE15/00061]'
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PIE15/00037','Num coordinados'] = 1.0
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PIE15/00061','Lista coordinados'] = '[PIE15/00037]'
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PIE15/00061','Num coordinados'] = 1.0


        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2014-040-C02-02','Lista coordinados'] = '[PCIN-2014-041-C02-01]'
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2014-040-C02-02','Num coordinados'] = 1.0
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2014-041-C02-01','Lista coordinados'] = '[PCIN-2014-040-C02-02]'
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2014-041-C02-01','Num coordinados'] = 1.0


        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-002-C02-01','Lista coordinados'] = '[PCIN-2013-003-C02-02]'
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-002-C02-01','Num coordinados'] = 1.0
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-003-C02-02','Lista coordinados'] = '[PCIN-2013-002-C02-01]'
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-003-C02-02','Num coordinados'] = 1.0


        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-011-C02-01','Lista coordinados'] = '[PCIN-2013-012-C02-02]'
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-011-C02-01','Num coordinados'] = 1.0
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-012-C02-02','Lista coordinados'] = '[PCIN-2013-011-C02-01]'
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-012-C02-02','Num coordinados'] = 1.0

        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-017-C03-01','Lista coordinados'] = '[PCIN-2013-018-C03-02, PCIN-2013-019-C03-03]'
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-017-C03-01','Num coordinados'] = 2.0
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-018-C03-02','Lista coordinados'] = '[PCIN-2013-017-C03-01, PCIN-2013-019-C03-03]'
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-018-C03-02','Num coordinados'] = 2.0
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-019-C03-03','Lista coordinados'] = '[PCIN-2013-017-C03-01, PCIN-2013-018-C03-02]'
        self.__coodProjectsDf__.loc[self.__coodProjectsDf__['REF'] == 'PCIN-2013-019-C03-03','Num coordinados'] = 2.0
    
    # '''
    #     Método que salva en la base de datos el dataframe generado. No se guardan todos los datos salvados sólo los que tienen utilidad final, el resto se generan porque puede ser interesante
    #     y porque ayudan a depurar los problemas.
    # '''        
    # def saveToDatabase (self):
    #     myDf = self.__coodProjectsDf__.loc[self.__coodProjectsDf__['Num coordinados'] >0][['REF','Num coordinados', 'Lista coordinados']]
    #     #myDf['Lista coordinados'] = myDf['Lista coordinados'].apply(lambda x: ', '.join(x))
    #     self.__indicadores__.setFields ('NCOORDINADOS', zip(myDf['Num coordinados'].tolist(),myDf['REF'].tolist()))
    #     self.__indicadores__.setFields ('PCOORDINADOS', zip(myDf['Lista coordinados'].tolist(),myDf['REF'].tolist()))
    #     #self.__indicadores__.savePandas (myDf)

    def save_to_excel(self, coordinatedfile):

        self.__coodProjectsDf__.to_excel(coordinatedfile,sheet_name='coordinados')

