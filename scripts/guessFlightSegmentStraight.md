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

## First estimate straigh line segments

```python
import xarray as xr
import numpy as np
import pandas as pd
import numpy.ma as ma

import matplotlib.pyplot as plt

from matplotlib.dates import DateFormatter
from datetime import datetime
```

### User input for straight line selection

```python
flightID = "HALO-20240921a"

bahamasFreq            = 100              # Hz
resamplingTime         =  60              # in seconds [interpolation/averaging interval of raw data]
minimumTimeForStraight =  10              # as number of resamplingTime intervalls
guessRange             =   4              # resampling intervalls before and after the estimated guess (not used currently)
```

```python
resamplingTimeStr = str(resamplingTime)+'s'
trackResampling   = resamplingTime*bahamasFreq 
```

### Open file

```python
ds = xr.open_zarr("ipns://latest.orcestra-campaign.org/products/HALO/position_attitude/"+flightID+".zarr")

roll = ds['roll'].resample(time=resamplingTimeStr).mean()
alt = ds.alt.resample(time=resamplingTimeStr).mean()

deltaHead = np.diff(ds.heading,n=1)
deltaHead = np.insert(deltaHead,0,0)
deltaHead = np.where( (deltaHead >  359) , deltaHead-360, deltaHead)
deltaHead = np.where( (deltaHead < -359) , deltaHead+360, deltaHead)

deltahead = [deltaHead[i:trackResampling+i].mean() for i in range(0,deltaHead.size,trackResampling)]
deltahead = np.insert(deltahead,0,0)
```

### Plot axis scaling

```python
minlat = np.min(ds.lat.values)
maxlat = np.max(ds.lat.values)
minlon = np.min(ds.lon.values)
maxlon = np.max(ds.lon.values)

xs=round(maxlon-minlon)
ys=round(maxlat-minlat)
```

### Plot full flight track

```python
fig = plt.figure(figsize=(xs,ys))
ax = fig.add_subplot()

plt.xticks(fontweight='light', fontsize=12)
plt.yticks(fontweight='light', fontsize=12)

ax.plot(ds.lon,ds.lat)

plt.title(f"{pd.Timestamp(ds.time.values[0]).to_pydatetime():%Y-%m-%d}")
plt.show()
```

### Flight altitude difference

```python
deltaalt = np.diff(alt,n=1)
deltaalt = np.insert(deltaalt,0,0)

fig = plt.figure(figsize=(16,9))
ax = fig.add_subplot()

resamplingTimeStr= str(resamplingTime)+'s'
ax.plot(alt.time,deltaalt)

timeFmt = DateFormatter("%H:%M:%S")
ax.xaxis.set_major_formatter(timeFmt)
plt.gcf().autofmt_xdate()

plt.xticks(rotation=60, fontweight='light', fontsize=12)
plt.yticks(fontweight='light', fontsize=12)

plt.ylim((-10,10))

plt.title("delta altitude")
plt.show()
```

### Delta flight heading

```python
fig = plt.figure(figsize=(16,9))
ax = fig.add_subplot()

ax.plot(alt.time,deltahead)

timeFmt = DateFormatter("%H:%M:%S")
ax.xaxis.set_major_formatter(timeFmt)

plt.gcf().autofmt_xdate()

plt.xticks(rotation=60, fontweight='light', fontsize=12)
plt.yticks(fontweight='light', fontsize=12)

plt.ylim((-0.005,0.005))

plt.title("delta heading")

plt.show()
```

### Flight roll

```python
roll = abs(roll)

fig = plt.figure(figsize=(16,9))
ax = fig.add_subplot()

ax.plot(roll.time,roll)

timeFmt = DateFormatter("%H:%M:%S")
ax.xaxis.set_major_formatter(timeFmt)
plt.gcf().autofmt_xdate()

plt.xticks(rotation=60, fontweight='light', fontsize=12)
plt.yticks(fontweight='light', fontsize=12)
plt.ylim((0,3))

plt.title("abs(roll)")
plt.show()
```

### Now get to the lines

```python
dheadmin=-0.003
dheadmax=0.003

straight = np.ma.masked_where( ( deltahead < dheadmin ) | ( deltahead > dheadmax ) | ( deltaalt < 5 ) & ( roll < 0.3 ), deltahead )
slices = np.ma.flatnotmasked_contiguous(straight)

slices_start = np.array([s.start for s in slices])
slices_end   = np.array([s.stop  for s in slices])

j=0
segment=0
for i in slices_start:
    ibeg=i
    iend=slices_end[j]
    straight_length = iend-ibeg+1
    j += 1

    iendtim = min(iend*trackResampling,ds.time.size-1)
    straight_start = ds.time[ibeg*trackResampling]
    straight_stop  = ds.time[iendtim]

    if ( straight_length <= minimumTimeForStraight ) :
        for index in range(ibeg, iend):
            straight.mask[index] = True
    else :
        print (f"{pd.Timestamp(straight_start.time.values).to_pydatetime():%H:%M:%S}" , " to ",
               f"{pd.Timestamp(straight_stop.time.values).to_pydatetime():%H:%M:%S}")
        segment += 1 
```

```python
fig = plt.figure(figsize=(16,9))
ax = fig.add_subplot()

ax.plot(alt.time,straight)

timeFmt = DateFormatter("%H:%M:%S")
ax.xaxis.set_major_formatter(timeFmt)
plt.gcf().autofmt_xdate()

plt.xticks(rotation=60, fontweight='light', fontsize=12)
plt.yticks(fontweight='light', fontsize=12)

plt.axhline(y=dheadmax, color='g', linestyle='-.')
plt.axhline(y=dheadmin, color='g', linestyle='-.')

plt.title("straight cluster")
plt.show()
```

### Start of straight line

```python
j=0
guessRange=0

fig = plt.figure(figsize=(xs,ys))
ax = fig.add_subplot()

ax.plot(ds.lon, ds.lat)

for i in slices_start:

    ibeg=i
    iend=slices_end[j]
    iendtim = min(iend*trackResampling,ds.time.size-1)

    straight_length = iend-ibeg+1
    straight_start_mid = ds.time[ibeg*trackResampling]
    straight_end_mid   = ds.time[iendtim]

    if ( straight_length > minimumTimeForStraight ) :

        print (f"{pd.Timestamp(straight_start_mid.time.values).to_pydatetime():%H:%M:%S}" , " to ",
               f"{pd.Timestamp(straight_end_mid.time.values).to_pydatetime():%H:%M:%S}")

        point_start_mid = ds.isel(time=(ibeg*trackResampling))

        ax.scatter(point_start_mid.lon, point_start_mid.lat, color="tab:green", zorder=3)
        ax.text   (point_start_mid.lon, point_start_mid.lat, f"{pd.Timestamp(straight_start_mid.time.values).to_pydatetime():%H:%M:%S}")

        point_end_mid = ds.isel(time=(iendtim))

        ax.scatter(point_end_mid.lon, point_end_mid.lat, color="tab:red", zorder=3)
        ax.text   (point_end_mid.lon, point_end_mid.lat, f"{pd.Timestamp(straight_end_mid.time.values).to_pydatetime():%H:%M:%S}")

        segment += 1

    j += 1

plt.show()
```

```python

```
