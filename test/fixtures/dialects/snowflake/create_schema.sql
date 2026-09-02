create schema mytestschema_clone_restore clone testschema;
create schema mytestdatabase1.mytestschema_clone_restore clone mytestdatabase2.testschema;
create schema mytestschema_clone_restore clone testschema before (timestamp => to_timestamp(40*365*86400));
create schema mytestschema comment = 'My test schema.';
create schema mytestschema tag (tag1 = 'foo', tag2 = 'bar');
create schema mytestschema with managed access;
create transient schema if not exists mytestschema default_ddl_collation = 'de_DE';
CREATE SCHEMA MYDB.MYSCHEMA COMMENT = "Space for landing my data";
CREATE SCHEMA IF NOT EXISTS MYDB.MYSCHEMA COMMENT = "Space for landing my data";
CREATE OR ALTER SCHEMA MYDB.MYSCHEMA;
CREATE SCHEMA governed_schema WITH CONTACT (STEWARD = my_db.my_schema.contact1, SUPPORT = contact2);
CREATE SCHEMA modern_schema DATA_RETENTION_TIME_IN_DAYS = 5 LOG_LEVEL = 'INFO' OBJECT_VISIBILITY = PRIVILEGED;
CREATE SCHEMA iceberg_schema
    EXTERNAL_VOLUME = 'my_volume'
    CATALOG = 'my_catalog'
    ICEBERG_DEFAULT_DDL_COLLATION = 'en-ci'
    ICEBERG_VERSION_DEFAULT = 2
    ICEBERG_MERGE_ON_READ_BEHAVIOR = 'AUTO'
    ENABLE_ICEBERG_MERGE_ON_READ = FALSE
    REPLACE_INVALID_CHARACTERS = TRUE
    STORAGE_SERIALIZATION_POLICY = OPTIMIZED
    CLASSIFICATION_PROFILE = 'my_profile'
    CATALOG_SYNC = 'my_open_catalog_integration'
    ENABLE_DATA_COMPACTION = TRUE
    OAUTH_AUTHORIZATION_SERVER = my_external_oauth_integration
    OAUTH_SCOPES_SUPPORTED = 'read,write';

-- docs create-schema: CLONE followed by the remaining clauses
--   [ CLONE <source_schema> [ { AT | BEFORE } ( ... ) ] [ IGNORE ... ] ]
--   [ WITH MANAGED ACCESS ] [ <params> ] [ [ WITH ] TAG ( ... ) ] [ WITH CONTACT ( ... ) ]
CREATE SCHEMA s1 CLONE s0 WITH MANAGED ACCESS DATA_RETENTION_TIME_IN_DAYS = 1;
CREATE OR REPLACE TRANSIENT SCHEMA IF NOT EXISTS s1 CLONE s0
    AT (OFFSET => -60)
    IGNORE TABLES WITH INSUFFICIENT DATA RETENTION
    IGNORE HYBRID TABLES
    WITH MANAGED ACCESS
    DATA_RETENTION_TIME_IN_DAYS = 1
    COMMENT = 'cloned'
    WITH TAG (env = 'dev')
    WITH CONTACT (STEWARD = c1);
-- docs create-schema: CREATE SCHEMA <name> FROM BACKUP SET <backup_set> IDENTIFIER '<backup_id>'
CREATE SCHEMA s1 FROM BACKUP SET my_backup_set IDENTIFIER 'backup_id_1';

-- docs create-schema parameters: DEFAULT_METADATA_WRITE_FORMAT = { SNOWFLAKE | ICEBERG }
CREATE SCHEMA s1 DEFAULT_METADATA_WRITE_FORMAT = ICEBERG;
CREATE SCHEMA s1 DEFAULT_METADATA_WRITE_FORMAT = SNOWFLAKE DATA_RETENTION_TIME_IN_DAYS = 1;
CREATE SCHEMA s1 CATALOG = 'SNOWFLAKE' DEFAULT_METADATA_WRITE_FORMAT = ICEBERG COMMENT = 'x';
CREATE SCHEMA s1 DATA_RETENTION_TIME_IN_DAYS = 1 COMMENT = 'x' DEFAULT_METADATA_WRITE_FORMAT = ICEBERG;
