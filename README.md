# Tools for Ingestion of PATSTAT and CORDIS data in IntelComp Data Space

## Initialize the repository

Comment on how to add the dbManager submodule (only if MySQL ingestion is required

## Configuration file

Copy config_default.cf as config.cf, and fill in the required information

## Download Cordis files

The list of URLs to the Cordis files to download should be provided in file `CORDISfiles.txt`. The download of the files can be carried out executing

```$ wget -i CORDISfiles.txt -P ./data/data_Pr_CORDIS/20220221/ --show-progress```

The path where the files will be downloaded should be modified accordingly

## Download PATSTAT files

The download of PATSTAT files cannot be automatized at this point. It is necessary to get the files for new versions via web, and using credentials. For IntelComp, UC3M will provide directly the new versions of PATSTAT every six months approximately (Spring and Autumn editions)

