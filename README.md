# HIS_2
HIS_2

## ODBC Database Connection

The app connects to MySQL through ODBC. Install the `pyodbc` Python package when building the app and install the matching MySQL Connector/ODBC driver on each computer that runs it. The ODBC driver is a separate system installation and is not included in the executable.

Set these Windows environment variables before launching `Qphn.exe`:

```bat
set DB_HOST=his-server.local
set DB_PORT=3306
set DB_NAME=his_db
set DB_USER=your_app_user
set DB_PASSWORD=your_password
set DB_ODBC_DRIVER=MySQL ODBC 9.7 Unicode Driver
dist\Qphn.exe
```

Use the exact driver name installed on the computer for `DB_ODBC_DRIVER`. `DB_HOST` can be a hostname rather than an IP address; for it to keep working when the server IP changes, your network must update that hostname's DNS record or otherwise provide a stable address. ODBC does not discover a changed server address on its own.
