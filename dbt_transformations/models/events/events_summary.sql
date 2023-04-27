{{ config(materialized='view') }}


with events_summary as (
    SELECT Id,
        RecordDate 
        IsRootEvent,
        EventCode,
        EventBaseCode,
        GoldsteinScale,
        NumMentions,
        NumSources,
        NumArticles,
        AvgTone,
        ActionGeo_Lat,
        ActionGeo_Long
    FROM (
        SELECT {{ source('gdelt', 'events') }}.GLOBALEVENTID as Id,
        {{ source('gdelt', 'events') }}.SQLDATE as RecordDate,
        {{ source('gdelt', 'events') }}.IsRootEvent,
        {{ source('gdelt', 'events') }}.EventCode,
        {{ source('gdelt', 'events') }}.EventBaseCode,
        {{ source('gdelt', 'events') }}.GoldsteinScale,
        {{ source('gdelt', 'events') }}.NumMentions,
        {{ source('gdelt', 'events') }}.NumSources,
        {{ source('gdelt', 'events') }}.NumArticles,
        {{ source('gdelt', 'events') }}.AvgTone,
        {{ source('gdelt', 'events') }}.ActionGeo_Lat,
        {{ source('gdelt', 'events') }}.ActionGeo_Long
        FROM {{ source('gdelt', 'events') }}
    )
)

SELECT *
FROM events_summary
