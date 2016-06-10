#!/usr/bin/python3
# coding: utf-8


import sys
import os
import re
import yaml
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QGroupBox, QAction,
                             QTextEdit, QVBoxLayout,QHBoxLayout, QGridLayout, QSplitter, 
                             QTableWidget, QTableWidgetItem, QCommonStyle, QTreeWidget, QTreeWidgetItem,
                             QAbstractItemView, QHeaderView, QMainWindow, QApplication)

from PyQt5.QtGui  import  QIcon, QBrush, QColor
from PyQt5.QtCore import QSettings, pyqtSignal


#-------------------------------------------------------------------------------
class Inspector(QTreeWidget):
    
    def __init__(self, parent):
        super().__init__(parent)
        #self.setAlternatingRowColors(True)
        self.setIndentation(16)
        self.setColumnCount(2)
        #self.header().resizeSection(0, 150)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        #self.header().setStretchLastSection(False)
        self.setHeaderLabels( ('Property', 'Value') );
        self.std_items   = self.addParent(self, 0, 'Standard', 'slon')
        self.usr_items   = self.addParent(self, 0, 'User Defined', 'mamont')
        self.field_items = self.addParent(self, 0, 'Field Details', '')
        
        self.addChild(self.std_items, 0, 'Ref', '?')
        self.addChild(self.std_items, 0, 'LibName', '~')
        self.addChild(self.std_items, 0, 'Value', '~')
        self.addChild(self.std_items, 0, 'Footprint', '~')
        self.addChild(self.std_items, 0, 'DocSheet', '~')
        self.addChild(self.std_items, 0, 'X', '~')
        self.addChild(self.std_items, 0, 'Y', '~')
        self.addChild(self.std_items, 0, 'Timestamp', '~')
    
        self.addChild(self.usr_items, 0, '<empty>', '?')

        self.addChild(self.field_items, 0, '<empty>', '?')
            
        
    def addParent(self, parent, column, title, data):
        item = QTreeWidgetItem(parent, [title])
        item.setData(column, Qt.UserRole, data)
        item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        item.setExpanded (True)
#       item.setBackground( 0, QBrush(QColor('#FFDCA4'), Qt.SolidPattern) )
#       item.setBackground( 1, QBrush(QColor('#FFDCA4'), Qt.SolidPattern) )
        return item
        
        
    def addChild(self, parent, column, title, data):
        item = QTreeWidgetItem(parent, [title])
        item.setData(column, Qt.UserRole, data)
        #item.setCheckState (column, Qt.Unchecked)
        return item
            
    def set_data(self, item, column, role):
        pass;
    
    def load(self, refs):
        
        comp = refs[0][0]
        
        print( (comp.__dict__) )
        #print(self.topLevelItem(0).childCount())
        for f in comp.Fields:
            print(f.InnerCode)
        
        for i in range( self.topLevelItem(0).childCount() ):
            item = self.topLevelItem(0).child(i)

            if item.data(0, Qt.DisplayRole) == 'Ref':
                item.setData(1, Qt.DisplayRole, comp.Ref)
                
            if item.data(0, Qt.DisplayRole) == 'LibName':
                item.setData(1, Qt.DisplayRole, comp.LibName)
                
            if item.data(0, Qt.DisplayRole) == 'Value':
                item.setData(1, Qt.DisplayRole, comp.Fields[1].Text)
                
            if item.data(0, Qt.DisplayRole) == 'Footprint':
                item.setData(1, Qt.DisplayRole, comp.Fields[2].Text)
                
            if item.data(0, Qt.DisplayRole) == 'DocSheet':
                item.setData(1, Qt.DisplayRole, comp.Fields[3].Text)
                
            if item.data(0, Qt.DisplayRole) == 'X':
                item.setData(1, Qt.DisplayRole, comp.PosX)
                                
            if item.data(0, Qt.DisplayRole) == 'Y':
                item.setData(1, Qt.DisplayRole, comp.PosY)
                
            if item.data(0, Qt.DisplayRole) == 'Timestamp':
                item.setData(1, Qt.DisplayRole, comp.Timestamp)
        
        
