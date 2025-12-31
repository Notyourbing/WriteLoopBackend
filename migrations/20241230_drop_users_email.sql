-- Drop email column from users table (registration no longer requires email).
ALTER TABLE users DROP COLUMN email;
