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

# Flight segmentation HALO-20240831a

```python
import matplotlib
import yaml
import hvplot.xarray
import xarray as xr
import numpy as np
import pandas as pd
import holoviews as hv
import matplotlib.pyplot as plt

from navdata import get_navdata_HALO
from utils import *

from orcestra.flightplan import bco, mindelo
cvao = mindelo
```

```python
platform = "HALO"
flight_id = "HALO-20240831a"
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
select maybe only the track from the respective flight day

```python
from orcestra.meteor import get_meteor_track
load_meteor = True
if load_meteor:
    meteor_track = get_meteor_track().sel(time=slice(takeoff, landing))
else:
    meteor_track = None
```

## Overview plot: HALO track, EC meeting point, and dropsonde locations

```python
plt.plot(ds.lon.sel(time=slice(takeoff, landing)), ds.lat.sel(time=slice(takeoff, landing)), label="HALO track")
plt.scatter(ds_drops.lon, ds_drops.lat, s=10, c="k", label="dropsondes")
plt.plot(ec_track.lon, ec_track.lat, c='C1', ls='dotted')
plt.plot(ds.lon.sel(time=t_ec, method="nearest"), ds.lat.sel(time=t_ec, method="nearest"), marker="*", ls=":", label="EC meeting point")
if pace_track: plt.plot(pace_track.lon, pace_track.lat, c="C2", ls=":", label="PACE track")
if meteor_track: plt.plot(meteor_track.lon, meteor_track.lat, c="C4", ls="-.", label="METEOR track")
plt.xlabel("longitude / °")
plt.ylabel("latitude / °")
plt.legend();
```

## Interactive plots

```python
c1 = 'ForestGreen'
c2 = 'Purple'
c3 = 'Orange'
c4 = 'Blue'
lw = 2

tko = hv.VLine(pd.Timestamp(takeoff)).opts(color = c1, line_width = lw)
ldn = hv.VLine(pd.Timestamp(landing)).opts(color = c1, line_width = lw)

# segment boundaries  
seg1s = hv.VLine(pd.Timestamp("2024-08-31T08:53:55")).opts(color = c2, line_width = lw) # straight_leg ascent
seg1e = hv.VLine(pd.Timestamp("2024-08-31T09:03:33")).opts(color = c2, line_width = lw)

seg2s = hv.VLine(pd.Timestamp("2024-08-31T09:05:37")).opts(color = c3, line_width = lw) # straight_leg ascent
seg2e = hv.VLine(pd.Timestamp("2024-08-31T09:08:20")).opts(color = c3, line_width = lw)

seg3s = hv.VLine(pd.Timestamp("2024-08-31T09:08:30")).opts(color = c4, line_width = lw) # straight_leg ascent irregularity: constant roll angle -1.3 degree
seg3e = hv.VLine(pd.Timestamp("2024-08-31T09:17:39")).opts(color = c4, line_width = lw)

seg4s = hv.VLine(pd.Timestamp("2024-08-31T09:18:04")).opts(color = c1, line_width = lw) # straight_leg ascent
seg4e = hv.VLine(pd.Timestamp("2024-08-31T09:21:09")).opts(color = c1, line_width = lw)

seg5s = hv.VLine(pd.Timestamp("2024-08-31T09:21:09")).opts(color = c2, line_width = lw) # straight_leg
seg5e = hv.VLine(pd.Timestamp("2024-08-31T09:43:24")).opts(color = c2, line_width = lw)

seg6s = hv.VLine(pd.Timestamp("2024-08-31T09:45:02")).opts(color = c3, line_width = lw) # straight_leg
seg6e = hv.VLine(pd.Timestamp("2024-08-31T11:05:50")).opts(color = c3, line_width = lw)

seg7s = hv.VLine(pd.Timestamp("2024-08-31T11:11:50")).opts(color = c4, line_width = lw) # straight_leg ascent
seg7e = hv.VLine(pd.Timestamp("2024-08-31T11:16:34")).opts(color = c4, line_width = lw)

seg8s = hv.VLine(pd.Timestamp("2024-08-31T11:16:34")).opts(color = c1, line_width = lw) # straight_leg
seg8e = hv.VLine(pd.Timestamp("2024-08-31T11:20:48")).opts(color = c1, line_width = lw)

