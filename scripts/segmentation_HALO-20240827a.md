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
import holoviews as hv

from navdata import get_navdata_HALO
from utils import *

from orcestra.flightplan import bco, mindelo
cvao = mindelo
```

```python
platform = "HALO"
flight_id = "HALO-20240827a"
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
t_ec
```

### Get PACE track
**loading the PACE track for the first time takes 6-7 minutes!**
Might be worth only if the flight report states a PACE coordination.

```python
# from get_pace import get_pace_track
# _pace_track = get_pace_track(to_dt(takeoff), to_dt(landing))

# pace_track = _pace_track.where(
#         (_pace_track.lat > ds.lat.min()-2) & (_pace_track.lat < ds.lat.max()+2) &
#         (_pace_track.lon > ds.lon.min()-2) & (_pace_track.lon < ds.lon.max()+2),
#         drop=True)
```

### Get METEOR track
select maybe only the track from the respective flight day

```python
from orcestra.meteor import get_meteor_track

meteor_track = get_meteor_track().sel(time=slice(takeoff, landing))
```

```python
dist_meteor, t_meteor = get_overpass_track(ds, meteor_track)
print(dist_meteor, t_meteor)
```

## Overview plot: HALO track, EC meeting point, and dropsonde locations

```python
plt.plot(ds.lon.sel(time=slice(takeoff, landing)), ds.lat.sel(time=slice(takeoff, landing)), label="HALO track")
plt.scatter(ds_drops.lon, ds_drops.lat, s=10, c="k", label="dropsondes")
plt.plot(ec_track.lon, ec_track.lat, c='C1', ls='dotted')
plt.plot(ds.lon.sel(time=t_ec, method="nearest"), ds.lat.sel(time=t_ec, method="nearest"), marker="*", ls=":", label="EC meeting point")
#plt.plot(pace_track.lon, pace_track.lat, c="C2", ls=":", label="PACE track")
plt.plot(meteor_track.lon, meteor_track.lat, c="C4", ls="-.", label="METEOR track")
plt.xlabel("longitude / °")
plt.ylabel("latitude / °")
plt.legend();
```

## Interactive plots

```python jupyter={"source_hidden": true}
# # Segment starts
# c1 = 'ForestGreen'
# c2 = 'Purple'
# c3 = 'Orange'
# c4 = 'Blue'
# lw = 2
# takeoff = hv.VLine(pd.Timestamp("2024-08-27 09:59:43")).opts(color = c1, line_width = lw)
# landing = hv.VLine(pd.Timestamp("2024-08-27 19:08:18")).opts(color = c1, line_width = lw)

# # seg1s = hv.VLine(pd.Timestamp("2024-08-27 10:04:14")).opts(color = c2, line_width = lw) #straight_leg ascent
# # seg1e = hv.VLine(pd.Timestamp("2024-08-27 10:29:27")).opts(color = c2, line_width = lw)

# # seg2s = hv.VLine(pd.Timestamp("2024-08-27 10:29:27")).opts(color = c3, line_width = lw) #straight_leg   short spike in roll angle at 10:39:42
# # seg2e = hv.VLine(pd.Timestamp("2024-08-27 10:55:11")).opts(color = c3, line_width = lw)

# # seg3s = hv.VLine(pd.Timestamp("2024-08-27 10:56:25")).opts(color = c4, line_width = lw) #straight_leg
# # seg3e = hv.VLine(pd.Timestamp("2024-08-27 11:04:24")).opts(color = c4, line_width = lw)

# # seg4s = hv.VLine(pd.Timestamp("2024-08-27 11:04:24")).opts(color = c1, line_width = lw) #straight_leg ascent
# # seg4e = hv.VLine(pd.Timestamp("2024-08-27 11:06:27")).opts(color = c1, line_width = lw)

# # seg5s = hv.VLine(pd.Timestamp("2024-08-27 11:06:27")).opts(color = c2, line_width = lw) #straight_leg
# # seg5e = hv.VLine(pd.Timestamp("2024-08-27 11:18:02")).opts(color = c2, line_width = lw)

