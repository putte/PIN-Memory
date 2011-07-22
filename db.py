# Copied from Dan Larsen (nerdcode)
# http://snippets.dzone.com/user/nerdcode
#
# Filename: db.py save in your Python dir
import e32db

class db:
    def __init__(self, dbpath):
	self.db = e32db.Dbms()
	self.dbv = e32db.Db_view()
	self.reset_counters()
	try:
	    self.db.open(unicode(dbpath))
	except:
	    self.db.create(unicode(dbpath))
	    self.db.open(unicode(dbpath))

    def reset_counters(self):
	self.affected_rows = 0
	self.num_rows = 0
	self.__internal_counter = 0

    def query(self, sql):
	self.reset_counters()
	if sql.lower().startswith('select'):
	    self.dbv.prepare(self.db, unicode(sql))
	    self.dbv.first_line()
	    self.num_rows = self.dbv.count_line()
        else:
            self.affected_rows = self.db.execute(unicode(sql))

    def next(self):
	row = {'id': 0}
	if self.num_rows < 1:
	    self.reset_counters()
	    raise StopIteration
	elif self.__internal_counter < self.num_rows:
	    self.dbv.get_line()
	    for i in range(self.dbv.col_count()):
		row[i] = self.dbv.col(i+1)
	    self.dbv.next_line()
	    self.__internal_counter += 1
	    return row
	else:
	    self.reset_counters()
	    raise StopIteration

    def __iter__(self):
	return self
