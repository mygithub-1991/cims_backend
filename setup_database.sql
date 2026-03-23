-- CIMS Database Setup Script
-- Run this script to create the database and user

-- Create database
CREATE DATABASE cims_db;

-- Create user
CREATE USER cims_user WITH PASSWORD 'Cims@2024';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cims_db TO cims_user;

-- Connect to the database
\c cims_db

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO cims_user;
