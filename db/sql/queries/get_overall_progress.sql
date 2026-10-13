SELECT
	student_name                            AS "Student Name",
	MAX(stat_date)     - MIN(stat_date)     AS Days,
    MAX(solved_all)    - MIN(solved_all)    AS Total,
	MAX(solved_easy)   - MIN(solved_easy)   AS Easy,
	MAX(solved_medium) - MIN(solved_medium) AS Medium,
	MAX(solved_hard)   - MIN(solved_hard)   AS Hard
FROM {table_name}
GROUP BY student_name
ORDER BY student_name;