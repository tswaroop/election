Create the data
===============

- Merge ../data/new/*.xlsx to get `data.csv` (with Sep & Oct data)
- python normalize.py ../data/new/data.csv data.csv reference.csv --columns "L1 Category" "L2 Category" "L3 Category" "Company Name" "Company City" "Search Type" "Center Name"
