-- Migration to add URL field to entities table
-- Run this if you've already created the entities table

ALTER TABLE entities ADD COLUMN IF NOT EXISTS url VARCHAR(500);
