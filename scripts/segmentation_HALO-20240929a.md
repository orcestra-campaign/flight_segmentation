---
jupyter:
  execution:
    timeout: 60
  jupytext:
    notebook_metadata_filter: execution
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

# Flight segmentation HALO-20240929a
This was the transfer flight from Barbados to Memmingen (the final HALO flight from Memmingen to Oberpfaffenhofen is not included).

```python
import matplotlib
import yaml
import hvplot.xarray
import holoviews as hv
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from navdata import get_navdata_HALO
from utils import *

from orcestra.flightplan import bco, mindelo
cvao = mindelo
```

```python
platform = "HALO"
flight_id = "HALO-20240929a"
```

## Loading data
### Get HALO position and attitude

```python
ds = get_navdata_HALO(flight_id)
```

```python
ds
```

### Get dropsonde launch times
No sondes dropped during this flight.

```python
#drops = get_sondes_l1(flight_id)
#ds_drops = ds.sel(time=drops.launch_time, method="nearest").swap_dims({"sonde_id": "time"})
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
No EC track and EC underpass on this flight.

```python
#ec_track = get_ec_track(flight_id, ds)
#dist_ec, t_ec = get_overpass_track(ds, ec_track)
```

### Get PACE track
**loading the PACE track for the first time takes 6-7 minutes!**
Might be worth only if the flight report states a PACE coordination. Based on your decision, choose `load_pace = True` or `load_pace = False`!

```python
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
```

### Get METEOR track
No coordination with Meteor anymore on this flight.

```python
#from orcestra.meteor import get_meteor_track

