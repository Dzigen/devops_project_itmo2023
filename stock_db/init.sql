CREATE DATABASE devops_db;
CREATE USER devops_user WITH PASSWORD 'devops_password';

ALTER DATABASE devops_db OWNER TO devops_user;

ALTER ROLE devops_user SET client_encoding TO 'utf8';
ALTER ROLE devops_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE devops_user SET timezone TO 'UTC';

/*
GRANT CONNECT ON DATABASE devops_db TO devops_user;
GRANT ALL PRIVILEGES ON DATABASE devops_db TO devops_user;
GRANT USAGE ON SCHEMA public TO devops_user;
*/
