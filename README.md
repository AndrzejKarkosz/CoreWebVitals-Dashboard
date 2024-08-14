### About project:
This dashboard enables the analysis of web page performance in terms of key performance metrics, identification of areas needing improvement, 
and monitoring of visual stability and response speed of web pages.
The dashboard was designed using the native Google Analytics 4 connector and Google Cloud Platform Big Query database. 
In order to implement the collection of information on the metrics used in the project, the necessary changes to the site's data layer must be implemented.
The following link elaborates on the individual steps: https://web.dev/articles/vitals?hl=pl

### Why Two approaches?
Data Transfer from GA4 to big query has a maximum number of events possible for export, which is 1 million events. Data Transfer is a good solution for small sites where the number of events does not exceed the specified limit. 
For sites where the total number of events for all 3 indicators is more than 1 million, it is recommended to use the API request. This involves setting up the environment and installing the necessary packages, but it allows you to maintain data integrity.

#### Content of the project:
The project contains 2 project folders and dashboard presentation file: 
    
    Core Web Vitals  Data Transfer (SQL)
    Core Web Vitals  API (Python)
    Dashboard.pdf - contains quick how Core Web Vitals looks like

Core Web Vitals API (Python) contains exactly 3 files:
    ETL script to Extract CLS, INP, LCP data from GA4 API, Transform data into prefferable shape and Load data into Big Query SQL table:
    
    Core_Web_Vitals_CLS_ETL.py
    Core_Web_Vitals_INP_ETL.py 
    Core_Web_Vitals_LCP_ETL.py
    
Core Web Vitals Data Transfer (SQL) contains exactly 4 files:

    CoreWebVitals_manual.pdf - step by step instruction how to connect data from GA4 to Big Query Database
    CWV_CLS.sql - CLS Indicator aggregation query, to create CLS data table using SQL.
    CWV_INP.sql - INP Indicator aggregation query, to create INP data table using SQL.
    CWV_LCP.sql - LCP Indicator aggregation query, to create LCP data table using SQL. 

### Built with: 
Poniżej zostały wyodrębnione technologie zastosowane w przygotowaniu narzędzia Core Web Vitals dashboard.

    - Google Analytics 4
    - Big Query (SQL)
    - Python
    - Looker Studio

            
### Dashboard Description

#### Page 1: Overview
The first page of the dashboard provides a general overview of key performance metrics for web pages, known as Core Web Vitals. These metrics include:

    LCP (Largest Contentful Paint) - the loading time of the largest content element visible on the page.
    INP (Interaction to Next Paint) - the response time to user interactions.
    CLS (Cumulative Layout Shift) - the visual stability of the page during its loading.

Each of these metrics is presented with average values over different periods and distribution of ratings (GOOD, NEEDS IMPROVEMENT, POOR).

#### Page 2: LCP Details
The second page focuses on detailed data regarding LCP:

    Average LCP over time - a line chart showing the changes in LCP values over the days.
    LCP Ratings Statistics - a table with the number of pages, events, and average LCP for each rating category.
    Average LCP by Device - a chart showing the differences in LCP values depending on the type of device (desktop, mobile, tablet).
    Number of LCP events over time - a column chart showing number of LCP events over time.
    LCP Page table - a table with all metrics and rating based on element on page.

#### Page 3: INP Details
The third page contains detailed information regarding INP:

    Average INP over time - a line chart showing changes in average INP on different days.
    Average INP by Device - a chart showing the differences in INP values depending on the type of device (desktop, mobile, tablet).
    INP Ratings Statistics - a table with the breakdown by rating categories, showing the number of pages, events, and average INP.
    Number of  INP events over time - a column chart showing number of INP events over time.
    INP Page table - a table with all metrics and rating based on element on page.

#### Page 4: CLS Details
The fourth page contains details regarding CLS:

    Average CLS over time - a line chart showing average CLS values over the days.
    Average CLS by Device - a chart showing the differences in CLS values depending on the type of device (desktop, mobile, tablet).
    CLS Ratings Statistics - a table showing the number of pages, events, and average CLS by rating category.
    Number of CLS events over time - a column chart showing number of CLS events over time.
    CLS Page table - a table with all metrics and rating based on element on page.
    







