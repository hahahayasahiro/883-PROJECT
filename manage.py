import argparse
from app.db import initialize

parser=argparse.ArgumentParser(description='Initialize synthetic SmartCampus data.')
parser.add_argument('--reset',action='store_true',help='Delete ALL local demo records and sessions and restore fixtures.')
parser.add_argument('--yes',action='store_true',help='Confirm resetting local synthetic data.')
args=parser.parse_args()
if args.reset and not args.yes:
    parser.error('Reset deletes local demo changes. Add --yes to confirm.')
initialize(reset=args.reset)
print('Synthetic demonstration database ready.')
