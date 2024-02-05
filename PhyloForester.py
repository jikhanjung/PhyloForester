from PyQt5.QtWidgets import QMainWindow, QHeaderView, QApplication, QAbstractItemView, \
                            QMessageBox, QTreeView, QTableView, QSplitter, QAction, QMenu, \
                            QStatusBar, QInputDialog, QToolBar, QTabWidget, QTabBar
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QKeySequence, QColor
from PyQt5.QtCore import Qt, QRect, QSortFilterProxyModel, QSettings, QSize, QTranslator, QModelIndex, QEvent, QProcess

from PyQt5.QtCore import pyqtSlot, pyqtSignal
import re,os,sys
from pathlib import Path
from peewee import *
from PIL.ExifTags import TAGS
import shutil, platform
import copy
import PfUtils as pu
from PfModel import *
from PfDialog import *


ICON = {}
ICON['new_project'] = pu.resource_path('icons/NewProject.png')
ICON['project'] = pu.resource_path('icons/Project.png')
ICON['datamatrix'] = pu.resource_path('icons/Datamatrix.png')
ICON['analysis'] = pu.resource_path('icons/Analysis.png')
ICON['preferences'] = pu.resource_path('icons/Preferences.png')
ICON['about'] = pu.resource_path('icons/About.png')
ICON['exit'] = pu.resource_path('icons/exit.png')

class PfTreeView(QTreeView):
    mousePressed = pyqtSignal(QEvent)
    def mousePressEvent(self, event):
        self.mousePressed.emit(event)
        super().mousePressEvent(event)


class PfTabBar(QTabBar):
    tabClicked = pyqtSignal(int)
    def __init__(self, parent=None):
        super(PfTabBar, self).__init__(parent)
        self._editor = QLineEdit(self)
        self._editor.setWindowFlags(Qt.Popup)
        self._editor.hide()
        self._editor.editingFinished.connect(self.finishEditing)

    def mousePressEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0:
            print(f"Tab {index} clicked")
            self.tabClicked.emit(index)             
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0:
            self.editTab(index)

    def editTab(self, index):
        rect = self.tabRect(index)
        globalRect = self.mapToGlobal(rect.topLeft())  # Map rect to global coordinates
        self._editor.setGeometry(globalRect.x(), globalRect.y(), rect.width(), rect.height())        
        #self._editor.setGeometry(rect)
        self._editor.setText(self.tabText(index))
        self._editor.show()
        self._editor.setFocus()
        self._editor.selectAll()
        self._current_index = index
        self._original_text = self.tabText(index)  # Store the original text

    def finishEditing(self):
        #new_text = self._editor.text()
        self._editor.hide()
        new_text = self._editor.text()
        # Check if the text has actually changed
        if new_text and new_text != self._original_text:
            self.setTabText(self._current_index, new_text)

            # Change the background color of the edited tab
            self.setTabBackgroundColor(self._current_index, QColor("yellow"))  # Set the desired color
        else:
            # No change in text, you can add logic here if needed
            pass

        self._editor.hide()

    def setTabBackgroundColor(self, index, color):
        # Apply style sheet to change the background color of the specific tab
        self.setStyleSheet(f"QTabBar::tab:{{background: {color.name()};}}")

class PfTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super(PfTabWidget, self).__init__(parent)
        self.selected_index = -1
        self.tabBar = PfTabBar(self)
        self.setTabBar(self.tabBar)
        self.tabBar.tabClicked.connect(self.onTabClicked)

    def onTabClicked(self, index):
        self.selected_index = index
        print(f"Tab {index} clicked in parent window")
        self.main_window.tabView_changed(index)
        #selected_datamatrix = self.main_window.datamatrix_list[index]



class PfTableView(QTableView):
    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            if not self.isPersistentEditorOpen(self.currentIndex()):
                self.edit(self.currentIndex())
        else:
            super().keyPressEvent(event)

    def isPersistentEditorOpen(self, index):
        return self.indexWidget(index) is not None
    
