SELECT
    stat_date            AS "Date",
    student_name         AS "Student Name",
    solved_all           AS "Total",
	solved_easy          AS "Easy",
	solved_medium        AS "Medium",
	solved_hard          AS "Hard",
	last_submission_time AS "Last Submission Time"
FROM {table_name}
WHERE stat_date = %s;