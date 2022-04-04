PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE participants (
   company text NOT NULL,
   full_name text NOT NULL,
   email text NOT NULL UNIQUE, 
   ticket_type text NOT NULL,
   position text NOT NULL,
   mobile text NULL,
   address text NULL,
   city text NOT NULL,
   first_printed DATE NULL,
   last_printed DATE NULL,
   num_of_times_printed INTEGER NOT NULL DEFAULT 0,
   registered DATE NULL DEFAULT CURRENT_TIMESTAMP
);
COMMIT;
