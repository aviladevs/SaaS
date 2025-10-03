-- Database: postgres

-- DROP DATABASE IF EXISTS postgres;

CREATE DATABASE postgres
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

COMMENT ON DATABASE postgres
    IS 'default administrative connection database';

	-- Cria o usuário 'admin' se não existir
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'admin') THEN
      CREATE USER admin WITH PASSWORD 'admin123';
   END IF;
END
$$;

-- Cria o banco 'consulting_db' se não existir
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'consulting_db') THEN
      CREATE DATABASE consulting_db OWNER admin;
   END IF;
END
$$;

-- Garante privilégios no banco
GRANT ALL PRIVILEGES ON DATABASE consulting_db TO admin;
