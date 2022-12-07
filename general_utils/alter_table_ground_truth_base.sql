PRAGMA foreign_keys=off;

BEGIN TRANSACTION;

DROP TABLE ground_truth;

CREATE TABLE ground_truth (
  id INTEGER PRIMARY KEY,
  filename_id INTEGER NOT NULL,
  class_name VARCHAR(30),
  bbox_left REAL,
  bbox_right REAL,
  bbox_bottom REAL,
  bbox_top REAL,
  FOREIGN KEY (filename_id) REFERENCES filenames (id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
);

COMMIT;

PRAGMA foreign_keys=on;

--purge database
VACUUM;
