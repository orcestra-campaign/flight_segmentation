ALL_FLIGHTS = $(patsubst scripts/segmentation_%.md,%,$(wildcard scripts/segmentation_HALO*.md))
ALL_SEGMENT_FILES = $(patsubst %, flight_segment_files/%.yaml, ${ALL_FLIGHTS})
ALL_REPORTS = $(patsubst %, reports/%.html, ${ALL_FLIGHTS})

all: reports/all_flights.yaml ${ALL_REPORTS} reports/index.html

.PHONY: all

reports/all_flights.yaml: ${ALL_SEGMENT_FILES}
	mkdir -p reports
	yq eval-all '. as $$item ireduce ({}; . *d {$$item.platform:{$$item.flight_id: $$item}})' $^ > $@

flight_segment_files/%.yaml: scripts/segmentation_%.md
	mkdir -p flight_segment_files
	for i in {1..5}; do jupytext --use-source-timestamp --execute $< && break || sleep 1 && echo "retrying..:"; done

reports/%.html: flight_segment_files/%.yaml scripts/report.py scripts/templates/flight.html
	mkdir -p reports
	python3 scripts/report.py $< $@

reports/index.html: reports/all_flights.yaml Makefile scripts/index.py scripts/templates/index.html
	mkdir -p reports
	python3 scripts/index.py -o $@ -s $<
