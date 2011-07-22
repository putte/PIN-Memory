#!/usr/bin/python
#
# PINmemory - Personal Information Number storage using AES encryption
# 
# Copyright (c) 2009 Patrik Sandenvik
# 
# Licensed under the MIT License ( http://www.opensource.org/licenses/mit-license.php ):
#
__exec_path = "E:\\Python\\"

import appuifw
import e32
import sys
import md5
sys.path.append(__exec_path)
from aes import AESModeOfOperation
from db import db
from os import remove

class Cipher:
    def __init__(self,pwd):
        self.iv = [205,87,67,187,30,243,198,109,254,157,203,98,125,100,34,222]
        self.moo = AESModeOfOperation()  
        m = md5.new()
        m.update(pwd)
        s = m.hexdigest()
        self.key = []
        for i in [0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]:
            self.key.append(int(s[i:i+2],16))

    def encrypt(self,input):
        mode,orig_len,outList=self.moo.encrypt(input,self.moo.modeOfOperation["OFB"],self.key,self.moo.aes.keySize["SIZE_128"],self.iv)
        ciph = u""
        for i in range(orig_len):
            ciph += unichr(outList[i])
        return ciph

    def decrypt(self, ciph):
        inList=[]
        for c in ciph:
            inList.append(ord(c))
        output = self.moo.decrypt(inList,None,self.moo.modeOfOperation["OFB"],self.key,self.moo.aes.keySize["SIZE_128"],self.iv)
        return unicode(output, "utf-8", 'ignore')
        
class Model:
    def __init__(self,pwd):
        dbFileName = 'C:\\data\\PINmemory.db'
        self.mydb = db(dbFileName)
        self.ciph = Cipher(pwd)
        try:
            # Check if tables exists
            self.mydb.query("select keyword from password")
        except SymbianError, (errno, errtext):
            if errno==-1: #kErrNotFound
                self.mydb.query("create table password (id counter, keyword varchar)")
                self.mydb.query("create table pincodes (id counter, name varchar, pin varchar)")
            else:
                print "Unexpected error:", errno
                raise

    def getKeyword(self):
        try:
            self.mydb.query("select keyword from password")
        except SymbianError, (errno, errtext):
            if errno==-1: #kErrNotFound
                return ''
        for row in self.mydb:
            kwd = self.ciph.decrypt(row[0])
            if kwd:
                return kwd
            else:
                return u"Invalid!"

    def initKeyword(self,kwd):
        self.mydb.query("insert into password (keyword) values ('%s')" % self.ciph.encrypt(kwd))

    def setKeyword(self,kwd):
        self.mydb.query("delete from password")
        self.initKeyword(kwd)

    def getCodeList(self):
        self.mydb.query("select name,pin,id from pincodes")
        codeList = []
        for row in self.mydb:
            codeList.append((row[0],self.ciph.decrypt(row[1]),row[2]))
        return codeList

    def addCode(self,name,pin):
        self.mydb.query("insert into pincodes (name,pin) values ('%s','%s')" % (name,self.ciph.encrypt(pin)))

    def deleteCode(self,id):
        self.mydb.query("delete from pincodes where id=%s" % id)

    def resetDatabase(self):
        self.mydb.query("delete from pincodes")
        self.mydb.query("delete from password")
        
class View:
    def __init__(self):
        appuifw.app.screen='normal'
        appuifw.app.body=None
        self.script_lock = e32.Ao_lock()
        self.title = appuifw.app.title=u'PINmemory'
        self.menu = [(u'Add', self.add),
                     (u'Edit', self.edit),
                     (u'Delete', self.delete),
                     (u'System...', ((u'Help', self.help),
                                     (u'Reset', self.reset),
                                     (u'Set control word', self.updateKeyword),
                                     (u'About', self.about)))] 
        appuifw.app.exit_key_handler = self.destroy
        self.startModel()
        self.script_lock.wait()

    def startModel(self):
        while True:
            pwd = appuifw.query(u'Enter password:', 'code')
            if pwd: break
            else: appuifw.note(u'Password must be set','error')
        self.myModel = Model(pwd)
        self.checkKeyword()
        self.handleRedraw()

    def handleRedraw(self):
        appuifw.app.menu=self.menu
        self.entries = sorted(self.myModel.getCodeList())
        self.codeList = []
        for i in range(len(self.entries)):
            self.codeList.append(self.entries[i][0:2])
        if self.codeList:
            self.lb = appuifw.Listbox(self.codeList,self.shout)
            appuifw.app.body=self.lb
        else:
            #No entries available, show blank screen
            appuifw.app.body=None

    def checkKeyword(self):
        kwd = self.myModel.getKeyword()
        if kwd:
            appuifw.note(u'Control word:\n%s' % kwd,'info')
        else:
            while True:
                kwd = appuifw.query(u'Enter control word:', 'text')
                if kwd: break
                else: appuifw.note(u'Control word must be set','error')
            self.myModel.initKeyword(kwd)
            appuifw.note(u'Control word set to: %s' % kwd, 'conf')

    def reset(self):
        if appuifw.query(u'Are you sure you want to reset? All PINs will be lost.', 'query'):
            self.myModel.resetDatabase()
            del self.myModel
            appuifw.app.body=None
            appuifw.note(u'Reset done','conf')
            self.startModel()

 
    def updateKeyword(self):
        kwd = self.myModel.getKeyword()
        newKwd = appuifw.query(u'Enter control word:', 'text', kwd)
        if newKwd:
            self.myModel.setKeyword(newKwd)
            appuifw.note(u'Control word set to: %s' % newKwd, 'conf')
 
    def destroy(self):
        appuifw.app.exit_key_handler = None
        self.script_lock.signal()

    def add(self):
        name = appuifw.query(u'Name:','text')
        if name:
            pin  = appuifw.query(u'PIN:','text')
            if pin:
                self.myModel.addCode(name,pin)
                self.handleRedraw()
                appuifw.note(u'%s added' % name, 'conf')

    def edit(self):
        if appuifw.app.body:
            index = self.lb.current()
            name = self.entries[index][0]
            pin  = self.entries[index][1]
            newName = appuifw.query(u'Name:','text', name)
            if newName:
                newPin  = appuifw.query(u'PIN:','text', pin )
                if newPin:
                    self.myModel.deleteCode(self.entries[index][2])
                    self.myModel.addCode(newName,newPin)
                    appuifw.note(u'%s updated' % newName, 'conf')
                    self.handleRedraw()
        else:
            appuifw.note(u'Nothing to edit', 'error')
                
    def delete(self):
        if appuifw.app.body:
            index = self.lb.current()
            name = self.entries[index][0]
            if appuifw.query(u'Delete %s?' % name, 'query'):
                self.myModel.deleteCode(self.entries[index][2])
                self.handleRedraw()
                appuifw.note(u'%s deleted' % name, 'conf')
        else:
            appuifw.note(u'Nothing to delete', 'error')

    def help(self):
        helpText = u"""Use only characters [a-z,A-Z,0-9] for PINs and control word"""
        appuifw.note(helpText, 'info')

    def about(self):
        aboutText = u"""PINmemory
Copyright \xa9 2009
Patrik Sandenvik"""
        appuifw.note(aboutText, 'info')

    def shout(self):
        index = self.lb.current()
        appuifw.note(u'%s\n%s' % (self.entries[index][0],self.entries[index][1]), 'info')
        

View()
