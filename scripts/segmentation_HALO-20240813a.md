---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Flight segmentation HALO-20240813a

```python
import matplotlib
import yaml
import hvplot.xarray
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from navdata import get_navdata_HALO
from utils import *
```

```python
platform = "HALO"
flight_id = "HALO-20240813a"
```

## Loading data
### Get HALO position and attitude

```python
ds = get_navdata_HALO(flight_id)
```

### Get dropsonde launch times

```python
drops = get_sondes_l1(flight_id)
ds_drops = ds.sel(time=drops, method="nearest")
```

### Defining takeoff and landing
On Barbads, the airport runway plus bumps make HALO move between 7.8-8m above WGS84, on Sal between 88.2-88.4m above WGS84. We therefore define the flight time such that altitude must be above 9m on Barbados and 90m on Sal.

```python
takeoff, landing, duration = get_takeoff_landing(flight_id, ds)
print("Takeoff time: " + str(takeoff))
print("Landing time: " + str(landing))
print(f"Flight duration: {int(duration / 60)}:{int(duration % 60)}")
```

### Get EC track and EC meeting point

```python
ec_track = get_ec_track(flight_id, ds)
dist_ec, t_ec = get_overpass_track(ds, ec_track)
```

### Get PACE track
**loading the PACE track for the first time takes 6-7 minutes!**
Might be worth only if the flight report states a PACE coordination.

<!-- #raw -->
load_pace = False

if load_pace:
    from get_pace import get_pace_track
    _pace_track = get_pace_track(to_dt(takeoff), to_dt(landing))
    
    pace_track = _pace_track.where(
            (_pace_track.lat > ds.lat.min()-2) & (_pace_track.lat < ds.lat.max()+2) &
            (_pace_track.lon > ds.lon.min()-2) & (_pace_track.lon < ds.lon.max()+2),
            drop=True)
else:
    pace_track = None
<!-- #endraw -->

### Get METEOR track
select maybe only the track from the respective flight day

```python
from orcestra.meteor import get_meteor_track

meteor_track = get_meteor_track().sel(time=slice(takeoff, landing))
```

## Overview plot: HALO track, EC meeting point, and dropsonde locations

```python
plt.scatter(ds.lon.sel(time=takeoff, method="nearest"), ds.lat.sel(time=takeoff, method="nearest"), marker="*", label="SAL")
plt.plot(ds.lon.sel(time=slice(takeoff, landing)), ds.lat.sel(time=slice(takeoff, landing)), label="HALO track")
plt.scatter(ds_drops.lon, ds_drops.lat, s=10, c="k", label="dropsondes")
plt.plot(ec_track.lon, ec_track.lat, c='C1', ls='dotted')
plt.plot(ds.lon.sel(time=t_ec, method="nearest"), ds.lat.sel(time=t_ec, method="nearest"), marker="*", ls=":", label="EC meeting point")
try:
    plt.plot(pace_track.lon, pace_track.lat, c="C2", ls=":", label="PACE track")
except NameError:
    pass
if meteor_track.time.size != 0:
    plt.plot(meteor_track.lon, meteor_track.lat, c="C4", ls="-", label="METEOR track")
plt.xlabel("longitude / °")
plt.ylabel("latitude / °")
plt.legend();
```

***NOTE: BAHAMAS data seems to miss the last bit of the flight before landing. Also obvious from the altitude plot blow.***


## Interactive plots

```python
ds["alt"].hvplot()
```

```python
ds["roll"].hvplot()
```

```python
ds["heading"].hvplot()
```

## Segments

defined as a tuple of time slice (`start`, `end`) , segment `kind`, `name`, `remarks`.

* in case of irregularities within a circle, 1 sec before the first and after the last sonde are chosen as start and end times
* use the list of `remarks` to state any deviations, also with respective times

Alternatively, you can also define the segments as dictionaries which also allows to add further attributes to single segments, e.g. a `radius` to a `circle` segment. At the end of the following code block all segments will be normalized by the `parse_segments` function.

