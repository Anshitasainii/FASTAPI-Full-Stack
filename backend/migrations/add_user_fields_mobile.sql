-- Migration Script: Add new fields to users table (using "mobile" as specified)
-- This version uses "mobile" instead of "mobile_number" to match your specification
-- Note: You'll need to update the code to use "mobile" instead of "mobile_number"

-- Add first_name column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS first_name VARCHAR(255) NULL AFTER name;

-- Add last_name column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_name VARCHAR(255) NULL AFTER first_name;

-- Add dob (Date of Birth) column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS dob DATE NULL AFTER last_name;

-- Add mobile column (as specified)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS mobile VARCHAR(20) NULL AFTER dob;

-- Update profile_image column size from VARCHAR(225) to VARCHAR(500) if it exists
ALTER TABLE users 
MODIFY COLUMN profile_image VARCHAR(500) NULL;

