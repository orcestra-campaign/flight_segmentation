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

# Flight segmentation template

a template for flight segmentation developers to work your way through the flight track piece by piece and define segments in time. An EC track and circles are exemplarily shown for 2024-08-13. A YAML file containing the segment time slices as well as optionally specified `kinds`, `name`, `irregularities` or `comments` is generated at the end.

If a flight includes overpasses of a station of the Meteor, you can import and use the function `plot_overpass` from `utils` which will also print the closest time and distance to the target.

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

from orcestra.flightplan import bco, mindelo
cvao = mindelo
```

```python
platform = "HALO"
flight_id = "HALO-20240907a"
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

meteor_track = get_meteor_track().sel(time=slice(takeoff, landing))
```

## Overview plot: HALO track, EC meeting point, and dropsonde locations

```python
plt.plot(ds.lon.sel(time=slice(takeoff, landing)), ds.lat.sel(time=slice(takeoff, landing)), label="HALO track")
plt.scatter(ds_drops.lon, ds_drops.lat, s=10, c="k", label="dropsondes")
plt.plot(ec_track.lon, ec_track.lat, c='C1', ls='dotted')
plt.plot(ds.lon.sel(time=t_ec, method="nearest"), ds.lat.sel(time=t_ec, method="nearest"), marker="*", ls=":", label="EC meeting point")
if pace_track: plt.plot(pace_track.lon, pace_track.lat, c="C2", ls=":", label="PACE track")
#plt.plot(meteor_track.lon, meteor_track.lat, c="C4", ls="-.", label="METEOR track")
plt.xlabel("longitude / °")
plt.ylabel("latitude / °")
plt.legend();
```

## Interactive plots

```python
import holoviews as hv
c1 = 'ForestGreen'
c2 = 'Purple'
c3 = 'Orange'
c4 = 'Blue'
lw = 2

tko = hv.VLine(takeoff).opts(color = c1, line_width = lw)
ldn = hv.VLine(landing).opts(color = c1, line_width = lw)

# segment boundaries  
seg1s = hv.VLine(pd.Timestamp("2024-09-07T12:56:12")).opts(color = c2, line_width = lw) # straight_leg ascent
seg1e = hv.VLine(pd.Timestamp("2024-09-07T13:22:03")).opts(color = c2, line_width = lw)

seg2s = hv.VLine(pd.Timestamp("2024-09-07T13:22:03")).opts(color = c3, line_width = lw) # straight_leg
seg2e = hv.VLine(pd.Timestamp("2024-09-07T13:53:07")).opts(color = c3, line_width = lw)

seg3s = hv.VLine(pd.Timestamp("2024-09-07T13:53:44")).opts(color = c4, line_width = lw) # straight_leg
seg3e = hv.VLine(pd.Timestamp("2024-09-07T13:55:33")).opts(color = c4, line_width = lw)

seg4s = hv.VLine(pd.Timestamp("2024-09-07T13:56:21")).opts(color = c1, line_width = lw) # straight_leg
seg4e = hv.VLine(pd.Timestamp("2024-09-07T14:27:45")).opts(color = c1, line_width = lw)

seg5s = hv.VLine(pd.Timestamp("2024-09-07T14:35:21")).opts(color = c2, line_width = lw) # straight_leg
seg5e = hv.VLine(pd.Timestamp("2024-09-07T14:38:38")).opts(color = c2, line_width = lw)

seg6s = hv.VLine(pd.Timestamp("2024-09-07T14:43:35")).opts(color = c3, line_width = lw) # straight_leg
seg6e = hv.VLine(pd.Timestamp("2024-09-07T14:51:22")).opts(color = c3, line_width = lw)

seg7s = hv.VLine(pd.Timestamp("2024-09-07T14:54:12")).opts(color = c4, line_width = lw) # counterclockwise circle
seg7e = hv.VLine(pd.Timestamp("2024-09-07T15:49:25")).opts(color = c4, line_width = lw)

seg8s = hv.VLine(pd.Timestamp("2024-09-07T15:53:28")).opts(color = c1, line_width = lw) # straight_leg
seg8e = hv.VLine(pd.Timestamp("2024-09-07T15:55:18")).opts(color = c1, line_width = lw)

seg9s = hv.VLine(pd.Timestamp("2024-09-07T15:59:33")).opts(color = c2, line_width = lw) # counterclockwise circle
seg9e = hv.VLine(pd.Timestamp("2024-09-07T17:01:03")).opts(color = c2, line_width = lw)

seg10s = hv.VLine(pd.Timestamp("2024-09-07T17:05:28")).opts(color = c3, line_width = lw) # straight_leg ascent
seg10e = hv.VLine(pd.Timestamp("2024-09-07T17:08:09")).opts(color = c3, line_width = lw)

