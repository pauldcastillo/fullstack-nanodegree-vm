Logs Analysis
=============

Code for analyzing news data database.

# Installation and Use

* Follow the directions for installing the Virtual Machine in the main directory, up to navigating back to /vagrant.
* Navigate to /logs_analysis_project/logs-analysis-project/.
* Add the newsdata.sql database.
* Run the following command: `psql -d news -f newsdata.sql`.
* Connect to the datebase: `psql news`.
* Add the below views.
* Disconnect from the datebase.
* Run the following command: `python logs_analysis.py`.

### Views
```
CREATE OR REPLACE VIEW page_views AS
    SELECT reverse(split_part(reverse(path), '/',1)) as slug,count(*) as  views
    FROM log
    WHERE path LIKE '/article/%' AND status = '200 OK'
    GROUP BY path
    ORDER BY views DESC;
```
```
CREATE OR REPLACE VIEW total_logs_per_day AS
    SELECT COUNT(*) AS requests, time::date AS date
    FROM log GROUP BY date;
```
```
CREATE VIEW errors_per_day AS
    SELECT COUNT(status) as errors, time::date AS date
    FROM log
    WHERE status = '404 NOT FOUND' GROUP BY date;
```


### Files Included
```
vagrant
|
|- logs-analysis-project
|    |
|    |- logs_analysis.py
|    |- logs_analysis_output.txt
|    |- README.md
```
