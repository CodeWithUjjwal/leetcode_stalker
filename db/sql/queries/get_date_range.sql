WITH ordered AS (
  SELECT
    stat_date,
    stat_date - (ROW_NUMBER() OVER (ORDER BY stat_date) * INTERVAL '1 day') AS grp
  FROM (SELECT DISTINCT stat_date FROM {table_name}) AS d
),
groups AS (
  SELECT
    MIN(stat_date) AS range_start,
    MAX(stat_date) AS range_end
  FROM ordered
  GROUP BY grp
)
SELECT
  CASE
    WHEN range_start = range_end THEN range_start::text
    ELSE range_start || ' to ' || range_end
  END AS "Date Ranges"
FROM groups
ORDER BY range_start;