#-------------------------------------------------------------------------------
class ComponentsTable(QTableWidget):
    
    cells_choosen = pyqtSignal([list])
    
    def __init__(self, parent):
        super().__init__(0, 2, parent)
        
        self.cellActivated.connect(self.cell_activated)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # select whole row
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)   # disable edit cells

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(20)
        self.setHorizontalHeaderLabels( ('Ref', 'Name') )

        b   = read_file('det-1/det-1.sch')
        rcl = raw_cmp_list(b)
        ipl = ['LBL'] 
        self.CmpDict = cmp_dict(rcl, ipl)
        self.update_cmp_list(self.CmpDict)
        
                
    #---------------------------------------------------------------------------    
    def cell_activated(self, row, col):
        items = self.selectedItems()
        refs = []
        for i in items:
            if i.column() == 0:
                refs.append( self.CmpDict[i.data(Qt.DisplayRole)] )
        
        print('emit "cells_choosen"')
        self.cells_choosen.emit(refs)
        
                        
    #---------------------------------------------------------------------------    
    def update_cmp_list(self, cd):

        keys = list( cd.keys() )
        keys.sort( key=split_alphanumeric )    

        self.setRowCount(len(cd))

        for idx, k in enumerate( keys ):
            Name = QTableWidgetItem(cd[k][0].LibName)
            Ref  = QTableWidgetItem(k)
          #  print(ref + ' ' + cd[ref].Name)
            self.setItem(idx, 0, Ref)
            self.setItem(idx, 1, Name)
                                        
#-------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        #----------------------------------------------------
        #
        #    Main Window
        #
        work_zone = QWidget(self)
        Layout    = QHBoxLayout(work_zone)
        self.setCentralWidget(work_zone)
        
        exitAction = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)        
        
        self.statusBar().showMessage('Ready')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAction)        
        
        self.CmpTabBox    = QGroupBox('Components', self)
        self.CmpTabLayout = QVBoxLayout(self.CmpTabBox)
        self.CmpTabLayout.setContentsMargins(4,10,4,4)
        self.CmpTabLayout.setSpacing(10)
        
        self.CmpTabLayout.setSizeConstraint(QVBoxLayout.SetMaximumSize)
        
        #----------------------------------------------------
        #
        #    Components table
        #
        self.CmpTable       = ComponentsTable(self) 
        self.CmpChooseButton = QPushButton('Choose', self)
        
        self.CmpTabLayout.addWidget(self.CmpTable)
        self.CmpTabLayout.addWidget(self.CmpChooseButton)
        
                
        #----------------------------------------------------
        #
        #    Select View
        #
        self.SelectView = QTreeWidget(self)
        self.SelectView.setColumnCount(2)
        self.SelectView.setHeaderLabels( ('Property', 'Value') );

        self.SVTopItem = QTreeWidgetItem(self.SelectView)
        self.SVTopItem.setText(1, 'Standard')
        
        self.SVItem1 = QTreeWidgetItem(self.SVTopItem)
        self.SVItem1.setText(0, 'sub-slonick')
        
        #----------------------------------------------------
        #
        #    Inspector
        #
        self.Inspector = Inspector(self)
        
        self.InspectorBox    = QGroupBox('Inspector', self)
        self.InspectorLayout = QVBoxLayout(self.InspectorBox)
        self.InspectorLayout.setContentsMargins(4,10,4,4)
        self.InspectorLayout.setSpacing(10)
        
        self.InspectorLayout.addWidget(self.Inspector)
                
        #----------------------------------------------------

        self.Splitter = QSplitter(self)
        self.Splitter.addWidget(self.CmpTabBox)
        self.Splitter.addWidget(self.SelectView)   
        self.Splitter.addWidget(self.InspectorBox) 
                 
        self.centralWidget().layout().addWidget(self.Splitter)
        
        
        #----------------------------------------------------
        self.CmpTable.cells_choosen.connect(self.Inspector.load)

        #----------------------------------------------------
        #
        #    Window
        #
        self.setWindowTitle('KiCad Schematic Component Manager')
        Settings = QSettings('kicad-tools', 'Schematic Component Manager')
        print(Settings.allKeys())
        if Settings.contains('geometry'):
            self.restoreGeometry( Settings.value('geometry') )
        else:
            self.setGeometry(100, 100, 1024, 768)

        if Settings.contains('cmptable'):
            w0, w1 = Settings.value('cmptable')
            self.CmpTable.setColumnWidth( 0, int(w0) )
            self.CmpTable.setColumnWidth( 1, int(w1) )
            
        if Settings.contains('splitter'):
            self.Splitter.restoreState( Settings.value('splitter') )
            
        self.show()
        
                
    #---------------------------------------------------------------------------    
    def closeEvent(self, event):
        print('close app')
        Settings = QSettings('kicad-tools', 'Schematic Component Manager')
        Settings.setValue( 'geometry', self.saveGeometry() )
        Settings.setValue( 'cmptable', [self.CmpTable.columnWidth(0), self.CmpTable.columnWidth(1)] )
        Settings.setValue( 'splitter', self.Splitter.saveState() )
        QWidget.closeEvent(self, event)
        
        