seg9s = hv.VLine(pd.Timestamp("2024-08-31T11:22:15")).opts(color = c2, line_width = lw) # circle counterclockwise
seg9e = hv.VLine(pd.Timestamp("2024-08-31T12:19:36")).opts(color = c2, line_width = lw)

seg10s = hv.VLine(pd.Timestamp("2024-08-31T12:22:31")).opts(color = c3, line_width = lw) # straight_leg
seg10e = hv.VLine(pd.Timestamp("2024-08-31T12:28:05")).opts(color = c3, line_width = lw)

seg11s = hv.VLine(pd.Timestamp("2024-08-31T12:28:23")).opts(color = c4, line_width = lw) # straight_leg irregularity: constant roll angle of about 1.2 degree
seg11e = hv.VLine(pd.Timestamp("2024-08-31T12:33:34")).opts(color = c4, line_width = lw)

seg12s = hv.VLine(pd.Timestamp("2024-08-31T12:34:03")).opts(color = c1, line_width = lw) # straight_leg irregularity: turbulence with up to plus/minus 1.8 degree roll angle deviation
seg12e = hv.VLine(pd.Timestamp("2024-08-31T12:49:34")).opts(color = c1, line_width = lw)

seg13s = hv.VLine(pd.Timestamp("2024-08-31T12:52:25")).opts(color = c2, line_width = lw) # circle counterclockwise irregularity: turbulences with up to plus/minus 4.5 degree roll angle deviation
seg13e = hv.VLine(pd.Timestamp("2024-08-31T13:48:01")).opts(color = c2, line_width = lw)

seg14s = hv.VLine(pd.Timestamp("2024-08-31T13:51:28")).opts(color = c3, line_width = lw) # straight_leg
seg14e = hv.VLine(pd.Timestamp("2024-08-31T14:17:23")).opts(color = c3, line_width = lw)

seg15s = hv.VLine(pd.Timestamp("2024-08-31T14:19:59")).opts(color = c4, line_width = lw) # circle counterclockwise
seg15e = hv.VLine(pd.Timestamp("2024-08-31T15:16:01")).opts(color = c4, line_width = lw)

seg16s = hv.VLine(pd.Timestamp("2024-08-31T15:19:37")).opts(color = c1, line_width = lw) # straight_leg descent
seg16e = hv.VLine(pd.Timestamp("2024-08-31T15:32:30")).opts(color = c1, line_width = lw)

seg17s = hv.VLine(pd.Timestamp("2024-08-31T15:32:30")).opts(color = c2, line_width = lw) # straight_leg
seg17e = hv.VLine(pd.Timestamp("2024-08-31T16:01:15")).opts(color = c2, line_width = lw)

seg18s = hv.VLine(pd.Timestamp("2024-08-31T16:08:10")).opts(color = c3, line_width = lw) # straight_leg
seg18e = hv.VLine(pd.Timestamp("2024-08-31T16:24:05")).opts(color = c3, line_width = lw)

seg19s = hv.VLine(pd.Timestamp("2024-08-31T16:27:42")).opts(color = c4, line_width = lw) # circle clockwise atr_coordination
seg19e = hv.VLine(pd.Timestamp("2024-08-31T17:03:55")).opts(color = c4, line_width = lw)

seg20s = hv.VLine(pd.Timestamp("2024-08-31T17:05:10")).opts(color = c1, line_width = lw) # radar_calibration
seg20e = hv.VLine(pd.Timestamp("2024-08-31T17:07:39")).opts(color = c1, line_width = lw)

seg21s = hv.VLine(pd.Timestamp("2024-08-31T17:09:16")).opts(color = c2, line_width = lw) # straight_leg descent
seg21e = hv.VLine(pd.Timestamp("2024-08-31T17:35:47")).opts(color = c2, line_width = lw)

seg22s = hv.VLine(pd.Timestamp("2024-08-31T17:36:32")).opts(color = c3, line_width = lw) # straight_leg
seg22e = hv.VLine(pd.Timestamp("2024-08-31T17:38:37")).opts(color = c3, line_width = lw)

