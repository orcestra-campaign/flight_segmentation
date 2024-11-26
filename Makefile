ALL_FLIGHTS = $(patsubst scripts/segmentation_%.md,%,$(wildcard scripts/segmentation_HALO*.md))
ALL_SEGMENT_FILES = $(patsubst %, flight_segment_files/%.yaml, ${ALL_FLIGHTS})
ALL_REPORTS = $(patsubst %, reports/%.html, ${ALL_FLIGHTS})

all: all_flights.yaml ${ALL_REPORTS}

.PHONY: all

all_flights.yaml: ${ALL_SEGMENT_FILES}
	yq eval-all '. as $$item ireduce ({}; . *d {$$item.platform:{$$item.flight_id: $$item}})' $^ > $@

flight_segment_files/%.yaml: scripts/segmentation_%.md
	mkdir -p flight_segment_files
	jupytext --execute $<

reports/%.html: flight_segment_files/%.yaml scripts/report.py scripts/templates/flight.html
	mkdir -p reports
	python3 scripts/report.py $< $@