#-------------------------------------------------------------------------------
class ComponentField:
    
    def __init__(self, rec):

        self.InnerCode = rec[0]
        
        if self.InnerCode == '0':
            self.Name = 'Ref'
        elif self.InnerCode == '1':
            self.Name = 'Value'
        elif self.InnerCode == '2':
            self.Name = 'Footprint'
        elif self.InnerCode == '3':
            self.Name = 'DocSheet'
        else:
            self.Name = rec[11]
            
        self.Text        = rec[1]
        self.Orientation = rec[2]
        self.PosX        = rec[3]
        self.PosY        = rec[4]
        self.FontSize    = rec[5]
        self.Visible     = True if int(rec[6]) == 0 else False
        self.HJustify    = rec[7]
        self.VJustify    = rec[8]
        self.FontItalic  = rec[9]
        self.FontBold    = rec[10]
    
class Component:
    
    def __init__(self):
        self.Ref = '~'
        self.LibName = '~'
        
    def parse_comp(self, rec):
        r = re.search('L ([\w-]+) ([\w#]+)', rec)
        if r:
            self.LibName, self.Ref = r.groups()
        else:
            print('E: invalid component L record, rec: "' + rec + '"')
            sys.exit(1)
            
        r = re.search('U (\d+) (\d+) ([\w\d]+)', rec)

        if r:
            self.PartNo, self.mm, self.Timestamp = r.groups()
        else:
            print('E: invalid component U record, rec: "' + rec + '"')
            sys.exit(1)

        r = re.search('P (\d+) (\d+)', rec)
        if r:
            self.PosX, self.PosY = r.groups()
        else:
            print('E: invalid component P record, rec: "' + rec + '"')
            sys.exit(1)
            
        cfre = re.compile('F\s+(\d+)\s+\"(.*?)\"\s+(H|V)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([LRCBT])\s+([LRCBT])([NI])([NB])\s+(?:\"(.*)\")*')
        r = re.findall(cfre, rec)
        
        r.sort(key=lambda x: int(x[0]))
        
        self.Fields = []
        for i in r:
            self.Fields.append( ComponentField(i) )
        
#       for i in self.Fields:
#           print(vars(i))
#
#       print('***********************')
            
        
#-------------------------------------------------------------------------------
def split_alphanumeric(x):
    r = re.split('(\d+)', x)
    
    return ( r[0], int(r[1]) )
#-------------------------------------------------------------------------------
def read_file(fname):
    with open(fname, 'rb') as f:
        b = f.read()
        
    return b.decode()
#-------------------------------------------------------------------------------
def raw_cmp_list(s):
    pattern = '\$Comp\n((?:.*\n)+?)\$EndComp'
    res = re.findall(pattern, s)
    
    return res

#-------------------------------------------------------------------------------
def cmp_dict(rcl, ipl):   # rcl: raw component list; ipl: ignore pattern list
    
    cdict = {}
    
    for i in rcl:
        cmp = Component()
        cmp.parse_comp(i)
        ignore = False
        for ip in ipl:
            r = re.search(ip+'.*\d+', cmp.Ref)
            if r:
                ignore = True
                continue
           
        if ignore:
            continue
            
        if not cmp.Ref in cdict:
            cdict[cmp.Ref] = []

        cdict[cmp.Ref].append(cmp)
     
        
           
    return cdict
#-------------------------------------------------------------------------------
if __name__ == '__main__':

    app  = QApplication(sys.argv)
    app.setStyleSheet('QGroupBox {\
                           border: 2px solid gray;\
                           border-radius: 4px;\
                           margin: 0px;\
                           margin-top: 1ex;\
                           padding: 0px;\
                           font-size: 12pt;\
                           font-weight: bold;\
                       }\
                       QGroupBox::title {\
                           subcontrol-origin: margin;\
                           subcontrol-position: top left;\
                           padding: 0px;\
                           left: 20px;\
                       }\
                      Inspector {\
                        alternate-background-color: #ffffd0;\
                      }\
                       Inspector {\
                           show-decoration-selected: 1;\
                       }\
                       QTreeView::item {\
                           border: 1px solid #d9d9d9;\
                           border-top-color: #d9d9d9;\
                           border-left-color: transparent;\
                           border-bottom-color: transparent;\
                       }\
                       QTreeView::item:has-children {\
                           left: 18px;\
                           background-color: #FFDCA4;\
                           border: 1px solid #d9d9d9;\
                           border-top-color: #d9d9d9;\
                           border-left-color: transparent;\
                           border-right-color: transparent;\
                           border-bottom-color: transparent;\
                       }\
                       QTreeWidget::item:hover {\
                           background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);\
                           border: 1px solid #bfcde4;\
                       }\
                       QTreeWidget::item:selected {\
                           border: 1px solid #567dbc;\
                       }\
                       QTreeWidget::item:selected:active{\
                           background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);\
                       }\
                       QTreeWidget::item:selected:!active {\
                           background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6b9be8, stop: 1 #577fbf);\
                       }'
                      )
    
    
     #background-color: #fffff0;\
    #                           border-top-color: transparent;\
    #                           border-bottom-color: transparent;\
    
    mwin = MainWindow()

    sys.exit( app.exec_() )
#-------------------------------------------------------------------------------


