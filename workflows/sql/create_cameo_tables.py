
create_cameo_type_script = """
CREATE TABLE IF NOT EXISTS cameo_type (
  Code String,
  Label String
) ENGINE = MergeTree()
ORDER BY (Code);
"""


create_cameo_religion_script = """
CREATE TABLE IF NOT EXISTS cameo_religion (
  Code String,
  Label String,
) ENGINE = MergeTree()
ORDER BY (Code);
"""

create_cameo_knowngroup_script = """
CREATE TABLE IF NOT EXISTS cameo_knowngroup (
  Code String,
  Label String
) ENGINE = MergeTree()
ORDER BY (Code);
"""


create_cameo_goldsteinscale_script = """
CREATE TABLE IF NOT EXISTS cameo_goldsteinscale (
  CameoEventCode String,
  GoldsteinScale String
) ENGINE = MergeTree()
ORDER BY (CameoEventCode);
"""


create_cameo_eventcodes_script = """
CREATE TABLE IF NOT EXISTS cameo_eventcodes (
  CameoEventCode String,
  EventDescription String
) ENGINE = MergeTree()
ORDER BY (CameoEventCode);
"""



create_cameo_ethnic_script = """
CREATE TABLE IF NOT EXISTS cameo_ethnic (
  Code String,
  Label String,
) ENGINE = MergeTree()
ORDER BY (Code);
"""



create_cameo_country_script = """
CREATE TABLE IF NOT EXISTS cameo_country (
  Code String,
  Label String,
) ENGINE = MergeTree()
ORDER BY (Code);
"""

create_cameo_fipscountry_script = """
CREATE TABLE IF NOT EXISTS cameo_fipscountry (
  Code String,
  Label String,
) ENGINE = MergeTree()
ORDER BY (Code);
"""
