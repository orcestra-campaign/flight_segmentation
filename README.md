# Segmentation of HALO research flights

The research flights during ORCESTRA can be divided into segments which are specific time intervals during a flight with coherent characteristics. The coherent characteristics, referred to as "kinds", typically refer to the aircraft's state during a flight maneuver as read out from the aircraft position and flight attitude data, such as a roughly contant heading, altitude, and roll angle on a `straight_leg`, or a fairly circular flight path on a `circle`. Further, kinds may indicate colocated measurements with the EarthCARE (EC) satellite (`ec_track`) or other campaign platforms such as the ATR aircraft (`atr_coordination`). Apart from time *intevals* referred to as `segments`, the flight segmentation also contains *single points in time* referred to as `events` which also get specified by kinds and mark, for instance, the time at which the aircraft was closest in space and time to the EC satellite (`ec_underpass`), the Meteor research vessel (`meteor_overpass`), or ground measurement stations such as the CVAO in Mindelo (`cvao_overpass`) or the BCO on Barbados (`bco_overpass`).

The goal of the flight segmentation is to provide a commonly agreed upon, consistent, and easy-to-use subsampling functionality that can be used by reserachers who work with the ORCESTRA measurement data. For instance, studies concerned with the EarthCARE validation can select all segments of kind `ec_track` to obtain all time intervals in which HALO was flying on the EarthCARE track. Similarly, all studies that analyse data taken on circular flight paths can use the flight segmentation to select segments of kind `circle`, and are thereby guaranteed to refer to the same commonly agreed upon subset of the campaign data. The `events` further enable the selection of colocated measurements that can directly be compared with each other.

