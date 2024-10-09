## Segmentation of flights during ORCESTRA

The PERCUSION research flights conducted during ORCESTRA can be divided into 
segments. A segment is a continuos interval of the flight path that has a set 
of associated characteristics, such as flight manuevers, Earthcare underpasses,
or instrument calibration procedures carried during the segment. 

Flight segments need not be unique nor complete: a given time during a flight 
may belong to any number of segments or none at all. Segments may overlap, 
allowing for flights to be segmented in multiple ways and at multiple levels of 
granularity.

The characteristics that can be associated with a segment are clearly defined, 
and correspond exclusively to one or more of the following:

| Characteristic    | Type            | Description                                                  |
| ----------------- | --------------- | -----------------------------------------                    |
| straight_leg      | Flight Geometry | A straight leg of the flight path.                           |
| circle            | Flight Geometry | A segment of the flight path circling a predefined center.   | 

A segment is thus completely defined by an id, start, end timestamp, and a set 
of associated characteristics. For ease of interpreting the segments a name and
multiple comments can also be associated with the segment.

Defining flight segments is important as the analysis of the data collected 
by each of the PERCUSION flights depends on characteristics of the segments. 
Moreover, having a common definition is important to assure consistency between 
these analyses.

This repository provides files listing all of the segments that have been 
identified for each of the PERCUSION flights. Further information on the 
respective flights can be found in the [flight reports](https://github.com/orcestra-campaign/book/tree/main/orcestra_book/reports) webpage.

## Reading the files

The flight segmentation data is provided in YAML files. YAML is a text based
human readable data format that uses python-like indentation for structuring its contents. 


Yaml files start with a header that describes the flight and continue with a 
list of the identified segments. The following is an example of a flight with 
two segments:

```yaml
nickname: EarthCARE echo
mission: ORCESTRA
platform: HALO
flight_id: HALO-20240816a
segments:
- segment_id: HALO-20240816a_01
  name: ferry_ascent
  start: 2024-08-16 11:39:05
  end: 2024-08-16 12:06:58
  kinds:
  - straight_leg
  comments: []
- segment_id: HALO-20240816a_02
  kinds:
  - straight_leg
  name: ferry_const_alt
  start: 2024-08-16 12:06:58
  end: 2024-08-16 12:51:55
  comments: [strange spike in roll angle at 12:19:37UTC]
```

For python users, the module [PyYAML](https://pyyaml.org) offers an easy to use 
way to read the data from the yaml files into plane python objects like lists 
and dictionaries.

Here is an example to read a file and print the circle start and end times from that file:

```python
import yaml
flightinfo = yaml.load(open("HALO_20240813a.yaml"))
print([(c["start"], c["end"]) for c in flightinfo["segments"] if "circle" in c["kinds"]])
```

### Notes
The segmentation copies and adapts many ideas from the [flight segmentation](https://github.com/eurec4a/flight-phase-separation) conducted for the EUREC4A field campaign.
