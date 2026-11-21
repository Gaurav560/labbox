-- Products gain a category. Existing rows get 'other' until someone sorts them.
ALTER TABLE product ADD COLUMN category VARCHAR(40) DEFAULT 'other' NOT NULL;
