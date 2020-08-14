import codecs
files = ['TSW-1.py', 
        'StorageQt.py',
        'Sound.py', 
        'BehaviourJournal.py',
        'ReminderJackWidget.py',
        'NewTaskDialog.py',
        'AnimatedTray.py',
        'Camera.py',
        'TabSettingsWidget.py',
        'Task.py',
        'KeyboardLog.py',
        'ScreenCapturer.py'
        ]
        
LINES = []
ls = set()
n_all =0
n_u  = 0
for fname in files:
    with codecs.open(fname,'r',encoding='utf-8') as f:
        lines = f.readlines()
        n_all+=len(lines)
        LINES+=lines

n_u = len(set(tuple(LINES)))
print('all: ', n_all)
print('unique: ', n_u)


def splitter(line):
    if len(line) == 0:
        return []
    line=line.strip().replace('\n','').replace('\r','')
    #print(line)
    res = ''
    #for index,c in enumerate(line):
    for c in line:
        #if not c.isalpha() and c != ' ':
        if not c.isalpha() and c != ' ' :
            res+=' '
        else:
            res+=c

    res=res.replace('  ',' ')
    res=res.replace('   ',' ')
    res=res.replace('    ',' ')
    res=res.replace('     ',' ')
    #print(len(res.split(' ')),res.split(' '))
    return [item for item in res.split(' ') if len(item) > 2 ]

tokens=[]
for l in LINES:
    if l != '':
        tokens += splitter(l)
print(tokens)
i = input()

tokens = list(set(tuple(tokens)))
tokens.sort()
with codecs.open('tokens_9-11-2019.txt', 'a+',encoding='utf-8') as f:
    for i,t in enumerate(tokens):
        print(i,t)
        f.write(t+'\n')
print(list(zip(tokens,range(0,len(tokens)-1))))
"""    
tokens = {}
for l in LINES:
    if len(l.strip()) != 0 and l.strip()[0] != #:
        _l = l
        for index, c in enumerate(l):
            if c == '#':
                _l = l[:index]
                break
"""