import logging
import sqlite3
import uuid
from contextlib import closing
from sqlite3 import OperationalError

import sqlparse
import os.path

from packages import special

_logger = logging.getLogger('litecli')

# FIELD_TYPES = decoders.copy()
# FIELD_TYPES.update({
#     FIELD_TYPE.NULL: type(None)
# })
import gzip, zipfile
import csv
import io
import boto
from gzip import GzipFile
from boto.s3.key import Key

class SQLExecute(object):

	databases_query = """
		PRAGMA database_list
	"""

	tables_query = """
		SELECT name
		FROM sqlite_master
		WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%'
		ORDER BY 1
	"""

	table_columns_query = """
		SELECT m.name as tableName, p.name as columnName
		FROM sqlite_master m
		LEFT OUTER JOIN pragma_table_info((m.name)) p ON m.name <> p.name
		WHERE m.type IN ('table','view') AND m.name NOT LIKE 'sqlite_%'
		ORDER BY tableName, columnName
	"""

	functions_query = '''SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES
	WHERE ROUTINE_TYPE="FUNCTION" AND ROUTINE_SCHEMA = "%s"'''

	def __init__(self, database):
		self.dbname = database
		self._server_type = None
		self.connection_id = None
		self.conn = None
		if not database:
			_logger.debug("Database is not specified. Skip connection.")
			return
		self.connect()
		#self._connect()

	def connect(self, database=None):
		db = database or self.dbname
		_logger.debug("Connection DB Params: \n" "\tdatabase: %r", database)

		db_name = os.path.expanduser(db)
		db_dir_name = os.path.dirname(os.path.abspath(db_name))
		if not os.path.exists(db_dir_name):
			raise Exception("Path does not exist: {}".format(db_dir_name))

		conn = sqlite3.connect(database=db_name, isolation_level=None)
		if self.conn:
			self.conn.close()

		self.conn = conn
		# Update them after the connection is made to ensure that it was a
		# successful connection.
		self.dbname = db
		# retrieve connection id
		self.reset_connection_id()
	def _connect(self, BUCKET_NAME):
		if 1:

			s3 = boto.connect_s3()
			bname=BUCKET_NAME
			self.bucket = s3.get_bucket(bname, validate=False)

			
					
	def run(self, statement, BUCKET_NAME):
		"""Execute the sql in the database and return the results. The results
		are a list of tuples. Each tuple has 4 values
		(title, rows, headers, status).
		"""
		#print self.conn
		if not hasattr(self, 'bucket') or not self.bucket:
			self._connect(BUCKET_NAME)
		# Remove spaces and EOL
		statement = statement.strip()
		if not statement:  # Empty string
			yield (None, None, None, None)

		# Split the sql into separate queries and run each one.
		# Unless it's saving a favorite query, in which case we
		# want to save them all together.
		if statement.startswith("\\fs"):
			components = [statement]
		else:
			components = sqlparse.split(statement)
			#print components
		for sql in components:
			# Remove spaces, eol and semi-colons.
			sql = sql.rstrip(";")

			# \G is treated specially since we have to set the expanded output.
			if sql.endswith("\\G"):
				special.set_expanded_output(True)
				sql = sql[:-2].strip()

			if not self.bucket and not (
				sql.startswith(".open")
				or sql.lower().startswith("use")
				or sql.startswith("\\u")
				or sql.startswith("\\?")
				or sql.startswith("\\q")
				or sql.startswith("help")
				or sql.startswith("exit")
				or sql.startswith("quit")
			):
				_logger.debug(
					"Not connected to database. Will not run statement: %s.", sql
				)


				
				#yield self.get_result2()
				raise OperationalError("Not connected to database.")
				# yield ('Not connected to database', None, None, None)
				# return

			cur = self.conn.cursor() if self.conn else None
			if 1:
				print (statement)
				#export LANG=en_US.utf-8
				#export LC_ALL=en_US.utf-8
				k = Key(self.bucket)
				stm=statement.split()
				limit=25
				if len(stm)==2:
					kname, limit=stm
				else:
					kname=stm[0]
				k.key = kname
				k.open()
				
				gzipped = GzipFile(None, 'rb', fileobj=k)
				reader = csv.reader(io.TextIOWrapper(gzipped, newline="", encoding="utf-8"), delimiter='^')
				if 1:
					data=[]
					for id,line in enumerate(reader):
						if id>=int(limit): break
						data.append([id+1]+line)
						
		
			
			try:  # Special command
				_logger.debug("Trying a dbspecial command. sql: %r", sql)
				for result in special.execute(cur, sql):
					yield result
			except special.CommandNotFound:  # Regular SQL
				_logger.debug("Regular sql statement. sql: %r", sql)
				#print(sql)
				#cur.execute(sql)
				
				yield self.get_result2(data)

	def get_result2(self, cur):
		"""Get the current result's data from the cursor."""
		title = headers = None

		# cursor.description is not None for queries that return result sets,
		# e.g. SELECT.
		
		if 1:
			headers = ['##']+['Col_%s' % x for x in range(1,len(cur[0]))]
			status = "{0} row{1} in set"
			#cursor = [x for x in range(10)]*10
			rowcount = len(cur)


		status = status.format(rowcount, "" if rowcount == 1 else "s")

		return (title, cur, headers, status)
	def get_result(self, cursor):
		"""Get the current result's data from the cursor."""
		title = headers = None

		# cursor.description is not None for queries that return result sets,
		# e.g. SELECT.
		if cursor.description is not None:
			headers = [x[0] for x in cursor.description]
			status = "{0} row{1} in set"
			cursor = list(cursor)
			rowcount = len(cursor)
		else:
			_logger.debug("No rows in result.")
			status = "Query OK, {0} row{1} affected"
			rowcount = 0 if cursor.rowcount == -1 else cursor.rowcount
			cursor = None

		status = status.format(rowcount, "" if rowcount == 1 else "s")

		return (title, cursor, headers, status)
	def tables(self):
		"""Yields table names"""

		with closing(self.conn.cursor()) as cur:
			_logger.debug("Tables Query. sql: %r", self.tables_query)
			cur.execute(self.tables_query)
			for row in cur:
				yield row

	def table_columns(self):
		"""Yields column names"""
		with closing(self.conn.cursor()) as cur:
			_logger.debug("Columns Query. sql: %r", self.table_columns_query)
			cur.execute(self.table_columns_query)
			for row in cur:
				yield row

	def databases(self):
		if not self.conn:
			return

		with closing(self.conn.cursor()) as cur:
			_logger.debug("Databases Query. sql: %r", self.databases_query)
			for row in cur.execute(self.databases_query):
				yield row[1]

	def functions(self):
		"""Yields tuples of (schema_name, function_name)"""

		with closing(self.conn.cursor()) as cur:
			_logger.debug("Functions Query. sql: %r", self.functions_query)
			cur.execute(self.functions_query % self.dbname)
			for row in cur:
				yield row

	def show_candidates(self):
		with closing(self.conn.cursor()) as cur:
			_logger.debug("Show Query. sql: %r", self.show_candidates_query)
			try:
				cur.execute(self.show_candidates_query)
			except sqlite3.DatabaseError as e:
				_logger.error("No show completions due to %r", e)
				yield ""
			else:
				for row in cur:
					yield (row[0].split(None, 1)[-1],)

	def server_type(self):
		self._server_type = ("sqlite3", "3")
		return self._server_type

	def get_connection_id(self):
		if not self.connection_id:
			self.reset_connection_id()
		return self.connection_id

	def reset_connection_id(self):
		# Remember current connection id
		_logger.debug("Get current connection id")
		# res = self.run('select connection_id()')
		self.connection_id = uuid.uuid4()
		# for title, cur, headers, status in res:
		#     self.connection_id = cur.fetchone()[0]
		_logger.debug("Current connection id: %s", self.connection_id)
