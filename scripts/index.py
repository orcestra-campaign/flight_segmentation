import os
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

    with open(args.outfile, "w") as outfile:
        outfile.write(tpl.render(meta=meta))

if __name__ == "__main__":
    _main()
