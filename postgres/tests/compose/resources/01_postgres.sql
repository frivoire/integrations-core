ALTER SYSTEM SET max_connections = '1000';
ALTER SYSTEM SET shared_buffers = '240MB';

CREATE USER datadog WITH PASSWORD 'datadog';
CREATE USER datadog_no_catalog WITH PASSWORD 'datadog';
CREATE USER bob WITH PASSWORD 'bob';
CREATE USER blocking_bob WITH PASSWORD 'bob';
CREATE USER dd_admin WITH PASSWORD 'dd_admin';
CREATE USER replicator WITH REPLICATION;
ALTER USER dd_admin WITH SUPERUSER;
REVOKE SELECT ON ALL tables IN SCHEMA pg_catalog from public;
GRANT SELECT ON pg_stat_database TO datadog;
GRANT SELECT ON pg_stat_database TO datadog_no_catalog;
GRANT SELECT ON ALL tables IN SCHEMA pg_catalog to datadog;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public to datadog;
CREATE DATABASE datadog_test;
GRANT ALL PRIVILEGES ON DATABASE datadog_test TO datadog;
CREATE DATABASE dogs;
GRANT USAGE on SCHEMA public to bob;
GRANT USAGE on SCHEMA public to blocking_bob;
CREATE DATABASE dogs_nofunc;
CREATE DATABASE dogs_noschema;

-- These databases must be enumerated like so because postgres does
-- not support the creation of databases in a transaction so functions
-- cannot be used to accomplish this same task. Anyone aware of a better
-- implementation is welcome to change it.
CREATE DATABASE dogs_0;
CREATE DATABASE dogs_1;
CREATE DATABASE dogs_2;
CREATE DATABASE dogs_3;
CREATE DATABASE dogs_4;
CREATE DATABASE dogs_5;
CREATE DATABASE dogs_6;
CREATE DATABASE dogs_7;
CREATE DATABASE dogs_8;
CREATE DATABASE dogs_9;
CREATE DATABASE dogs_10;
CREATE DATABASE dogs_11;
CREATE DATABASE dogs_12;
CREATE DATABASE dogs_13;
CREATE DATABASE dogs_14;
CREATE DATABASE dogs_15;
CREATE DATABASE dogs_16;
CREATE DATABASE dogs_17;
CREATE DATABASE dogs_18;
CREATE DATABASE dogs_19;
CREATE DATABASE dogs_20;
CREATE DATABASE dogs_21;
CREATE DATABASE dogs_22;
CREATE DATABASE dogs_23;
CREATE DATABASE dogs_24;
CREATE DATABASE dogs_25;
CREATE DATABASE dogs_26;
CREATE DATABASE dogs_27;
CREATE DATABASE dogs_28;
CREATE DATABASE dogs_29;
CREATE DATABASE dogs_30;
CREATE DATABASE dogs_31;
CREATE DATABASE dogs_32;
CREATE DATABASE dogs_33;
CREATE DATABASE dogs_34;
CREATE DATABASE dogs_35;
CREATE DATABASE dogs_36;
CREATE DATABASE dogs_37;
CREATE DATABASE dogs_38;
CREATE DATABASE dogs_39;
CREATE DATABASE dogs_40;
CREATE DATABASE dogs_41;
CREATE DATABASE dogs_42;
CREATE DATABASE dogs_43;
CREATE DATABASE dogs_44;
CREATE DATABASE dogs_45;
CREATE DATABASE dogs_46;
CREATE DATABASE dogs_47;
CREATE DATABASE dogs_48;
CREATE DATABASE dogs_49;
CREATE DATABASE dogs_50;
CREATE DATABASE dogs_51;
CREATE DATABASE dogs_52;
CREATE DATABASE dogs_53;
CREATE DATABASE dogs_54;
CREATE DATABASE dogs_55;
CREATE DATABASE dogs_56;
CREATE DATABASE dogs_57;
CREATE DATABASE dogs_58;
CREATE DATABASE dogs_59;
CREATE DATABASE dogs_60;
CREATE DATABASE dogs_61;
CREATE DATABASE dogs_62;
CREATE DATABASE dogs_63;
CREATE DATABASE dogs_64;
CREATE DATABASE dogs_65;
CREATE DATABASE dogs_66;
CREATE DATABASE dogs_67;
CREATE DATABASE dogs_68;
CREATE DATABASE dogs_69;
CREATE DATABASE dogs_70;
CREATE DATABASE dogs_71;
CREATE DATABASE dogs_72;
CREATE DATABASE dogs_73;
CREATE DATABASE dogs_74;
CREATE DATABASE dogs_75;
CREATE DATABASE dogs_76;
CREATE DATABASE dogs_77;
CREATE DATABASE dogs_78;
CREATE DATABASE dogs_79;
CREATE DATABASE dogs_80;
CREATE DATABASE dogs_81;
CREATE DATABASE dogs_82;
CREATE DATABASE dogs_83;
CREATE DATABASE dogs_84;
CREATE DATABASE dogs_85;
CREATE DATABASE dogs_86;
CREATE DATABASE dogs_87;
CREATE DATABASE dogs_88;
CREATE DATABASE dogs_89;
CREATE DATABASE dogs_90;
CREATE DATABASE dogs_91;
CREATE DATABASE dogs_92;
CREATE DATABASE dogs_93;
CREATE DATABASE dogs_94;
CREATE DATABASE dogs_95;
CREATE DATABASE dogs_96;
CREATE DATABASE dogs_97;
CREATE DATABASE dogs_98;
CREATE DATABASE dogs_99;
CREATE DATABASE dogs_100;
