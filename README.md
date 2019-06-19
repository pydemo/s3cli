# s3cli
Preview gz S3 files in shell/cli interface.


## Provide bucket name

```
host:/home/user/s3cli $ ~/python3/bin/python3 main.py
Provide bucket name.
```

## Cli entry


```
host:/home/user/s3cli $ ~/python3/bin/python3 main.py my_bucket_name
S3>
```

## Preview compressed file on AWS S3

```
S3> racct/DY_Position_SD/file_0_100.2019-06-17.13_39_12.IQ.csv.gz 45

+----+--------------------+-------+----------+----------+------------+--------------------------------+-----------+-------------+-------------+--------+----
| ## | Col_1              | Col_2 | Col_3    | Col_4    | Col_5      | Col_6                          | Col_7     | Col_8       | Col_9       | Col_10 | Col
+----+--------------------+-------+----------+----------+------------+--------------------------------+-----------+-------------+-------------+--------+----
| 1  | TEST-FUT-TEST      | JPY   | TEST   | FUTURES  | TEST-JPAE | TEST 10YR BOND TEST MAR04     | 0.0 | 0.0         | 0.0         | LONG   |
| 2  | TEST-FUT-TEST      | JPY   | TEST   | FUTURES  | TEST-JPAE | TEST 10YR BOND TEST MAR04     | 0.0 | 0.0         | 0.0         | LONG   |
| 3  | TEST-FUT-TEST      | JPY   | TEST   | FUTURES  | TEST-SPAE | TEST NIKKEI 225 TEST MAR04     | 0.0 | 0.0         | 0.0         | LONG   |
...
...
...
| 43 | TEST-OPS-TEST      | USD   | TEST     | CURRENCY | CAD.C-TEST | CANADIAN TEST                | 0.0       | 0.0         | 0.0         | LONG   | 0.0
| 44 | TEST-OPS-TEST      | USD   | TEST     | CURRENCY | CAD.C-TEST | CANADIAN TEST                | 0.0       | 0.0         | 0.0         | LONG   | 0.0
| 45 | TEST-OPS-TEST      | USD   | TEST     | CURRENCY | CAD.C-TEST | CANADIAN TEST                | 0.0       | 0.0         | 0.0         | LONG   | 0.0


```


