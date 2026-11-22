# Safar: SQL from zero

Safar is a bus ticket booking app. Its PostgreSQL database runs next to you, and `psql` is already connected to
it: type `psql` for a prompt (`\dt` lists the tables, `\d bookings` describes one, `\q` leaves).

Every chapter has its own folder. Write each answer in its file, below the comment, and run it from the folder:

    cd /workspace/02-asking-for-rows && psql -f q1.sql

Chapters 9 to 13 change the database. If you ever want the original data back, press Reset lab.