# # seg6s = hv.VLine(pd.Timestamp("2024-08-27 11:18:59")).opts(color = c3, line_width = lw) #straight_leg
# # seg6e = hv.VLine(pd.Timestamp("2024-08-27 11:26:12")).opts(color = c3, line_width = lw)

# # seg7s = hv.VLine(pd.Timestamp("2024-08-27 11:26:31")).opts(color = c4, line_width = lw) #straight_leg
# # seg7e = hv.VLine(pd.Timestamp("2024-08-27 11:28:34")).opts(color = c4, line_width = lw)

# # seg8s = hv.VLine(pd.Timestamp("2024-08-27 11:31:26")).opts(color = c1, line_width = lw) #straight_leg
# # seg8e = hv.VLine(pd.Timestamp("2024-08-27 11:33:30")).opts(color = c1, line_width = lw)

# # seg9s = hv.VLine(pd.Timestamp("2024-08-27 11:33:58")).opts(color = c2, line_width = lw) #straight_leg
# # seg9e = hv.VLine(pd.Timestamp("2024-08-27 11:35:56")).opts(color = c2, line_width = lw)

# # seg10s = hv.VLine(pd.Timestamp("2024-08-27 11:38:41")).opts(color = c3, line_width = lw) #straight_leg   slight turn in track with slowly changing roll angle
# # seg10e = hv.VLine(pd.Timestamp("2024-08-27 11:56:44")).opts(color = c3, line_width = lw)

# # seg11s = hv.VLine(pd.Timestamp("2024-08-27 11:59:20")).opts(color = c4, line_width = lw) #circle   counterclockwise
# # seg11e = hv.VLine(pd.Timestamp("2024-08-27 12:56:08")).opts(color = c4, line_width = lw)

# # seg12s = hv.VLine(pd.Timestamp("2024-08-27 13:14:37")).opts(color = c1, line_width = lw) #circle   counterclockwise   turbulences/spikes 13:36:46-13:38:08 and 14:02:03-14:03:21
# # seg12e = hv.VLine(pd.Timestamp("2024-08-27 14:14:09")).opts(color = c1, line_width = lw)

# # seg13s = hv.VLine(pd.Timestamp("2024-08-27 14:17:22")).opts(color = c2, line_width = lw) #straight_leg   slight turn   BAHAMAS measurement gap between 14:37:22 and 14:57:20
# # seg13e = hv.VLine(pd.Timestamp("2024-08-27 14:37:22")).opts(color = c2, line_width = lw)

# # seg14s = hv.VLine(pd.Timestamp("2024-08-27 14:57:20")).opts(color = c3, line_width = lw) #circle   counterclockwise   BAHAMAS measurement gap between 14:37:22 and 14:57:20
# # seg14e = hv.VLine(pd.Timestamp("2024-08-27 15:50:27")).opts(color = c3, line_width = lw)

# # seg15s = hv.VLine(pd.Timestamp("2024-08-27 15:59:45")).opts(color = c4, line_width = lw) #straight_leg    
# # seg15e = hv.VLine(pd.Timestamp("2024-08-27 16:16:37")).opts(color = c4, line_width = lw)

# # seg16s = hv.VLine(pd.Timestamp("2024-08-27 16:21:25")).opts(color = c1, line_width = lw) #straight_leg
# # seg16e = hv.VLine(pd.Timestamp("2024-08-27 17:03:06")).opts(color = c1, line_width = lw)

# # seg17s = hv.VLine(pd.Timestamp("2024-08-27 17:03:16")).opts(color = c2, line_width = lw) #steep turn
# # seg17e = hv.VLine(pd.Timestamp("2024-08-27 17:06:15")).opts(color = c2, line_width = lw)

