-- Inicialización de la base de datos PostgreSQL
-- Las tablas son creadas por SQLAlchemy + Flask-Migrate

CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
  EXECUTE format('ALTER DATABASE %I SET timezone TO ''America/Argentina/Buenos_Aires''', current_database());
END $$;
