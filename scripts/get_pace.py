import os
import sys
import xarray as xr
import fsspec
import requests
from itertools import count
from collections import defaultdict
import re

def get_pace_hkt_entries(t_start, t_end):
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
        yield from new_entries
        if len(new_entries) < batch_size:
            break

def load_pace_track(url):
    return xr.open_dataset(fsspec.open_local("simplecache::" + url), engine="netcdf4", group="navigation_data")[["orb_time", "orb_lon", "orb_lat", "orb_alt"]].rename({"orb_records": "time", "orb_time": "time", "orb_lon": "lon", "orb_lat": "lat", "orb_alt": "alt"})

def get_pace_track(t_start, t_end):
    entries = list(get_pace_hkt_entries(t_start, t_end))
    urls = [e["links"][0]["href"] for e in entries]
    dss = [load_pace_track(url) for url in urls]
    return xr.concat(dss, dim="time")

def url2filename(url):
    return "parts/" + url.split("/")[-1].replace("HKT", "TRACK")

def main():
    from datetime import date, datetime, timedelta, UTC
    import logging
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url")
    parser.add_argument("-d", "--date", type=date.fromisoformat)
    parser.add_argument("--start", type=datetime.fromisoformat)
    parser.add_argument("--stop", type=datetime.fromisoformat)
    parser.add_argument("-o", "--output")
    parser.add_argument("-m", "--makefile", action="store_true", default=False, help="generate Makefile")
    args = parser.parse_args()

    if args.date:
        start = datetime(args.date.year, args.date.month, args.date.day, tzinfo=UTC)
        stop_date = args.date + timedelta(days=1)
        stop = datetime(stop_date.year, stop_date.month, stop_date.day, tzinfo=UTC)
    elif args.start and args.stop:
        start = args.start
        stop = args.stop
    else:
        start = stop = None

    if args.output:
        if start and stop:
            logging.basicConfig(level=logging.DEBUG)
            pace_track = get_pace_track(start, stop)
        elif args.url:
            pace_track = load_pace_track(args.url)
        pace_track.to_netcdf(args.output)
    else:
        if start and stop:
            urls = [e["links"][0]["href"] for e in get_pace_hkt_entries(start, stop)]
        else:
            urls = [args.url]

        if args.makefile:
            outfile = sys.stdout

            part_re = re.compile(r"(.+\.[0-9]{8})T[0-9]{6}.TRACK.nc")
            files_by_day = defaultdict(list)
            for url in urls:
                partfile = url2filename(url)
                if m := part_re.match(partfile):
                    dayfile = m.group(1) + ".DAY.TRACK.nc"

                    files_by_day[dayfile].append(partfile)

            outfile.write("ALL_PARTS = " + " ".join(map(url2filename, urls)) + "\n\n")
            outfile.write("ALL_DAY_PARTS = " + " ".join(files_by_day) + "\n\n")

            outfile.write("all: PACE.TRACK.nc\n\n.PHONY: all\n\n")

            for url in urls:
                outfile.write(f"{url2filename(url)}:\n\tpython3 {sys.argv[0]} -u '{url}' -o $@\n\n")

            join_pace = os.path.join(os.path.dirname(sys.argv[0]), "join_pace.py")

            for dayfile, partfiles in files_by_day.items():
                partfiles = list(sorted(partfiles))
                outfile.write(f"{dayfile}: {' '.join(partfiles)}\n\tpython3 {join_pace} -o $@ -i $^\n\n")

            outfile.write(f"PACE.TRACK.nc: {' '.join(sorted(files_by_day))}\n\tpython3 {join_pace} -o $@ -i $^\n\n")

        else:
            for url in urls:
                print(url)

if __name__ == "__main__":
    exit(main())