seg11s = hv.VLine(pd.Timestamp("2024-09-07T17:10:25")).opts(color = c4, line_width = lw) # straight_leg
seg11e = hv.VLine(pd.Timestamp("2024-09-07T17:36:23")).opts(color = c4, line_width = lw)

# Inbetween these segments there are a couple of seeminly straight legs where the heading is constant but the roll angle is around 1.2 degrees.

seg12s = hv.VLine(pd.Timestamp("2024-09-07T17:51:40")).opts(color = c1, line_width = lw) # clockwise circle
seg12e = hv.VLine(pd.Timestamp("2024-09-07T18:59:37")).opts(color = c1, line_width = lw)

seg13s = hv.VLine(pd.Timestamp("2024-09-07T19:02:48")).opts(color = c2, line_width = lw) # straight_leg
seg13e = hv.VLine(pd.Timestamp("2024-09-07T19:31:16")).opts(color = c2, line_width = lw)

seg14s = hv.VLine(pd.Timestamp("2024-09-07T19:32:37")).opts(color = c3, line_width = lw) # straight_leg
seg14e = hv.VLine(pd.Timestamp("2024-09-07T19:36:31")).opts(color = c3, line_width = lw)

seg15s = hv.VLine(pd.Timestamp("2024-09-07T19:38:24")).opts(color = c4, line_width = lw) # straight_leg
seg15e = hv.VLine(pd.Timestamp("2024-09-07T19:46:37")).opts(color = c4, line_width = lw)

seg16s = hv.VLine(pd.Timestamp("2024-09-07T19:47:48")).opts(color = c1, line_width = lw) # straight_leg
seg16e = hv.VLine(pd.Timestamp("2024-09-07T20:14:41")).opts(color = c1, line_width = lw)

seg17s = hv.VLine(pd.Timestamp("2024-09-07T20:16:46")).opts(color = c2, line_width = lw) # straight_leg descent
seg17e = hv.VLine(pd.Timestamp("2024-09-07T20:22:00")).opts(color = c2, line_width = lw)

seg18s = hv.VLine(pd.Timestamp("2024-09-07T20:22:19")).opts(color = c3, line_width = lw) # straight_leg descent
seg18e = hv.VLine(pd.Timestamp("2024-09-07T20:35:50")).opts(color = c3, line_width = lw)

seg19s = hv.VLine(pd.Timestamp("2024-09-07T20:36:50")).opts(color = c4, line_width = lw) # straight_leg descent irregularity: turbulences (roll angles beyond plus/minus 1 degree)
seg19e = hv.VLine(pd.Timestamp("2024-09-07T20:40:31")).opts(color = c4, line_width = lw)
```

```python
alt = ds["alt"].hvplot()
alt * tko * ldn * \
 seg11s * seg11e #seg1s * seg1e * seg2s * seg2e * seg3s * seg3e * seg4s * seg4e * seg5s * seg5e * seg6s * seg6e * seg7s * seg7e * seg8s * seg8e * seg9s * seg9e * \
 #seg10s * seg10e * seg11s * seg11e * seg12s * seg12e * seg13s * seg13e * seg14s * seg14e * seg15s * seg15e * seg16s * seg16e * seg17s * seg17e * seg18s * seg18e * seg19s * seg19e 
```

```python
heading = ds["heading"].hvplot()
heading * tko * ldn * \
 seg11s * seg11e #seg1s * seg1e * seg2s * seg2e * seg3s * seg3e * seg4s * seg4e * seg5s * seg5e * seg6s * seg6e * seg7s * seg7e * seg8s * seg8e * seg9s * seg9e * \
 #seg10s * seg10e * seg11s * seg11e * seg12s * seg12e * seg13s * seg13e * seg14s * seg14e * seg15s * seg15e * seg16s * seg16e * seg17s * seg17e * seg18s * seg18e * seg19s * seg19e 
```

```python
roll = ds["roll"].hvplot()
roll * tko * ldn * \
 seg11s * seg11e #seg1s * seg1e * seg2s * seg2e * seg3s * seg3e * seg4s * seg4e * seg5s * seg5e * seg6s * seg6e * seg7s * seg7e * seg8s * seg8e * seg9s * seg9e * \
 #seg10s * seg10e * seg11s * seg11e * seg12s * seg12e * seg13s * seg13e * seg14s * seg14e * seg15s * seg15e * seg16s * seg16e * seg17s * seg17e * seg18s * seg18e * seg19s * seg19e
```

## Segments

defined as a tuple of time slice (`start`, `end`) , segment `kind`, `name`, `remarks`.

* in case of irregularities within a circle, 1 sec before the first and after the last sonde are chosen as start and end times
* use the list of `remarks` to state any deviations, also with respective times

Alternatively, you can also define the segments as dictionaries which also allows to add further attributes to single segments, e.g. a `radius` to a `circle` segment. At the end of the following code block all segments will be normalized by the `parse_segments` function.

```python
seg1 = (
    slice("2024-09-07T12:56:12", "2024-09-07T13:22:03"),
    ["straight_leg", "ascent"],
    "eastward ferry",
    []
)

