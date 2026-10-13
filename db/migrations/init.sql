CREATE TABLE IF NOT EXISTS students (
    student_name  TEXT PRIMARY KEY,
    leetid        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS storage (
    stat_date            DATE      NOT NULL,
    student_name         TEXT      NOT NULL,
    solved_all           INTEGER   NOT NULL,
    solved_easy          INTEGER   NOT NULL,
    solved_medium        INTEGER   NOT NULL,
    solved_hard          INTEGER   NOT NULL,
    last_submission_time TIMESTAMP NOT NULL,

    PRIMARY KEY (stat_date, student_name)
);