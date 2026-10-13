INSERT INTO {table_name}
(
    stat_date,
    student_name,
    solved_all,
    solved_easy,
    solved_medium,
    solved_hard,
    last_submission_time
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (stat_date, student_name)
DO UPDATE SET
    solved_all = EXCLUDED.solved_all,
    solved_easy = EXCLUDED.solved_easy,
    solved_medium = EXCLUDED.solved_medium,
    solved_hard = EXCLUDED.solved_hard,
    last_submission_time = EXCLUDED.last_submission_time;