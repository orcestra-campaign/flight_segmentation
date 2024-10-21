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

# Flight segmentation HALO-20240821a

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
from utils import get_sondes_l1, seg2yaml, get_takeoff_landing
```

```python
flight_id = "HALO-20240821a"
```

## Get HALO position and attitude

```python
ds = get_navdata_HALO(flight_id)
```

## Get dropsonde launch times

```python
drops = get_sondes_l1(flight_id)
ds_drops = ds.sel(time=drops, method="nearest")
```

## Interactive plots

```python
ds["alt"].hvplot()
```

```python
ds["roll"].hvplot()
```

### Defining takeoff and landing
On Barbads, the airport runway plus bumps make HALO move between 7.8-8m above WGS84, on Sal between 88.2-88.4m above WGS84. We therefore define the flight time such that altitude must be above 9m on Barbados and 90m on Sal.

```python
takeoff, landing, duration = get_takeoff_landing(flight_id, ds)
print("Takeoff time: " + str(takeoff))
print("Landing time: " + str(landing))
print(f"Flight duration: {int(duration / 60)}:{int(duration % 60)}")
```

### Plot flight track and dropsonde locations

```python
plt.plot(ds.lon.sel(time=slice(takeoff, landing)), ds.lat.sel(time=slice(takeoff, landing)))
plt.scatter(ds_drops.lon, ds_drops.lat, s=10, c="k")
plt.xlabel("longitude / °")
plt.ylabel("latitude / °");
```

## Segments

defined as a tuple of time slice (`start`, `end`) , segment `kind`, `name`, `irregularities`, and `comments`.

* in case of irregularities within a circle, 1 sec before the first and after the last sonde are chosen as start and end times
* use the irregularities to state any deviations, also with respective times
* use the comments field to state any further relevant information.

```python
seg1 = (
    slice("2024-08-21T12:26:22", "2024-08-21T12:54:23"),
    ["straight_leg", "ascent"], 
    "ascending ferry to EC track",
)

seg2 = (
    slice("2024-08-21T12:54:24", "2024-08-21T12:59:39"),
    ["straight_leg"],
    "ferry to EC track",
)

seg3 = (
    slice("2024-08-21T13:01:44", "2024-08-21 13:28:01"),
    ["straight_leg", "ec_track"],
    "EC track southward",
)

seg4 = (
    slice("2024-08-21T13:28:02", "2024-08-21T13:30:01"),
    ["straight_leg", "ascent", "ec_track"],
    "ascending EC track southward",
)

seg5 = (
    slice("2024-08-21T13:30:02", "2024-08-21T14:07:09"),
    ["straight_leg"],
    "EC track southward",
    ["turbulences around 13:46:36"] # radar calibration?
)

seg6 = (
    slice("2024-08-21T14:09:53", "2024-08-21T15:06:30"),
    ["circle"],
    "southern circle clockwise",
)

seg7 = (
    slice("2024-08-21T15:10:35", "2024-08-21T15:12:53"),
    ["straight_leg", "ec_track"],
    "Ec track northward", 
)

seg8 = (
    slice("2024-08-21T15:15:38", "2024-08-21T16:12:30"),
    ["circle"],
    "mid circle counterclockwise",
    ["no sondes dropped due to air traffic"]
)

seg9 = (
    slice("2024-08-21T16:15:26", "2024-08-21T16:51:44"),
    ["straight_leg", "ec_track"],
    "Ec track northward", 
    ["early circle start due to 1st sonde. Roll angle stable after 21:10:04"],
)

seg10 = (
    slice("2024-08-21T16:54:41", "2024-08-21T17:50:18"),
    ["circle"],
    "northern circle clockwise",
    ["slight deviation from circular path from 17:41:12 to 17:45:54"],
)

seg11 = (
    slice("2024-08-21T17:54:24", "2024-08-21T18:51:27"),
    ["circle"],
    "extra circle counterclockwise",
)