seg23s = hv.VLine(pd.Timestamp("2024-08-31T17:38:43")).opts(color = c4, line_width = lw) # straight_leg descent irregularity: turbulences up to plus/minus 2.7 degree roll angle deviation shortly before touch down
seg23e = hv.VLine(pd.Timestamp("2024-08-31T17:40:58")).opts(color = c4, line_width = lw)
```

```python jupyter={"source_hidden": true}
alt = ds["alt"].hvplot()
alt * tko * ldn * \
 seg1s * seg1e * seg2s * seg2e * seg3s * seg3e * seg4s * seg4e * seg5s * seg5e * seg6s * seg6e * seg7s * seg7e * seg8s * seg8e * seg9s * seg9e * \
 seg10s * seg10e * seg11s * seg11e * seg12s * seg12e * seg13s * seg13e * seg14s * seg14e * seg15s * seg15e * seg16s * seg16e * seg17s * seg17e * \
 seg18s * seg18e * seg19s * seg19e * seg20s * seg20e * seg21s * seg21e * seg22s * seg22e * seg23s * seg23e
```

```python
heading = ds["heading"].hvplot()
heading * tko * ldn * \
 seg1s * seg1e * seg2s * seg2e * seg3s * seg3e * seg4s * seg4e * seg5s * seg5e * seg6s * seg6e * seg7s * seg7e * seg8s * seg8e * seg9s * seg9e * \
 seg10s * seg10e * seg11s * seg11e * seg12s * seg12e * seg13s * seg13e * seg14s * seg14e * seg15s * seg15e * seg16s * seg16e * seg17s * seg17e * \
 seg18s * seg18e *  seg19s * seg19e * seg20s * seg20e * seg21s * seg21e * seg22s * seg22e * seg23s * seg23e
```

```python
roll = ds["roll"].hvplot()
roll * tko * ldn * \
 seg1s * seg1e * seg2s * seg2e * seg3s * seg3e * seg4s * seg4e * seg5s * seg5e * seg6s * seg6e * seg7s * seg7e * seg8s * seg8e * seg9s * seg9e * \
 seg10s * seg10e * seg11s * seg11e * seg12s * seg12e * seg13s * seg13e * seg14s * seg14e * seg15s * seg15e * seg16s * seg16e * seg17s * seg17e * \
 seg18s * seg18e * seg19s * seg19e * seg20s * seg20e * seg21s * seg21e * seg22s * seg22e * seg23s * seg23e
```

## Segments

defined as a tuple of time slice (`start`, `end`) , segment `kind`, `name`, `remarks`.

* in case of irregularities within a circle, 1 sec before the first and after the last sonde are chosen as start and end times
* use the list of `remarks` to state any deviations, also with respective times

Alternatively, you can also define the segments as dictionaries which also allows to add further attributes to single segments, e.g. a `radius` to a `circle` segment. At the end of the following code block all segments will be normalized by the `parse_segments` function.

```python
seg1 = (
    slice("2024-08-31T08:53:55", "2024-08-31T09:03:33"),
    ["straight_leg", "ascent"],
    "eastward ascending ferry",
    [],
)

seg2 = (
    slice("2024-08-31T09:05:37", "2024-08-31T09:08:20"),
    ["straight_leg", "ascent", "ec_track"],
    "ascending EC track",
    []
)

seg3 = (
    slice("2024-08-31T09:08:30", "2024-08-31T09:17:39"),
    ["straight_leg", "ascent", "ec_track"],
    "southward EC track",
    ["irregularity: constant nonzero roll angle of -1.3 degree"]
)

seg4 = (
    slice("2024-08-31T09:18:04", "2024-08-31T09:21:09"),
    ["straight-leg", "ascent", "ec_track"],
    "southward EC track",
    []
)

seg5 = (
    slice("2024-08-31T09:21:09", "2024-08-31T09:43:24"),
    ["straight_leg", "ec_track"],
    "later EC underpass",
    []
)

seg6 = (
    slice("2024-08-31T09:45:02", "2024-08-31T11:05:50"),
    ["straight_leg", "ec_track"],
    "long southward EC track",
    []
)

seg7 = (
    slice("2024-08-31T11:11:50", "2024-08-31T11:16:34"),
    ["straight_leg", "ascent", "ec_track"],
    "descending EC track",
    []
)

seg8 = (
    slice("2024-08-31T11:16:34", "2024-08-31T11:20:48"),
    ["straight_leg", "ec_track"],
    "northward EC track",
    []
)

seg9 = (
    slice("2024-08-31T11:22:15", "2024-08-31T12:19:36"),
    ["circle"],
    "southern counterclockwise circle",
    []
)

