{{ config(order_by='(RecordDate)', engine='MergeTree()', materialized='table') }}


with events_geography as (
    SELECT *
    FROM (
        SELECT {{ source('gdelt', 'events') }}.GLOBALEVENTID as Id,
        {{ source('gdelt', 'events') }}.SQLDATE as RecordDate,
        {{ source('gdelt', 'events') }}.GoldsteinScale as GoldsteinScale,
        {{ source('gdelt', 'events') }}.AvgTone as AvgTone,
        {{ source('gdelt', 'events') }}.ActionGeo_Lat as ActionGeo_Lat,
        {{ source('gdelt', 'events') }}.ActionGeo_Long as ActionGeo_Long,
        Actor1_CountryName.Label as Actor1_Country,
        Actor2_CountryName.Label as Actor2_Country,
        CameoEvent.EventDescription as EventDescription,
        CameoType.Label as EventType
        FROM {{ source('gdelt', 'events') }}
        LEFT OUTER JOIN {{ source('gdelt', 'cameo_country') }} as Actor1_CountryName ON {{ source('gdelt', 'events') }}.Actor1CountryCode = Actor1_CountryName.Code
        LEFT OUTER JOIN {{ source('gdelt', 'cameo_country') }} as Actor2_CountryName ON {{ source('gdelt', 'events') }}.Actor2CountryCode = Actor2_CountryName.Code
        LEFT OUTER JOIN {{ source('gdelt', 'cameo_eventcodes') }} as CameoEvent ON {{ source('gdelt', 'events') }}.EventCode = CameoEvent.CameoEventCode
        LEFT OUTER JOIN {{ source('gdelt', 'cameo_type') }} as CameoType ON {{ source('gdelt', 'events') }}.Actor1Type1Code = CameoType.Code
        WHERE isNotNull(ActionGeo_Lat)  And  isNotNull(ActionGeo_Long) AND isNotNull(Actor1CountryCode)
    )
)

SELECT *
FROM events_geography
