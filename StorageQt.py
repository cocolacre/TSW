import sys,time
import sip
#sip.setapi('QString', 1)
from PyQt4 import QtCore, QtGui, QtTest,QtSql
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class StorageQt(QtCore.QObject):
    """
	BUG 1:
		Given time_created string as time.strftime("%Y-%m-%d %H:%M:%S")
		we get a corrupted field in DB using query.prepare(cmd).
		SOLVED by using ' instead of " within the query string:
		    "INSERT INTO tasks VALUES(NULL,'{0}','{1}',{2},'{3}','{4}','{5}',{6})"
            cmd1 = cmd.format("name", "3293295075",1,"parent",t,"ACTIVE",1)	
    """
    def __init__(self):
        super(QtCore.QObject, self).__init__()
        self.q = ''
        self.db = self.createConnection()
        
    def createConnection(self):
        """
        1) It is important to create Query after the call to db.open() ! 
        """
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('appdata.db')
        if not db.open():
            QtGui.QMessageBox.critical(None, QtGui.qApp.tr("Cannot open database"),
                    QtGui.qApp.tr("Unable to establish a database connection.\n"
                                "This example needs SQLite support. Please read "
                                "the Qt SQL driver documentation for information "
                                "how to build it.\n\n"
                                "Click Cancel to exit."),
                    QtGui.QMessageBox.Cancel)
            return False
        
        query = QtSql.QSqlQuery()
        self.q=query
        cmd = "SELECT name FROM sqlite_master WHERE type in ('table','view')"
        self.ex(cmd)
        while query.next():
            data = query.value(0)
            print(data)
        
        # pragma foreign_keys = ON;
        
        ### tasks ###
        cmd = "CREATE TABLE IF NOT EXISTS tasks(id integer primary key autoincrement, name varchar(100), uuid varchar(36), level int, parent varchar(36), time_created varchar(24), status varchar, priority int, description varchar(2048), time_completed varchar(24), time_spent int, time_spent_prediction int)"
        self.ex(cmd)
        ### /tasks ###
        
        cmd = "CREATE TABLE IF NOT EXISTS tasks_trash(id integer primary key autoincrement, name varchar(100), uuid varchar(36), level int, parent varchar(36), time_created varchar(24), status varchar, priority int)"
        self.ex(cmd)
        cmd = "CREATE TABLE IF NOT EXISTS activity_log(id integer primary key autoincrement, time varchar(24), activity varchar(16))"
        self.ex(cmd)
        cmd = "CREATE TABLE IF NOT EXISTS metadata(key varchar(64) UNIQUE, value varchar(64))"
        self.ex(cmd)
        cmd = "INSERT INTO metadata(key,value) SELECT 'targeted_task', '' WHERE NOT EXISTS(SELECT 1 FROM metadata WHERE key = 'targeted_task' AND value != '')"
        self.ex(cmd)
        
        ### reminders ###
        # remind regularly, once
        cmd = "CREATE TABLE IF NOT EXISTS reminders(id integer primary key autoincrement, name varchar(100), uuid varchar(36), time_created varchar(24), status varchar, mode varchar(32), description varchar(2048), times_reminded int)"
        self.ex(cmd)
        
        cmd = "CREATE TABLE IF NOT EXISTS reminders_archive(int, name varchar(100), uuid varchar(36), time_created varchar(24), status varchar, description varchar(2048), times_reminded int)"
        self.ex(cmd)
        ### /reminders ###

        cmd = "CREATE TABLE IF NOT EXISTS behaviour_classes(id integer primary key autoincrement, name varchar(100), description varchar(2048), attribute varchar(64))"
        self.ex(cmd)
        
        #schema = ['id integer primary key autoincrement',
        #          'behaviourId int',
        #          'comment varchar(2048)',
        #          'time_created varchar(24)',
        #          'start_at varchar(24)',
        #          'duration varchar(24)',
        #          'variance REAL DEFAULT 0.5',
        #          'FOREIGN KEY(behaviourId) REFERENCES behaviour_classes(name)',
        #          "time_completed varchar(24) DEFAULT '?'"
        #         ]
        #cmd = "CREATE TABLE IF NOT EXISTS journal(" + " ".join(schema) + ")"
        cmd = "CREATE TABLE IF NOT EXISTS behaviour_journal(id integer primary key autoincrement, behaviourId int, comment varchar(2048), time_created varchar(24), time_started varchar(24), predicted_duration int, duration int, quality int, source varchar(256),  variance REAL DEFAULT 0.5)"
        self.ex(cmd)
        
        
        #cmd = "CREATE TABLE IF NOT EXISTS journal(id integer primary key autoincrement, behaviourId int, comment varchar(1024), time_created varchar(24), start_at varchar(24), duration int, variance REAL, source varchar(64),  FOREIGN KEY(behaviourId) REFERENCES behaviour_classes(id));"
        #self.ex(cmd)
        
        #SELECT journal.id, journal.behaviourId, behaviour_classes.name FROM journal,behaviour_classes WHERE(journal.behaviourId = behaviour_classes.id);
        ### notes ###
        
        ### /notes ###
        
        #cmd = "INSERT INTO metadata(key,value) SELECT 'afk_time_sum', 0 WHERE NOT EXISTS(SELECT 1 FROM metadata WHERE key = 'afk_time_sum' AND value != 0)"
        #self.ex(cmd)
        #cmd = "INSERT INTO metadata(key,value) SELECT 'slack_time_sum', 0 WHERE NOT EXISTS(SELECT 1 FROM metadata WHERE key = 'slack_time_sum' AND value != 0)"
        #self.ex(cmd)
        #cmd = "INSERT INTO metadata(key,value) SELECT 'work_time_sum', 0 WHERE NOT EXISTS(SELECT 1 FROM metadata WHERE key = 'work_time_sum' AND value != 0)"
        #self.ex(cmd)
        
        #cmd = "INSERT INTO metadata(key,value) SELECT 'targeted_task', '' WHERE NOT EXISTS(SELECT 1 FROM metadata WHERE key = 'targeted_task' AND value != '')"
        #cmd = "CREATE TABLE IF NOT EXISTS activity_time_sum(activity varchar(16), sum_seconds int)"
        
        
        #[!!!]
        #cmd = "CREATE TABLE IF NOT EXISTS business(... ... ...)"
        
        cmd = "CREATE TABLE IF NOT EXISTS expected_behaviour(id integer primary key autoincrement, time_created varchar(24), type varchar(32), policy varchar(32), description varchar(1024), name varchar(256), uuid varchar(36), level int, duration int,  time_started varchar(24), time_started_expected varchar(24), time_completed varchar(24), time_completed_expected varchar(24),  status varchar(16), priority int)"
        
        self.ex(cmd)
        return True
    def store_task(self, tasks):
        """
        convert tasks to db format and insert into db
        """
        pass
    def load_active_tasks(self):
        """
        Load tasks data from db, convert to qt-data format 
        and display within TaskStack widget
        """
        pass
		
    def ex(self, cmd='',show=False):
        query = self.q
        if cmd == '':
            cmd = "SELECT name FROM sqlite_master WHERE type in ('table',view')"
        res = self.q.prepare(cmd)
        if not res:
            print('ERROR! Bad query!')
            #error = self.q.lastError()
            #print(error.text())
            #sys.exit()
            #ADD ERROR NOTIFICATION CODE HERE
            print(cmd)
            #return res
        #res = query.exec_()
        res = self.q.exec_()
        #print('Query size:', self.q.size())
        if show:
            #while self.q.next():
            #    print(self.q.value(0))
            self.show_query_result(query = self.q)
        return res

    def fetch(self,cmd=''):
        query = self.q
        if cmd == '':
            return None
        else:
            res = self.ex(cmd)
            records = []
            while self.q.next():
                nFields = self.q.record().count()
                record = []
                for fid in range(nFields):
                    record.append(self.q.value(fid))
                    # DO WE NEED A COPY OF A VALUE???

            #records.append(tuple(record))
                records.append(tuple(record))
        #if we fetched single record
        if len(records) == 1:
            record = records[0]
            # and it has a single field - return just the single value.
            if len(record) == 1:
                return record[0]
            return record
        return records
				
    #def load_last_task(self):
    #    """
    #    this method is created while solving TIME-FORMAT problem.
    #    """
    #    t = time.strftime("%Y-%m-%d %H:%M:%S")
    #    cmd = 'SELECT * FROM tasks ORDER BY id DESC LIMIT 1'.format(main
    #    cmd = 'SELECT * FROM tasks WHERE id = (SELECT MAX(id) FROM tasks)'
    #    self.ex(cmd,show = True)
    #    self.show_query_result()


    def show_query_result(self,query = ''):
        """
		Not working. Information is lost during method call with query as argument.
		"""
        if query == '':
            query = self.q
        records = []
        while self.q.next():
            nFields = self.q.record().count()
            record =[] # lets return this later as tuple
            for fid in range(nFields):
                record.append(self.q.value(fid))
            records.append(tuple(record))
            for record in records:
                print(record)
        
    def add_field(self, table='tasks', new_field_name='time_completed',  new_field_type='varchar(24)'):
        """
		0) ALTER TABLE tasks_trash ADD COLUMN description varchar(256);
		1) create temp duplicate table
		"""
        # create duplicate table:
        #tmp_table_name = table+'_temp'
        #
        #copy from temp table to
        #cmd = 'INSERT INTO tasks SELECT * FROM tasks_new;'
        pass
		
if __name__ == '__main__':
    db = StorageQt()
    #db.load_last_task()
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    cmd = """INSERT INTO tasks VALUES(NULL,'{0}','{1}',{2},'{3}','{4}','{5}',{6})"""
    cmd1 = cmd.format("2222 QtSql db.ex(cmd)", "3293295075",1,"parent",t,"ACTIVE",1)
    db.ex(cmd1)
    time.sleep(2)
    cmd2 = cmd.format("333 QtSql db.q.exec_(cmd)", "3293295075",1,"parent",t,"ACTIVE",1)
    print('cmd2: ',cmd2)
    db.q.prepare(cmd2)
    db.q.exec_()
    #db.load_last_task()
