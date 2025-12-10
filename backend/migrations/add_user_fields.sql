-- Migration Script: Add new fields to users table
-- Run this script to update your MySQL users table

-- Add first_name column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS first_name VARCHAR(255) NULL AFTER name;

-- Add last_name column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_name VARCHAR(255) NULL AFTER first_name;

-- Add dob (Date of Birth) column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS dob DATE NULL AFTER last_name;

-- Add mobile_number column (Note: User specified "mobile" but code uses "mobile_number")
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS mobile_number VARCHAR(20) NULL AFTER dob;

-- Update profile_image column size from VARCHAR(225) to VARCHAR(500) if it exists
ALTER TABLE users 
MODIFY COLUMN profile_image VARCHAR(500) NULL;

-- Note: If your MySQL version doesn't support "IF NOT EXISTS" in ALTER TABLE,
-- you can use this alternative approach:
-- 
-- ALTER TABLE users ADD COLUMN first_name VARCHAR(255) NULL;
-- ALTER TABLE users ADD COLUMN last_name VARCHAR(255) NULL;
-- ALTER TABLE users ADD COLUMN dob DATE NULL;
-- ALTER TABLE users ADD COLUMN mobile VARCHAR(20) NULL;
-- ALTER TABLE users MODIFY COLUMN profile_image VARCHAR(500) NULL;

