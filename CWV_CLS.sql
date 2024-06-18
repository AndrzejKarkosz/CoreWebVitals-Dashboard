-- Creating query to filter highest value of indicator in event (metrid_id)
WITH web_vitals_events AS (
    SELECT * FROM (
        SELECT *, ROW_NUMBER() OVER (
        PARTITION BY (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'metric_id')
        ORDER BY (SELECT COALESCE(value.double_value, value.int_value) FROM UNNEST(event_params) WHERE key = 'metric_value') DESC
      ) AS is_last_received_value
    FROM `core-web-vitals-424311.analytics_300253194.events_*`
    WHERE (event_name = 'CLS'))),

-- Creating main query - all fields that we want to analyze in dashboard
    Main_query AS(
    SELECT
        PARSE_DATE("%Y%m%d",event_date) as event_date,
        event_name,
        (SELECT COALESCE(value.double_value, value.int_value) FROM UNNEST(event_params) WHERE key = "metric_value") AS metric_value,
        (SELECT COALESCE(value.double_value, value.int_value) FROM UNNEST(event_params) WHERE key = "largest_shift_time") AS largest_shift_time,
        (SELECT COALESCE(value.string_value) FROM UNNEST(event_params) WHERE key = "metric_id") AS metric_id,
        (SELECT COALESCE(value.string_value) FROM UNNEST(event_params) WHERE key = "largest_shift_target") AS largest_shift_target,
        (SELECT COALESCE(value.string_value) FROM UNNEST(event_params) WHERE key = "page_location_clean") AS page_location_clean,
        device.web_info.browser as browser,
        device.category as device,
        traffic_source.medium AS source_medium,
        traffic_source.source AS search_engine
    FROM 
      web_vitals_events
    WHERE is_last_received_value = 1
    ORDER BY is_last_received_value desc
      ),
-- This step is not needed because we already filter highest value of metric_id, but if you want to create query that filters all duplicates, You can use this instead of web_vitals_events
    check_duplicates AS(
        SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY metric_id, CAST(metric_value as string)) AS duplicate_check
        FROM Main_query
      ),
-- Creating the main query logic - Google recommends using the 75th percentile of the data, but due to the size of the site we use the 90th percentile.
      percentile AS(
        SELECT
          event_date,
          event_name,
          page_location_clean,
          APPROX_QUANTILES(metric_value, 100)[offset(90)] as p90
        FROM 
           Main_query
         GROUP BY 1,2,3
        ),

-- Merging value of daily percentile value for given page to actual value
    merged_cls as (
      SELECT 
    main.*,
    per.p90
    FROM Main_query as main
    LEFT JOIN percentile as per
    ON main.event_date = per.event_date
    AND main.event_name = per.event_name
    AND main.page_location_clean = per.page_location_clean
    WHERE main.metric_value <= per.p90
    )
-- Creating main table for dashboard
    SELECT 
        event_date,
        event_name, 
        metric_id,
        largest_shift_target,
        page_location_clean,
        browser,
        device,
        source_medium,
        search_engine,
        ROUND(SUM(metric_value)/1000,3) AS metric_value,
        ROUND(SUM(largest_shift_time)/1000,3) as largest_shift_time,
      FROM merged_cls
      GROUP BY 1,2,3,4,5,6,7,8,9