# # seg18s = hv.VLine(pd.Timestamp("2024-08-27 17:09:09")).opts(color = c3, line_width = lw) #straight_leg   
# # seg18e = hv.VLine(pd.Timestamp("2024-08-27 17:21:24")).opts(color = c3, line_width = lw)

# # seg19s = hv.VLine(pd.Timestamp("2024-08-27 17:21:35")).opts(color = c4, line_width = lw) #steep turn
# # seg19e = hv.VLine(pd.Timestamp("2024-08-27 17:24:39")).opts(color = c4, line_width = lw)

# # seg20s = hv.VLine(pd.Timestamp("2024-08-27 17:28:06")).opts(color = c1, line_width = lw) #straight_leg   
# # seg20e = hv.VLine(pd.Timestamp("2024-08-27 17:33:37")).opts(color = c1, line_width = lw)

# # seg21s = hv.VLine(pd.Timestamp("2024-08-27 17:33:37")).opts(color = c2, line_width = lw) #straight_leg   descent  
# # seg21e = hv.VLine(pd.Timestamp("2024-08-27 17:39:30")).opts(color = c2, line_width = lw)

# # seg22s = hv.VLine(pd.Timestamp("2024-08-27 17:43:57")).opts(color = c3, line_width = lw) #circle   counterclockwise
# # seg22e = hv.VLine(pd.Timestamp("2024-08-27 18:19:07")).opts(color = c3, line_width = lw)

# # seg23s = hv.VLine(pd.Timestamp("2024-08-27 18:19:07")).opts(color = c4, line_width = lw) #steep turn
# # seg23e = hv.VLine(pd.Timestamp("2024-08-27 18:21:37")).opts(color = c4, line_width = lw)

# # seg24s = hv.VLine(pd.Timestamp("2024-08-27 18:24:25")).opts(color = c1, line_width = lw) #elongated turn
# # seg24e = hv.VLine(pd.Timestamp("2024-08-27 18:30:51")).opts(color = c1, line_width = lw)

# # seg25s = hv.VLine(pd.Timestamp("2024-08-27 18:37:50")).opts(color = c2, line_width = lw) #straight_leg    
# # seg25e = hv.VLine(pd.Timestamp("2024-08-27 18:48:54")).opts(color = c2, line_width = lw)

# seg26s = hv.VLine(pd.Timestamp("2024-08-27 18:54:20")).opts(color = c3, line_width = lw) #straight_leg   descent    
# seg26e = hv.VLine(pd.Timestamp("2024-08-27 19:03:33")).opts(color = c3, line_width = lw)

# seg27s = hv.VLine(pd.Timestamp("2024-08-27 19:04:09")).opts(color = c4, line_width = lw) #straight_leg   descent    
# seg27e = hv.VLine(pd.Timestamp("2024-08-27 19:08:18")).opts(color = c4, line_width = lw)
```

```python jupyter={"source_hidden": true}
# alt = ds["alt"].hvplot()

# alt * takeoff * landing * seg1s * seg1e * seg2s * seg2e * seg3s * seg3e * seg4s * seg4e * seg5s * seg5e * seg6s * seg6e * \
#     seg7s * seg7e * seg8s * seg8e * seg9s * seg9e * seg10s * seg10e * seg11s * seg11e * seg12s * seg12e * seg13s * \
#     seg13e * seg14s * seg14e * seg15s * seg15e * seg16s * seg16e * seg17s * seg17e * seg18s * seg18e * seg19s * seg19e * \
#     seg20s * seg20e * seg21s * seg21e * seg22s * seg22e * seg23s * seg23e * seg24s * seg24e * seg25s * seg25e * seg26s * seg26e * seg27s * seg27e
```

```python jupyter={"source_hidden": true}
# heading = ds["heading"].hvplot()

