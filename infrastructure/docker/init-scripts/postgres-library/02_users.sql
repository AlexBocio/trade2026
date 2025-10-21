-- ==================================================
-- User Creation and Permissions
-- ==================================================

-- Create library service user
CREATE USER library_service WITH PASSWORD 'change_in_production_2025';

-- Grant schema usage
GRANT USAGE ON SCHEMA public TO library_service;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO library_service;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO library_service;

-- Grant future permissions (for new tables)
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO library_service;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO library_service;

-- Grant execute on functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO library_service;

-- Create read-only user for monitoring
CREATE USER library_readonly WITH PASSWORD 'readonly_2025';
GRANT USAGE ON SCHEMA public TO library_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO library_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO library_readonly;

-- ==================================================
-- END OF USER SETUP
-- ==================================================