The segments of all reasearch flights are specified and stored in a yaml-file called [all_flights.yaml](https://orcestra-campaign.github.io/flight_segmentation/all_flights.yaml) which gets its input from segmentation markdown-files for all individual flights. These segmentation files are stored in [scripts](https://github.com/orcestra-campaign/flight_segmentation/tree/main/scripts) and act as the single point of truth for the definition of segments. A Github CI executes all segmentation files and updates the all_flights.yaml upon each commit to this repository. This allows collaborators to add or modify segments and events as they see fit.

A tutorial with practical examples for how to import and use the flight segmentation for data analyses are provided on the [ORCESTRA campaign website](https://orcestra-campaign.org/halo_flight_segmentation.html).


## Structure of the all_flights.yaml file
The example excerpt from the all_flights.yaml file below demonstrates the structure of the flight segmentation. 

#### File and flight header
Allowing for other sub-campaigns to include their flight/ship track segmentation, the file begins with a general header stating the campaign platform (HALO, ATR, METEOR,...) followed by the `flight_id` (e.g. HALO-20240811a) of the first segmented flight, and general information about this flight: Its `mission` affiliation (ORCESTRA), `platform`, `flight_id`, as well as `takeoff` and `landing` time. 

#### Events
Next, `events` lists all the single points in time when underpasses and overpasses occurred. An event is specified by a *unique* `event_id`, constructed from the `flight_id` and a 4-digit hash computed from the event `time`, a `name`, a `time`, and the event `kinds` (e.g. ec_underpass). [LINK TO KINDS SECTION] The attribute `remarks` may contain custom comments about irregularities or other noteworthy information. Last, the `distance` between HALO and the other platform (e.g. EarthCARE satellite), as projected on the Earth's surface, is provided in meters.

#### Segments
After the event listing, `segments` lists all identified flight segments which follow a similar structure as `events` with a *unique* `segment_id`, a name, a specification of the time interval by a `start` and `end` time (which both enter the computation of the hash used for `segment_id`), `kinds`, and `remarks`.

#### General remarks on events and segments attributes
Mandatory components:
- `segment_id`: unique identifier of the segment, constructed as the combination of the `flight_id` and the last four digits of a hash computed from the start and end time of the segment
- `start`: start time of the segment in format `YYYY-MM-DD HH:MM:SS`, e.g. 2024-08-13 14:56:37. 
- `end`: end time of the segment in same format as start time. 
Optional components:
- `kinds`: Can be thought of as tags which label coherent characteristics of the flight segment. See a list of all tags currently in use below.
- `name`: Short (1 - 3 words) qualitative description of the segment, does not have to be unique
- `irregularities`: lists irregularities such as deviations from envisioned flight track due to deep convection, or circles in which no sondes were dropped. Generally meant to be a free text field for proper explanations, this category may contain some standardized *irregularity tags* (**to be decided on**) for automatic checking, and these should be prepended to the explanatory string of the irregularity.
- `comments`: lists custom comments such as the distance to the exact EC overpass position in the case of an `ec_overpass` segment

Example excerpt from the all_flights.yaml file:
```yaml
HALO:
  HALO-20240811a:
    mission: ORCESTRA
    platform: HALO
    flight_id: HALO-20240811a
    takeoff: 2024-08-11 11:59:34
    landing: 2024-08-11 20:35:56
    events:
      - event_id: HALO-20240811a_243c
        name: EC meeting point
        time: 2024-08-11 15:51:53.745187
        kinds:
          - ec_underpass
        remarks: []
        distance: 1123
    segments:
      - segment_id: HALO-20240811a_7051
        name: EC_track_southward_const_alt
        start: 2024-08-11 12:29:59
        end: 2024-08-11 14:03:40
        kinds:
          - straight_leg
          - ec_track
        remarks:
          - 'irregularity: turbulence 2024-08-11T13:02:15 - 2024-08-11T13:12:00'
      - segment_id: HALO-20240811a_50ca
        name: circle_south
        start: 2024-08-11 14:17:00
        end: 2024-08-11 15:16:17
        kinds:
          - circle
        remarks: []
        clat: 5.000066183128026
        clon: -26.999928980187303
        radius: 133094.75108481143
```


**Note:** Time ranges are defined as semi-open intervals, i.e. while the start time is inside the segment, the end time is not. This allows for an unambiguous definition of exactly consecutive segments. In the case of underpass and overpass segments, the start and end times are identical.

## Definition of kinds
Kinds may or may not apply/be adopted for all platforms. For version 1 of the segmentation of HALO flights, one or more of the following kinds are assigned to each segment:

### circle:
- can be identified by a constant change of aircraft heading, a duration of about 60 min, as well as a roughly constant roll angle of 1.5-3 degrees (positive or negative, depending on turning clockwise or counter-clockwise) for the standard circle with a radius of about 133km. Duration and roll angle change with the chosen circle radius. The smaller ATR circle has a radius of approximately 70km and a larger roll angle of 3-5 degree depending on and varying with the wind speed and direction at the respective altitude.
- in most cases associated with the launch of dropsondes, typically 12 per circle at every 30&deg; heading. In cases where the first/last dropsonde of the circle was launched before/after the roll angle and change in heading match the circle characteristics described above, the start/end time of the circle segment is taken to be the `launch_time` of the respective dropsonde minus/plus 1 sec. 
- Circle dropsondes were sometimes droped before/after the roll angle reached its circle value in which case the launch time of the sonde  marks the beginning/end of the circle period (minus/plus a few seconds, so that the sonde is included in the circle segment). 
- Some circles were highly irregular due to detours around convective towers. In these cases, an irregularity note need to be added.

### ATR_coordination:
- circle that was also flown by the ATR aircraft on the same day

### straight_leg:
- can be identified by an approximately constant aircraft heading and a roll angle close to 0&deg; 
- short-term deviations of the roll angle can occur due to turbulence and extreme cases should be mentioned as irregularities; strong deviations my also be radar calibration maneuvers in which case they need to be listed as a separate `radar_calibration` segment.
- while segments in which the aircraft was ascending or descending are often of kind `straight_leg`, `straight_leg` segments with roughly constant altitude need to be separated from those with continuous ascent/descent.

### ec_track:
- straight leg along the EarthCARE track

### ascent:
- straight leg or circle during which the altitude was constantly increased (slight altitude changes of a few meters do not count)

### descent:
- straight leg or circle during which the altitude was constantly decreased (slight altitude changes of a few meters do not count)

### radar_calibration:
- maneuver typically conducted during straight legs, where the aircraft tilts to a roll angle of first about -20&deg; and then +20&deg;.
- if conducted during a straight leg, the straight leg is split into three flight segments:
1.) `straight_leg`, 2.) `radar_calibration`, 3.) `straight_leg`.
- segments start and end at about 0&deg; roll angle.