# heading * takeoff * landing * seg1s * seg1e * seg2s * seg2e * seg3s * seg3e * seg4s * seg4e * seg5s * seg5e * seg6s * seg6e * \
#     seg7s * seg7e * seg8s * seg8e * seg9s * seg9e * seg10s * seg10e * seg11s * seg11e * seg12s * seg12e * seg13s * \
#     seg13e * seg14s * seg14e * seg15s * seg15e * seg16s * seg16e * seg17s * seg17e * seg18s * seg18e * seg19s * seg19e * \
#     seg20s * seg20e * seg21s * seg21e * seg22s * seg22e * seg23s * seg23e * seg24s * seg24e * seg25s * seg25e * seg26s * seg26e * seg27s * seg27e
```

```python jupyter={"source_hidden": true}
# roll = ds["roll"].hvplot()

# roll * takeoff * landing * seg1s * seg1e * seg2s * seg2e * seg3s * seg3e * seg4s * seg4e * seg5s * seg5e * seg6s * seg6e * \
#     seg7s * seg7e * seg8s * seg8e * seg9s * seg9e * seg10s * seg10e * seg11s * seg11e * seg12s * seg12e * seg13s * \
#     seg13e * seg14s * seg14e * seg15s * seg15e * seg16s * seg16e * seg17s * seg17e * seg18s * seg18e * seg19s * seg19e * \
#     seg20s * seg20e * seg21s * seg21e * seg22s * seg22e * seg23s * seg23e * seg24s * seg24e * seg25s * seg25e * seg26s * seg26e * seg27s * seg27e
```

## Segments

defined as a tuple of time slice (`start`, `end`) , segment `kind`, `name`, `remarks`.

* in case of irregularities within a circle, 1 sec before the first and after the last sonde are chosen as start and end times
* use the list of `remarks` to state any deviations, also with respective times

Alternatively, you can also define the segments as dictionaries which also allows to add further attributes to single segments, e.g. a `radius` to a `circle` segment. At the end of the following code block all segments will be normalized by the `parse_segments` function.

```python
seg1 = (
    slice("2024-08-27T10:04:14", "2024-08-27 10:29:27"),
    ["straight_leg", "ascent"],
    "ascending ferry to EC track",
)

seg2 = (
    slice("2024-08-27T10:29:27", "2024-08-27T10:55:11"),
    ["straight_leg"],
    "ferry to EC track",
    ["irregularity: spike in roll angle at 10:39:42"]
)

seg3 = (
    slice("2024-08-27T10:56:25", "2024-08-27T11:04:24"),
    ["straight_leg", "ec_track"],
    "southward EC track",
)

seg4 = (
    slice("2024-08-27T11:04:24", "2024-08-27T11:06:27"),
    ["straight_leg", "ascent", "ec_track"],
    "southward EC track",
)

seg5 = (
    slice("2024-08-27T11:06:27", "2024-08-27T11:18:02"),
    ["straight_leg", "ec_track"],
    "southward EC track",
)

seg6 = (
    slice("2024-08-27T11:18:59", "2024-08-27T11:26:12"),
    ["straight_leg"],
    "departure from EC track",
)

seg7 = (
    slice("2024-08-27T11:26:33", "2024-08-27T11:28:34"),
    ["straight_leg"],
    "leg away from EC track",
)

seg8 = (
    slice("2024-08-27T11:31:26", "2024-08-27T11:33:30"),
    ["straight_leg"],
    "back towards EC track",
)

seg9 = (
    slice("2024-08-27T11:33:58", "2024-08-27T11:35:56"),
    ["straight_leg"],
    "back to EC track",
)

seg10 = (
    slice("2024-08-27T11:38:41", "2024-08-27T11:56:44"),
    ["straight_leg", "ec_track"],
    "", #any coordination? Why sonde?
    ["sonde dropped at 11:40:32"]
)

seg11 = (
    slice("2024-08-27T11:59:38", "2024-08-27T12:56:05"),
    ["circle"],
    "counterclockwise southern circle",
    ["dropsonde failures"]
)

seg12 = (
    slice("2024-08-27T13:14:37", "2024-08-27T14:14:09"),
    ["circle"],
    "counterclockwise middle circle",
    ["irregularity due to turbulences: 13:36:46-13:38:08 and 14:02:03-14:03:21"]
)

