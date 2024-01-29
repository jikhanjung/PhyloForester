from PyQt5.QtWidgets import QMainWindow, QHeaderView, QApplication, QAbstractItemView, \
                            QMessageBox, QTreeView, QTableView, QSplitter, QAction, QMenu, \
                            QStatusBar, QInputDialog, QToolBar
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QKeySequence
from PyQt5.QtCore import Qt, QRect, QSortFilterProxyModel, QSettings, QSize, QTranslator

from PyQt5.QtCore import pyqtSlot
import re,os,sys
from pathlib import Path
from peewee import *
from PIL.ExifTags import TAGS
import shutil
import copy
import PfUtils as pu
from PfModel import *
from PfDialog import PreferencesDialog, DatasetDialog


ICON = {}
ICON['new_dataset'] = pu.resource_path('icons/NewDataset.png')
ICON['dataset'] = pu.resource_path('icons/Dataset.png')
ICON['preferences'] = pu.resource_path('icons/Preferences.png')
ICON['about'] = pu.resource_path('icons/About.png')
ICON['exit'] = pu.resource_path('icons/exit.png')


class PhyloForesterMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(pu.resource_path('icons/PhyloForester.png')))
        self.setWindowTitle("{} v{}".format(self.tr("PhyloForester"), pu.PROGRAM_VERSION))

        self.tableView = QTableView()
        self.treeView = QTreeView()

        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(32,32))

        self.actionNewDataset = QAction(QIcon(pu.resource_path(ICON['new_dataset'])), self.tr("New Dataset\tCtrl+N"), self)
        self.actionNewDataset.triggered.connect(self.on_action_new_dataset_triggered)
        self.actionNewDataset.setShortcut(QKeySequence("Ctrl+N"))

        self.actionPreferences = QAction(QIcon(pu.resource_path(ICON['preferences'])), "Preferences", self)
        self.actionPreferences.triggered.connect(self.on_action_edit_preferences_triggered)
        self.actionExit = QAction(QIcon(pu.resource_path(ICON['exit'])), "Exit\tCtrl+W", self)
        self.actionExit.triggered.connect(self.on_action_exit_triggered)
        self.actionExit.setShortcut(QKeySequence("Ctrl+W"))
        self.actionAbout = QAction(QIcon(pu.resource_path(ICON['about'])), "About\tF1", self)
        self.actionAbout.triggered.connect(self.on_action_about_triggered)
        self.actionAbout.setShortcut(QKeySequence("F1"))

        self.toolbar.addAction(self.actionNewDataset)
        self.toolbar.addAction(self.actionPreferences)
        self.toolbar.addAction(self.actionAbout)
        self.addToolBar(self.toolbar)

        self.main_menu = self.menuBar()
        self.file_menu = self.main_menu.addMenu("File")
        self.file_menu.addAction(self.actionExit)
        self.edit_menu = self.main_menu.addMenu("Edit")
        self.edit_menu.addAction(self.actionPreferences)
        self.data_menu = self.main_menu.addMenu("Data")
        self.data_menu.addAction(self.actionNewDataset)


        self.m_app = QApplication.instance()
        self.m_app.toolbar_icon_size = "Small"
        self.read_settings()

        self.initUI()
        self.check_db()

        self.reset_views()
        self.load_dataset()

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)


    @pyqtSlot()
    def on_action_new_dataset_triggered(self):
        # open new dataset dialog
        #return
        self.dlg = DatasetDialog(self)
        self.dlg.setModal(True)

        ret = self.dlg.exec_()
        self.load_dataset()
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
            gDatabase.create_tables([PfDataset, PfTaxon, PfCharacter, PfDatamatrix,])

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

        #self.treeView = MyTreeView()
        self.hsplitter.addWidget(self.treeView)
        self.hsplitter.addWidget(self.tableView)
        self.hsplitter.setSizes([300, 800])

        self.setCentralWidget(self.hsplitter)

        return

        self.treeView.doubleClicked.connect(self.on_treeView_doubleClicked)
        #self.treeView.mousePressEvent = self.on_treeView_clicked
        #self.treeView.clicked.connect(self.on_treeView_clicked)
        self.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.doubleClicked.connect(self.on_tableView_doubleClicked)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.open_dataset_menu)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.open_object_menu)


        #self.resize(800, 600)
        #self.setMinimumSize(400, 300)
        #self.move(300, 300)
        #self.show(

    def load_dataset(self):
        self.dataset_model.clear()
        self.selected_dataset = None
        all_record = PfDataset.select()
        for rec in all_record:
            #rec.unpack_wireframe()
            item1 = QStandardItem(rec.dataset_name)# + " (" + str(rec.object_list.count()) + ")")
            item2 = QStandardItem(str(rec.id))
            item1.setIcon(QIcon(pu.resource_path(ICON['dataset'])))
            item1.setData(rec)
            
            self.dataset_model.appendRow([item1,item2])#,item2,item3] )
            #if rec.children.count() > 0:
            #    self.load_subdataset(item1,item1.data())
        self.treeView.expandAll()
        self.treeView.hideColumn(1)

    def reset_views(self):
        self.reset_treeView()
        self.reset_tableView()


    def reset_treeView(self):
        self.dataset_model = QStandardItemModel()
        self.treeView.setModel(self.dataset_model)
        self.treeView.setHeaderHidden(True)
        self.dataset_selection_model = self.treeView.selectionModel()
        self.dataset_selection_model.selectionChanged.connect(self.on_dataset_selection_changed)
        header = self.treeView.header()
        self.treeView.setSelectionBehavior(QTreeView.SelectRows)

        self.treeView.setDragEnabled(True)
        self.treeView.setAcceptDrops(True)
        self.treeView.setDropIndicatorShown(True)
        self.treeView.dropEvent = self.dropEvent

    def reset_tableView(self):
        self.datamatrix_model = QStandardItemModel()
        header_labels = ["ID", "Taxon Name", ]

        self.datamatrix_model.setColumnCount(len(header_labels))
        self.datamatrix_model.setHorizontalHeaderLabels( header_labels )
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.datamatrix_model)
        self.tableView.setModel(self.proxy_model)
        self.tableView.setColumnWidth(0, 50)
        self.tableView.setColumnWidth(1, 200)
        #self.tableView.setColumnWidth(2, 50)
        #self.tableView.setColumnWidth(3, 50)
        header = self.tableView.horizontalHeader()    
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableView.verticalHeader().setDefaultSectionSize(20)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.data_selection_model = self.tableView.selectionModel()
        self.data_selection_model.selectionChanged.connect(self.on_data_selection_changed)

        #self.tableView.setDragEnabled(True)
        #self.tableView.setAcceptDrops(True)
        #self.tableView.setDropIndicatorShown(True)
        #self.tableView.dropEvent = self.tableView_drop_event
        #self.tableView.dragEnterEvent = self.tableView_drag_enter_event
        #self.tableView.dragMoveEvent = self.tableView_drag_move_event

        self.tableView.setSortingEnabled(True)
        self.tableView.sortByColumn(0, Qt.AscendingOrder)
        self.datamatrix_model.setSortRole(Qt.UserRole)
        #self.clear_object_view()

    def on_dataset_selection_changed(self, selected, deselected):
        #print("dataset selection changed")
        indexes = selected.indexes()
        #print(indexes)
        if indexes:
            #self.object_model.clear()
            item1 =self.dataset_model.itemFromIndex(indexes[0])
            ds = item1.data()
            self.selected_dataset = ds
            #self.load_object()
            #self.actionAnalyze.setEnabled(True)
            #self.actionNewObject.setEnabled(True)
            #self.actionExport.setEnabled(True)
        else:
            #self.actionAnalyze.setEnabled(False)
            #self.actionNewObject.setEnabled(False)
            #self.actionExport.setEnabled(False)
            pass

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