seg2 = (
    slice("2024-09-07T13:22:03", "2024-09-07T13:53:07"),
    ["straight_leg"],
    "eastward ferry",
    []
)

seg3 = (
    slice("2024-09-07T13:53:44", "2024-09-07T13:55:33"),
    ["straight_leg"],
    "eastward ferry",
    []
)

seg4 = (
    slice("2024-09-07T13:56:21", "2024-09-07T14:27:45"),
    ["straight_leg"],
    "approach first circle",
    []
)


seg5 = (
    slice("2024-09-07T14:35:21", "2024-09-07T14:38:38"),
    ["straight_leg"],
    "leg inside circle",
    []
)

seg6 = (
    slice("2024-09-07T14:43:35", "2024-09-07T14:51:22"),
    ["straight_leg"],
    "leg inside circle",
    []
)

seg7 = (
    slice("2024-09-07T14:54:12", "2024-09-07T15:49:25"),
    ["circle"],
    "counterclockwise southern circle",
    []
)

seg8 = (
    slice("2024-09-07T15:53:28", "2024-09-07T15:55:18"),
    ["straight_leg", "ec_track"],
    "northward ec track",
    []
)

seg9 = (
    slice("2024-09-07T15:59:33", "2024-09-07T17:01:03"),
    ["circle"],
    "counterclockwise middle circle",
    ["irregularities: permission denied for some sondes which were then dropped on straight leg through circle instead"]
)

seg10 = (
    slice("2024-09-07T17:05:28", "2024-09-07T17:08:09"),
    ["straight_leg", "ascent"],
    "leg back to ec track",
    []
)

seg11 = (
    slice("2024-09-07T17:10:25", "2024-09-07T17:36:23"),
    ["straight_leg", "ec_track"],
    "leg through circle",
    ["sondes dropped inside circle"]
)

seg12 = (
    slice("2024-09-07T17:51:40", "2024-09-07T18:59:37"),
    ["circle"],
    "clockwise northern circle",
    ["more than full circle"]
)

seg13 = (
    slice("2024-09-07T19:02:48", "2024-09-07T19:31:16"),
    ["straight_leg"],
    "westward ferry",
    []
)

seg14 = (
    slice("2024-09-07T19:32:37", "2024-09-07T19:36:31"),
    ["straight_leg"],
    "westward ferry",
    []
)

seg15 = (
    slice("2024-09-07T19:38:24", "2024-09-07T19:46:37"),
    ["straight_leg"],
    "westward ferry",
    []
)

seg16 = (
    slice("2024-09-07T19:47:48", "2024-09-07T20:14:41"),
    ["straight_leg"],
    "westward ferry",
    []
)

seg17 = (
    slice("2024-09-07T20:16:46", "2024-09-07T20:22:00"),
    ["straight_leg", "descent"],
    "westward descending ferry",
    []
)

seg18 = (
    slice("2024-09-07T20:22:19", "2024-09-07T20:35:50"),
    ["straight_leg", "descent"],
    "airport approach",
    []
)

seg19 = (
    slice("2024-09-07T20:36:50", "2024-09-07T20:40:31"),
    ["straight_leg", "descent"],
    "final descent",
    ["irregularities: turbulence with roll angles larger/smaller 1 degree"]
)



# add all segments that you want to save to a yaml file later to the below list
segments = [parse_segment(s) for s in [seg1, seg2, seg3, seg4, seg5, seg6, seg7, seg8, seg9, seg10, seg11, seg12, seg13, seg14, seg15, seg16, seg17, seg18, seg19]]
```

### Quick plot for working your way through the segments piece by piece
select the segment that you'd like to plot and optionally set the flag True for plotting the previous segment in your above specified list as well. The latter can be useful for the context if you have segments that are close or overlap in space, e.g. a leg crossing a circle.

```python jupyter={"source_hidden": true, "outputs_hidden": true}
seg=parse_segment(seg19)
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
seg = parse_segment(seg18)
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
#Problem with EC track!

# events = [
#     ec_event(ds, ec_track),
#     {"name": "example",
#      "kinds": ["cvao_overpass"],
#      "time": "2024-08-13T14:55:00",
#      "remarks": ["this is an example event", "it includes the distance to the target in meters"],
#      "distance": 123,
#     }
# ]
# events
```

## Save segments and events to YAML file

```python
yaml.dump(to_yaml(platform, flight_id, ds, segments, events),
          open(f"../flight_segment_files/{flight_id}.yaml", "w"),
          sort_keys=False)
```
