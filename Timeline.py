import sip
sip.setapi("QString", 1)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
#from Pixmaps import *

import time, uuid


#class TabPressFilter(QtCore.QObject):
#    def eventFilter(self, widget, event):
#        if event.type() == QEvent.KeyPress
#            if event.nativeScanCode() == 
#            return False
#        else:
#            return False

    
class TimelineView(QtGui.QGraphicsView):
    def __init__(self):
        pass
    def setupViewport(self, target):
        pass

class Timeline(QtGui.QWidget):
    """
    
    QWidget-based widgets can be directly embedded into a QGraphicsScene using QGraphicsProxyWidget.
    
    However, itemsBoundingRect() is a relatively time consuming function, as it operates by collecting positional information for every item on the scene. Because of this, you should always set the scene rect when operating on large scenes.
    
    The heart of QTimeLine lies in the valueForTime() function, which generates a value between 0 and 1 for a given time.
    
    What elements do we wanna see in order to make neironal ignition better?
        activity trace; 
        events;
            task creation, completion, achievements, activity icons(including window types, git commits, schedule failures or satisfaction events, comments\notes, typing speed,traffic,
        window trace; semantic trace;
        some manual user controlled polled metrics like mood, hunger, entropy, the magnitude of desire\tonus
        behavioral , social events;
        new behaviour indicators;
        due dates; (with priorities)
        reminders;
        suggestions;
        other cyber structures aimed at user's rank boosting.
        beware-like notes (like "Expect the X core to be agressive within the next period")
        
    What should the user be able to achieve easily via this system?
        Quickly access diverse summary info, suggest and compare different schedules
        (it will allow for smarter behaviour correction. We should even trace the process of scheule comparison to reenforce such a behaviour and provoke the user to generally spent more time on it)
        The core should build quality correlations with the both sides of the timeframe and initiate 
        active neighbour neuronal tackling thus engaging other subsystems into a densier time consideration. 
            (this will (probably) allow for stronger order and adaptation enforcement within the tribe)
            
    Floors\rows:
        Top row indicates purely\solely work\slack\afk trace.
        Another row: tasks
        etc
    1) On add\insert:
        
            set horizontal scrollbar
            QTimer->redraw_moment_border(QGraphicsLineItem.pos().x()+=1)
                add_item:
                    x1 = dateTimeToSceneX(item.time_started)
                    #x2 = dateTimeToSceneX(item.time_completed_prediction)
                    x2 = dateTimeToSceneX(item.time_completed)
                    y1 = item.get_item_top(item.level, item.attribute)
                    y2 = item.get_item_bottom(item.level, item.attribute)
                    
                    rect=QGraphicsRectItem(x1,x2, y1,y2,*args)
                    QGraphicsScene.addItem(rect,x1,x2,y1,y2, *attrs)
                    scene.update() #redraw?
                
                insert_item (*way):
                    if way == "just move to the right the later items (and start indicating the need
                        to reconsider their position)
                        
    """
    def __init__(self,parent=None):
        """
            TODO:
            1)Temp. create a shortcut to add_expected_behaviour_record
              within TSW.
            2) MOVE TO NEW THREAD: self.action_project = sorted(self.action_project,key=
            
        """
        super().__init__(parent)
        #self.gw = QtGui.QGraphicsWidget(
        self.scene = QtGui.QGraphicsScene()
        #self.view  = QtGui.QGraphicsView(self.scene,parent=parent)
        self.view  = QtGui.QGraphicsView(self.scene)
        self.view.setFixedHeight(150)
        self.scene_w = 44000
        self.scene_h = 80
        self.view.setSceneRect(-self.scene_w , -self.scene_h , self.scene_w*2 , self.scene_h*2)
        #self.scene.addText("Welcome to behavioral entropy reduction system interface!")
        #self.view.setViewport(parent)
        #self.view.show()
        #int(time.mktime(time.strptime("2019-10-20 13:58:00", "%Y-%m-%d %H:%M:%S")))
        self.initialSecond =int(time.mktime(time.strptime("2019-10-20 13:58:00", "%Y-%m-%d %H:%M:%S")))
        self.pxToSecRatio = 60 # seconds per unit of the scene coordinate.
        self.timeXCenter = int(time.time()/self.pxToSecRatio) #set x=0 as current time by default
        
        self.colors = {'work':QtGui.QColor(0,200,0), 
                  'slack':QtGui.QColor(230,0,0),
                  'afk':QtGui.QColor(230,230,0),
                  'power off':QtGui.QColor(90,90,90)
                 }
        
        self.load_pixmaps()
        self.plus_icon = QtGui.QPixmap(QtCore.QString('resources/plus-black-16px.png'))
        self.ring_icon = QtGui.QPixmap(QtCore.QString('resources/ring-black-16px.png'))
        self.make_grid()
        self.add_activity_rect()
        self.view.centerOn(0,-7)
        self.action_project = []
        
        
    def load_pixmaps(self):
        import Pixmaps
        self.icons = {
                 4: Pixmaps.pxm_siga,
                 5: Pixmaps.pxm_nature,
                 6: Pixmaps.pxm_bottle,
                 7: Pixmaps.pxm_bone,
                 8: Pixmaps.pxm_jaws,
                 9: Pixmaps.pxm_sandals,
                 10:Pixmaps.pxm_obb,
                 11:Pixmaps.pxm_polovnik,
                 12:Pixmaps.pxm_grape,
                 13:Pixmaps.pxm_glasses,
                 14:Pixmaps.pxm_flywing,
                 15:Pixmaps.pxm_blueherb,
                 16:Pixmaps.pxm_banana,
                 17:Pixmaps.pxm_obb
                 }
        
    def add_item(self,item,*args, **kwargs):
        pass
    
    def remove_selected_item(self,*args,**kwargs):
        pass
    
    def propagate(self,*args,**kwargs):
        """
        Propagate the moment, evaluate readings, update UI.
        Scroll the view, move the moment border.
        
        """
        pass
        
    def change_mode(self,*args,**kwargs):
        """
        Change timeline display mode: toogle drawing metrics, change colorization,
        toogle some elements.
            Elements:
                Task metrics, event metrics, comments, media, predictions, 
                code lines, input density, activity types, differentials, integrals,
                external events (like FC price, google trends), target semantics 
                exposure, labour metrics, entropy metrics.
        """
        pass
    
    def insert_item(self,*args,**kwargs):
        """
        Insert an item and proceed with adapting the schedule.
        Choose wether to drop some items out, to move them forward, to combine
        those actions, to schedule rescheduling, to set reminders, to create conditional events.
        ===2019-12-07 17:42===
            >_< looks like a sex dimorphism ancient dick pilot operating generator..
        
        """
        pass
        
    def make_grid(self):
        opt = 1
        if opt == 0:
            self.cell_w = 30
            self.cell_h = 20
            self.pen = QtGui.QPen(QtGui.QColor(220,220,220))
            #self.scene.addLine(0,0,100,100,self.pen)
            for i in range(-20,120,10):
                self.scene.addLine(-400,i,500,i,self.pen)
            for i in range(-1600,1600,30):
                self.scene.addLine(i,-50, i, 150, self.pen)
        elif opt == 1:
            #чередующиеся цветом дни , выходные - подкрасим.
            #начиная с месяца назад, нарисовать чередующиеся ректы.
            months = {1:'JAN',2:'FEB',3:'MAR',4:'APR',5:'MAY',6:'JUN',7:'JUL',8:'AUG',9:'SEP',10:'OCT',11:'NOV',12:'DEC'}
            wdays={0:'MON',1:'TUE',2:'WED',3:'THU',4:'FRI',5:'SAT',6:'SUN'}
            start_day = "2019-10-27 00:00:00"
            format_code = "%Y-%m-%d %H:%M:%S"
            x = self.time_str_to_scene_x(start_day)
            #draw the grid from x to today+a week.
            start_day_int = time.mktime(time.strptime(start_day, format_code))
            numDays = int((time.time() - start_day_int)/(3600*24))+7
            
            pen_even =   QtGui.QPen( QtGui.QColor(255,255,255)) #color from activity name.
            brush_even = QtGui.QBrush(QtGui.QColor(255,255,255))
            pen_odd =    QtGui.QPen(QtGui.QColor(220,220,220)) #color from activity name.
            brush_odd =  QtGui.QBrush(QtGui.QColor(220,220,220))
            pen_hour = QtGui.QPen(QtGui.QColor(180,180,180))
            brush_hour = QtGui.QBrush(QtGui.QColor(180,180,180))
            
            day = start_day_int
            for i in range(numDays):
                if i%2:
                    brush = brush_even
                    pen = pen_even
                else:
                    brush = brush_odd
                    pen = pen_odd
                y = -75 #top of day frame rect.
                w = 60*24
                h = 150
                self.scene.addRect(x,y,w,h,pen,brush)
                #insert date, weekday.
                tt = time.localtime(day)
                mday,wday, mon = tt.tm_mday, wdays[tt.tm_wday], months[tt.tm_mon]
                #insert hour marks.
                
                pen = QtGui.QPen(QtGui.QColor(180,180,180))
                for i in range(1,24):
                    hx=x+i*60
                    self.scene.addLine(hx,-50,hx,75,pen)
                    hlabel = self.scene.addText(str(i))
                    hlabel.setPos(hx-7,-65)
                    
                for i in range(1,4):
                    day_label = self.scene.addText(wday.upper() + ' ' + str(mday) + ' ' + mon.upper())
                    #day_label.setPos(x+720,y)
                    day_label.setPos(x+i*360,y-2) #
                
                x +=1440
                day+=3600*24
            
            #draw_horizontals = False
            draw_horizontals = True
            if draw_horizontals:
                pen = QtGui.QPen(QtGui.QColor(180,180,180))
                gap = 20
                nGaps = 8
                for i in range(nGaps):
                    self.scene.addLine(-1000,-nGaps*gap/2 +gap*i,1000,-nGaps*gap/2+gap*i,pen)
                self.scene.addLine(-1000,0,1000,0)
                
            
    def time_str_to_scene_x(self,timestamp):
        #for now let's say 1px=1 minute. X=0 corresponds to 26-11-2019 22:20:00
        format_code = "%Y-%m-%d %H:%M:%S"
        x = int(time.mktime(time.strptime(timestamp, format_code))/self.pxToSecRatio)-self.timeXCenter
        #self.now = 
        return x
    
    def add_activity_rect(self,record=''):
        if record == '':
            #placeholder example record
            record = [999999, "2019-11-27 00:00:00",777,'work']
        x = self.time_str_to_scene_x(record[1]) #record[1] is a timestamp
        #print('add_activity_rect X:', x)
        #if x > -1*self.scene_w:
        format_code = "%Y-%m-%d %H:%M:%S"
        if int(time.mktime(time.strptime(record[1],format_code))) > self.initialSecond:
            w = record[2]/self.pxToSecRatio #duration 
            y = -40
            h = 20
            pen = QtGui.QPen(self.colors[record[3]]) #color from activity name.
            brush = QtGui.QBrush(self.colors[record[3]])
            self.scene.addRect(x,y,w,h,pen,brush)
        else:
            pass
            
    def add_bj_record_rect(self,record=''):
        pass
        
    def add_task_creation_icon(self,task_item):
        """
        TODO: check for intersection with other icon. If intersect - do smth,
        so we can see this on timeline.
        """
        time_created = task_item.time_created #string.
        if len(time_created) != 19:
            return None
        format_code = "%Y-%m-%d %H:%M:%S"
        #only render neccesary icons that are younger than self.initialSecond
        if int(time.mktime(time.strptime(time_created,format_code))) > self.initialSecond:
            x = self.time_str_to_scene_x(time_created)
            if abs(x) < 100:
                print('abs(x) < 100',task_item.id)
            pixmap=self.scene.addPixmap(self.plus_icon)
            pixmap.setPos(x,-20)
        else:
            pass
    
    def add_task_completion_icon(self,task_item):
        time_completed = task_item.time_completed #string.
        if len(time_completed) != 19:
            return None
        format_code = "%Y-%m-%d %H:%M:%S"
        #only render neccesary icons that are younger than self.initialSecond
        if int(time.mktime(time.strptime(time_completed,format_code))) > self.initialSecond:
            x = self.time_str_to_scene_x(time_completed)
            if abs(x) < 100:
                print('abs(x) < 100',task_item.id)
            pixmap=self.scene.addPixmap(self.ring_icon)
            pixmap.setPos(x,-20)
        else:
            pass
    
    def add_bj_record_icon(self,behaviour_record):
        #opt = 1
        #if opt == 1:
        #    return None
        #else:
        #    pass
        y = -4
        time_started = behaviour_record.time_started
        if len(time_started)!=19:
            return None
        format_code = "%Y-%m-%d %H:%M:%S"
        if int(time.mktime(time.strptime(time_started,format_code))) > self.initialSecond:
            x = self.time_str_to_scene_x(time_started)
            pixmap=self.scene.addPixmap(self.icons[behaviour_record.id])
            pixmap.setPos(x,y)
            w = behaviour_record.duration
            if w > 10:
                pixmap_w = pixmap.boundingRect().width()
                pixmap_h = pixmap.boundingRect().height()
                delta_w =  w - pixmap_w #if icon width is bigger than 
                #record duration (minutes=pixels AS OF NOW)
                if delta_w > 0:
                    self.scene.addLine(x + pixmap_w, y + int(pixmap_h/2), x+w, y + int(pixmap_h/2))
                    self.scene.addLine(x+w, y, x+w, y+pixmap_h)
    
    def add_work_statistics_A(self):
        """
        For each week:
            get work done (in minutes) during week.
            compare to previous week.
            draw difference.
        """
        pass
    def add_daily_stats(self,daily_stats):
        """
        Dirty prototype. 
        Improve later.
        """
        y = 20
        h = 20
        w = 1440
        prev_ratio = 0
        for day in daily_stats:
            timestamp = day['day']+' 00:00:00'
            x = self.time_str_to_scene_x(timestamp)
            ratio = day['work_to_nonwork']
            if ratio - prev_ratio > 0:
                color = QtGui.QColor(255-int(255*(ratio-prev_ratio)),255,255-int(255*(ratio-prev_ratio))) #green
            else:
                color = QtGui.QColor(255,255-int(-255*(ratio-prev_ratio)),255-int(-255*(ratio-prev_ratio))) #red
            prev_ratio = ratio
            pen = QtGui.QPen(color)
            brush = QtGui.QBrush(color)
            #self.scene.addRect(x,y,w,h,pen,brush)
            ratio_label = self.scene.addText('work:' + str(day['work'])+ '  ratio:' + str(day['work_to_nonwork']))
            ratio_label.setPos(x+720,y)
    def add_expected_behaviour_record_empty(self):
        self.add_expected_behaviour_record()
    def add_expected_behaviour_record(self,record=None,by_uuid=None):
        """
        Arguments:
            record:
                If non None, this argument must contain an object 
                describing expected behaviour record data.
                Attributes:
                    time_created varchar(24), 
                    type varchar(32),
                        #job, duty, houshold task, etc...
                    policy varchar(32),
                        #how to move other record or this one 
                        #in case of intersection\prolongation\force major
                    description varchar(1024), 
                    name varchar(256), 
                    uuid varchar(36), 
                    level int,
                    duration int,
                    time_started varchar(24), 
                    time_started_expected varchar(24), 
                    time_completed varchar(24), 
                    time_completed_expected varchar(24),  
                    status varchar(16), 
                    priority int
            by_uuid:
                If record is None and this argument contains 
                a valid uuid string - the record with this 
                uuid is fetched from DB.
        
        Valid usage:
            add_expected_behaviour_record(some_record)
            add_expected_behaviour_record()
            add_expected_behaviour_record(by_uuid='uuid_string_123456789012345')
        
        Method description:
            A) record=None
                1) Determine nearest free interval within the future timeline.
                2) Prepare dummy record with default values.
                3) Add a record rectangle to timeline scene.
                4) Start editing left border: drag and use arrows, display 
                   time_started_expected and _completed labels, 
                   check constraints,
                   press Return, 
                   edit right border the same way,
                   press Return,
                   (optionally) edit Name, priority, type, level
        """
        if record == None:
            format_code = "%Y-%m-%d %H:%M:%S"
            record = type('expected_behaviour_record',(dict,),{})()
            record.time_created = time.strftime(format_code, time.localtime())
            record.type='assignment'
            record.policy='today privilege' #find next free interval today or 
            #next record with lower priority and substitute.
            record.description = 'placeholder record description'
            record.name = 'Placeholder'
            record.uuid = uuid.uuid1()
            record.level = 1
            record.priority = 10 #highest priority means only manual interval change.
            record.duration = 15*60 #default duration in seconds = 15 minutes.
            
            #interval  =  self.get_next_free_interval(record)
            interval  =  self.get_next_free_interval()
            print('get_next_free_interval INTERVAL: ', interval.start, interval.end)
            record.time_started_expected  = interval.start
            record.time_completed_expected = interval.end
            record.time_started_expected_epoch =  interval.start_epoch
            record.time_completed_expected_epoch = interval.end_epoch
            #WE MUST LATER VERIFY actual to expected correspondence
            #UTILIZE timers.
            record.time_started = record.time_started_expected
            record.time_completed = record.time_completed_expected
            record.status = 'expected' #unverified(past), verified
            self.action_project.append(record)
            self.action_project = sorted(self.action_project,key=lambda record: record.time_started_expected_epoch)
            #ADD DB CODE HERE.
            #
            #ADD RECORD RECT.
            y =20
            h = 10 #per level
            x= self.time_str_to_scene_x(record.time_started_expected)
            w = int(record.duration / self.pxToSecRatio)
            pen = QtGui.QPen(QtGui.QColor(207,90,207))
            brush = QtGui.QBrush(QtGui.QColor(207,90,207))
            self.scene.addRect(x,y,w,h,pen,brush)

            
    def get_next_free_interval(self, record=None, format='epoch',delay=60):
        """
        Obtain the next free interval of the given duration 
        that contains no records with higher priority within
        the future timeline.
        Return an interval start in strptime format.
        
        TODO:
            (currently working on record=None case)
            duration (and other attrs) extraction from record object.
        """
        format_code = "%Y-%m-%d %H:%M:%S"
        if record == None:
            duration=15*60
            priority=5
        if len(self.action_project) == 0: #no expected behaviour has been encybered yet.
            print('get_next_free_interval EMPTY action_project')
            start_epoch = int(time.time())  + delay #delay: since NOW.
            end_epoch = start_epoch + duration
            start = time.strftime(format_code,time.localtime(start_epoch))
            end = time.strftime(format_code,time.localtime(end_epoch))
            interval = type('interval',(dict,),{})()
            interval.start_epoch = start_epoch
            interval.start = start
            interval.end_epoch = end_epoch
            interval.end = end
            interval.size = interval.end_epoch - interval.start_epoch
            if interval.size < 0:
                print('!!! [ERROR] !!! get_next_free_interval : negative interval length!')
                
            return interval
        else:
            now = int(time.time())
            #action project is the same as expected behaviour sequence\records list.
            #rename later.
            N =  len(self.action_project)
            infos = """
            LATER: 1) mind the priority, policy etc.
                   2) avoid epoch->string conversion, add start/end_epoch values
                      directly as record attributes
            """
            for ind, expected_behaviour in enumerate(self.action_project):
                if int(time.mktime(time.strptime(expected_behaviour.time_completed, format_code))) < now:
                    continue #skip past records.
                #check for a time gap (and priority) between the currently indexed and the next record.
                if ind+1 == N: #this is the last record. Return the undefined future.
                    interval = type('interval',(dict,),{})()
                    interval.start = expected_behaviour.time_completed_expected
                    interval.start_epoch = int(time.mktime(time.strptime( interval.start,format_code)))
                    interval.end_epoch = interval.start_epoch + duration
                    interval.end = time.strftime(format_code, time.localtime(interval.end_epoch))
                    #if format == 'epoch':
                    #    return 
                    return interval
                else:
                    #check for a gap between the current and the next record.
                    interval = type('interval',(dict,),{})()
                    interval.start = expected_behaviour.time_completed_expected
                    interval.start_epoch = expected_behaviour.time_completed_expected_epoch
                    next_record = self.action_project[ind+1]
                    interval.end = next_record.time_started_expected
                    interval.end_epoch = next_record.time_started_expected_epoch
                    gap_size = interval.end_epoch - interval.start_epoch
                    if gap_size >= duration:
                        #found matching interval. return it.
                        interval.end_epoch = interval.start_epoch + duration
                        interval.end = time.strftime(format_code, time.localtime(interval.end_epoch))
                        return interval
                    else:
                        continue #keep on looking.