class PfItemModel(QStandardItemModel):
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            current_value = self.data(index, role)
            if current_value == value:
                return False
            # Change color if the data changes
            result = super(PfItemModel, self).setData(index, value, role)
            if result:
                self.dataChanged.emit(index, index, [Qt.BackgroundRole])
                self.itemFromIndex(index).setBackground(QColor('yellow'))
            return result
        return False
    
    def resetColors(self):
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                item = self.item(row, column)
                if item is not None:
                    item.setBackground(QColor('white'))  # Or any default color

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        #if index.column() == 0:  # Replace with your column number
        #    return super().flags(index) & ~Qt.ItemIsEditable
        return super().flags(index)

    #def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.DisplayRole):
    #    if role == Qt.TextAlignmentRole:
    #        return Qt.AlignCenter  # Align text center

class PhyloForesterMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(pu.resource_path('icons/PhyloForester.png')))
        self.setWindowTitle("{} v{}".format(self.tr("PhyloForester"), pu.PROGRAM_VERSION))

        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(32,32))

        self.actionNewProject = QAction(QIcon(pu.resource_path(ICON['new_project'])), self.tr("New Project\tCtrl+N"), self)
        self.actionNewProject.triggered.connect(self.on_action_new_project_triggered)
        self.actionNewProject.setShortcut(QKeySequence("Ctrl+N"))

        self.actionPreferences = QAction(QIcon(pu.resource_path(ICON['preferences'])), "Preferences", self)
        self.actionPreferences.triggered.connect(self.on_action_edit_preferences_triggered)
        self.actionExit = QAction(QIcon(pu.resource_path(ICON['exit'])), "Exit\tCtrl+W", self)
        self.actionExit.triggered.connect(self.on_action_exit_triggered)
        self.actionExit.setShortcut(QKeySequence("Ctrl+W"))
        self.actionAbout = QAction(QIcon(pu.resource_path(ICON['about'])), "About\tF1", self)
        self.actionAbout.triggered.connect(self.on_action_about_triggered)
        self.actionAbout.setShortcut(QKeySequence("F1"))

        self.toolbar.addAction(self.actionNewProject)
        self.toolbar.addAction(self.actionPreferences)
        self.toolbar.addAction(self.actionAbout)
        self.addToolBar(self.toolbar)

        self.main_menu = self.menuBar()
        self.file_menu = self.main_menu.addMenu("File")
        self.file_menu.addAction(self.actionExit)
        self.edit_menu = self.main_menu.addMenu("Edit")
        self.edit_menu.addAction(self.actionPreferences)
        self.data_menu = self.main_menu.addMenu("Data")
        self.data_menu.addAction(self.actionNewProject)


        self.m_app = QApplication.instance()
        self.m_app.toolbar_icon_size = "Small"
        self.read_settings()

        self.initUI()
        self.check_db()

        self.reset_views()
        self.load_treeview()

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(self.tr("Ready"))

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
        self.process.readyReadStandardError.connect(self.onReadyReadStandardError)
        self.process.finished.connect(self.onProcessFinished)
        self.process.errorOccurred.connect(self.handleError)
        self.edtAnalysisOutput = QTextEdit()


    @pyqtSlot()
    def on_action_new_project_triggered(self):
        # open new project dialog
        #return
        self.dlg = ProjectDialog(self)
        self.dlg.setModal(True)

        ret = self.dlg.exec_()
        self.load_treeview()
        self.reset_tableView()

    @pyqtSlot()
    def on_action_edit_preferences_triggered(self):
        #print("edit preferences")
        self.preferences_dialog = PreferencesDialog(self)
        #self.preferences_dialog.setWindowModality(Qt.ApplicationModal)
        self.preferences_dialog.show()

    @pyqtSlot()
    def on_action_about_triggered(self):
        return

    @pyqtSlot()
    def on_action_exit_triggered(self):
        return

    def set_toolbar_icon_size(self, size):
        if size.lower() == 'small':
            self.toolbar.setIconSize(QSize(24,24))
        elif size.lower() == 'medium':
            self.toolbar.setIconSize(QSize(32,32))
        else:
            self.toolbar.setIconSize(QSize(48,48))

    def update_settings(self):
        #print("update settings bgcolor",self.preferences_dialog.bgcolor)
        size = self.m_app.toolbar_icon_size
        self.set_toolbar_icon_size(size)

    def read_settings(self):
        #self.m_app.settings = QSettings(QSettings.IniFormat, QSettings.UserScope,pu.COMPANY_NAME, pu.PROGRAM_NAME)
        self.m_app.storage_directory = os.path.abspath(pu.DEFAULT_STORAGE_DIRECTORY)
        self.m_app.toolbar_icon_size = self.m_app.settings.value("ToolbarIconSize", "Medium")
        self.m_app.remember_geometry = pu.value_to_bool(self.m_app.settings.value("WindowGeometry/RememberGeometry", True))
        if self.m_app.remember_geometry is True:
            #print('loading geometry', self.remember_geometry)
            self.setGeometry(self.m_app.settings.value("WindowGeometry/MainWindow", QRect(100, 100, 1400, 800)))
        else:
            self.setGeometry(QRect(100, 100, 1400, 800))

    def write_settings(self):
        self.m_app.remember_geometry = pu.value_to_bool(self.m_app.settings.value("WindowGeometry/RememberGeometry", True))
        if self.m_app.remember_geometry is True:
            self.m_app.settings.setValue("WindowGeometry/MainWindow", self.geometry())

    def check_db(self):
        gDatabase.connect()
        tables = gDatabase.get_tables()
        if tables:
            return
            print(tables)
        else:
            gDatabase.create_tables([PfProject, PfDatamatrix,PfAnalysis])

    def closeEvent(self, event):
        self.write_settings()
        #if self.analysis_dialog is not None:
        #    self.analysis_dialog.close()
        event.accept()

    def initUI(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(self.tr("Ready"))

        self.hsplitter = QSplitter(Qt.Horizontal)


        self.treeView = PfTreeView()
        self.tabView = PfTabWidget()
        self.tabView.main_window = self

        self.empty_widget = QWidget()

        self.add_empty_tabview()

        #self.treeView = MyTreeView()
        self.hsplitter.addWidget(self.treeView)
        self.hsplitter.addWidget(self.tabView)
        self.hsplitter.setSizes([300, 800])

        self.setCentralWidget(self.hsplitter)

        self.treeView.mousePressed.connect(self.on_treeView_clicked)
        self.treeView.doubleClicked.connect(self.on_treeView_doubleClicked)
        self.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.open_treeview_menu)

        return

        self.treeView.doubleClicked.connect(self.on_treeView_doubleClicked)
        #self.treeView.mousePressEvent = self.on_treeView_clicked
        #self.treeView.clicked.connect(self.on_treeView_clicked)
        self.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.doubleClicked.connect(self.on_tableView_doubleClicked)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.open_treeview_menu)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.open_object_menu)


        #self.resize(800, 600)
        #self.setMinimumSize(400, 300)
        #self.move(300, 300)
        #self.show(

    def on_treeView_clicked(self, event):
        index = self.treeView.indexAt(event.pos())
        if not index.isValid():  # Click is on empty space
            self.treeView.clearSelection()
            self.treeView.setCurrentIndex(QModelIndex())  # Deselect current item
            self.tabView.clear()
            self.add_empty_tabview()
            self.selected_project = None

    def add_empty_tabview(self):
        #self.tabView.addTab(self.empty_widget, "Datamatrix")
        self.tabView.setAcceptDrops(True)
        self.tabView.dropEvent = self.tableView_drop_event
        self.tabView.dragEnterEvent = self.tableView_drag_enter_event
        self.tabView.dragMoveEvent = self.tableView_drag_move_event

    def open_treeview_menu(self, position):
        indexes = self.treeView.selectedIndexes()
        if len(indexes) > 0:


            action_add_project = QAction("Add new project")
            action_add_project.triggered.connect(self.on_action_new_project_triggered)
            action_edit_project = QAction("Edit project")
            action_edit_project.triggered.connect(self.on_action_edit_project_triggered)
            action_add_datamatrix = QAction("Add datamatrix")
            action_add_datamatrix.triggered.connect(self.on_action_add_datamatrix_triggered)
            action_delete_datamatrix = QAction("Delete datamatrix")
            action_delete_datamatrix.triggered.connect(self.on_action_delete_datamatrix_triggered)
            action_edit_datamatrix = QAction("Edit datamatrix")
            action_edit_datamatrix.triggered.connect(self.on_action_edit_datamatrix_triggered)
            action_run_analysis = QAction("Run analysis")
            action_run_analysis.triggered.connect(self.on_action_run_analysis_triggered)
            action_refresh_tree = QAction("Reload")
            action_refresh_tree.triggered.connect(self.load_treeview)

            level = 0
            index = indexes[0]
            item1 =self.project_model.itemFromIndex(index)
            ds = item1.data()

            menu = QMenu()

            if isinstance(ds, PfProject):
                level = 1
                menu.addAction(action_edit_project)
                menu.addAction(action_add_datamatrix)
            elif isinstance(ds, PfDatamatrix):                
                level = 2
                menu.addAction(action_edit_datamatrix)
                menu.addAction(action_delete_datamatrix)
                menu.addAction(action_run_analysis)


            #menu.addAction(action_add_project)
            menu.addAction(action_refresh_tree)
            menu.exec_(self.treeView.viewport().mapToGlobal(position))

    def on_action_edit_project_triggered(self):
        indexes = self.treeView.selectedIndexes()
        index = indexes[0]
        item1 =self.project_model.itemFromIndex(index)
        project = item1.data()
        if isinstance(project, PfProject):
            self.dlg = ProjectDialog(self)
            self.dlg.setModal(True)
            self.dlg.set_project( project )
            ret = self.dlg.exec_()
            if ret == 0:
                return
            elif ret == 1:
                self.load_treeview()
                self.reset_tableView()

    def on_action_edit_datamatrix_triggered(self):
        indexes = self.treeView.selectedIndexes()
        index = indexes[0]
        item1 =self.project_model.itemFromIndex(index)
        dm = item1.data()
        if isinstance(dm, PfDatamatrix):
            self.dlg = DatamatrixDialog(self)
            self.dlg.setModal(True)
            self.dlg.set_datamatrix( dm )
            ret = self.dlg.exec_()
            if ret == 0:
                return
            elif ret == 1:
                self.load_treeview()
                self.reset_tableView()                

    def on_action_run_analysis_triggered(self):
        indexes = self.treeView.selectedIndexes()
        index = indexes[0]
        item1 =self.project_model.itemFromIndex(index)
        dm = item1.data()
        if isinstance(dm, PfDatamatrix):
            self.run_analysis(dm)

    def run_analysis(self, selected_datamatrix):
        self.analysis_dialog = AnalysisDialog(self)
        self.analysis_dialog.setModal(True)
        self.analysis_dialog.set_datamatrix(selected_datamatrix)
        #self.analysis_dialog.show()

        ret = self.analysis_dialog.exec_()
        if ret == 0:
            print(" analysis ret 0")
        elif ret == 1:
            print("analysis dialog ret 1")
            self.startAnalysis()

        project = self.selected_project
        datamatrix = selected_datamatrix
        self.load_treeview()
        self.reset_tableView()
        self.select_project(project)
        self.load_datamatrices()
        #self.select_datamatrix(datamatrix)

    def on_action_add_datamatrix_triggered(self):
        pass

    def on_action_delete_datamatrix_triggered(self):
        #print("delete datamatrix")
        indexes = self.treeView.selectedIndexes()
        index = indexes[0]
        item1 =self.project_model.itemFromIndex(index)
        dm = item1.data()
        if isinstance(dm, PfDatamatrix):
            #print("deleting datamatrix:", dm.datamatrix_name)
            selected_project = dm.project
            dm.delete_instance()
            self.load_treeview()
            self.selected_project = selected_project
            self.load_datamatrices()
            #self.load_analyses()
        #pass

    def load_treeview(self):
        self.project_model.clear()
        self.selected_project = None
        project_list = PfProject.select()
        for project in project_list:
            #rec.unpack_wireframe()
            item1 = QStandardItem(project.project_name)# + " (" + str(rec.object_list.count()) + ")")
            item2 = QStandardItem(str(project.id))
            item1.setIcon(QIcon(pu.resource_path(ICON['project'])))
            item1.setData(project)
            
            self.project_model.appendRow([item1,item2])#,item2,item3] )
            if project.datamatrices.count() > 0:
                dm_list = PfDatamatrix.select().where(PfDatamatrix.project == project)
                for dm in dm_list:
                    item3 = QStandardItem(dm.datamatrix_name)
                    item3.setIcon(QIcon(pu.resource_path(ICON['datamatrix'])))
                    item3.setData(dm)
                    item1.appendRow([item3])
                    if dm.analyses.count() > 0:
                        for analysis in dm.analyses:
                            item4 = QStandardItem(analysis.analysis_name)
                            item4.setIcon(QIcon(pu.resource_path(ICON['analysis'])))
                            item4.setData(analysis)
                            item3.appendRow([item4])

            #if rec.children.count() > 0:
            #    self.load_subproject(item1,item1.data())
        self.treeView.expandAll()
        self.treeView.hideColumn(1)

    def reset_views(self):
        self.reset_treeView()
        self.reset_tableView()


    def reset_treeView(self):
        self.project_model = QStandardItemModel()
        self.treeView.setModel(self.project_model)
        self.treeView.setHeaderHidden(True)
        self.project_selection_model = self.treeView.selectionModel()
        self.project_selection_model.selectionChanged.connect(self.on_treeview_selection_changed)
        header = self.treeView.header()
        #self.treeView.setSelectionBehavior(QTreeView.SelectRows)

        self.treeView.setDragEnabled(True)
        self.treeView.setAcceptDrops(True)
        self.treeView.setDropIndicatorShown(True)
        self.treeView.dropEvent = self.dropEvent
        self.treeView.dropEvent = self.treeView_drop_event
        self.treeView.dragEnterEvent = self.treeView_drag_enter_event
        self.treeView.dragMoveEvent = self.treeView_drag_move_event




    def reset_tableView(self):
        #self.datamatrix_model = PfItemModel()
        pass
        #header_labels = ["Taxon Name", ]

        #self.datamatrix_model.setColumnCount(len(header_labels))
        #self.datamatrix_model.setHorizontalHeaderLabels( header_labels ) 
        #self.proxy_model = QSortFilterProxyModel()
        #self.proxy_model.setSourceModel(self.datamatrix_model)
        #self.tableView.setModel(self.proxy_model)
        #self.tableView.setColumnWidth(0, 200)
        #self.tableView.setColumnWidth(1, 200)
        #self.tableView.setColumnWidth(2, 50)
        #self.tableView.setColumnWidth(3, 50)
        #header = self.tableView.horizontalHeader()    
        #header.setSectionResizeMode(0, QHeaderView.Stretch)
        #self.tableView.verticalHeader().setDefaultSectionSize(20)
        #self.tableView.verticalHeader().setVisible(False)
        #self.tableView.setSelectionBehavior(QTableView.SelectRows)
        #self.data_selection_model = self.tableView.selectionModel()
        #self.data_selection_model.selectionChanged.connect(self.on_data_selection_changed)
        #self.tableView.sortByColumn(0, Qt.AscendingOrder)
        #self.datamatrix_model.setSortRole(Qt.UserRole)
        #self.clear_object_view()

    def treeView_drop_event(self, event):
        print("treeView_drop_event")
        file_name_list = event.mimeData().text().strip().split("\n")
        if len(file_name_list) == 0:
            return
        self.add_datamatrix(file_name_list)

    def tableView_drop_event(self, event):
        print("tableView_drop_event")
        file_name_list = event.mimeData().text().strip().split("\n")
        if len(file_name_list) == 0:
            return
        self.add_datamatrix(file_name_list)


    def add_datamatrix(self, file_name_list):
        create_new_project = False
        if self.selected_project is None:
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("No project is selected. Do you want to create a project with this file?")
            msgBox.setWindowTitle("Warning")
            msgBox.setWindowModality(Qt.ApplicationModal)
            msgBox.setWindowFlags(msgBox.windowFlags() | Qt.WindowStaysOnTopHint)
                    
            createButton = msgBox.addButton("Create New Project", QMessageBox.AcceptRole)
            cancelButton = msgBox.addButton(QMessageBox.Cancel)

            msgBox.exec_()

            if msgBox.clickedButton() == createButton:
                # Logic to create a new project
                create_new_project = True
                print("Creating new project...")
            elif msgBox.clickedButton() == cancelButton:
                # Cancel logic or do nothing
                #print("Cancelled")            
                return
            #QMessageBox.warning(self, "Warning", "Select a project first.")
            #return

        total_count = len(file_name_list)
        current_count = 0

        for file_name in file_name_list:

            file_name = pu.process_dropped_file_name(file_name)

            #print("file_name:", file_name)
            # get filename base
            # check if the project exists
            # if not, create a new project
            if create_new_project:
                project_name = os.path.basename(file_name)
                project = PfProject()
                project.project_name = project_name
                project.save()
                self.selected_project = project
                #self.load_project()
                create_new_project = False
            dm = PfDatamatrix()
            dm.project = self.selected_project
            dm.datamatrix_name = os.path.basename(file_name)
            dm.import_file(file_name)
            dm.save()
            if dm.taxa_list is not None and dm.project.taxa_str is None:
                dm.project.taxa_str = ",".join(dm.taxa_list)
                dm.project.save()

            if os.path.isdir(file_name):
                self.statusBar.showMessage("Cannot process directory...",2000)

        project = self.selected_project
        self.load_treeview()
        self.reset_tableView()
        self.select_project(project)

    def tableView_drag_enter_event(self, event):
        #print("drag enter event")
        event.accept()
        return

    def tableView_drag_move_event(self, event):
        #print("tree view drag move event")
        event.accept()
        return

    def treeView_drag_enter_event(self, event):
        #print("tree view drag enter event")
        event.accept()
        return

    def treeView_drag_move_event(self, event):
        event.accept()
        return


    def on_treeview_selection_changed(self, selected, deselected):
        #print("project selection changed")
        indexes = selected.indexes()
        #print(indexes)
        if indexes:
            #self.object_model.clear()
            item1 =self.project_model.itemFromIndex(indexes[0])
            data = item1.data()

            if isinstance(data, PfDatamatrix):
                dm_item = item1
                dm = dm_item.data()
                prj_item = item1.parent()
                prj = prj_item.data()
                print("dm:", dm.datamatrix_name, dm.id)
                if prj_item.hasChildren():
                    dm_idx = 0
                    for i in range(prj_item.rowCount()):                    
                        print(i, prj_item.child(i,0).data())
                        item = prj_item.child(i,0)
                        if item.data().id == dm.id:
                            print("found", item.data().id)
                            dm_idx = i
                            break
                self.selected_datamatrix = data
                self.selected_project = prj
                self.load_datamatrices()
                self.tabView.setCurrentIndex(dm_idx)

            elif isinstance(data, PfProject):
                prj_item = item1
                self.selected_project = data
                if prj_item.hasChildren():
                    dm_item = prj_item.child(0,0)
                    dm = dm_item.data()
                    self.selected_datamatrix = dm
                    self.load_datamatrices()
                else:
                    self.tabView.clear()
                    self.add_empty_tabview()
            #self.actionAnalyze.setEnabled(True)
            #self.actionNewObject.setEnabled(True)
            #self.actionExport.setEnabled(True)
        else:
            #self.actionAnalyze.setEnabled(False)
            #self.actionNewObject.setEnabled(False)
            #self.actionExport.setEnabled(False)
            pass

    def on_treeView_doubleClicked(self, index):
        self.dlg = ProjectDialog(self)
        self.dlg.setModal(True)
        self.dlg.set_project( self.selected_project )
        ret = self.dlg.exec_()
        if ret == 0:
            return
        elif ret == 1:
            if self.selected_project is None: #deleted
                self.load_treeview()
                self.reset_tableView()
            else:
                project = self.selected_project
                self.reset_treeView()
                self.load_treeview()
                self.reset_tableView()
                self.select_project(project)

    def select_project(self,project,node=None):
        if project is None:
            return
        if node is None:
            node = self.project_model.invisibleRootItem()   

        for i in range(node.rowCount()):
            item = node.child(i,0)
            if item.data() == project:
                self.treeView.setCurrentIndex(item.index())
                break
            self.select_project(project,node.child(i,0))

    def on_data_selection_changed(self, selected, deselected):
        selected_data_list = self.get_selected_data_list()
        if selected_data_list is None or len(selected_data_list) != 1:
            return

    def get_selected_data_list(self):
        selected_indexes = self.tableView.selectionModel().selectedRows()
        if len(selected_indexes) == 0:
            return None

        new_index_list = []
        model = selected_indexes[0].model()
        if hasattr(model, 'mapToSource'):
            for index in selected_indexes:
                new_index = model.mapToSource(index)
                new_index_list.append(new_index)
            selected_indexes = new_index_list
        
        selected_object_list = []
        for index in selected_indexes:
            item = self.datamatrix_model.itemFromIndex(index)
            print( item.text() )
            #object_id = int(object_id)
            #object = MdObject.get_by_id(object_id)
            #selected_object_list.append(object)

        return selected_object_list


    def load_datamatrices(self):
        self.datamatrix_list = PfDatamatrix.select().where(PfDatamatrix.project == self.selected_project)
        taxa_list = self.selected_project.get_taxa_list()

        self.datamatrix_model_list = []
        self.table_view_list = []
        self.selected_datamatrix = None
        self.tabView.clear()

        if len(self.datamatrix_list) == 0:
            self.add_empty_tabview()
            return

        for dm in self.datamatrix_list:
            datamatrix_model = PfItemModel()
            table_view = PfTableView()
            table_view.setModel(datamatrix_model)
            if self.selected_datamatrix is None:
                self.selected_datamatrix = dm
                self.selected_tableview = table_view

            self.datamatrix_model_list.append(datamatrix_model)
            self.table_view_list.append(table_view)
            #table_view.setDragEnabled(True)
            table_view.setAcceptDrops(True)
            table_view.setDropIndicatorShown(True)
            table_view.dropEvent = self.tableView_drop_event
            table_view.dragEnterEvent = self.tableView_drag_enter_event
            table_view.dragMoveEvent = self.tableView_drag_move_event
            table_view.setSortingEnabled(False)

            dm_widget = QWidget()
            dm_layout = QVBoxLayout()
            button_layout = QHBoxLayout()
            btn_analyze = QPushButton("Analyze")
            btn_analyze.clicked.connect(self.on_btn_analyze_clicked)
            btn_save_dm = QPushButton("Save")
            btn_save_dm.clicked.connect(self.on_btn_save_dm_clicked)
            button_layout.addWidget(btn_analyze)
            button_layout.addWidget(btn_save_dm)
            dm_layout.addWidget(table_view)
            dm_layout.addLayout(button_layout)
            dm_widget.setLayout(dm_layout)


            self.tabView.addTab(dm_widget, dm.datamatrix_name)
            data_list = dm.datamatrix_as_list()
            #print("data_list", data_list)

            header_labels = []
            character_list_len = len(data_list[0])
            for i in range(character_list_len):
                header_labels.append("{}".format(i+1))

            datamatrix_model.setColumnCount(len(header_labels))
            datamatrix_model.setHorizontalHeaderLabels( header_labels )

            vheader = taxa_list
            #for i, row in enumerate(taxa_list):
            #    vheader.append(row[0])

            datamatrix_model.setVerticalHeaderLabels( vheader )
            #self.tableView.verticalHeader().setDefaultSectionSize(20)
            #self.tableView.verticalHeader().setVisible(False)

            for i in range(character_list_len):
                #header_labels.append("{}".format(i+1))
                table_view.setColumnWidth(i, 30)

            #for dm in dm_list:
            for i, row in enumerate(data_list):
                #rec.unpack_wireframe()
                #item1 = QStandardItem(row[0])
                #item1.setIcon(QIcon(pu.resource_path(ICON['project'])))
                #item1.setData()
                for j, col in enumerate(row):
                    if isinstance(col, list):
                        col = " ".join(col)
                    item1 = QStandardItem(col)
                    item1.setTextAlignment(Qt.AlignCenter)

                    #item1.setIcon(QIcon(pu.resource_path(ICON['project'])))
                    #item1.setData()
                    datamatrix_model.setItem(i,j,item1)

    def load_analyses(self, datamatrix):
        self.analysis_list = PfAnalysis.select().where(PfAnalysis.datamatrix == datamatrix)
        #self.analysis_model.clear()
        for analysis in self.analysis_list:
            item1 = QStandardItem(analysis.analysis_name)
            item1.setIcon(QIcon(pu.resource_path(ICON['analysis'])))
            item1.setData(analysis)
            #self.analysis_model.appendRow([item1])

    def on_btn_save_dm_clicked(self):
        idx = self.tabView.selected_index
        #print("save dm", idx)


        self.selected_datamatrix = self.datamatrix_list[idx]
        self.selected_tableview = self.table_view_list[idx]
        # iterate through the tableview
        #print("dm:", self.selected_datamatrix.datamatrix_name)

        data_list = []

        self.selected_tableview.model().resetColors()
        for row in range(self.selected_tableview.model().rowCount()):
            data_row = []
            for column in range(self.selected_tableview.model().columnCount()):
                item = self.selected_tableview.model().item(row, column)
                if item is not None:
                    item.setBackground(QColor('white'))
                    data_row.append(item.text())
                    #print(item.text(),)
                    #print(item.data())
                    #print(item.textAlignment())
                    #print(item.textAlignment())
            data_list.append(data_row)
        #print(data_list)

        
        #self.tabView.selected_index
        #return
        if self.selected_datamatrix is None:
            print("no selected_dm")
            return
        dm = self.selected_datamatrix

        dm.datamatrix_json = json.dumps(data_list,indent=4)
        dm.save()            
    
    def on_btn_analyze_clicked(self):
        if self.selected_datamatrix is None:
            return
        self.run_analysis(self.selected_datamatrix)


