import xarray as xr
import fsspec
import requests
from itertools import count

def get_pace_track(t_start, t_end):
    entries = []
    batch_size = 100
    for i in count(1): 
        headers = {
        "Accept": "application/json, text/plain, */*",
        }
        data = {
            "echo_collection_id": "C2832273136-OB_CLOUD",
            "page_num": i,
            "page_size": batch_size,
            "temporal": f"{t_start:%Y-%m-%dT%H:%M:%S.000Z},{t_end:%Y-%m-%dT%H:%M:%S.000Z}",
            "sort_key": "start_date",
        }
        res = requests.post("https://cmr.earthdata.nasa.gov/search/granules.json", headers=headers, data=data)
        res.raise_for_status()
        content = res.json()
        new_entries = content["feed"]["entry"]
        entries += new_entries
        if len(new_entries) < batch_size:
            break
    urls = ["simplecache::" + e["links"][0]["href"] for e in entries]
    dss = [xr.open_dataset(fsspec.open_local(url), engine="netcdf4", group="navigation_data")[["orb_time", "orb_lon", "orb_lat", "orb_alt"]]
           for url in urls]
    return xr.concat(dss, dim="orb_records").rename({"orb_records": "time", "orb_time": "time", "orb_lon": "lon", "orb_lat": "lat", "orb_alt": "alt"})

def main():
    from datetime import date, datetime, timedelta, UTC
    import logging
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("date", type=date.fromisoformat)
    parser.add_argument("-o", "--output")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    start = datetime(args.date.year, args.date.month, args.date.day, tzinfo=UTC)
    stop_date = args.date + timedelta(days=1)
    stop = datetime(stop_date.year, stop_date.month, stop_date.day, tzinfo=UTC)
    pace_track = get_pace_track(start, stop)

    if args.output:
        pace_track.to_netcdf(args.output)
    else:
        print(pace_track)

if __name__ == "__main__":
    exit(main())