### ec_underpass:
- defined as the time when the EC satellite is almost exactly above HALO

### pace_underpass:
- defined as the time when the PACE satellite is almost exactly above HALO

### meteor_overpass:
- defined as the time when HALO flies above or passes close by METEOR

### bco_overpass:
- defined as the time when HALO flies above or passes close by the Barbados Cloud Observatory (BCO)

### mindelo_overpass:
- defined as the time when HALO flies above or passes close by the Mindelo research station


## Workflow for HALO segmentation - general overview
The flight segmentation workflow broadly consists of three phases:
1. Segmentation of a flight
2. Review of the segmentation in pairs (the person who performed the segmentation + one other colleague)
3. Handover of the final flight segmentation (along with suggestions for how to improve the flight report where necessary) to the corresponding flight-PI for cross-checking.

### For developers
The following workflow for generating the flight segmentation YAML files is suggested:

1. Install the requirements noted [here](environment.yaml) as well as the [IPFS Desktop App](https://docs.ipfs.tech/install/ipfs-desktop/), e.g. on Mac via `brew install --cask ipfs`.
2. Build a respective python environment, e.g. `mamba  env create -f environment.yaml`
3. Assign yourself to an open segmentation issue of this repository.
4. Use a copy of the file `scripts/segmentation_template.md`, open it as ipython notebook, and load the BAHAMAS and dropsonde data to determine the individual segments, using a mix of bokeh and other plots of roll angle, altitude, heading or other measures.
5. Save your segments from the notebook to a YAML file.
6. test and check the YAML file using the `scripts/report.py`: `python3 scripts/report.py flight_segment_files/HALO-20240813a.yaml reports/HALO-20240813a.html`. This will create an HTML file that you can be opened in any browser and check the details of the flight segments.
7. If necessary, adjust the times and further info in the notebook and update the YAML file. Redo step 4 until you are satisfied with all segments.
8. Add your final YAML file to the repository by creating a pull request and assigning a reviewer. Don't add the `reports/*.html` files. THey will be generated automatically when you do the pull request and serve as a first check to validate the new YAML file.
9. Review your yaml file together with one other colleague
10. Check for inconsistencies with the flight report and send corresponding suggestions for improvement, together with your reviewed flight segmentation to the respective flight-PI for final feedback.


## Reading the files

The flight segmentation data is provided in YAML files. YAML is a text based, human readable data format that uses python-like indentation for structuring its contents. It is often used for configuration files and due to its great human readability very suited for version control, which is one reason we wanted to use it here.
For python users, the module [PyYAML](https://pyyaml.org) (included in Anaconda) offers an easy to use way to read the data from the yaml files into plane python objects like lists and dictionaries.
Here is an example to read a file and print the circle start and end times from that file:

```
import yaml
flightinfo = yaml.load(open("HALO_20240813a.yaml"))
print([(c["start"], c["end"]) for c in flightinfo["segments"] if "circle" in c["kinds"]])
```

## Further information

The segmentation copies and adapts many ideas from the [flight segmentation](https://github.com/eurec4a/flight-phase-separation) conducted for the EUREC4A field campaign.

Further information on the respective flight can be found in the
[flight reports](https://github.com/orcestra-campaign/book/tree/main/orcestra_book/reports).
