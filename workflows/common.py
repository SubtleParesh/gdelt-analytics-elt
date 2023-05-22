import os
import warnings
from dataclasses import dataclass, field
from enum import Enum

from hydra import compose, initialize

warnings.simplefilter(action="ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

DataFileType = Enum("DatafileType", "Event Mentions GKG")

data_url_prefix = "http://data.gdeltproject.org/gdeltv2/"

config_path = "./"


@dataclass
class GdeltRawFileExtension:
    export = ".export.csv.zip"
    mentions = ".mentions.csv.zip"
    gkg = ".gkg.csv.zip"


class Table:
    events = "events"
    mentions = "mentions"
    cameo_type = "cameo_type"
    cameo_religion = "cameo_religion"
    cameo_knowngroup = "cameo_knowngroup"
    cameo_goldsteinscale = "cameo_goldsteinscale"
    cameo_eventcodes = "cameo_eventcodes"
    cameo_ethnic = "cameo_ethnic"
    cameo_country = "cameo_country"
    cameo_fipscountry = "cameo_fipscountry"

    def create_gdelt_events_table(self):
        return self._read_file("./workflows/sql/create_events_table.sql")

    def create_gdelt_mentions_table(self):
        return self._read_file("./workflows/sql/create_mentions_table.sql")

    def create_gdelt_gkg_table(self):
        return self._read_file("./workflows/sql/create_gkg_table.sql")

    def create_gdelt_cameo_tables(self):
        return self._read_file("./workflows/sql/create_cameo_tables.sql")

    def _read_file(self, filename):
        with open(filename, "r") as file:
            return file.read()


@dataclass
class DaskConfiguration:
    n_workers: int = 1
    threads_per_worker: int = 1
    memory_limit: str = "2GiB"
    processes: bool = True


@dataclass
class ServiceConfiguration:
    username: str = "admin"
    password: str = "password"
    ip_address: str = "127.0.0.1"
    port: str = "8080"


@dataclass
class Configuration:
    ip_address: str
    dask: DaskConfiguration
    clickhouse: ServiceConfiguration = field(default_factory=ServiceConfiguration)
    minio: ServiceConfiguration = field(default_factory=ServiceConfiguration)


initialize(config_path="../")
config: Configuration
if os.getenv("ENV") == "prod":
    cfg = compose(config_name="config.server.yaml")
    config = Configuration(**cfg.config)
else:
    cfg = compose(config_name="config.local.yaml")
    config = Configuration(**cfg.config)
