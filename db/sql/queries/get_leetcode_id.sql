SELECT
	student_name                                   AS "Student Name",
	CONCAT('https://leetcode.com/u/', leetid, '/') AS "Leetcode Profile Link"
FROM {table_name}
WHERE student_name = %s;