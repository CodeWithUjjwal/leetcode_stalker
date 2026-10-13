SELECT
	student_name AS "Student Name",
	COUNT(*)     AS Entries
FROM {table_name}
GROUP BY student_name
ORDER BY student_name;