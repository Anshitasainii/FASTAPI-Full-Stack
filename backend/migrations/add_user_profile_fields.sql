-- Migration Script: Add professional profile fields to users table

-- Add professional_summary column
ALTER TABLE users
ADD COLUMN IF NOT EXISTS professional_summary TEXT NULL AFTER mobile;

-- Add gender column
ALTER TABLE users
ADD COLUMN IF NOT EXISTS gender VARCHAR(20) NULL AFTER professional_summary;

-- Add job_status column
ALTER TABLE users
ADD COLUMN IF NOT EXISTS job_status VARCHAR(50) NULL AFTER gender;

