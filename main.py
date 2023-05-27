from datetime import datetime

from workflows.main_flow import main_flow

if __name__ == "__main__":
    master_csv_list_url = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"
    last_15mins_csv_list_url = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

    # Change this value based upon your bandwidth and time.
    # Prefer first run of year 2023 which should take around 15mins to 30mins based upon you bandwidth
    min_date = "1/5/2023"
    config_file = "config.local.yaml"

    main_flow(
        master_csv_list_url=master_csv_list_url,
        min_date=min_date,
        max_datetime=datetime(2023, 7, 1),
        config_file=config_file,
        clean_start=True,
    )
