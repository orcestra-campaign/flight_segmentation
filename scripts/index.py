import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)

def _main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("flight_ids", nargs="+", help="flight ids")
    parser.add_argument("-o", "--outfile", default="index.html", help="output filename")
    args = parser.parse_args()

    tpl = env.get_template("index.html")

    with open(args.outfile, "w") as outfile:
        outfile.write(tpl.render(flight_ids=args.flight_ids))

if __name__ == "__main__":
    _main()