seg10 = (
    slice("2024-08-31T12:22:31", "2024-08-31T12:28:05"),
    ["straight_leg", "ec_track"],
    "EC track inside circle",
    []
)

seg11 = (
    slice("2024-08-31T12:28:23", "2024-08-31T12:33:34"),
    ["straight_leg", "ec_track"],
    "EC track inside circle",
    ["irregularity: constant nonzero roll angle of about 1.2 degree"]
)

seg12 = (
    slice("2024-08-31T12:34:03", "2024-08-31T12:49:34"),
    ["straight_leg", "ec_track"],
    "northward EC track",
    ["irregularity: turbulence with up to plus/minus 1.8 degree roll angle deviation"]
)

seg13 = (
    slice("2024-08-31T12:52:25", "2024-08-31T13:48:01"),
    ["circle"],
    "middle counterclockwise circle",
    ["irregularity: turbulence with up to plus/minus 4.5 degree roll angle deviation"]
)

seg14 = (
    slice("2024-08-31T13:51:28", "2024-08-31T14:17:23"),
    ["straight_leg", "ec_track"],
    "EC track through circle",
    ["irregularity: turbulence with up to plus/minus 4.6 degree roll angle deviation"]
)

seg15 = (
    slice("2024-08-31T14:19:59", "2024-08-31T15:16:01"),
    ["circle"],
    "northern counterclockwise circle",
    []
)

seg16 = (
    slice("2024-08-31T15:19:37", "2024-08-31T15:32:30"),
    ["straight_leg", "descent", "ec_track"],
    "EC track inside circle",
    []
)

seg17 = (
    slice("2024-08-31T15:32:30", "2024-08-31T16:01:15"),
    ["straight_leg", "ec_track"],
    "northward EC track through ATR cicle",
    []
)

seg18 = (
    slice("2024-08-31T16:08:10", "2024-08-31T16:24:05"),
    ["straight_leg", "ec_track"],
    "southward EC track through ATR circle",
    []
)

seg19 = (
    slice("2024-08-31T16:27:38", "2024-08-31T17:03:55"),
    ["circle", "atr_coordination"],
    "ATR circle",
    []
)

seg20 = (
    slice("2024-08-31T17:05:10", "2024-08-31T17:07:39"),
    ["radar_calibration"],
    "Radar calibration maneuver",
    []
)

seg21 = (
    slice("2024-08-31T17:09:16", "2024-08-31T17:35:47"),
    ["straight_leg", "descent"],
    "northward descending ferry",
    []
)

seg22 = (
    slice("2024-08-31T17:36:32", "2024-08-31T17:38:37"),
    ["straight_leg"],
    "northward ferry",
    []
)

seg23 = (
    slice("2024-08-31T17:38:43", "2024-08-31T17:40:58"),
    ["straight_leg", "descent"],
    "final descent",
    ["irregularity: turbulence up to plus/minus 2.7 degree roll angle deviation shortly before touch down", "irregularity: slight change of heading"]
)


# add all segments that you want to save to a yaml file later to the below list
segments = [parse_segment(s) for s in [seg1, seg2, seg3, seg4, seg5, seg6, seg7, seg8, seg9, seg10, seg11, seg12, seg13, seg14, seg15, seg16, seg17, seg18, seg19, seg20, seg21, seg22, seg23]]
```

### Quick plot for working your way through the segments piece by piece
select the segment that you'd like to plot and optionally set the flag True for plotting the previous segment in your above specified list as well. The latter can be useful for the context if you have segments that are close or overlap in space, e.g. a leg crossing a circle.

```python
seg=parse_segment(seg23)
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
seg = parse_segment(seg23)
plt.plot(ds.lon.sel(time=slice(takeoff, landing)), ds.lat.sel(time=slice(takeoff, landing)))
plt.plot(ds.lon.sel(time=seg["slice"]), ds.lat.sel(time=seg["slice"]), color='red', label="selected segment", zorder=10)
plt.scatter(ds_drops.lon, ds_drops.lat, s=10, c="k", label="dropsondes")
plt.plot(ec_track.lon, ec_track.lat, c='C1', ls='dotted')
plt.plot(ds.lon.sel(time=t_ec, method="nearest"), ds.lat.sel(time=t_ec, method="nearest"),
         marker="*", ls=":", label="EC meeting point", zorder=20)
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

```python

```
