if [[ $# != 2 ]]
then
    echo "Usage: $0 <database_name> <engine>"
    exit 1
fi

DBNAME=$1
ENGINE=$2
if [[ $ENGINE == "innodb" ]]; then
   ROW_FORMAT="ROW_FORMAT=COMPRESSED"
fi

cat <<EOF
CREATE DATABASE IF NOT EXISTS $DBNAME DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE $DBNAME;

CREATE TABLE tls201_appln (
  appln_id int(11) NOT NULL DEFAULT '0',
  appln_auth char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  appln_nr varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  appln_kind char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '00',
  appln_filing_date date NOT NULL DEFAULT '9999-12-31',
  appln_filing_year smallint NOT NULL DEFAULT '9999',
  appln_nr_epodoc varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  appln_nr_original varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  ipr_type char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  receiving_office char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  internat_appln_id int(11) NOT NULL DEFAULT '0',
  int_phase varchar(11) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  reg_phase varchar(11) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  nat_phase varchar(11) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  earliest_filing_date date NOT NULL DEFAULT '9999-12-31',
  earliest_filing_year smallint NOT NULL DEFAULT '9999',
  earliest_filing_id int NOT NULL DEFAULT '0',
  earliest_publn_date date NOT NULL DEFAULT '9999-12-31',
  earliest_publn_year smallint NOT NULL DEFAULT '9999',
  earliest_pat_publn_id int NOT NULL DEFAULT '0',
  granted char(1) NOT NULL DEFAULT 'N',
  docdb_family_id int NOT NULL DEFAULT '0',
  inpadoc_family_id int NOT NULL DEFAULT '0',
  docdb_family_size smallint NOT NULL default '0',
  nb_citing_docdb_fam smallint NOT NULL default '0',
  nb_applicants smallint NOT NULL default '0',
  nb_inventors smallint NOT NULL default '0'
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls202_appln_title (
  appln_id int(11) NOT NULL DEFAULT '0',
  appln_title_lg char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  appln_title text COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  AVG_ROW_LENGTH=600;



CREATE TABLE tls203_appln_abstr (
  appln_id int(11) NOT NULL DEFAULT '0',
  appln_abstract_lg char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  appln_abstract text COLLATE utf8mb4_unicode_ci
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  AVG_ROW_LENGTH=800;



CREATE TABLE tls204_appln_prior (
  appln_id int(11) NOT NULL DEFAULT '0',
  prior_appln_id int(11) NOT NULL DEFAULT '0',
  prior_appln_seq_nr smallint(6) NOT NULL DEFAULT '0'
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  AVG_ROW_LENGTH=800;



CREATE TABLE tls205_tech_rel (
  appln_id int(11) NOT NULL DEFAULT '0',
  tech_rel_appln_id int(11) NOT NULL DEFAULT '0'
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  AVG_ROW_LENGTH=100;



CREATE TABLE tls206_person (
  person_id int NOT NULL DEFAULT '0',
  person_name varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  person_name_orig_lg varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  person_address varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL,
  person_ctry_code char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  nuts char(5) NOT NULL DEFAULT '',
  nuts_level smallint  NOT NULL DEFAULT '9',
  doc_std_name_id int NOT NULL DEFAULT '0',
  doc_std_name varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  psn_id int NOT NULL DEFAULT '0',
  psn_name varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  psn_level smallint NOT NULL DEFAULT '0',
  psn_sector varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  han_id int NOT NULL DEFAULT '0',
  han_name varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  han_harmonized int NOT NULL DEFAULT '0'
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  AVG_ROW_LENGTH=100;



CREATE TABLE tls207_pers_appln (
  person_id int(11) NOT NULL DEFAULT '0',
  appln_id int(11) NOT NULL DEFAULT '0',
  applt_seq_nr smallint(6) NOT NULL DEFAULT '0',
  invt_seq_nr smallint(6) NOT NULL DEFAULT '0'
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls209_appln_ipc (
  appln_id int(11) NOT NULL DEFAULT '0',
  ipc_class_symbol varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  ipc_class_level char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  ipc_version date NOT NULL DEFAULT '9999-12-31',
  ipc_value char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  ipc_position char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  ipc_gener_auth char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls210_appln_n_cls (
  appln_id int(11) NOT NULL DEFAULT '0',
  nat_class_symbol varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls211_pat_publn (
  pat_publn_id int(11) NOT NULL DEFAULT '0',
  publn_auth char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  publn_nr varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  publn_nr_original varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  publn_kind char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  appln_id int(11) NOT NULL DEFAULT '0',
  publn_date date NOT NULL DEFAULT '9999-12-31',
  publn_lg char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  publn_first_grant char(1) NOT NULL DEFAULT 'N',
  publn_claims smallint(6) DEFAULT NULL
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls212_citation (
  pat_publn_id int(11) NOT NULL DEFAULT '0',
  citn_replenished int NOT NULL DEFAULT '0',
  citn_id smallint(6) NOT NULL DEFAULT '0',
  citn_origin char(3) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  cited_pat_publn_id int(11) NOT NULL DEFAULT '0',
  cited_appln_id int(10) unsigned NOT NULL DEFAULT '0',
  pat_citn_seq_nr smallint(6) NOT NULL DEFAULT '0',
  cited_npl_publn_id varchar(32) NOT NULL DEFAULT '0',
  npl_citn_seq_nr smallint(6) NOT NULL DEFAULT '0',
  citn_gener_auth char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  PACK_KEYS=0;



CREATE TABLE tls214_npl_publn (
  npl_publn_id varchar(32) NOT NULL DEFAULT '0',
  xp_nr int(11) NOT NULL DEFAULT '0',
  npl_type char(1) NOT NULL DEFAULT '',
  npl_biblio longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  npl_author nvarchar(1000) NOT NULL DEFAULT '',
  npl_title1 nvarchar(1000) NOT NULL DEFAULT '',
  npl_title2 nvarchar(1000) NOT NULL DEFAULT '',
  npl_editor nvarchar(500) NOT NULL DEFAULT '',
  npl_volume varchar(50) NOT NULL DEFAULT '',
  npl_issue varchar(50) NOT NULL DEFAULT '',
  npl_publn_date varchar(8) NOT NULL DEFAULT '',
  npl_publn_end_date varchar(8) NOT NULL DEFAULT '',
  npl_publisher nvarchar(500) NOT NULL DEFAULT '',
  npl_page_first varchar(200) NOT NULL DEFAULT '',
  npl_page_last varchar(200) NOT NULL DEFAULT '',
  npl_abstract_nr varchar(50) NOT NULL DEFAULT '',
  npl_doi varchar(500) NOT NULL DEFAULT '',
  npl_isbn varchar(30) NOT NULL DEFAULT '',
  npl_issn varchar(30) NOT NULL DEFAULT '',
  online_availability varchar(500) NOT NULL DEFAULT '',
  online_classification varchar(35) NOT NULL DEFAULT '',
  online_search_date varchar(8) NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  AVG_ROW_LENGTH=150;



CREATE TABLE tls215_citn_categ (
  pat_publn_id int(11) NOT NULL DEFAULT '0',
  citn_replenished int NOT NULL DEFAULT '0',
  citn_id smallint(6) NOT NULL DEFAULT '0',
  citn_categ char(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  relevant_claim smallint(6) NOT NULL DEFAULT 0
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls216_appln_contn (
  appln_id int(11) NOT NULL DEFAULT '0',
  parent_appln_id int(11) NOT NULL DEFAULT '0',
  contn_type char(3) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;


CREATE TABLE tls231_inpadoc_legal_event (
  event_id int NOT NULL DEFAULT '0',
  appln_id int(11) NOT NULL DEFAULT '0',
  event_seq_nr smallint(6) NOT NULL DEFAULT '0',
  event_type char(3) NOT NULL DEFAULT '  ',
  event_auth char(2) NOT NULL DEFAULT '  ',
  event_code varchar(4)  NOT NULL DEFAULT '',
	event_filing_date date NOT NULL DEFAULT '9999-12-31',
  event_publn_date date NOT NULL DEFAULT '9999-12-31',
  event_effective_date date NOT NULL DEFAULT '9999-12-31',
  event_text varchar(1000) NOT NULL DEFAULT '',
  ref_doc_auth char(2) NOT NULL DEFAULT '  ',
  ref_doc_nr varchar(20) NOT NULL DEFAULT '',
  ref_doc_kind char(2) NOT NULL DEFAULT '  ',
  ref_doc_date date NOT NULL DEFAULT '9999-12-31',
  ref_doc_text varchar(1000) NOT NULL DEFAULT '',
  party_type varchar(3) NOT NULL DEFAULT '   ',
  party_seq_nr smallint NOT NULL default '0',
  party_new varchar(1000) NOT NULL DEFAULT '',
  party_old varchar(1000) NOT NULL DEFAULT '',
  spc_nr varchar(40) NOT NULL DEFAULT '',
  spc_filing_date date NOT NULL DEFAULT '9999-12-31',
  spc_patent_expiry_date date NOT NULL DEFAULT '9999-12-31',
  spc_extension_date date NOT NULL DEFAULT '9999-12-31',
  spc_text varchar(1000) NOT NULL DEFAULT '',
  designated_states varchar(1000) NOT NULL DEFAULT '',
  extension_states varchar(30) NOT NULL DEFAULT '',
  fee_country char(2) NOT NULL DEFAULT '  ',
  fee_payment_date date NOT NULL DEFAULT '9999-12-31',
  fee_renewal_year smallint NOT NULL default '9999',
  fee_text varchar(1000) NOT NULL DEFAULT '',
  lapse_country char(2) NOT NULL DEFAULT '  ',
  lapse_date date NOT NULL DEFAULT '9999-12-31',
  lapse_text varchar(1000) NOT NULL DEFAULT '',
  reinstate_country char(2) NOT NULL DEFAULT '  ',
  reinstate_date date NOT NULL DEFAULT '9999-12-31',
  reinstate_text varchar(1000) NOT NULL DEFAULT '',
  class_scheme varchar(4) NOT NULL DEFAULT '',
  class_symbol varchar(50) NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  AVG_ROW_LENGTH=100;



CREATE TABLE tls222_appln_jp_class (
  appln_id int(11) NOT NULL DEFAULT '0',
  jp_class_scheme varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  jp_class_symbol varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls223_appln_docus (
  appln_id int(11) NOT NULL DEFAULT '0',
  docus_class_symbol varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls224_appln_cpc (
  appln_id int(11) NOT NULL DEFAULT '0',
  cpc_class_symbol varchar(19) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls225_docdb_fam_cpc (
  docdb_family_id int NOT NULL DEFAULT '0',
  cpc_class_symbol varchar(19) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  cpc_gener_auth char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  cpc_version date NOT NULL DEFAULT '9999-12-31',
  cpc_position char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  cpc_value char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  cpc_action_date date NOT NULL DEFAULT '9999-12-31',
  cpc_status char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  cpc_data_source char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls226_person_orig (
  person_orig_id int(11) NOT NULL DEFAULT '0',
  person_id int(11) NOT NULL DEFAULT '0',
  source char(5) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  source_version varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  name_freeform varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  person_name_orig_lg varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  last_name varchar(400) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  first_name varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  middle_name varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  address_freeform varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  address_1 varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  address_2 varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  address_3 varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  address_4 varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  address_5 varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  street varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  city varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  zip_code varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  state char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  person_ctry_code char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  residence_ctry_code char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  role varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls227_pers_publn (
  person_id int(11) NOT NULL DEFAULT '0',
  pat_publn_id int(11) NOT NULL DEFAULT '0',
  applt_seq_nr smallint(6) NOT NULL DEFAULT '0',
  invt_seq_nr smallint(6) NOT NULL DEFAULT '0'
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls228_docdb_fam_citn (
  docdb_family_id int(11) NOT NULL DEFAULT '0',
  cited_docdb_family_id int(11) NOT NULL DEFAULT '0'
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls229_appln_nace2 (
  appln_id int(11) NOT NULL DEFAULT '0',
  nace2_code char(5) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  weight float NOT NULL DEFAULT '1'
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls230_appln_techn_field (
  appln_id int(11) NOT NULL DEFAULT '0',
  techn_field_nr tinyint NOT NULL DEFAULT '0',
  weight float NOT NULL DEFAULT '1'
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls801_country (
  ctry_code varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  iso_alpha3 varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  st3_name varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  organisation_flag char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  continent varchar(25) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  eu_member char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  epo_member char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  oecd_member char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  discontinued char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  AVG_ROW_LENGTH=100;


CREATE TABLE tls803_legal_event_code (
  event_auth char(2) NOT NULL DEFAULT '',
  event_code varchar(4) NOT NULL DEFAULT '',
  event_impact char(1) NOT NULL DEFAULT '',
  event_descr varchar(250) NOT NULL DEFAULT '',
  event_descr_orig varchar(250) NOT NULL DEFAULT '',
  event_category_code char(1) NOT NULL DEFAULT '',
  event_category_title varchar(100) NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  AVG_ROW_LENGTH=100;



CREATE TABLE tls901_techn_field_ipc (
  ipc_maingroup_symbol varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  techn_field_nr tinyint(4) NOT NULL DEFAULT '0',
  techn_sector varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  techn_field varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  AVG_ROW_LENGTH=100;



CREATE TABLE tls902_ipc_nace2 (
  ipc varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  not_with_ipc varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  unless_with_ipc varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  nace2_code char(5) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  nace2_weight float NOT NULL DEFAULT '1',
  nace2_descr varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls904_nuts (
  nuts varchar(5) NOT NULL,
  nuts_level int NOT NULL DEFAULT '0',
  nuts_label varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;



CREATE TABLE tls909_eee_ppat (
  person_id int(11) NOT NULL DEFAULT '0',
  person_ctry_code char(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  person_name varchar(400) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  hrm_l1 varchar(400) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  hrm_l2 varchar(400) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  hrm_level tinyint(4) NOT NULL DEFAULT '0',
  hrm_l2_id int(11) NOT NULL DEFAULT '0',
  sector varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  person_address varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL,
  doc_std_name_id int(11) NOT NULL DEFAULT '0',
  pat_cnt int(11) NOT NULL
) ENGINE=${ENGINE} $ROW_FORMAT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci  AVG_ROW_LENGTH=100;

EOF