#meteor_track = get_meteor_track().sel(time=slice(takeoff, landing))
```

## Overview plot: HALO track, EC meeting point, and dropsonde locations

```python
plt.plot(ds.lon.sel(time=slice(takeoff, landing)), ds.lat.sel(time=slice(takeoff, landing)), label="HALO track")
#plt.scatter(ds_drops.lon, ds_drops.lat, s=10, c="k", label="dropsondes")
#plt.plot(ec_track.lon, ec_track.lat, c='C1', ls='dotted')
#plt.plot(ds.lon.sel(time=t_ec, method="nearest"), ds.lat.sel(time=t_ec, method="nearest"), marker="*", ls=":", label="EC meeting point")
if pace_track: plt.plot(pace_track.lon, pace_track.lat, c="C2", ls=":", label="PACE track")
#plt.plot(meteor_track.lon, meteor_track.lat, c="C4", ls="-.", label="METEOR track")
plt.xlabel("longitude / °")
plt.ylabel("latitude / °")
plt.legend();
```

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
seg1 = (
    slice("2024-09-29T21:58:50", "2024-09-29T22:28:33"),
    ["straight_leg", "ascent"],
    "straight_leg_ascent",
    [],
)

seg2 = (
    slice("2024-09-29T22:28:33", "2024-09-29T23:16:37"),
    ["straight_leg"],
    "straight_leg_northeastward_1",
    [],
)

seg3 = (
    slice("2024-09-29T23:17:40", "2024-09-29T23:37:55"),
    ["straight_leg"],
    "straight_leg_primarily_eastward_1",
    [],
)

seg4 = (
    slice("2024-09-29T23:37:57", "2024-09-29T23:58:23"),
    ["straight_leg"],
    "straight_leg_primarily_eastward_2",
    ["irregularity: constant nonzero roll angle of about 0.6 degree"],
)

seg5 = (
    slice("2024-09-29T23:58:30", "2024-09-30T00:02:42"),
    ["straight_leg"],
    "straight_leg_primarily_eastward_3",
    [],
)

seg6 = (
    slice("2024-09-30T00:03:44", "2024-09-30T00:41:27"),
    ["straight_leg"],
    "straight_leg_northeastward_2",
    [],
)

seg7 = (
    slice("2024-09-30T00:42:38", "2024-09-30T00:47:55"),
    ["straight_leg"],
    "straight_leg_northeastward_3",
    [],
)

seg8 = (
    slice("2024-09-30T00:48:58", "2024-09-30T02:08:47"),
    ["straight_leg"],
    "straight_leg_northeastward_4",
    [],
)

seg9 = (
    slice("2024-09-30T02:09:53", "2024-09-30T02:36:39"),
    ["straight_leg"],
    "straight_leg_northeastward_5",
    [],
)

seg10 = (
    slice("2024-09-30T02:36:41", "2024-09-30T02:44:22"),
    ["straight_leg", "ascent"],
    "straight_leg_northeastward_ascent",
    ["irregularity: constant nonzero roll angle of about 0.6 degree", 
     "irregularity: mix of constant altitude and ascent"]
)

seg11 = (
    slice("2024-09-30T02:44:25", "2024-09-30T03:43:51"),
    ["straight_leg"],
    "straight_leg_northeastward_6",
    [],
)

seg12 = (
    slice("2024-09-30T03:45:23" , "2024-09-30T04:28:07"),
    ["straight_leg"],
    "straight_leg_northeastward_7",
    [],
)

seg13 = (
    slice("2024-09-30T04:29:17", "2024-09-30T04:38:21"),
    ["straight_leg"],
    "straight_leg_primarily_eastward_4",
    [],
)

seg14 = (
    slice("2024-09-30T04:38:50", "2024-09-30T04:42:20"),
    ["straight_leg", "ascent"],
    "straight_leg_eastward_ascent",
    [],
)

seg15 = (
    slice("2024-09-30T04:42:20", "2024-09-30T05:20:06"),
    ["straight_leg"],
    "straight_leg_primarily_eastward_5",
    [],
)

seg16 = (
    slice("2024-09-30T05:24:44", "2024-09-30T05:28:30"),
    ["straight_leg"],
    "straight_leg_northeastward_8",
    [],
)

seg17 = (
    slice("2024-09-30T05:29:59", "2024-09-30T05:52:24"),
    ["straight_leg"],
    "straight_leg_primarily_eastward_6",
    [],
)

seg18 = (
    slice("2024-09-30T05:53:31", "2024-09-30T06:06:04"),
    ["straight_leg"],
    "straight_leg_northeastward_9",
    [],
)

seg19 = (
    slice("2024-09-30T06:06:22", "2024-09-30T06:14:37"),
    ["straight_leg"],
    "straight_leg_northeastward_10",
    [],
)

seg20 = (
    slice("2024-09-30T06:16:24", "2024-09-30T06:22:15"),
    ["straight_leg"],
    "straight_leg_northeastward_11",
    [],
)

seg21 = (
    slice("2024-09-30T06:23:56", "2024-09-30T06:31:55"),
    ["straight_leg"],
    "straight_leg_northeastward_12",
    [],
)

seg22 = (
    slice("2024-09-30T06:34:56", "2024-09-30T06:38:56"),
    ["straight_leg", "descent"],
    "straight_leg_northeastward_descent_1",
    [],
)

seg23 = (
    slice("2024-09-30T06:44:00", "2024-09-30T06:46:22"),
    ["straight_leg"],
    "straight_leg_northeastward_13",
    [],
)

seg24 = (
    slice("2024-09-30T06:46:22", "2024-09-30T06:57:00"),
    ["straight_leg", "descent"],
    "straight_leg_northeastward_descent_2",
    ["irregularity: turbulence with roll angle deviations up to +-1.3 degree", 
     "short section without descent between 06:48:57 and 06:50:16"]
)

seg25 = (
    slice("2024-09-30T06:58:52", "2024-09-30T07:02:08"),
    ["straight_leg"],
    "straight_leg_northeastward_14",
    ["irregularity: turbulence with roll angle deviations up to +-1.7 degree"]
)

seg26 = (
    slice("2024-09-30T07:02:08", "2024-09-30T07:05:33"),
    ["straight_leg", "descent"],
    "straight_leg_northeastward_descent_3",
    ["irregularity: turbulence with roll angle deviations up to +-1.8 degree"]
)

seg27 = (
    slice("2024-09-30T07:09:52", "2024-09-30T07:13:05"),
    ["straight_leg", "descent"],
    "final_descent_to_airport",
    ["irregularity: turbulence with roll angle deviations up to +-1.8 degree"]
)

# add all segments that you want to save to a yaml file later to the below list
segments = [parse_segment(s) for s in [seg1, seg2, seg3, seg4, seg5, seg6, seg7, seg8, seg9, seg10, seg11, 
                                       seg12, seg13, seg14, seg15, seg16, seg17, seg18, seg19, seg20, seg21, 
                                       seg22, seg23, seg24, seg25, seg26, seg27]]
```