if __name__ == "__main__":
    #QApplication : 프로그램을 실행시켜주는 클래스
    #with open('log.txt', 'w') as f:
    #    f.write("hello\n")
    #    # current directory
    #    f.write("current directory 1:" + os.getcwd() + "\n")
    #    f.write("current directory 2:" + os.path.abspath(".") + "\n")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(pu.resource_path('icons/PhyloForester.png')))
    app.settings = QSettings(QSettings.IniFormat, QSettings.UserScope,pu.COMPANY_NAME, pu.PROGRAM_NAME)

    translator = QTranslator()
    app.language = app.settings.value("language", "en")
    translator.load(pu.resource_path("translations/PhyloForester_{}.qm".format(app.language)))
    app.installTranslator(translator)

    #app.settings = 
    #app.preferences = QSettings("Modan", "Modan2")

    #WindowClass의 인스턴스 생성
    myWindow = PhyloForesterMainWindow()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()


''' 
How to make an exe file

pyinstaller --onefile --noconsole --add-data "icons/*.png;icons" --add-data "translations/*.qm;translations" --icon="icons/PhyloForester.png" PhyloForester.py

pyinstaller --onedir --noconsole --add-data "icons/*.png;icons" --add-data "translations/*.qm;translations" --icon="icons/PhyloForester.png" --noconfirm PhyloForester.py

pylupdate5 PhyloForester.py -ts translations/PhyloForester_en.ts
pylupdate5 PhyloForester.py -ts translations/PhyloForester_ko.ts

linguist


'''