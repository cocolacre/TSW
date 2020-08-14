import sip
#sip.setapi('QString', 1)
from PyQt4 import QtCore, QtGui, QtTest,QtSql
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import gc
import queue, copy
import sys,time
import subprocess as sp
import os,ctypes
import datetime
import sqlite3
import cv2
import screen,keyboard
from uuid import uuid4 as get_UUID
from datetime import timedelta


class Task(QtGui.QTreeWidgetItem):
    """
    Task()
    Task(add_to_tree)
    Task(add_to_tree = True, db_record_tuple = RECORD)
    
    Currently Task methods for set attributes and db-record are in:
	    add_child_proc
		add_task_proc
		load_tasks
		    when loading - transform DB records to Task objects.
		updateTaskItem
			when itemChanged() from editing treeWidgetItem - need to update the db and the Task object from the treeWidgetItem.
				res = task_item.__setattr__(fields[field], task_item.text(field))
			We can put DB-update code into the Task attribute setter!
			
			
		target_task
		    when targeting - we need to store this event and associate with task.
		complete_task
			update 
				1) Task TreeWidgetItem object(UI) 
				2) Task object attr, 
				3) task db record, 
				4) task journal db record			
			task_item.status = 'DONE'
			task_item.dict['status'] = 'DONE'
		priority_up, priority_down
			1) db
			2) UI item
			3) Task
		remove_task_proc
			0) remove from treeWidget.tasks list
			1) remove treeWidget child(ui item)
			2) remove from db
		save_task_description
			0) Task
			1) DB record
			(UI item edited already)
		
    """
    def __lt__(self, other):
        tree = self.treeWidget()
        if not tree:
            col = 0
        else:
            col = self.treeWidget().sortColumn()
        res =  self.sortData(col) < other.sortData(col)
        return res

    def __init__(self,popup=False,id = '-1',name='New task...',uuid='', level=0, parent = 'None',  time_created = '', status='ACTIVE', priority=0, description='',time_completed='', time_spent="",time_spent_prediction=0,add_to_tree=False,db_record_tuple = None):
        super(QtGui.QTreeWidgetItem, self).__init__()
        self._sortData = {}
        self.fields={'id':0,
						'name':1,
						'uuid':2,
						'level':3,
						'parent':4,
						'time_created':5,
						'status':6,
						'priority':7,
						'description':8,
						'time_completed':9,
                        'time_spent':10,
                        'time_spent_prediction':11}
        for index,key in enumerate(list(self.fields.keys())):
            self.fields[index] = key
        self.columns = {'name':0, 
						'id':1, 
						'time_created':2, 
						'status':3,
						'priority':4,
						'time_completed':5,
                        'time_spent':6,
                        'time_spent_prediction':7}
        for index,key in enumerate(list(self.columns.keys())):
            self.columns[index] = key
        #print(self.fields)
        #self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        self.id = str(id)
        self.name = name

        if uuid == '':
            self.uuid = str(get_UUID())
        else:
            if len(uuid) != 36:
                print('Error! Wrong UUID string! len(uuid) != 36 !')
                print('Creating NEW uuid for the Task object')
                self.uuid = str(get_UUID())
            else:
                self.uuid = uuid
        self.level = level
        self.parent = parent
        if time_created == '':
            print('NEW TASK!')
            self.time_created = time.strftime("%Y-%m-%d %H:%M:%S")
            print(self.time_created)
        else:
            self.time_created = time_created
        self.status = status
        self.priority = priority
        self.description =description
        self.time_completed=time_completed
        if type(self.time_completed) != str:
            self.time_completed = ''
        else:
            self.time_completed=str(time_completed)
        
        if time_spent == '':
            self.time_spent=0
        else:
            self.time_spent=time_spent
        
        self.time_spent_prediction = time_spent_prediction
        
        
        #if type(self.time_spent)
        self.data = 'Task data. E.g. working dir, files, URL, context media, etc.'
        self.targeted = False
        self.add_to_tree = add_to_tree
        self.setSortData(1,int(self.id))
        self.setText(1,self.id)
        
        self.setText(0,self.name)
        # 1:Left,2:Right,4:Center,8:Justify
        self.setTextAlignment(0, 0x0001)
        #self.setText(1,self.time_created)
        self.setText(2, self.started_to_ago())
        self.setText(3, self.status)
        self.setText(4, str('{:02d}'.format(self.priority)))
        #self.setText(5, str(self.time_completed))
        if len(self.time_completed) > 1:
            opt = 2 #for developing Lead Time format.
            if opt==1:
                lifespan = time.mktime(time.strptime(self.time_completed,"%Y-%m-%d %H:%M:%S")) - time.mktime(time.strptime(self.time_created,"%Y-%m-%d %H:%M:%S"))
                #print(lifespan)
                self.setText(5, self.seconds_to_datetime_string_A(lifespan))
            elif opt==2:
                lead_time = ''
                time_format = "%Y-%m-%d %H:%M:%S"
                time_created_datetime = datetime.datetime.strptime(self.time_created, time_format)
                time_completed_datetime =datetime.datetime.strptime(self.time_completed, time_format)
                delta = time_completed_datetime - time_created_datetime
                lead_time = self.delta_time_to_string(delta)
                self.setText(5,lead_time)
        else:
            self.setText(5, str(self.time_completed))
        if self.time_spent == 0 and self.status == 'DONE':
            self.setText(6, "?...")
        elif self.time_spent == '' or self.time_spent == 0:
            self.setText(6, "")
        else:
            self.setText(6, str(self.time_spent))
        
        #self.setText(7, str(self.time_spent_prediction)+'m')
        self.setText(7, str(self.time_spent_prediction*60))
        
        self.setTextAlignment(3, 0x0004)
        green = QtGui.QColor(0,255,0)
        yellow = QtGui.QColor(255,242,0)
        red = QtGui.QColor(255,0,0)
        status_color = {'ACTIVE':yellow, 'DONE':green, 'CURRENT':red}
        self.setBackgroundColor(3,status_color[self.status])
        #print('Set new color: ', status_color[self.status])
        
    def get_lead_time(self):
        if self.time_completed == '':
            print("ERROR! Task.get_lead_time() called while task's  'time_completed' is not set.")
            return "?"
        else:
            lead_time = ''
            time_format = "%Y-%m-%d %H:%M:%S"
            time_created_datetime = datetime.datetime.strptime(self.time_created, time_format)
            time_completed_datetime =datetime.datetime.strptime(self.time_completed, time_format)
            delta = time_completed_datetime - time_created_datetime
            lead_time = self.delta_time_to_string(delta)
            return lead_time
        
    ##########################################
    ###   <SORTING EXPERIMENTAL FIX>        ###
    ##########################################
    def sortData(self, column):
        return self._sortData.get(column, self.text(column))
        
    def setSortData(self, column,data):
        self._sortData[column] = data
		
    ##########################################
    ###   </SORTING EXPERIMENTAL FIX>      ###
    ##########################################
    def seconds_to_datetime_string_A(self,seconds):
        interval = ''
        days = seconds // (3600*24)
        if days != 0:
            interval = interval+ '{0}d'.format(int(days))
        hours = (seconds // 3600) - days*24
        if hours > 0:
            interval=interval + '{0}h'.format(int(hours))
        minutes = seconds % 60
        #if minutes > 0 and days == 0:
        if minutes > 0:
            interval=interval + '{0}m'.format(int(minutes))
            seconds = int(seconds - hours*3600 - minutes*60)
        else:
            interval = '< 1 min'
        return interval
        
    def seconds_to_datetime_string(self,seconds):
        t = int(seconds)
        D = int(t / 86400)
        t = int(t % 86400)        
        H = int(t / 3600)
        t = int(t % 3600)
        M = int(t / 60)
        S = int(t % 60)
        time_string = ''
        for i, item in enumerate([D,H,M,S]):
            if len(str(item)) == 1:
                time_string+='0'+str(item)+':'
            elif len(str(item)) == 2:
                time_string+=str(item)+':'
            else:
                time_string+=str(item)+'!ERROR!'
        time_string = time_string[:-1]
        return time_string
	
    def started_to_ago_2(self):

        now = datetime.datetime.now()
        time_format = "%Y-%m-%d %H:%M:%S"
        time_created_datetime = datetime.datetime.strptime(self.time_created, time_format)
        delta = now - time_created_datetime
        ago = ''
        if delta.days > 0:
            ago = ago+ '{0}d'.format(delta.days)
        hours = int(delta.seconds / 3600)
        if hours > 0:
            ago=ago + '{0}h'.format(hours)
        minutes = int((delta.seconds - hours*3600)/60)
        if minutes > 0:
            ago = ago + '{0}m'.format(minutes)
        seconds = int(delta.seconds - hours*3600 - minutes*60)
        return ago
    
    def started_to_ago(self):
        """
        <24h : 12h33m
        >24h <7d : 2d12h
        >7d: 77d
        """
        now = datetime.datetime.now()
        time_format = "%Y-%m-%d %H:%M:%S"
        time_created_datetime = datetime.datetime.strptime(self.time_created, time_format)
        delta = now - time_created_datetime
        ago = ''
        if delta.seconds < 3600 and delta.days == 0:
            ago = ago + '{0}m'.format(int(delta.seconds/60))
        elif delta.seconds >3600 and delta.seconds < 24*3600 and delta.days == 0:
            hours = int(delta.seconds/3600)
            minutes = int((delta.seconds - hours*3600)/60)
            ago = ago + '{0}h {1}m'.format(hours,minutes)
        #elif delta.seconds>24*3600 and delta.seconds < 7*24*3600:
        elif delta.days >=1 and delta.days <=7:
            days = delta.days
            hours = int(delta.seconds / 3600)
            ago=ago+"{0}d {1}h".format(days,hours)
        else:
            ago=ago+"{0}d".format(delta.days)
        return ago
	
    def delta_time_to_string(self,delta):
        lead_time = ''
        if delta.seconds < 60 and delta.days == 0:
            lead_time = '?'
        elif delta.seconds >= 60 and delta.seconds < 3600 and delta.days == 0:
            lead_time = lead_time + '{0}m'.format(int(delta.seconds*1.0/60.0))
        elif delta.seconds >3600 and delta.seconds < 24*3600 and delta.days == 0:
            hours = int(delta.seconds/3600)
            minutes = int((delta.seconds - hours*3600)/60)
            lead_time = lead_time + '{0}h {1}m'.format(hours,minutes)
        elif delta.days >=1 and delta.days <=7:
            days = delta.days
            hours = int(delta.seconds / 3600)
            lead_time=lead_time+"{0}d {1}h".format(days,hours)
        else:
            lead_time=lead_time+"{0}d".format(delta.days)
        return lead_time

    def task_from_db_record(self):
        """
        Construct Task object from db record tuple.
        Db record tuple must contain all Task attributes in the following order:
        (name, uuid, level, parent, time_created, status, priority)
        
        """
        
        pass
                    
    def toTree(self):
        """
        move to main window treeWidget.
        """
        pass
    def toString(self):
        pass
    def toList(self):
        """
        Task object into list object ['task name', 'uuid', ...]
        """
        pass
    def setFocus(self):
        #fix for alt+E failing to return focus to the treeWidget
        #says 'Task object has no setFocus()'
        #can't reproduce the bug, but anyway.
        self.treeWidget().setFocus()
        
if __name__ == '__main__':
    from StorageQt import StorageQt
    db = StorageQt()	
    t = Task(name = 'TASK NAME 1')
    