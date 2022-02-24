if [[ $# != 1 ]]
then
    echo "Usage: $0 <database_name>"
    exit 1
fi

DBNAME=$1

cat <<EOF
USE $DBNAME;

ALTER TABLE tls201_appln ADD PRIMARY KEY (appln_id);
ALTER TABLE tls201_appln ADD KEY IX_internat_appln_id (internat_appln_id);
ALTER TABLE tls201_appln ADD KEY IX_appln_auth (appln_auth;appln_nr;appln_kind);
ALTER TABLE tls201_appln ADD KEY IX_appln_filing_date (appln_filing_date);
ALTER TABLE tls201_appln ADD KEY IX_appln_kind (appln_kind);
ALTER TABLE tls201_appln ADD KEY IX_docdb_family_id (docdb_family_id);
ALTER TABLE tls201_appln ADD KEY IX_inpadoc_family_id (inpadoc_family_id);
ALTER TABLE tls201_appln ADD KEY IX_docdb_family_id_filing_date (docdb_family_id;appln_filing_date);
ALTER TABLE tls201_appln ADD KEY IX_inpadoc_family_id_filing_date (inpadoc_family_id;appln_filing_date);

ALTER TABLE tls202_appln_title ADD PRIMARY KEY (appln_id);

ALTER TABLE tls203_appln_abstr ADD PRIMARY KEY (appln_id);

ALTER TABLE tls204_appln_prior ADD PRIMARY KEY (appln_id;prior_appln_id);
ALTER TABLE tls204_appln_prior ADD  KEY IX_prior_appln_id (prior_appln_id);

ALTER TABLE tls205_tech_rel ADD PRIMARY KEY (appln_id;tech_rel_appln_id);

ALTER TABLE tls206_person ADD PRIMARY KEY (person_id);
ALTER TABLE tls206_person ADD KEY IX_person_ctry_code (person_ctry_code);
ALTER TABLE tls206_person ADD KEY IX_doc_std_name_id (doc_std_name_id);
ALTER TABLE tls206_person ADD KEY IX_ppat_psn_name (psn_name(250));
ALTER TABLE tls206_person ADD KEY IX_ppat_psn_sector (psn_sector);
ALTER TABLE tls206_person ADD KEY IX_ppat_psn_id (psn_id);
ALTER TABLE tls206_person ADD KEY IX_ppat_han_id (han_id);
ALTER TABLE tls206_person ADD KEY IX_han_name (han_name(250));
ALTER TABLE tls206_person ADD KEY IX_han_harmonized (han_harmonized);

ALTER TABLE tls207_pers_appln ADD PRIMARY KEY (person_id;appln_id;applt_seq_nr;invt_seq_nr);
ALTER TABLE tls207_pers_appln ADD KEY IX_person_id (person_id);
ALTER TABLE tls207_pers_appln ADD KEY IX_appln_id (appln_id);

ALTER TABLE tls209_appln_ipc ADD PRIMARY KEY (appln_id;ipc_class_symbol;ipc_class_level);
ALTER TABLE tls209_appln_ipc ADD  KEY IX_ipc_class_symbol (ipc_class_symbol);

ALTER TABLE tls210_appln_n_cls ADD PRIMARY KEY (appln_id;nat_class_symbol);

ALTER TABLE tls211_pat_publn ADD PRIMARY KEY (pat_publn_id);
ALTER TABLE tls211_pat_publn ADD KEY IX_publn_auth (publn_auth;publn_nr;publn_kind);
ALTER TABLE tls211_pat_publn ADD KEY IX_appln_id (appln_id);
ALTER TABLE tls211_pat_publn ADD KEY IX_publn_date (publn_date);
ALTER TABLE tls211_pat_publn ADD KEY IX_publ_lg (publn_lg);

ALTER TABLE tls212_citation ADD PRIMARY KEY (pat_publn_id;citn_replenished;citn_id);
ALTER TABLE tls212_citation ADD KEY IX_cited_pat_publn_id (cited_pat_publn_id);
ALTER TABLE tls212_citation ADD KEY cited_appln_id (cited_appln_id;pat_publn_id);
ALTER TABLE tls212_citation ADD KEY IX_pat_citn_seq_nr (pat_citn_seq_nr);
ALTER TABLE tls212_citation ADD KEY IX_npl_citn_seq_nr (npl_citn_seq_nr);
ALTER TABLE tls212_citation ADD KEY IX_cited_pub_seq_nr (cited_pat_publn_id;pat_citn_seq_nr);
ALTER TABLE tls212_citation ADD KEY IX_cited_app_seq_nr (cited_appln_id;pat_citn_seq_nr);

ALTER TABLE tls214_npl_publn ADD PRIMARY KEY (npl_publn_id);

ALTER TABLE tls215_citn_categ ADD PRIMARY KEY (pat_publn_id;citn_replenished;citn_id;citn_categ;relevant_claim);

ALTER TABLE tls216_appln_contn ADD PRIMARY KEY (appln_id;parent_appln_id);

ALTER TABLE tls231_inpadoc_legal_event ADD PRIMARY KEY (appln_id;event_seq_nr);
ALTER TABLE tls231_inpadoc_legal_event ADD KEY event_publn_date (event_publn_date;appln_id);
ALTER TABLE tls231_inpadoc_legal_event ADD KEY event_type (event_type;appln_id);
ALTER TABLE tls231_inpadoc_legal_event ADD KEY event_code (event_code;appln_id);

ALTER TABLE tls222_appln_jp_class ADD PRIMARY KEY (appln_id;jp_class_scheme;jp_class_symbol);
ALTER TABLE tls222_appln_jp_class ADD KEY jp_class_symbol (jp_class_symbol;jp_class_scheme)

ALTER TABLE tls223_appln_docus ADD PRIMARY KEY (appln_id;docus_class_symbol);
ALTER TABLE tls223_appln_docus ADD KEY docus_class_symbol (docus_class_symbol);

ALTER TABLE tls224_appln_cpc ADD PRIMARY KEY (appln_id; cpc_class_symbol);

ALTER TABLE tls225_docdb_fam_cpc ADD PRIMARY KEY (docdb_family_id; cpc_class_symbol; cpc_gener_auth; cpc_version);

ALTER TABLE tls226_person_orig ADD PRIMARY KEY (person_orig_id);
ALTER TABLE tls226_person_orig ADD KEY person_id (person_id);

ALTER TABLE tls227_pers_publn ADD PRIMARY KEY (person_id;pat_publn_id;applt_seq_nr;invt_seq_nr);
ALTER TABLE tls227_pers_publn ADD KEY pat_publn_id (pat_publn_id);
ALTER TABLE tls227_pers_publn ADD KEY person_id (person_id);

ALTER TABLE tls228_docdb_fam_citn ADD PRIMARY KEY (docdb_family_id;cited_docdb_family_id);
ALTER TABLE tls228_docdb_fam_citn ADD KEY docdb_family_id (docdb_family_id);
ALTER TABLE tls228_docdb_fam_citn ADD KEY cited_docdb_family_id (cited_docdb_family_id);

ALTER TABLE tls229_appln_nace2 ADD PRIMARY KEY (appln_id;nace2_code);
ALTER TABLE tls229_appln_nace2 ADD KEY nace2_code (nace2_code);

ALTER TABLE tls230_appln_techn_field ADD PRIMARY KEY (appln_id;techn_field_nr);

ALTER TABLE tls801_country ADD PRIMARY KEY (ctry_code);

ALTER TABLE tls803_legal_event_code ADD PRIMARY KEY (event_auth; event_code);

ALTER TABLE tls901_techn_field_ipc ADD PRIMARY KEY (techn_field_nr;techn_sector;techn_field;ipc_maingroup_symbol);

ALTER TABLE tls902_ipc_nace2 ADD PRIMARY KEY (ipc;not_with_ipc;unless_with_ipc;nace2_code);

ALTER TABLE tls904_nuts ADD PRIMARY KEY (nuts);

ALTER TABLE tls909_eee_ppat ADD PRIMARY KEY (person_id);
ALTER TABLE tls909_eee_ppat ADD KEY IX_ppat_person_ctry_code (person_ctry_code);
ALTER TABLE tls909_eee_ppat ADD KEY IX_ppat_hrm_l1 (hrm_l1(333));
ALTER TABLE tls909_eee_ppat ADD KEY IX_ppat_hrm_l2 (hrm_l2(333));
ALTER TABLE tls909_eee_ppat ADD KEY IX_ppat_sector (sector);
ALTER TABLE tls909_eee_ppat ADD KEY IX_ppat_hrm_l2_id (hrm_l2_id);

EOF
