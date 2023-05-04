import warnings
from enum import Enum

warnings.simplefilter(action="ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

DataFileType = Enum("DatafileType", "Event Mentions GKG")

# Change Ip Address in case of Using VM , Defaulted for docker based development
# Do not use 127.0.0.1, mostly it be 192.*.*.* on your local machine
ip_address = "10.0.2.4"

export_data_file_type_suffix = ".export.csv.zip"
mentions_data_file_type_suffix = ".mentions.csv.zip"
gkg_data_file_type_suffix = ".gkg.csv.zip"

events_table_name = "events"
mentions_table_name = "mentions"

data_url_prefix = "http://data.gdeltproject.org/gdeltv2/"

cameo_type = "cameo_type"
cameo_religion = "cameo_religion"
cameo_knowngroup = "cameo_knowngroup"
cameo_goldsteinscale = "cameo_goldsteinscale"
cameo_eventcodes = "cameo_eventcodes"
cameo_ethnic = "cameo_ethnic"
cameo_country = "cameo_country"
cameo_fipscountry = "cameo_fipscountry"


def read_file(filename):
    with open(filename, "r") as file:
        return file.read()

def create_gdelt_events_table() :
    return read_file("./workflows/sql/create_events_table.sql")
    
def create_gdelt_mentions_table() :
    return read_file("./workflows/sql/create_mentions_table.sql")

def create_gdelt_gkg_table() :
    return read_file("./workflows/sql/create_gkg_table.sql")

def create_gdelt_cameo_tables() :
    return read_file("./workflows/sql/create_cameo_tables.sql")