seg12 = (
    slice("2024-08-21T18:55:03", "2024-08-21T19:05:17"),
    ["straight_leg", "ec_track"],
    "EC track northward", 
)

seg13 = (
    slice("2024-08-21T19:06:55", "2024-08-21T19:22:43"),
    ["straight_leg"],
    "ferry to airport",
)

seg14 = (
    slice("2024-08-21T19:22:43", "2024-08-21T19:36:26"),
    ["straight_leg", "descent"],
    "descending ferry to airport", 
)

seg15 = (
    slice("2024-08-21T19:37:03", "2024-08-21T19:48:21"),
    ["straight_leg", "descent"],
    "descending ferry to airport", 
)

seg16 = (
    slice("2024-08-21T19:49:28", "2024-08-21T19:52:38"),
    ["straight_leg", "descent"],
    "final descent",  
)


# add all segments that you want to save to a yaml file later to the below list
segments = [seg1, seg2, seg3, seg4, seg5, seg6, seg7, seg8, seg9, seg10, seg11, seg12, seg13, seg14, seg15, seg16]
```

### Quick plot for working your way through the segments piece by piece
select the segment that you'd like to plot and optionally set the flag True for plotting the previous segment in your above specified list as well. The latter can be useful for the context if you have segments that are close or overlap in space, e.g. a leg crossing a circle.

```python
seg=seg4
add_previous_seg = False

###########################

fig = plt.figure(figsize=(12, 5))
gs = fig.add_gridspec(2,2)
ax1 = fig.add_subplot(gs[:, 0])

# extend the segment time period by 3min before and after to check outside dropsonde or roll angle conditions
seg_drops = slice(pd.Timestamp(seg[0].start) - pd.Timedelta("3min"), pd.Timestamp(seg[0].stop) + pd.Timedelta("3min"))
ax1.plot(ds.lon.sel(time=seg_drops), ds.lat.sel(time=seg_drops), "C0")

# plot the previous segment as well as the chosen one
if add_previous_seg:
    if segments.index(seg) > 0:
        seg_before = segments[segments.index(seg) - 1]
        ax1.plot(ds.lon.sel(time=seg_before[0]), ds.lat.sel(time=seg_before[0]), color="grey")
ax1.plot(ds.lon.sel(time=seg[0]), ds.lat.sel(time=seg[0]), color="C1")

# plot dropsonde markers for extended segment period as well as for the actually defined period
ax1.scatter(ds_drops.lon.sel(time=seg_drops), ds_drops.lat.sel(time=seg_drops), c="C0")
ax1.scatter(ds_drops.lon.sel(time=seg[0]), ds_drops.lat.sel(time=seg[0]), c="C1")

ax2 = fig.add_subplot(gs[0, 1])
ds["alt"].sel(time=seg_drops).plot(ax=ax2, color="C0")
ds["alt"].sel(time=seg[0]).plot(ax=ax2, color="C1")

ax3 = fig.add_subplot(gs[1, 1])
ds["roll"].sel(time=seg_drops).plot(ax=ax3, color="C0")
ds["roll"].sel(time=seg[0]).plot(ax=ax3, color="C1")

#Check dropsonde launch times compared to the segment start and end times
print(f"Segment time: {seg[0].start} to {seg[0].stop}")
print(f"Dropsonde launch times: {ds_drops.time.sel(time=seg_drops).values}")
```

## Identify visually which straight_leg segments lie on EC track

```python
seg = seg16
plt.plot(ds.lon.sel(time=slice(takeoff, landing)), ds.lat.sel(time=slice(takeoff, landing)))
plt.plot(ds.lon.sel(time=seg[0]), ds.lat.sel(time=seg[0]), color = 'red')
plt.scatter(ds_drops.lon, ds_drops.lat, s=10, c="k")
plt.xlabel("longitude / °")
plt.ylabel("latitude / °");
```

## Save segments to YAML file

```python
yaml.dump(seg2yaml(flight_id, ds, segments),
          open(f"../flight_segment_files/{flight_id}.yaml", "w"),
          sort_keys=False)
```

```python

```
