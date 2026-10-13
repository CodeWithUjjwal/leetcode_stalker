WITH ranked_progress AS (
	SELECT
	    student_name,
	    solved_all,
		solved_easy,
		solved_medium,
		solved_hard,
		ROW_NUMBER() OVER (PARTITION BY student_name ORDER BY stat_date DESC) AS rk
	FROM {table_name}
)
SELECT
	student_name                                                                            AS "Student Name",
	MAX(CASE rk WHEN 1 THEN solved_all END)    - MAX(CASE rk WHEN 2 THEN solved_all END)    AS Total,
	MAX(CASE rk WHEN 1 THEN solved_easy END)   - MAX(CASE rk WHEN 2 THEN solved_easy END)   AS Easy,
	MAX(CASE rk WHEN 1 THEN solved_medium END) - MAX(CASE rk WHEN 2 THEN solved_medium END) AS Medium,
	MAX(CASE rk WHEN 1 THEN solved_hard END)   - MAX(CASE rk WHEN 2 THEN solved_hard END)   AS Hard
FROM ranked_progress
WHERE rk <= 2
GROUP BY student_name
ORDER BY student_name;