seg13 = (
    slice("2024-08-27T14:17:22", "2024-08-27T14:37:22"),
    ["straight_leg", "ec_track"],
    "northward leg through middle circle",
    ["start of BAHAMAS measurement gap: 14:37:22 and 14:57:20"]
)

seg14 = (
    slice("2024-08-27T14:50:53", "2024-08-27T15:50:27"),
    ["circle"],
    "counterclockwise nothern circle",
    ["end of BAHAMAS measurement gap: 14:37:22 and 14:57:20"]
)

seg15 = (
    slice("2024-08-27T15:59:45", "2024-08-27T16:16:37"),
    ["straight leg", "ec_track"],
    "leg through northern circle",
    ["contains EC overpass"]
)

seg16 = (
    slice("2024-08-27T16:21:25", "2024-08-27T17:03:06"),
    ["straight_leg"],
    "ferry to ATR circle",
)

seg17 = (
    slice("2024-08-27T17:03:16", "2024-08-27T17:06:15"),
    ["kind"],
    "steep turn",
    ["steep turn with constant roll angle, perhaps worth a new segment type `turn`?"]
)

seg18 = (
    slice("2024-08-27T17:09:09", "2024-08-27T17:21:24"),
    ["straight_leg"],
    "back track with sonde",
    ["sonde dropped at 17:13:41"]
)

seg19 = (
    slice("2024-08-27T17:21:35", "2024-08-27T17:24:39"),
    ["kind"],
    "name",
    ["another steep turn"]
)

seg20 = (
    slice("2024-08-27T17:28:06", "2024-08-27T17:33:37"),
    ["straight leg"],
    "leg to ATR circle",
)

seg21 = (
    slice("2024-08-27T17:33:37", "2024-08-27T17:39:30"),
    ["straight_leg", "descent"],
    "descending leg to ATR circle",
)

seg22 = (
    slice("2024-08-27T17:43:57", "2024-08-27T18:19:07"),
    ["circle", "ATR_coordination"],
    "counterclockwise ATR circle",
    ["sonde failures"]
)

seg23 = (
    slice("2024-08-27T18:19:20", "2024-08-27T18:21:37"),
    ["kind"],
    "name",
    ["another steep turn"]
)

seg24 = (
    slice("2024-08-27T18:24:25", "2024-08-27T18:30:51"),
    ["kind"],
    "elongated turn",
    ["remark"]
)

seg25 = (
    slice("2024-08-27T18:37:50", "2024-08-27T18:48:54"),
    ["straight_leg"],
    "ferry to Sal",
)

seg26 = (
    slice("2024-08-27T18:54:20", "2024-08-27T19:03:33"),
    ["straight_leg", "descent"],
    "decending ferry to Sal",
)

seg27 = (
    slice("2024-08-27T19:04:09", "2024-08-27T19:08:18"),
    ["straight_leg", "descent"],
    "final descent",
)


# add all segments that you want to save to a yaml file later to the below list
segments = [parse_segment(s) for s in [seg1, seg2, seg3, seg4, seg5, seg6, seg7, seg8, 
                                       seg9, seg10, seg11, seg12, seg13, seg14, seg15, 
                                       seg16, seg18, seg20, seg21, seg22, seg25, 
                                       seg26, seg27]]
```

### Quick plot for working your way through the segments piece by piece
select the segment that you'd like to plot and optionally set the flag True for plotting the previous segment in your above specified list as well. The latter can be useful for the context if you have segments that are close or overlap in space, e.g. a leg crossing a circle.

```python
seg=parse_segment(seg14)
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
seg = parse_segment(seg7)
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
    {"name": "Meteor overpass",
     "kinds": ["meteor_overpass"],
     "time": to_dt(t_meteor),
     "remarks": ["computed time does not match Meteor track plot and report is ambiguous", "distance could not be computed"],
     "distance": float('nan'),
    }
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
