-- seed_data.sql
DELETE FROM words;
DELETE FROM movies;

INSERT INTO movies (id, title, year) VALUES (1, 'Forrest Gump', 1994);
INSERT INTO words (movie_id, english, russian, example) VALUES
(1, 'bench', 'скамейка', 'He sat on a bench in the park.'),
(1, 'chocolate', 'шоколад', 'Life is like a box of chocolates.'),
(1, 'run', 'бежать', 'Run, Forrest, run!'),
(1, 'shrimp', 'креветка', 'Bubba loved shrimp.');

INSERT INTO movies (id, title, year) VALUES (2, 'Titanic', 1997);
INSERT INTO words (movie_id, english, russian, example) VALUES
(2, 'iceberg', 'айсберг', 'The ship hit an iceberg.'),
(2, 'promise', 'обещание', 'You must promise me you will survive.'),
(2, 'ocean', 'океан', 'The Titanic sank in the Atlantic Ocean.');