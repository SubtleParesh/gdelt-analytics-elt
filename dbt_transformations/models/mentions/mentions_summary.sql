{{ config(materialized='view') }}


with mentions_summary as (
    SELECT Id,
        RecordDate,
        MentionType,
        Confidence
    FROM (
        SELECT {{ source('gdelt', 'mentions') }}.GLOBALEVENTID as Id,
        {{ source('gdelt', 'mentions') }}.EventTimeDate as RecordDate,
        {{ source('gdelt', 'mentions') }}.MentionType,
        {{ source('gdelt', 'mentions') }}.Confidence
        FROM {{ source('gdelt', 'mentions') }}
    )
)

SELECT * FROM mentions_summary
