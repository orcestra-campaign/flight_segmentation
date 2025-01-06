import xarray as xr

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infiles", nargs="+")
    parser.add_argument("-o", "--outfile")
    args = parser.parse_args()

    ds = xr.open_mfdataset(list(sorted(args.infiles)))
    ds.to_netcdf(args.outfile)


if __name__ == "__main__":
    exit(main())
