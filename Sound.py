##################   79 characters   #########################################
##################   as said in PEP  #########################################

from PyQt4 import QtCore, QtGui, QtTest,QtSql
import time, os, sys, random
import keyboard

class Sound(QtCore.QObject):
    def __init__(self):
        super(QtCore.QObject, self).__init__()
        resources_dir = "resources\sounds"
        self.sounds_filenames = os.listdir(resources_dir)
        self.qsounds = [QtGui.QSound(resources_dir+"\\"+sound) for sound in self.sounds_filenames]
        self.sounds = dict(zip(self.sounds_filenames, self.qsounds))
        #trying async call to sound.target:
        #self.target = QtGui.QSound(resources_dir+"\\priest_lexaeterna.wav")
        
    def play_random_sound(self):
        which = random.randint(0, len(self.qsounds) -1)
        #print(self.sounds_filenames[which])
        self.sounds[self.sounds_filenames[which]].play()

    def short_click(self):
        self.sounds['SHORT-red_eruma_damage-5-percent.wav'].play()
    
    def complete(self):
        self.sounds['sonic-final-check.wav'].play()

    def jump(self):
        jumps = ['sonic-jump-spring.wav','sonic-jump.wav']
        which = random.randint(0,1)
        jump = jumps[which]
        self.sounds[jump].play()

    def hit(self):
        hits = [hit for hit in list(filter(lambda x: '_hit' in x, self.sounds_filenames))]
        which = random.randint(0, len(hits) -1)
        self.sounds[hits[which]].play()
    
    def hop_up(self):
	    # yoyo_hop2.wav
        self.sounds['yoyo_hop2.wav'].play()

    def hop_down(self):
        self.sounds['worm_tail_die.wav'].play()
	
    def sort_cycle(self):
        sounds = ['teddy_bear_move.wav','horong_attack.wav']
        which = random.randint(0, len(sounds) -1)
        self.sounds[sounds[which]].play()
    
    def deleted(self):
        sounds = ['apocalips_h_attack.wav','aqua_elemental_atk.wav', 'martin_die.wav']
        #sounds = ['martin_die.wav']
        which = random.randint(0, len(sounds) -1)
        self.sounds[sounds[which]].play()
        #self.sounds['martin_die.wav'].play()

    def restart(self):
        self.sounds['long-reloading-1.wav'].play()

    def open_stash(self):
        self.sounds['ef_coin.wav'].play()
     
    def phase_change(self):
        self.sounds['sonic_pshhhhhj.wav'].play()
    def error(self):
        self.sounds['sonic-lose-rings.wav'].play()
    def poof(self):		
        self.sounds['sonic_pooop.wav'].play()
    def initiate(self): #used for WORK initiation.
        work_sounds = ["ac_concentration.wav",
        "black_maximize_power_sword_bic.wav",
        "black_overthrust.wav",
        "black_weapon_perfection.wav",
        "lg_prestige.wav",
        "priest_lexaeterna.wav",
        ]
        which = random.randint(0,3)
        self.sounds[work_sounds[which]].play()
    
    def inhibit(self):
        inhibit_sounds = [
        "ef_decagility.wav",
        "priest_slowpoison.wav",
        "fshoooo.wav"
        ]
        which = random.randint(0,2)
        self.sounds[inhibit_sounds[which]].play()
    
    def target(self):
        print('Sound.target:')
        self.sounds['priest_lexaeterna.wav'].play()
        
if __name__ == '__main__':
    s = Sound()
    s.play_random_sound()
    time.sleep(1)
    s.play_random_sound()
    time.sleep(1)
    s.play_random_sound()
    time.sleep(1)
    s.play_random_sound()
    time.sleep(1)