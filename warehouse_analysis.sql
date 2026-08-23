/*
 * Logistics Warehouse Choke Analysis
 * Submitted by: Anand Raj
 * Tool: DuckDB (Local Execution)
 * Description: Processes nested JSON shipment tracking events to identify
 * bottlenecked courier hubs using historical P90 dwell times and active backlogs.
 */

WITH raw_shipments AS (
    -- Forcing the schema here because letting DuckDB auto-infer crashes 
    -- when some tracking array elements randomly miss the 'location' key.
    SELECT * FROM read_json(
        'dataset.json',
        columns={
            'shipment_id': 'VARCHAR',
            'latest_status': 'VARCHAR',
            'latest_location': 'VARCHAR',
            'deduped_track_details': 'JSON[]'
        }
    )
),

parsed_tracking AS (
    -- Flatten the array and clean up the strings/timestamps
    SELECT 
        shipment_id,
        latest_status,
        latest_location,
        -- Safely extract location (returns NULL if missing) and clean up extra spaces
        TRIM(REGEXP_REPLACE(UPPER(t.event->>'location'), '\s+', ' ', 'g')) AS hub_location,
        
        -- Strip out ' UTC' so strptime can parse the timestamp cleanly
        strptime(REGEXP_REPLACE(t.event->>'ctime', ' UTC$', ''), [
            '%Y-%m-%d %H:%M:%S.%f', 
            '%Y-%m-%d %H:%M:%S'
        ]) AS scan_time
    FROM raw_shipments,
    UNNEST(deduped_track_details) AS t(event)
    WHERE (t.event->>'location') IS NOT NULL 
      AND TRIM(t.event->>'location') != ''
),

transit_times AS (
    -- Calculate how long the parcel stayed at this specific hub
    -- LEAD() peeks at the next chronological scan for the same shipment
    SELECT 
        shipment_id,
        hub_location,
        scan_time AS arrival_time,
        LEAD(scan_time) OVER (PARTITION BY shipment_id ORDER BY scan_time ASC) AS departure_time,
        -- Convert the time difference into hours
        epoch(LEAD(scan_time) OVER (PARTITION BY shipment_id ORDER BY scan_time ASC) - scan_time) / 3600.0 AS dwell_hrs
    FROM parsed_tracking
    WHERE scan_time IS NOT NULL
),

historical_stats AS (
    -- Build benchmark metrics for each warehouse.
    -- P90 is a much better metric than average here to catch tail-end delays.
    SELECT 
        hub_location,
        COUNT(shipment_id) AS total_hops,
        ROUND(AVG(dwell_hrs), 2) AS avg_dwell_hrs,
        ROUND(MEDIAN(dwell_hrs), 2) AS median_dwell_hrs,
        ROUND(QUANTILE_CONT(dwell_hrs, 0.90), 2) AS p90_dwell_hrs
    FROM transit_times
    WHERE dwell_hrs >= 0
    GROUP BY hub_location
),

active_backlog AS (
    -- Find parcels that are currently stuck based on the assignment cutoff date
    SELECT 
        TRIM(REGEXP_REPLACE(UPPER(latest_location::VARCHAR), '\s+', ' ', 'g')) AS hub_location,
        COUNT(DISTINCT shipment_id) AS pending_shipments,
        ROUND(AVG(epoch(TIMESTAMP '2023-10-07 23:59:59' - last_scan) / 3600.0), 2) AS avg_delay_hrs
    FROM (
        SELECT 
            shipment_id,
            latest_status,
            latest_location,
            MAX(scan_time) AS last_scan
        FROM parsed_tracking
        -- Exclude parcels that already reached the customer or got cancelled
        WHERE latest_status NOT IN ('Delivered', 'RTO Delivered', 'Cancelled')
        GROUP BY shipment_id, latest_status, latest_location
    )
    -- A parcel is flagged as 'stuck' if it hasn't moved in 48 hours relative to Oct 7
    WHERE epoch(TIMESTAMP '2023-10-07 23:59:59' - last_scan) / 3600.0 > 48.0
    GROUP BY hub_location
),

final_classification AS (
    -- Bring historical stats and active backlogs together to flag choked hubs
    SELECT 
        COALESCE(h.hub_location, b.hub_location) AS courier_warehouse,
        COALESCE(b.pending_shipments, 0) AS active_stuck_shipments,
        COALESCE(b.avg_delay_hrs, 0.0) AS avg_hours_stuck,
        COALESCE(h.total_hops, 0) AS historical_volume,
        COALESCE(h.median_dwell_hrs, 0.0) AS median_dwell_hours,
        COALESCE(h.p90_dwell_hrs, 0.0) AS p90_dwell_hours,
        
        -- Choke logic: High backlog OR historically terrible P90 OR aging stuck parcels
        CASE 
            WHEN COALESCE(b.pending_shipments, 0) >= 5 
              OR COALESCE(h.p90_dwell_hrs, 0.0) > 48.0 
              OR (COALESCE(b.pending_shipments, 0) >= 2 AND COALESCE(b.avg_delay_hrs, 0.0) > 72.0)
            THEN 'Prioritize for Clearing'
            ELSE 'Ignore'
        END AS priority_category
        
    FROM historical_stats h
    FULL OUTER JOIN active_backlog b 
      ON h.hub_location = b.hub_location
    WHERE COALESCE(h.hub_location, b.hub_location) != ''
)

-- Final select with sorting to put the worst offenders at the top
SELECT 
    courier_warehouse,
    active_stuck_shipments,
    avg_hours_stuck,
    median_dwell_hours,
    p90_dwell_hours,
    priority_category
FROM final_classification
ORDER BY 
    CASE WHEN priority_category = 'Prioritize for Clearing' THEN 0 ELSE 1 END,
    active_stuck_shipments DESC, 
    p90_dwell_hours DESC;