```python
# 2 legs heading north to the EC track
sl0 = (
    slice("2024-08-13T14:18:23", "2024-08-13T14:44:00"),
    ["straight_leg", "ascent"],
    "ascending ferry",
)
sl1 = (
    slice("2024-08-13T14:44:00", "2024-08-13T14:56:37"),
    ["straight_leg"],
    "ferry constant altitude",
)

# EC track time: full track south, won't be saved to the YAML file
ec = (
    slice("2024-08-13T15:04:14", "2024-08-13T17:13:36"),
    ["straight_leg", "ec_track"],
    "full EC track",
    ["several height level changes, for details, see subsegments"]
)

# EC track split into sub-segments
ec1a = (
    slice("2024-08-13T15:04:14", "2024-08-13T15:18:00"),
    ["straight_leg", "ec_track"],
    "southward EC track",
)
# in between those two segments there was a holding pattern to wait for EC
# followed by the decision to descent to lower flight altitude befor meeting EC
ec1b = (
    slice("2024-08-13T15:28:11", "2024-08-13T15:32:18"),
    ["straight_leg", "descent", "ec_track"],
    "descent to FL360",
)
# meeting EC on a low leg due to cirrus clouds
ec1 = (
    slice("2024-08-13T15:32:18", "2024-08-13T15:52:22"),
    ["straight_leg", "ec_track"],
    "EC track low leg",
    ["intentional low flight altitude to be below cirrus clouds", "includes EC underpass"]
)
ec1c = (
    slice("2024-08-13T15:52:22", "2024-08-13T15:57:05"),
    ["straight_leg", "ascent", "ec_track"],
    "ascent to FL410",
)
ec2 = (
    slice("2024-08-13T15:57:05", "2024-08-13T17:01:53"),
    ["straight_leg", "ec_track"],
    "EC track mid leg",
    ["includes one dropsonde launch"],
)
ec2a = (
    slice("2024-08-13T17:01:53", "2024-08-13T17:05:35"),
    ["straight_leg", "ec_track", "ascent"],
    "ascent to FL430",
)
ec3 = (
    slice("2024-08-13T17:05:35", "2024-08-13T17:13:36"),
    ["straight_leg", "ec_track"],
    "EC track high leg",
)

sl_south = (
    slice("2024-08-13T17:16:49", "2024-08-13T17:19:35"),
    ["straight_leg"],
    "straight leg south",
    ["irregularity: spikes with roll angle deviation up to +-3.6 deg"],
)

c1 = (
    slice("2024-08-13 17:21:20", "2024-08-13 18:23:20"),
    ["circle"],
    "circle south",
    ["irregularity: 18:06:02 - 18:12:08 deviation from circle track with roll angle deviations up to +-15 deg due to deep convection"],
)

slc1c2a = (
    slice("2024-08-13T18:28:22", "2024-08-13T18:52:16"),
    ["straight_leg"],
    "leg crossing circle south",
)

slc1c2b = (
    slice("2024-08-13T18:52:16", "2024-08-13T18:57:56"),
    ["straight_leg", "ascent"],
    "ascending leg crossing circle south",
)

slc1c2c = (
    slice("2024-08-13T18:57:56", "2024-08-13T19:12:49"),
    ["straight_leg"],
    "leg to circle 2",
    ["irregularity: turbulence with roll angle deviations up to +-4.5 deg"],
)

c2 = (
    slice("2024-08-13T19:15:37", "2024-08-13T20:13:48"),
    ["circle"],
    "circle mid",
)

slc2c3a = (
    slice("2024-08-13T20:17:49", "2024-08-13T20:27:56"),
    ["straight_leg"],
    "leg1 crossing circle mid",
)

slc2c3b = (
    slice("2024-08-13T20:28:18", "2024-08-13T20:33:12"),
    ["straight_leg"],
    "leg2 crossing circle mid",
    ["irregularity: constant nonzero roll angle of about 1.3 deg"],
)

slc2c3c = (
    slice("2024-08-13T20:33:16", "2024-08-13T21:04:54"),
    ["straight_leg"],
    "leg to and through circle north",
    ["irregularity: roll angle spikes between 20:47:19 - 20:47:49, at 20:57:20 and at 21:00:16"],
)

c3 = (
    slice("2024-08-13T21:09:04", "2024-08-13T22:07:31"),
    ["circle"],
    "circle north",
    ["early circle start due to 1st sonde. Roll angle stable after 21:10:04"],
)

# the below segment has roll angel deviations and two hight level changes such
# that it is not worth being added to the final segmentation of this flight.
slc3catr = (
    slice("2024-08-13T22:09:37", "2024-08-13T22:17:51"),
    ["straight_leg"],
    "leg to ATR circle",
    ["irregularity: roll angel deviation 22:12:41 - 22:13:13"]
)

catr = (
    slice("2024-08-13 22:21:00", "2024-08-13 22:59:14"),
    ["circle", "atr_coordination"],
    "ATR circle",
)

# add all segments that you want to save to a yaml file later to the below list
segments = [parse_segment(s) for s in [sl0, sl1, ec1a, ec1b, ec1, ec1c,
                                       ec2, ec2a, ec3, sl_south, c1,
                                       slc1c2a, slc1c2b, slc1c2c, c2,
                                       slc2c3a, slc2c3b, slc2c3c, c3, catr]]
```

### Quick plot for working your way through the segments piece by piece
select the segment that you'd like to plot and optionally set the flag True for plotting the previous segment in your above specified list as well. The latter can be useful for the context if you have segments that are close or overlap in space, e.g. a leg crossing a circle.

