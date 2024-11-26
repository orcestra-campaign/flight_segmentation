import os
import datetime
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)

def _main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", default="index.html", help="output filename")
    parser.add_argument("-s", "--segmentfile", default="all_flights.yaml", help="compiled segment file")
    args = parser.parse_args()

    tpl = env.get_template("index.html")

    with open(args.segmentfile) as segmentfile:
        meta = yaml.safe_load(segmentfile)

    circle_count = len([segment
                        for flights in meta.values()
                        for flight in flights.values()
                        for segment in flight["segments"]
                        if "circle" in segment["kinds"]])

    total_duration = sum([flight["landing"] - flight["takeoff"]
                          for flights in meta.values()
                          for flight in flights.values()], start=datetime.timedelta(0))


    with open(args.outfile, "w") as outfile:
        outfile.write(tpl.render(meta=meta, circle_count=circle_count, total_duration=total_duration / datetime.timedelta(hours=1)))

if __name__ == "__main__":
    _main()
