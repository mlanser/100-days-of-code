# #100DaysOfCode Log - Round 4 - [Martin Lanser]

This is the official log for the 4th part of my #100DaysOfCode challenge. The objective for R4 is to build an actual application using a frmework such as [Cement](https://builtoncement.com/) or [Click](https://palletsprojects.com/p/click/).

Started on [Sunday June 14, 2020].

## Log

### R4D1 - 14JUN2020
* Create 'SpeedTest' application folder/stub.
* Started work on sample TODO app to learn the 'Cement' framework.

### R4D2 - 15JUN2020
* Hit some major roadblocks. Starting over with 'Click' framework.
* Started work on sample weather info app that gets data from [OpenWeatherMap.org](https://openweathermap.org)

### R4D3 - 16JUN2020
* More work on sample weather info app.
* Also checking out [DietPi](https://dietpi.com/) OS for RPI

### R4D4 - 17JUN2020
* Working on another Click sample app to create QR code for Wifi network creds.

### R4D5 - 18JUN2020
* Continuing working on Wifi QR code sample app.
* Start work on new more comprehensive Wifi app.

### R4D6 - 19JUN2020
* Continuing working on Wifi2 app.

### R4D7 - 20JUN2020
* Added config mgmt and QR code generation for Wifi2 app.

### R4D8 - 21JUN2020
* Added speed test code and a bit more error handling to Wifi2 app.

### R4D9 - 22JUN2020
* Added feature to store speed test data to CSV file.

### R4D10 - 23JUN2020
* Finished feature to store speed test data to CSV file.
* Started working on other formats as well.

### R4D11 - 24JUN2020
* Finished feature to store speed test data to JSON file.

### R4D12 - 25JUN2020
* Started feature to store speed test data to SQLite.

### R4D13 - 26JUN2020
* Working storing speed test data to SQLite.

### R4D14 - 27JUN2020
* Refactoring and cleanup.
* More work on SQLite code.

### R4D15 - 28JUN2020
* More refactoring and cleanup.
* Added ability to update/set and show all settings.

### R4D16 - 29JUN2020
* More refactoring and cleanup.
* Adding more error handling and smarter utility functions.

### R4D17 - 30JUN2020
* More refactoring and cleanup.

### R4D18 - 01JUL2020
* More refactoring and cleanup.
* Finished CSV data store features.

### R4D19 - 02JUL2020
* More refactoring and cleanup.
* Bug fixes.

### R4D20 - 03JUL2020
* More bug fixes.
* Reworking SQLite db storage.

### R4D21 - 04JUL2020
* More bug fixes.
* More refactoring.

### R4D22 - 05JUL2020
* Finally finished all data store functions except InfluxDB.
* More refactoring for better and more flexible modules.

### R4D23 - 06JUL2020
* Starting work on InfluxDB connector.
* More refactoring to streamline data storage functions.
* Extend app settings using config parser's Extended Interpolation feature.

### R4D24 - 07JUL2020
* More refactoring and cleanup.

### R4D25 - 08JUL2020
* More refactoring and cleanup.

### R4D26 - 09JUL2020
* Working on integrating InfluxDB support.

### R4D26 - 09JUL2020
* Still working on integrating InfluxDB support.
* Reworking how we save time stamps.

### R4D27 - 10JUL2020
* Still working on integrating InfluxDB support.
* Reworking how we save timestamps, use UTC, present in local time, etc..

### R4D28 - 11JUL2020
* Still working on integrating InfluxDB support.
* Reworking how we save time stamps.

### R4D29 - 12JUL2020
* Crawling out of datetime-UTC-localtime rabbit hole.
* Totally re-doing SpeedTest to use the Python API instead.
* Still working on Influx stuff.

### R4D30 - 13JUL2020
* Still working on Influx stuff.

### R4D31 - 14JUL2020
* Still working on Influx stuff.

### R4D32 - 15JUL2020
* Still working on Influx stuff.
* Creating sep support for InfluxDB 1.x (using InfluxQL) and Influx Cloud (using Flux queries),
* Fixed first/last records in SQLite historic data.

### R4D33 - 16JUL2020
* Almost finished InfluxDB 1.x integration.

### R4D33 - 17JUL2020
* Finished InfluxDB 1.x integration and fixed problem w returning 'last' N records.

### R4D33 - 18JUL2020
* Starting integration with InfluxDB Cloud.

### R4D34 - 19JUL2020
* Finished integration with InfluxDB Cloud.
* Started integration with MariaDB

### R4D35 - 20JUL2020
* Adding SQL support to WIFI2 app.
* Redesigning data structure for SQL support. Will add indexed ID col and also index timestamp cols.
* Refactoring code to make better use of classes, etc.