```python
seg=parse_segment(catr)
print(seg["kinds"])
add_previous_seg = True

###########################

fig = plt.figure(figsize=(12, 5))
gs = fig.add_gridspec(2,2)
ax1 = fig.add_subplot(gs[:, 0])

# extend the segment time period by 3min before and after to check outside dropsonde or roll angle conditions
seg_drops = slice(pd.Timestamp(seg["slice"].start) - pd.Timedelta("3min"), pd.Timestamp(seg["slice"].stop) + pd.Timedelta("3min"))
ax1.plot(ds.lon.sel(time=seg_drops), ds.lat.sel(time=seg_drops), "C0")

# plot the previous segment as well as the chosen one
if add_previous_seg:
    if segments.index(seg) > 0:
        seg_before = segments[segments.index(seg) - 1]
        ax1.plot(ds.lon.sel(time=seg_before["slice"]), ds.lat.sel(time=seg_before["slice"]), color="grey")
ax1.plot(ds.lon.sel(time=seg["slice"]), ds.lat.sel(time=seg["slice"]), color="C1")

# plot dropsonde markers for extended segment period as well as for the actually defined period
ax1.scatter(ds_drops.lon.sel(time=seg_drops), ds_drops.lat.sel(time=seg_drops), c="C0")
ax1.scatter(ds_drops.lon.sel(time=seg["slice"]), ds_drops.lat.sel(time=seg["slice"]), c="C1")

ax2 = fig.add_subplot(gs[0, 1])
ds["alt"].sel(time=seg_drops).plot(ax=ax2, color="C0")
ds["alt"].sel(time=seg["slice"]).plot(ax=ax2, color="C1")

ax3 = fig.add_subplot(gs[1, 1])
ds["roll"].sel(time=seg_drops).plot(ax=ax3, color="C0")
ds["roll"].sel(time=seg["slice"]).plot(ax=ax3, color="C1")

#Check dropsonde launch times compared to the segment start and end times
print(f"Segment time: {seg["slice"].start} to {seg["slice"].stop}")
print(f"Dropsonde launch times: {ds_drops.time.sel(time=seg_drops).values}")
```

### Identify visually which straight_leg segments lie on EC track

```python
seg = parse_segment(ec1)
print(seg["kinds"])
plt.plot(ds.lon.sel(time=slice(takeoff, landing)), ds.lat.sel(time=slice(takeoff, landing)))
plt.plot(ds.lon.sel(time=seg["slice"]), ds.lat.sel(time=seg["slice"]), color='red', label="selected segment", zorder=10)
plt.scatter(ds_drops.lon, ds_drops.lat, s=10, c="k", label="dropsondes")
plt.plot(ec_track.lon, ec_track.lat, c='C1', ls='dotted')
plt.plot(ds.lon.sel(time=t_ec, method="nearest"), ds.lat.sel(time=t_ec, method="nearest"),
         marker="*", ls=":", label="EC meeting point", zorder=20)
#plt.plot(pace_track.lon, pace_track.lat, c="C2", ls=":", label="PACE track")
plt.xlabel("longitude / °")
plt.ylabel("latitude / °")
plt.legend();
```

## Events

```python
events = [
    ec_event(ds, ec_track),
]
events
```

## Save segments and events to YAML file

```python
yaml.dump(to_yaml(platform, flight_id, ds, segments, events),
          open(f"../flight_segment_files/{flight_id}.yaml", "w"),
          sort_keys=False)
```

## Import YAML and test it

```python
flight = yaml.safe_load(open(f"../flight_segment_files/{flight_id}.yaml", "r"))
```

```python
kinds = set(k for s in segments for k in s["kinds"])
```

```python
fig, ax = plt.subplots()

for k, c in zip(['straight_leg', 'circle', 'radar_calibration'], ["C0", "C1", "C2"]):
    for s in flight["segments"]:
        if k in s["kinds"]:
            t = slice(s["start"], s["end"])
            ax.plot(ds.lon.sel(time=t), ds.lat.sel(time=t), c=c, label=s["name"])
ax.set_xlabel("longitude / °")
ax.set_ylabel("latitude / °");
```

### Check circle radius

```python
from orcestra.flightplan import LatLon, FlightPlan, IntoCircle

for s in flight["segments"]:
    if "circle" not in s["kinds"]: continue
    d = ds.sel(time=slice(s["start"], s["end"]))
    start = LatLon(float(d.lat[0]), float(d.lon[0]), label="start")
    center = LatLon(s["clat"], s["clon"], label="center")
    FlightPlan([start, IntoCircle(center, s["radius"], 360)]).preview()
    plt.plot(d.lon, d.lat)
```