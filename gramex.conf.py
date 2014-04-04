# Typical settings in development
# -------------------------------

auth = 'self'                   # Login provider. Can be: google|self|ldap
filecache = '.cache'            # Path for filesystem caching

# Production configuration
# ------------------------
# Uncomment the below lines for production and set their values

# port = 8888                     # Run on port. Auto-increments.

nobrowser = False               # Do not start webbrowser (default False)
nodebug = False                 # Prevent autoreload if source changes
# usage = True                    # Enable usage stats at /admin/

secret = 'ibn-microsoft'        # Keep this same for all apps within a client

# Advanced production configuration
# ---------------------------------
# These options are not often used, but are available if required

# home = '.'                      # Start in folder
# cookie_expires = 365            # days for login cookie expiry. 0 for session

# ldap_server = 'domain.com'      # LDAP / ActiveDirectory server IP / hostname
# auth_case_sensitive = True      # Don't convert username to lowercase

# redis = 'appname'               # app name for redis caching (overrides filecache)
# redis_db = 0                    # redis database number (default: 0)
# redis_host = 'localhost'        # redis hostname (default: localhost)
# redis_port = 6379               # redis port (default 6379)

# logging = 'error'               # Set the Python log level. debug|info|warning|error|none
# log_file_prefix = 'path'        # Path prefix for log files.
# log_to_stderr                   # Send log output to stderr
