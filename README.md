# Misc-Scripts
Miscellaneous Scripts

This repository will contain scripts that I have not integrated into any of the LEAPPs because they take long to run or because they are for edge case use.

myActivity.py
- Will take large MyActivity.html files from a Google Return and converted them into a CSV file containing the timestamp, search information, and text content.
- If using Excel to view the CSV make sure to import it so unicode values are properly decoded.
- The CSV file will be named data.csv and will be created in the same directory as the script.
- Usage: myActivity.py <path/to/MyActivity.html>