### Quick plot for working your way through the segments piece by piece
select the segment that you'd like to plot and optionally set the flag True for plotting the previous segment in your above specified list as well. The latter can be useful for the context if you have segments that are close or overlap in space, e.g. a leg crossing a circle.

```python
seg=parse_segment(seg27)
add_previous_seg = False

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
#ax1.scatter(ds_drops.lon.sel(time=seg_drops), ds_drops.lat.sel(time=seg_drops), c="C0")
#ax1.scatter(ds_drops.lon.sel(time=seg["slice"]), ds_drops.lat.sel(time=seg["slice"]), c="C1")

ax2 = fig.add_subplot(gs[0, 1])
ds["alt"].sel(time=seg_drops).plot(ax=ax2, color="C0")
ds["alt"].sel(time=seg["slice"]).plot(ax=ax2, color="C1")

ax3 = fig.add_subplot(gs[1, 1])
ds["roll"].sel(time=seg_drops).plot(ax=ax3, color="C0")
ds["roll"].sel(time=seg["slice"]).plot(ax=ax3, color="C1")

#Check dropsonde launch times compared to the segment start and end times
print(f"Segment time: {seg["slice"].start} to {seg["slice"].stop}")
#print(f"Dropsonde launch times: {ds_drops.time.sel(time=seg_drops).values}")
```

### Identify visually which straight_leg segments lie on EC track

```python
seg = parse_segment(seg26)
plt.plot(ds.lon.sel(time=slice(takeoff, landing)), ds.lat.sel(time=slice(takeoff, landing)))
plt.plot(ds.lon.sel(time=seg["slice"]), ds.lat.sel(time=seg["slice"]), color='red', label="selected segment", zorder=10)
#plt.scatter(ds_drops.lon, ds_drops.lat, s=10, c="k", label="dropsondes")
#plt.plot(ec_track.lon, ec_track.lat, c='C1', ls='dotted')
#plt.plot(ds.lon.sel(time=t_ec, method="nearest"), ds.lat.sel(time=t_ec, method="nearest"),
#         marker="*", ls=":", label="EC meeting point", zorder=20)
if pace_track: plt.plot(pace_track.lon, pace_track.lat, c="C2", ls=":", label="PACE track")
plt.xlabel("longitude / °")
plt.ylabel("latitude / °")
plt.legend();
```

## Events
events are different from segments in having only **one** timestamp. Examples are the usual "EC meeting points" or station / ship overpasses. In general, events include a mandatory `event_id` and `time`, as well as optional statements on `name`, a list of `kinds`, the `distance` in meters, and a list of `remarks`. Possible `kinds`include:
- `ec_underpass`
- `meteor_overpass`
- `bco_overpass`
- `cvao_overpass`

The `event_id` will be added when saving it to YAML.

The EC underpass event can be added to a list of events via the function `ec_event`.

```python
events = []
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
kinds = set(k for s in flight["segments"] for k in s["kinds"])
kinds
```

```python
fig, ax = plt.subplots()

for k, c in zip(['straight_leg', 'circle', ], ["C0", "C1"]):
    for s in flight["segments"]:
        if k in s["kinds"]:
            t = slice(s["start"], s["end"])
            ax.plot(ds.lon.sel(time=t), ds.lat.sel(time=t), c=c, label=s["name"])
ax.set_xlabel("longitude / °")
ax.set_ylabel("latitude / °");
```
