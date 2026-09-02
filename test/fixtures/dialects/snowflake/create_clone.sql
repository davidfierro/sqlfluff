CREATE DATABASE mytestdb_clone CLONE mytestdb;

CREATE SCHEMA mytestschema_clone CLONE testschema;

CREATE TABLE orders_clone CLONE orders;

CREATE SCHEMA mytestschema_clone_restore CLONE testschema BEFORE (TIMESTAMP => TO_TIMESTAMP(40*365*86400));

CREATE TABLE orders_clone_restore CLONE orders AT (TIMESTAMP => TO_TIMESTAMP_TZ('04/05/2013 01:02:03', 'mm/dd/yyyy hh24:mi:ss'));

CREATE TABLE orders_clone_restore CLONE orders BEFORE (STATEMENT => '8e5d0ca9-005e-44e6-b858-a8f5b37c5726');

CREATE TRANSIENT SCHEMA clone_schema CLONE source_schema;

CREATE SCHEMA clone_schema CLONE source_schema IGNORE HYBRID TABLES;

CREATE OR REPLACE SCHEMA clone_schema
    CLONE source_schema
    IGNORE TABLES WITH INSUFFICIENT DATA RETENTION
    COPY GRANTS;

CREATE TRANSIENT DATABASE clone_db CLONE source_db;

CREATE OR REPLACE TRANSIENT TABLE orders_clone CLONE orders AT (OFFSET => -3600);

CREATE DATABASE clone_db
    CLONE source_db
    BEFORE (STATEMENT => '8e5d0ca9-005e-44e6-b858-a8f5b37c5726')
    IGNORE HYBRID TABLES
    COPY GRANTS;

-- docs create-clone: [ INCLUDE INTERNAL STAGES ] for databases and schemas
CREATE DATABASE clone_db CLONE source_db INCLUDE INTERNAL STAGES;
CREATE SCHEMA clone_schema CLONE source_schema INCLUDE INTERNAL STAGES;
CREATE OR REPLACE DATABASE clone_db CLONE source_db
    AT (TIMESTAMP => '2025-04-01 12:00:00'::TIMESTAMP)
    IGNORE TABLES WITH INSUFFICIENT DATA RETENTION
    IGNORE HYBRID TABLES
    INCLUDE INTERNAL STAGES;
CREATE SCHEMA clone_schema CLONE source_schema
    INCLUDE INTERNAL STAGES
    IGNORE HYBRID TABLES;

-- docs create-clone: event tables, alerts and database roles
CREATE EVENT TABLE clone_events CLONE source_events;
CREATE OR REPLACE EVENT TABLE clone_events CLONE source_events AT (OFFSET => -3600);
CREATE ALERT clone_alert CLONE source_alert;
CREATE OR REPLACE ALERT IF NOT EXISTS clone_alert CLONE source_alert;
CREATE DATABASE ROLE clone_role CLONE source_role;
CREATE OR REPLACE DATABASE ROLE IF NOT EXISTS db1.clone_role CLONE db1.source_role;

-- docs create-clone: dynamic table and Iceberg table clones with Time Travel
--   CREATE [ OR REPLACE ] DYNAMIC TABLE <name> CLONE <source> [ { AT | BEFORE } ( ... ) ]
--     [ TARGET_LAG = ... WAREHOUSE = <warehouse_name> ]
--   CREATE [ OR REPLACE ] ICEBERG TABLE [ IF NOT EXISTS ] <name> CLONE <source>
--     [ { AT | BEFORE } ( ... ) ] [ COPY GRANTS ]
CREATE OR REPLACE DYNAMIC TABLE dt_clone CLONE dt_source
  AT (TIMESTAMP => '2025-04-01 12:00:00'::TIMESTAMP)
  TARGET_LAG = '1 hour'
  WAREHOUSE = my_wh;
CREATE OR REPLACE ICEBERG TABLE IF NOT EXISTS iceberg_clone CLONE iceberg_source
  BEFORE (STATEMENT => '8e5d0ca9-005e-44e6-b858-a8f5b37c5726')
  COPY GRANTS;

-- docs create-clone examples (verbatim)
CREATE DATABASE restored_db CLONE my_db
  AT (TIMESTAMP => DATEADD(days, -4, current_timestamp)::timestamp_tz)
  IGNORE TABLES WITH INSUFFICIENT DATA RETENTION;
CREATE OR REPLACE SCHEMA clone_ht_schema CLONE ht_schema
  IGNORE HYBRID TABLES;
CREATE SCHEMA S2 CLONE S1 AT(TIMESTAMP => '2025-04-01 12:00:00');
CREATE SCHEMA S3 CLONE S1;
CREATE SCHEMA source_clone CLONE source;

-- docs create-clone: tables, dynamic tables and Iceberg tables
CREATE TABLE IF NOT EXISTS orders_clone CLONE orders;
CREATE OR REPLACE TABLE orders_clone CLONE orders BEFORE (OFFSET => -3600);
CREATE DYNAMIC TABLE dt_clone CLONE dt_source;
CREATE DYNAMIC TABLE dt_clone CLONE dt_source TARGET_LAG = DOWNSTREAM WAREHOUSE = my_wh;
CREATE OR REPLACE DYNAMIC TABLE dt_clone CLONE dt_source BEFORE (OFFSET => -3600) TARGET_LAG = '20 minutes' WAREHOUSE = my_wh;
CREATE ICEBERG TABLE iceberg_clone CLONE iceberg_source;
CREATE OR REPLACE ICEBERG TABLE iceberg_clone CLONE iceberg_source AT (OFFSET => -3600);

-- docs create-clone: { ALERT | FILE FORMAT | SEQUENCE | STAGE | STREAM | TASK }
CREATE FILE FORMAT ff_clone CLONE ff_source;
CREATE OR REPLACE FILE FORMAT IF NOT EXISTS ff_clone CLONE ff_source;
CREATE SEQUENCE seq_clone CLONE seq_source;
CREATE OR REPLACE SEQUENCE IF NOT EXISTS seq_clone CLONE seq_source;
CREATE STAGE stage_clone CLONE stage_source;
CREATE OR REPLACE STAGE IF NOT EXISTS stage_clone CLONE stage_source;
CREATE STREAM stream_clone CLONE stream_source;
CREATE OR REPLACE STREAM IF NOT EXISTS stream_clone CLONE stream_source;
CREATE TASK task_clone CLONE task_source;
CREATE OR REPLACE TASK IF NOT EXISTS task_clone CLONE task_source;
