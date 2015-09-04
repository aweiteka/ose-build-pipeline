#!/usr/bin/python

import sys
from scan_dir import Scan

# Where is the dir mounted
scan_dir = sys.argv[1]

# hours_old is an optional kw that
# says how old the cve input data
# can be

scan = Scan(scan_dir, hours_old=2)

# perform the scan
print "Scanning directory %s" % scan_dir
scan.scan()

# details is an optional kw that
# when true will spit out the
# cve details in json

scan.report_results(details=True)
