
create_cameo_type_script = """
CREATE DICTIONARY IF NOT EXISTS cameo_type_dict (
  Code String,
  Label String
) 
PRIMARY KEY Code
SOURCE(CLICKHOUSE(TABLE 'gdelt.cameo_type'))
LIFETIME(MIN 0 MAX 0)
-- COMPLEX_KEY_HASHED_ARRAY layout data is used as we have very few number of rows, one can used hashed or other options if too many rows present in data
LAYOUT(COMPLEX_KEY_HASHED_ARRAY())
"""


create_cameo_religion_script = """
CREATE DICTIONARY IF NOT EXISTS cameo_religion_dict (
  Code String,
  Label String
)
PRIMARY KEY Code
SOURCE(CLICKHOUSE(TABLE 'gdelt.cameo_religion'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(COMPLEX_KEY_HASHED_ARRAY())
"""

create_cameo_knowngroup_script = """
CREATE DICTIONARY IF NOT EXISTS cameo_knowngroup_dict (
  Code String,
  Label String
)
PRIMARY KEY Code
SOURCE(CLICKHOUSE(TABLE 'gdelt.cameo_knowngroup'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(COMPLEX_KEY_HASHED_ARRAY())
"""


create_cameo_goldsteinscale_script = """
CREATE DICTIONARY IF NOT EXISTS cameo_goldsteinscale_dict (
  CameoEventCode String,
  GoldsteinScale String
)
PRIMARY KEY CameoEventCode
SOURCE(CLICKHOUSE(TABLE 'gdelt.cameo_goldsteinscale'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(COMPLEX_KEY_HASHED_ARRAY())
"""


create_cameo_eventcodes_script = """
CREATE DICTIONARY IF NOT EXISTS cameo_eventcodes_dict (
  CameoEventCode String,
  EventDescription String
)
PRIMARY KEY CameoEventCode
SOURCE(CLICKHOUSE(TABLE 'gdelt.cameo_eventcodes'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(COMPLEX_KEY_HASHED_ARRAY())
"""



create_cameo_ethnic_script = """
CREATE DICTIONARY IF NOT EXISTS cameo_ethnic_dict (
  Code String,
  Label String
)
PRIMARY KEY Code
SOURCE(CLICKHOUSE(TABLE 'gdelt.cameo_ethnic'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(COMPLEX_KEY_HASHED_ARRAY())
"""



create_cameo_country_script = """
CREATE DICTIONARY IF NOT EXISTS cameo_country_dict (
  Code String,
  Label String
)
PRIMARY KEY Code
SOURCE(CLICKHOUSE(TABLE 'gdelt.cameo_country'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(COMPLEX_KEY_HASHED_ARRAY())
"""

create_cameo_fipscountry_script = """
CREATE DICTIONARY IF NOT EXISTS cameo_fipscountry_dict (
  Code String,
  Label String
)
PRIMARY KEY Code
SOURCE(CLICKHOUSE(TABLE 'gdelt.cameo_fipscountry'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(COMPLEX_KEY_HASHED_ARRAY())
"""
