CREATE TABLE IF NOT EXISTS mentions (
  GLOBALEVENTID UInt64,
  EventTimeDate DateTime,
  MentionTimeDate DateTime,
  MentionType Int64,
  MentionSourceName Nullable(String),
  MentionIdentifier Nullable(String),
  SentenceID Nullable(Int64),
  Actor1CharOffset Nullable(Int64),
  Actor2CharOffset Nullable(Int64),
  ActionCharOffset Nullable(Int64),
  InRawText Nullable(Int64),
  Confidence Nullable(Int64),
  MentionDocLen Nullable(Int64),
  MentionDocTone Nullable(Float64),
  MentionDocTranslationInfo Nullable(String),
  Extras Nullable(String)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(EventTimeDate)
ORDER BY (EventTimeDate, GLOBALEVENTID);