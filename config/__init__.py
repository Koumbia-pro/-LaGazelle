
"""Project package initialization.

PyMySQL provides a pure-Python MySQLdb-compatible driver, which avoids the
native compiler requirement on shared hosts such as o2switch.
"""

import pymysql


pymysql.install_as_MySQLdb()
