INSERT INTO mentions
SELECT *
FROM s3('http://10.49.0.2:39191/gdelt/cameo/country/*.parquet')
