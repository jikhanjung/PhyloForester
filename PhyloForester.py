from PyQt5.QtWidgets import QMainWindow, QHeaderView, QApplication, QAbstractItemView, \
                            QMessageBox, QTreeView, QTableView, QSplitter, QAction, QMenu, \
                            QStatusBar, QInputDialog, QToolBar, QTabWidget, QTabBar,QStyledItemDelegate, QPlainTextEdit 
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QKeySequence, QColor
from PyQt5.QtCore import Qt, QRect, QSortFilterProxyModel, QSettings, QSize, QTranslator, QModelIndex, QEvent, QProcess, QAbstractTableModel

from PyQt5.QtCore import pyqtSlot, pyqtSignal
import re,os,sys
import logging
from pathlib import Path
from peewee import *

# Initialize logger
logger = logging.getLogger(__name__)
from PIL.ExifTags import TAGS
import shutil, platform
import copy
import PfUtils as pu
from PfModel import *
from PfDialog import *
import PfLogger
import matplotlib.pyplot as plt
from peewee_migrate import Router

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

class PfItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        super().paint(painter, option, index)  # Draw default item content

        if index.column() == 1:  # Check if it's the progress bar column
            item_data = index.model().data(index, Qt.UserRole + 10) or -1 # Access progress data
            rect = option.rect
            if isinstance( item_data, str ):
                # datamatrix, not analysis
                text_x = rect.x() + 10
                text_y = rect.y() + rect.height() - 5
                painter.drawText(text_x, text_y, item_data)
                return

            progress_value = item_data.get('percentage', -1)
            status = item_data.get('status', -1)
            #print("item_data:", item_data)
            #print("progress value:", progress_value)

            #if isinstance(progress_value, str):

            if 0 < progress_value < 100 and status == ANALYSIS_STATUS_RUNNING:
                bar_width = int(0.9 * rect.width())
                bar_height = int(0.9 * rect.height())
                bar_x = rect.x() + int((rect.width() - bar_width) / 2)
                bar_y = rect.y() + int((rect.height() - bar_height) / 2)

                # Draw background
                painter.fillRect(rect, QColor(0xf0f0f0))  # Light gray background

                # Draw progress bar
                progress_width = int(bar_width * progress_value / 100)
                painter.fillRect(bar_x, bar_y, progress_width, bar_height, QColor(0x99ccff))  # Blue progress bar
                # Optionally draw text label (adjust position as needed)
                #text_x = bar_x + progress_width + 5
                #text_y = bar_y + int((bar_height - painter.fontMetrics().height()) / 2)
                #painter.drawText(text_x, text_y, f"{progress_value}%")
                text_x = rect.x() + 10
                text_y = rect.y() + rect.height() - 5
                painter.drawText(text_x, text_y, f"{progress_value}%")
            else:
                text_x = rect.x() + 10
                text_y = rect.y() + rect.height() - 5
                painter.drawText(text_x, text_y, status)



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
            logger.debug(f"Tab {index} clicked")
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
        logger.debug(f"Tab {index} clicked in parent window")
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

class PfTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []  # Initialize with provided data or an empty list
        self._vheader_data = []
        self._hheader_data = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        d = self._data[index.row()][index.column()]
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if isinstance(d, str):
                return d #self._data[index.row()][index.column()]
            elif isinstance(d, list):
                return " ".join(d)
            elif isinstance(d, dict) and 'value' in d:
                return d['value']
        if role == Qt.BackgroundRole:
            # if d is str or list, return default color
            if isinstance(d, (str, list)):
                return None
            elif isinstance(d, dict) and d.get('changed', False):
                return QColor('yellow')
        if role == Qt.ToolTipRole:
            # Check if this is the cell you want a tooltip for
            #if index.row() == 1 and index.column() == 2:
            return "Tooltip for cell ({}, {})".format(index.row(), index.column())
            #if isinstance(d, )#and self._data[index.row()][index.column()].get('changed', False):
            #return QColor('yellow')  # Highlight changed cells
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter | Qt.AlignVCenter
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False
        if index.row() >= len(self._data) or index.column() >= len(self._data[0]):
            return False

        self._data[index.row()][index.column()] = {'value': value, 'changed': True}
        self.dataChanged.emit(index, index, [role, Qt.BackgroundRole])
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return super().flags(index) | Qt.ItemIsEditable

    def resetColors(self):
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                d = self._data[row][column]
                if isinstance(d, dict) and d.get('changed', False):
                    d['changed'] = False
                #if self._data[row][column].get('changed', False):
                #    self._data[row][column]['changed'] = False
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, self.columnCount() - 1), [Qt.BackgroundRole])

    def load_data(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                # Return the header text for the given horizontal section
                return "{}".format(section+1)
            elif orientation == Qt.Vertical:
                # Return the header text for the given vertical section
                if len( self._vheader_data ) == 0:
                    return "{}".format(section)
                else:
                    return "{}".format(self._vheader_data[section])
        if role == Qt.ToolTipRole and orientation == Qt.Vertical:
            # Customize tooltip text based on section (row index)
            return f"{self._vheader_data[section]}"
        #return None

    #def headerData(self, section, orientation, role=Qt.DisplayRole):

    def setVerticalHeader(self, header_data):
        self._vheader_data = header_data
    def setHorizontalHeader(self, header_data):
        self._hheader_data = header_data

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

        # Initialize logger first
        self.logger = PfLogger.setup_logger(__name__, logging.INFO)
        self.logger.info("=" * 60)
        self.logger.info(f"PhyloForester v{pu.PROGRAM_VERSION} starting")
        self.logger.info(f"Platform: {platform.system()} {platform.release()}")
        self.logger.info(f"Python: {sys.version}")
        self.logger.info("=" * 60)

        self.setWindowIcon(QIcon(pu.resource_path('icons/PhyloForester.png')))
        self.setWindowTitle("{} v{}".format(self.tr("PhyloForester"), pu.PROGRAM_VERSION))
        self.data_storage = { 'project': {}, 'datamatrix': {}, 'analysis': {} }

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
        #self.edtAnalysisOutput = QTextEdit()


    @pyqtSlot()
    def on_action_new_project_triggered(self):
        # open new project dialog
        #return
        self.dlg = ProjectDialog(self, logger=self.logger)
        self.dlg.setModal(True)

        ret = self.dlg.exec_()
        self.load_treeview()
        self.reset_tableView()

    @pyqtSlot()
    def on_action_edit_preferences_triggered(self):
        #print("edit preferences")
        self.preferences_dialog = PreferencesDialog(self, logger=self.logger)
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
        #self.m_app.storage_directory = os.path.abspath(pu.DEFAULT_STORAGE_DIRECTORY)
        self.m_app.tnt_path = self.m_app.settings.value("SoftwarePath/TNT", "")
        self.m_app.iqtree_path = self.m_app.settings.value("SoftwarePath/IQTree", "")
        self.m_app.mrbayes_path = self.m_app.settings.value("SoftwarePath/MrBayes", "")
        #print("tnt path:", self.m_app.tnt_path)
        #print("iqtree path:", self.m_app.iqtree_path)
        #print("mrbayes path:", self.m_app.mrbayes_path)
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
        migrations_path = pu.resource_path("migrations")
        gDatabase.connect()
        router = Router(gDatabase, migrate_dir=migrations_path)

        # Auto-discover and run migrations
        router.run()        
        return

        tables = gDatabase.get_tables()
        if tables:
            return
            #print(tables)
        else:
            gDatabase.create_tables([PfProject, PfDatamatrix,PfAnalysis,PfPackage,PfTree])

    def closeEvent(self, event):
        self.logger.info("=" * 60)
        self.logger.info("PhyloForester shutting down")
        self.logger.info("=" * 60)
        self.write_settings()
        #if self.analysis_dialog is not None:
        #    self.analysis_dialog.close()
        event.accept()

    def initUI(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(self.tr("Ready"))

        self.hsplitter = QSplitter(Qt.Horizontal)


        #self.treeView = PfTreeView()
        self.treeView = PfTreeView()
        #self.tabView = PfTabWidget()
        #self.tabView.main_window = self

        self.empty_widget = QWidget()
        self.empty_widget.setAcceptDrops(True)
        self.empty_widget.dropEvent = self.tableView_drop_event
        self.empty_widget.dragEnterEvent = self.tableView_drag_enter_event
        self.empty_widget.dragMoveEvent = self.tableView_drag_move_event

        #self.add_empty_tabview()

        #self.treeView = MyTreeView()
        self.hsplitter.addWidget(self.treeView)
        self.hsplitter.addWidget(self.empty_widget)
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

    def startAnalysis(self, analysis = None):
        # Command to run (example: list directory contents)
        if not analysis:
            try:
                analysis_list = PfAnalysis.select().where(
                    PfAnalysis.analysis_status == ANALYSIS_STATUS_READY
                ).order_by(PfAnalysis.created_at)

                if len(analysis_list) == 0:
                    self.logger.info("No ready analyses to start")
                    return

                self.analysis = analysis_list[0]
                self.logger.info(f"Starting analysis: {self.analysis.analysis_name}")

            except OperationalError as e:
                self.logger.error(f"Database error while fetching analysis: {e}")
                QMessageBox.critical(self, "Database Error",
                                   f"Failed to access database:\n{e}")
                return
            except Exception as e:
                self.logger.error(f"Unexpected error while fetching analysis: {e}")
                return
        else:
            self.analysis = analysis
        #print("analysis:", self.analysis.analysis_name)
        datamatrix = self.analysis.datamatrix

        if self.analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            command = str(self.m_app.tnt_path)
            fileext = '.nex'
            datamatrix_str = datamatrix.as_nexus_format()
        elif self.analysis.analysis_type == ANALYSIS_TYPE_ML:
            command = str(self.m_app.iqtree_path)
            fileext = '.phy'
            datamatrix_str = datamatrix.as_phylip_format()

        elif self.analysis.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            command = str(self.m_app.mrbayes_path)
            #command = "D:/Phylogenetics/MrBayes-3.2.7-WINbin/mb.3.2.7-win64.exe"
            fileext = '.nex'
            datamatrix_str = datamatrix.as_nexus_format()

        self.logger.info(f"Analysis command: {command}")
        self.logger.info(f"Analysis type: {self.analysis.analysis_type}")

        result_directory = self.analysis.result_directory#.replace(" ","_")
        self.logger.info(f"Result directory: {result_directory}")        

        if not os.path.isdir( result_directory ):
            os.makedirs( result_directory )

        data_filename = datamatrix.datamatrix_name + fileext
        #if self.analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
        data_filename = data_filename.replace(" ","_")

        data_file_location = os.path.join( result_directory, data_filename )#.replace(" ","_")

        # Write data file with error handling
        try:
            pu.safe_file_write(data_file_location, datamatrix_str)
            self.logger.info(f"Data file written: {data_file_location}")
        except pu.FileOperationError as e:
            self.logger.error(f"Failed to write data file: {e}")
            QMessageBox.critical(self, "File Error",
                                f"Failed to save analysis data:\n{e}")
            self.analysis.analysis_status = ANALYSIS_STATUS_FAILED
            self.analysis.save()
            return

        self.process.setWorkingDirectory(result_directory)
        #print("working directory:", self.process.workingDirectory())
        #print("result directory:", result_directory)        

        self.analysis.start_datetime = datetime.datetime.now()
        self.analysis.analysis_status = ANALYSIS_STATUS_RUNNING
        self.analysis.save()

        if self.analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            run_file_name = os.path.join( pu.resource_path("data/aquickie.run") )
            try:
                shutil.copy( run_file_name, result_directory )
                self.logger.info(f"Run file copied: {run_file_name}")
            except (FileNotFoundError, PermissionError, OSError) as e:
                self.logger.warning(f"Failed to copy run file: {e}")
                QMessageBox.warning(self, "File Warning",
                                   f"Failed to copy run file:\n{e}\n\nAnalysis may not work correctly.")
                # Continue anyway as this might not be critical
            my_os = platform.system()
            if my_os == 'Linux':
                argument_separator = ","
            else:
                argument_separator = ";"
            #run argument setting
            run_argument_list = [ "proc", data_file_location, argument_separator, "aquickie", argument_separator ]

        elif self.analysis.analysis_type == ANALYSIS_TYPE_ML:
            #run analysis - IQTree
            #run argument setting
            run_argument_list = [ "-s", data_file_location, "-nt", "AUTO"]
            if datamatrix.datatype == DATATYPE_MORPHOLOGY:
                run_argument_list.extend( ["-st", "MORPH"] )
            if self.analysis.ml_bootstrap_type == BOOTSTRAP_TYPE_NORMAL:
                run_argument_list.extend( ["-b", str(self.analysis.ml_bootstrap)] )
            elif self.analysis.ml_bootstrap_type == BOOTSTRAP_TYPE_ULTRAFAST:
                run_argument_list.extend( ["-bb", str(self.analysis.ml_bootstrap)] )
            #print( run_argument_list )
        elif self.analysis.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            command_filename = self.create_mrbayes_command_file( data_filename, self.analysis.result_directory, self.analysis )
            run_argument_list = [ command_filename ]
            #run_argument_list = [package.run_path, command_filename]
            self.logger.info(f"MrBayes command: {command}, args: {run_argument_list}")

        # Start process with error handling
        try:
            # Check if executable exists
            if not os.path.isfile(command):
                raise pu.ProcessExecutionError(
                    f"Analysis software not found: {command}\n\n"
                    f"Please configure the path in Preferences.\n"
                    f"(Edit → Preferences → Software Paths)")

            # Check execute permission (Linux/macOS)
            if platform.system() != 'Windows':
                if not os.access(command, os.X_OK):
                    raise pu.ProcessExecutionError(
                        f"No execute permission for: {command}\n\n"
                        f"Please make the file executable with:\n"
                        f"chmod +x {command}")

            self.process.start(command, run_argument_list)

            # Wait for process to start (max 5 seconds)
            if not self.process.waitForStarted(5000):
                error_msg = self.process.errorString()
                raise pu.ProcessExecutionError(
                    f"Failed to start analysis process.\n\n"
                    f"Command: {command}\n"
                    f"Error: {error_msg}")

            self.logger.info(f"Process started successfully: {command}")
            self.data_storage['analysis'][self.analysis.id]['widget'].append_output(
                "Analysis started successfully")

        except pu.ProcessExecutionError as e:
            self.logger.error(f"Process execution failed: {e}")
            QMessageBox.critical(self, "Execution Error", str(e))

            # Mark analysis as failed
            self.analysis.analysis_status = ANALYSIS_STATUS_FAILED
            self.analysis.save()

            # Update UI
            if self.analysis.id in self.data_storage['analysis']:
                self.data_storage['analysis'][self.analysis.id]['widget'].append_output(
                    f"ERROR: {e}")
                # Update analysis viewer if visible
                widget = self.hsplitter.widget(1)
                if hasattr(widget, 'set_analysis'):
                    widget.set_analysis(self.analysis)

            # Try to start next analysis in queue
            self.startAnalysis()
            return
        
        self.data_storage['analysis'][self.analysis.id]['widget'].append_output("process started")
        #edtOutput = self.data_storage['analysis'][self.analysis.id]['output']
        #print("output textedit:", edtOutput)
        #edtOutput.appendPlainText("process started")

    def create_mrbayes_command_file(self, data_filename, result_directory, analysis):
        data_filename = os.path.join( result_directory, data_filename )
        command_filename = "run.nex"
        command_text = """begin mrbayes;
   set autoclose=yes nowarn=yes;
   execute {dfname};
   lset nst={nst} rates={nrates};
   mcmc nruns={nruns} ngen={ngen} samplefreq={samplefreq} file={dfname} burnin={burnin} Savebrlens=No;
   sump burnin={burnin};
   sumt burnin={burnin} Showtreeprobs=No;
end;""".format( dfname=data_filename, nst=analysis.mcmc_nst, nrates=analysis.mcmc_nrates, nruns=analysis.mcmc_nruns, ngen=analysis.mcmc_ngen, samplefreq=analysis.mcmc_samplefreq,burnin=analysis.mcmc_burnin)
        #print(command_text)

        command_filepath = os.path.join(result_directory,command_filename)
        f = open(command_filepath, "w")
        f.write(command_text)
        f.close()
        return command_filepath

    def onReadyReadStandardOutput(self):
        #print("standard output")
        #output = self.process.readAllStandardOutput().data() #.decode()
        if self.analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            output = self.process.readAllStandardOutput().data().decode('cp437')
            #print("ML analysis")
        else:
            output = self.process.readAllStandardOutput().data().decode()
        #print("output:",output)

        self.progress_check(output)

        self.data_storage['analysis'][self.analysis.id]['widget'].append_output(output)
        #print("output textedit:", self.data_storage['analysis'][self.analysis.id]['output'])

        #self.edtAnalysisOutput.append(output)

    def onReadyReadStandardError(self):
        #print("standard error")
        if self.analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            output = self.process.readAllStandardError().data().decode('cp437')
            #print("ML analysis")
        else:
            output = self.process.readAllStandardError().data().decode()
        self.progress_check(output)
        self.update_analysis_info(self.analysis)
        #print("error:", output)
        #self.edtAnalysisOutput.append(output)

    def onProcessFinished(self):
        exitCode = self.process.exitCode()
        self.logger.info(f"Process finished with exit code: {exitCode}")
        # This method will be called when the external process finishes
        #self.edtAnalysisOutput.append("\nProcess Finished\n")
        #print("Process Finished")
        # Here, you can also handle process exit code and status
        self.analysis.analysis_status = ANALYSIS_STATUS_FINISHED
        self.logger.info(f"Analysis status updated: {self.analysis.analysis_status}")
        self.analysis.completion_percentage = 100
        self.analysis.finish_datetime = datetime.datetime.now()
        self.analysis.save()
        self.generate_consensus_tree(self.analysis)
        self.update_analysis_info(self.analysis)

        self.startAnalysis()

    def progress_check(self, output):
        total_step = 0
        curr_step = 0
        if self.analysis.analysis_type == ANALYSIS_TYPE_ML:
            total_step = self.analysis.ml_bootstrap
        elif self.analysis.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            total_step = self.analysis.mcmc_ngen

        progress_filename = os.path.join( self.analysis.result_directory,"progress.log" )

        with open(progress_filename, 'ab') as file:
            file.write(output.encode('utf-8'))
            file.flush()  # Flush internal Python buffer
            os.fsync(file.fileno())

        for line in output.splitlines():
            progress_found = False
            if self.analysis.analysis_type == ANALYSIS_TYPE_ML:
                progress_match = re.match(r"===> START BOOTSTRAP REPLICATE NUMBER (\d+)",line)

                if progress_match:
                    progress_found = True
                    curr_step = progress_match.group(1)
                    #print("progress detected", curr_step, flush=True)
                    #print("<", line,">", flush=True,end='')

            elif self.analysis.analysis_type == ANALYSIS_TYPE_BAYESIAN:
                progress_match = re.match(r"^\s+(\d+).*(\d+:\d+:\d+)$",line)
                #progress_match = re.match("(\d+)\s+-- .+ --\s+(\d+:\d+\d+)",line)
                if progress_match:
                    progress_found = True
                    curr_step = progress_match.group(1)
                    #print("progress detected", curr_step, flush=True)
                    
            if progress_found:
                percentage = float(round( ( float(curr_step) / float(total_step) ) * 1000 )) / 10.0
                self.analysis.completion_percentage = percentage
                #self.data_storage['analysis'][self.analysis.id]['tree_item'].setData(self.analysis.completion_percentage, Qt.UserRole + 10)
                self.analysis.save()

                self.update_analysis_info(self.analysis)

    def generate_consensus_tree(self, analysis):
        '''Tree file Processing'''
        tree_name = ''
        if analysis.analysis_type == ANALYSIS_TYPE_ML:
            tree_name = "ML Consensus tree"
            tree_filename = os.path.join( analysis.result_directory, analysis.datamatrix.datamatrix_name + ".phy.treefile" )
            if not os.path.exists(tree_filename):
                return
            tree = Phylo.read( tree_filename, "newick" )
        elif analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            tree_name = "Parsimony Consensus tree"
            tree_filename = os.path.join( analysis.result_directory, "aquickie.tre" )
            #tree = Phylo.read( tree_filename, "nexus" )
            if not os.path.exists(tree_filename):
                return
            tf = pu.PhyloTreefile()
            tf.readtree(tree_filename,'Nexus')
            #print(tf.block_hash)
            tree = Phylo.read(io.StringIO(tf.tree_text_hash['tnt_1']), "newick")
            for clade in tree.find_clades():
                if clade.name:
                    taxon_index = int(clade.name) - 1
                    taxa_list = analysis.datamatrix.get_taxa_list()
                    clade.name = taxa_list[taxon_index]
                    #print(clade.name)
                    #clade.name = tf.taxa_hash[clade.name]

        elif analysis.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            tree_name = "Bayesian Consensus tree"
            tree_filename = os.path.join( analysis.result_directory, analysis.datamatrix.datamatrix_name.replace(" ","_") + ".nex.con.tre" )
            #print(tree_filename)
            tf = pu.PhyloTreefile()
            ret = tf.readtree(tree_filename,'Nexus')
            if not ret:
                self.logger.error(f"Error reading treefile: {tree_filename}")
                return
            #print(tf.tree_text_hash)
            #tree_text = tf.tree_text_hash['con_50_majrule']
            #handle = 
            tree = Phylo.read(io.StringIO(tf.tree_text_hash['con_50_majrule']), "newick")
            for clade in tree.find_clades():
                if clade.name and tf.taxa_hash[clade.name]:
                    #print(clade.name)
                    clade.name = tf.taxa_hash[clade.name]

        string_io = io.StringIO()
        # Write the tree in Newick format to the text stream
        Phylo.write(tree, string_io, "newick")
        # Get the Newick string from the text stream
        newick_string = string_io.getvalue()
        # Close the StringIO object if it's not needed anymore
        string_io.close()

        consensus_tree = PfTree()
        #consensus_tree.project = analysis.project
        consensus_tree.analysis = analysis
        consensus_tree.tree_type = TREE_TYPE_CONSENSUS
        consensus_tree.tree_name = "Consensus Tree"
        consensus_tree.newick_text = newick_string
        consensus_tree.save()

    def update_analysis_info(self, analysis):
        #self.data_storage['analysis'][analysis.id]['tree_item'].setData(analysis.completion_percentage, Qt.UserRole + 10)
        analysis = PfAnalysis.get(PfAnalysis.id == analysis.id)
        av = self.data_storage['analysis'][analysis.id]['widget']
        #analysis_view.set_analysis(analysis)
        av.update_info(analysis)

        if self.data_storage['analysis'][analysis.id]['tree_item'] is not None:
            #print("item:", self.data_storage['analysis'][analysis.id]['tree_item'])
            analysis_status = { 'status': analysis.analysis_status, 'percentage': analysis.completion_percentage }
            #print("status:", analysis_status)
            self.data_storage['analysis'][analysis.id]['tree_item'].setData(analysis_status, Qt.UserRole + 10)
            self.treeView.update()
        #else:
            #print("item is none")
        #self.treeView.repaint()

        #self.data_storage['analysis'][analysis.id]['completion'].setText(f"{analysis.completion_percentage}%")
        #self.data_storage['analysis'][analysis.id]['widget'].update()
        #self.data_storage['analysis'][analysis.id]['widget'].repaint()

        #pass

    def handleError(self, error):
        """Handle QProcess errors"""
        error_messages = {
            QProcess.FailedToStart: "Failed to start (file not found or no permission)",
            QProcess.Crashed: "Process crashed unexpectedly",
            QProcess.Timedout: "Process timed out",
            QProcess.WriteError: "Write error to process",
            QProcess.ReadError: "Read error from process",
            QProcess.UnknownError: "Unknown error"
        }

        error_type = error_messages.get(error, "Unknown error")
        error_detail = self.process.errorString()

        self.logger.error(f"Process error: {error_type}")
        self.logger.error(f"Error details: {error_detail}")

        # Update analysis status
        if hasattr(self, 'analysis') and self.analysis:
            self.analysis.analysis_status = ANALYSIS_STATUS_FAILED
            self.analysis.save()

            # Update UI
            if self.analysis.id in self.data_storage['analysis']:
                self.data_storage['analysis'][self.analysis.id]['widget'].append_output(
                    f"ERROR: {error_type}\n{error_detail}")

                # Update analysis viewer
                widget = self.hsplitter.widget(1)
                if hasattr(widget, 'set_analysis'):
                    widget.set_analysis(self.analysis)

            # Show error dialog
            QMessageBox.critical(self, "Analysis Error",
                                f"Analysis failed: {error_type}\n\n"
                                f"Details: {error_detail}\n\n"
                                f"The analysis has been marked as failed.")

        # Try to start next analysis
        self.startAnalysis()

    def on_treeView_clicked(self, event):
        index = self.treeView.indexAt(event.pos())
        if not index.isValid():  # Click is on empty space
            self.treeView.clearSelection()
            self.treeView.setCurrentIndex(QModelIndex())  # Deselect current item
            #self.tabView.clear()
            self.selected_project = None
            widget = self.hsplitter.widget(1)
            if widget == self.empty_widget:
                return
            self.hsplitter.replaceWidget(1,self.empty_widget)

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
            action_add_analysis = QAction("Add analysis")
            action_add_analysis.triggered.connect(self.on_action_add_analysis_triggered)
            action_run_analysis = QAction("Run analysis")
            action_run_analysis.triggered.connect(self.on_action_run_analysis_triggered)
            action_stop_analysis = QAction("Stop analysis")
            action_stop_analysis.triggered.connect(self.on_action_stop_analysis_triggered)
            action_delete_analysis = QAction("Delete analysis")
            action_delete_analysis.triggered.connect(self.on_action_delete_analysis_triggered)
            action_refresh_tree = QAction("Reload")
            action_refresh_tree.triggered.connect(self.load_treeview)

            level = 0
            index = indexes[0]
            item1 =self.project_model.itemFromIndex(index)
            obj = item1.data()

            menu = QMenu()

            if isinstance(obj, PfProject):
                level = 1
                obj = PfProject.get(PfProject.id == obj.id)
                menu.addAction(action_edit_project)
                menu.addAction(action_add_datamatrix)
            elif isinstance(obj, PfDatamatrix):                
                level = 2
                obj = PfDatamatrix.get(PfDatamatrix.id == obj.id)
                menu.addAction(action_edit_datamatrix)
                menu.addAction(action_delete_datamatrix)
                menu.addAction(action_add_analysis)
            elif isinstance(obj, PfAnalysis):
                level = 3
                obj = PfAnalysis.get(PfAnalysis.id == obj.id)
                if obj.analysis_status == ANALYSIS_STATUS_READY:
                    menu.addAction(action_run_analysis)
                elif obj.analysis_status == ANALYSIS_STATUS_RUNNING:
                    menu.addAction(action_stop_analysis)
                elif obj.analysis_status in [ ANALYSIS_STATUS_FINISHED, ANALYSIS_STATUS_STOPPED ]:
                    menu.addAction(action_delete_analysis)


            #menu.addAction(action_add_project)
            menu.addAction(action_refresh_tree)
            menu.exec_(self.treeView.viewport().mapToGlobal(position))

    def on_action_edit_project_triggered(self):
        indexes = self.treeView.selectedIndexes()
        index = indexes[0]
        item1 =self.project_model.itemFromIndex(index)
        project = item1.data()
        if isinstance(project, PfProject):
            self.dlg = ProjectDialog(self, logger=self.logger)
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
            self.dlg = DatamatrixDialog(self, logger=self.logger)
            self.dlg.setModal(True)
            self.dlg.set_datamatrix( dm )
            ret = self.dlg.exec_()
            if ret == 0:
                return
            elif ret == 1:
                self.load_treeview()
                self.update_datamatrix_table()
                #self.reset_tableView()

    def on_action_run_analysis_triggered(self):
        indexes = self.treeView.selectedIndexes()
        index = indexes[0]
        item1 =self.project_model.itemFromIndex(index)
        obj = item1.data()
        if not isinstance(obj, PfAnalysis):
            return

        self.startAnalysis(obj)


    def on_action_add_analysis_triggered(self):
        indexes = self.treeView.selectedIndexes()
        index = indexes[0]
        item1 =self.project_model.itemFromIndex(index)
        dm = item1.data()
        if not isinstance(dm, PfDatamatrix):
            return

        self.analysis_dialog = AnalysisDialog(self, logger=self.logger)
        self.analysis_dialog.set_datamatrix(dm)
        self.analysis_dialog.setModal(True)
        #self.analysis_dialog.show()

        ret = self.analysis_dialog.exec_()

        project = self.selected_project
        #datamatrix = dm
        self.load_treeview()
        self.reset_tableView()
        self.select_project(project)
        if ret == 0:
            self.logger.debug("Analysis dialog returned 0 (cancelled)")
        elif ret == 1:
            self.logger.debug("Analysis dialog returned 1 (start analysis)")
            self.startAnalysis()

        #self.load_datamatrices()
        #self.select_datamatrix(datamatrix)

    def on_action_stop_analysis_triggered(self):
        indexes = self.treeView.selectedIndexes()
        index = indexes[0]
        item1 =self.project_model.itemFromIndex(index)
        an = item1.data()


        self.logger.debug("Stopping analysis - validating analysis object")
        if not isinstance(an, PfAnalysis):
            return
            #self.stop_analysis(an)
        # refresh analysis object
        an = PfAnalysis.get(PfAnalysis.id == an.id)

        self.logger.debug("Stopping analysis - killing process")
        self.process.kill()
        if self.process.state() != QProcess.NotRunning:
            if not self.process.waitForFinished(3000):  # Wait for up to 3000 ms
                self.process.kill()  # Forcefully kill the process if it didn't terminate
                self.process.waitForFinished()  # Wait for the process to be killed

        if self.process.state() == QProcess.NotRunning:
            self.logger.info(f"Successfully stopped analysis: {an.analysis_name}")
            an.analysis_status = ANALYSIS_STATUS_STOPPED
            an.finish_datetime = datetime.datetime.now()
            an.save()
        else:
            self.logger.warning(f"Failed to stop analysis process: {an.analysis_name}")

        self.update_analysis_info(an)



    def on_action_add_datamatrix_triggered(self):
        indexes = self.treeView.selectedIndexes()
        index = indexes[0]
        item1 =self.project_model.itemFromIndex(index)
        prj = item1.data()
        if isinstance(prj, PfProject):
            self.dlg = DatamatrixDialog(self, logger=self.logger)
            self.dlg.setModal(True)
            dm = PfDatamatrix()
            dm.project = prj
            self.dlg.set_datamatrix( dm )
            ret = self.dlg.exec_()
            if ret == 0:
                return
            elif ret == 1:
                self.load_treeview()
                self.reset_tableView()                

    def on_action_delete_datamatrix_triggered(self):
        #print("delete datamatrix")
        indexes = self.treeView.selectedIndexes()
        index = indexes[0]
        item1 =self.project_model.itemFromIndex(index)
        dm = item1.data()
        if isinstance(dm, PfDatamatrix):
            #print("deleting datamatrix:", dm.datamatrix_name)
            selected_project = dm.project
            analysis_list = dm.analyses
            if len(analysis_list) > 0:
                for an in analysis_list:
                    
                    if self.empty_widget != self.hsplitter.widget(1):
                        self.hsplitter.replaceWidget(1,self.empty_widget)
                    self.data_storage['analysis'][an.id]['widget'].close()
                    self.data_storage['analysis'][an.id]['object'] = None
                    self.data_storage['analysis'][an.id]['widget'] = None
                    self.data_storage['analysis'][an.id]['tree_item'] = None
                    # remove self.data_storage['analysis'][an_id]
                    del self.data_storage['analysis'][an.id]
                    #an.delete_instance()

            dm.delete_instance()
            self.load_treeview()
            self.selected_project = selected_project
            self.load_datamatrices(selected_project)

    def on_action_delete_analysis_triggered(self):
        indexes = self.treeView.selectedIndexes()
        index = indexes[0]
        item1 =self.project_model.itemFromIndex(index)
        analysis = item1.data()
        if isinstance(analysis, PfAnalysis):
            #print("deleting datamatrix:", dm.datamatrix_name)
            self.selected_datamatrix = analysis.datamatrix
            self.selected_project = self.selected_datamatrix.project
            an_id = analysis.id
            analysis.delete_instance()
            self.load_treeview()

            self.hsplitter.replaceWidget(1,self.empty_widget)
            self.data_storage['analysis'][an_id]['widget'].close()
            self.data_storage['analysis'][an_id]['object'] = None
            self.data_storage['analysis'][an_id]['widget'] = None
            self.data_storage['analysis'][an_id]['tree_item'] = None
            # remove self.data_storage['analysis'][an_id]
            del self.data_storage['analysis'][an_id]
            #self.data_storage['analysis'].
            #self.data_storage['datamatrix'][self.selected_datamatrix.id]['analyses'].remove(an_id)
            return

            # remove from treeview
            parent_item = item1.parent()
            self.project_model.removeRow(item1.row())

            self.selected_project = self.selected_datamatrix.project
            if len(self.data_storage['datamatrix'][self.selected_datamatrix.id]['analyses']) > 0:
                an_id = self.data_storage['datamatrix'][self.selected_datamatrix.id]['analyses'][0]
                self.selected_analysis = self.data_storage['analysis'][an_id]['object']
                self.hsplitter.replaceWidget(1, self.data_storage['analysis'][an_id]['widget'])
            else:
                # select parent item
                self.treeView.setCurrentIndex(parent_item.index())
                self.hsplitter.replaceWidget(1,self.empty_widget)
            #self.selected_datamatrix = selected


    def reset_views(self):
        self.reset_treeView()
        self.reset_tableView()


    def reset_treeView(self):
        self.project_model = QStandardItemModel(0,2,self)
        #self.project_model.setHeaderData(1, Qt.Horizontal, "bbb")
        self.treeView.setModel(self.project_model)
        self.treeView.setHeaderHidden(True)
        self.project_selection_model = self.treeView.selectionModel()
        self.project_selection_model.selectionChanged.connect(self.on_treeview_selection_changed)
        #header = self.treeView.header()
        # set horizontal header text
        #header.set
        
        #self.treeView.setSelectionBehavior(QTreeView.SelectRows)

        self.treeView.setDragEnabled(True)
        self.treeView.setAcceptDrops(True)
        self.treeView.setDropIndicatorShown(True)
        #self.treeView.dropEvent = self.dropEvent
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
        #print("treeView_drop_event", event.source())
        if event.source() == self.treeView:
            # datamatrix copy or move
            target_index=self.treeView.indexAt(event.pos())
            target_item = self.project_model.itemFromIndex(target_index)
            if not target_item:
                return
            target_object = target_item.data()
            if target_object is None:
                return
            if target_object is not None and isinstance(target_object, PfAnalysis):
                target_project = target_object.datamatrix.project
            elif target_object is not None and isinstance(target_object, PfDatamatrix):
                target_project = target_object.project
            elif target_object is not None and isinstance(target_object, PfProject):
                target_project = target_object

            source_index = event.source().currentIndex()
            source_item = self.project_model.itemFromIndex(source_index)
            source_object = source_item.data()
            if source_object is not None and isinstance(source_object, PfAnalysis):
                return
            elif source_object is not None and isinstance(source_object, PfDatamatrix):
                source_datamatrix = source_object

            ''' copy move logic
            shift_clicked = False
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                shift_clicked = True
            '''

            if source_datamatrix is not None:
                new_datamatrix = source_datamatrix.copy()
                new_datamatrix.project = target_project
                datamatrix_name_list = [dm.datamatrix_name for dm in target_project.datamatrices]
                new_datamatrix.datamatrix_name = pu.get_unique_name(source_datamatrix.datamatrix_name, datamatrix_name_list)
                new_datamatrix.save()
                self.load_treeview()
                self.select_project(target_project)
        elif event.mimeData().hasUrls():
            # file import
            file_name_list = event.mimeData().text().strip().split("\n")
            if len(file_name_list) == 0:
                return
            self.add_datamatrix(file_name_list)

    def tableView_drop_event(self, event):
        #print("tableView_drop_event")
        file_name_list = event.mimeData().text().strip().split("\n")
        if len(file_name_list) == 0:
            return
        self.add_datamatrix(file_name_list)

    def add_datamatrix(self, file_name_list):
        create_new_project = False
        if self.selected_project is None:
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("No project is selected. Do you want to create a new project with this file?")
            msgBox.setWindowTitle("Warning")
            msgBox.setWindowModality(Qt.ApplicationModal)
            msgBox.setWindowFlags(msgBox.windowFlags() | Qt.WindowStaysOnTopHint)
                    
            createButton = msgBox.addButton("Create a New Project", QMessageBox.AcceptRole)
            cancelButton = msgBox.addButton(QMessageBox.Cancel)

            msgBox.exec_()

            if msgBox.clickedButton() == createButton:
                # Logic to create a new project
                create_new_project = True
                self.logger.info("Creating a new project...")
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
            # print current time
            #print("importing file:", file_name, "at", datetime.datetime.now())
            dm.import_file(file_name)
            dm.save()
            #if dm.taxa_list is not None and dm.project.taxa_str is None:
            #    dm.project.taxa_str = ",".join(dm.taxa_list)
            #    dm.project.save()

            if os.path.isdir(file_name):
                self.statusBar.showMessage("Cannot process directory...",2000)

        project = self.selected_project
        #print("load treeview:", file_name, "at", datetime.datetime.now())
        self.load_treeview()
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

    def show_selected_analysis(self):
        if self.selected_analysis is None:
            return
        if self.selected_analysis.id in self.data_storage['analysis']:
            #analysis_ref = self.data_storage['analysis'][self.selected_analysis.id]
            av = self.data_storage['analysis'][self.selected_analysis.id]['widget']
            if av is None:
                av = self.data_storage['analysis'][self.selected_analysis.id]['widget'] = AnalysisViewer(logger=self.logger)
                av.set_analysis(self.selected_analysis)
                av.update_info(self.selected_analysis)
            #print("analysis widget created", analysis_ref['widget'], analysis_ref['output'])

    def update_datamatrix_table(self):
        #print("update_datamatrix_table", self.selected_datamatrix.id)
        if self.selected_datamatrix is None:
            return
        #print(self.data_storage['datamatrix'])
        if self.selected_datamatrix.id in self.data_storage['datamatrix']:
            self.data_storage['datamatrix'][self.selected_datamatrix.id]['widget'] = self.create_datamatrix_table(self.selected_datamatrix)

    def create_datamatrix_table(self, dm):
        #print("create datamatrix table", dm.datamatrix_name, dm.get_taxa_list())
        #print("create datamatrix table begins at", datetime.datetime.now())
        dm_widget = QWidget()
        table_view = PfTableView()
        self.data_storage['datamatrix'][dm.id]['widget'] = dm_widget
        self.data_storage['datamatrix'][dm.id]['table'] = table_view
        
        dm_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        btn_add_character = QPushButton("Add Character")
        btn_add_character.clicked.connect(self.on_btn_add_character_clicked)
        btn_add_taxon = QPushButton("Add Taxon")
        btn_add_taxon.clicked.connect(self.on_btn_add_taxon_clicked)
        btn_analyze = QPushButton("Analyze")
        btn_analyze.clicked.connect(self.on_btn_analyze_clicked)
        btn_save_dm = QPushButton("Save")
        btn_save_dm.clicked.connect(self.on_btn_save_dm_clicked)
        button_layout.addWidget(btn_add_character)
        button_layout.addWidget(btn_add_taxon)
        button_layout.addWidget(btn_analyze)
        button_layout.addWidget(btn_save_dm)
        dm_layout.addWidget(table_view)
        dm_layout.addLayout(button_layout)
        dm_widget.setLayout(dm_layout)

        datamatrix_model = PfTableModel()
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
        #verticalHeader = table_view.verticalHeader()
        #verticalHeader.setSectionResizeMode(QHeaderView.Fixed)
        #verticalHeader.setDefaultSectionSize(150)
        #horizontalHeader = table_view.horizontalHeader()
        #horizontalHeader.setSectionResizeMode(QHeaderView.Fixed)
        #horizontalHeader.setDefaultSectionSize(20)
        #horizontalHeader.resizeSection(0, 200)
        #horizontalHeader.resizeSection(1, 50)

        data_list = dm.datamatrix_as_list()
        self.datamatrix = data_list
        if data_list is None:
            return dm_widget

        # setting headers
        table_view.verticalHeader().setFixedWidth(200)
        table_view.horizontalHeader().setDefaultSectionSize(15)

        '''
        header_labels = []
        character_list = dm.get_character_list()
        character_list_len = max( dm.n_chars, len(data_list[0] ) )
        if len(character_list) == 0:
            character_list = [""] * character_list_len

        for i in range(len(character_list)):
            header_labels.append("{}".format(i+2))
        '''

        vheader = dm.get_taxa_list()
        #print("vheader:", vheader)
        datamatrix_model.setVerticalHeader(vheader)
        hheader = dm.get_character_list()
        #print("hheader:", hheader)
        #print("n char, n taxa:", dm.n_chars, dm.n_taxa)

        if len(data_list) < len(vheader):
            for i in range(len(vheader) - len(data_list)):
                data_list.append(["0"] * len(hheader))
        #datamatrix_model.setHorizontalHeader(header_labels)
        #datamatrix_model.setColumnCount(len(header_labels))
        #datamatrix_model.setHorizontalHeaderLabels( header_labels )
        '''

        vheader = dm.get_taxa_list()
        datamatrix_model.setVerticalHeaderLabels( vheader )

        for i in range(character_list_len):
            table_view.setColumnWidth(i, 30)
        '''
        #print("datamatrix", dm.datamatrix_name, "table data setting from", datetime.datetime.now())

        datamatrix_model.load_data(data_list)
        '''
        for i, row in enumerate(dm.get_taxa_list()):
            if i >= len(data_list):
                for j in range(character_list_len):
                    item = QStandardItem("")
                    item.setTextAlignment(Qt.AlignCenter)
                    datamatrix_model.setItem(i,j,item)
            else:
                for j in range(character_list_len):
                    if j >= len(data_list[i]):
                        item1 = QStandardItem("")
                        item1.setTextAlignment(Qt.AlignCenter)
                    else:
                        col = data_list[i][j]
                        if isinstance(col, list):
                            col = " ".join(col)
                        item1 = QStandardItem(col)
                        item1.setTextAlignment(Qt.AlignCenter)
                    datamatrix_model.setItem(i,j,item1)
        '''
        #print("datamatrix", dm.datamatrix_name, "table data setting ends at", datetime.datetime.now())
        return dm_widget

    #def on_an_widget2_resize(self, event):
    #    print("an_widget2 resize event")
    #    print("widget size:",self.hsplitter.widget(1).size())


    def _create_analysis_widget(self, analysis):
        an = analysis

        an_widget = QWidget()
        an_tabview = QTabWidget()
        an_widget2 = QWidget()
        #an_widget2.resizeEvent = self.on_an_widget2_resize
        tree_widget = TreeViewer()
        tree_widget.set_analysis(an)
        #print("analysis", an.analysis_name, "tree widget:", tree_widget)

        self.data_storage['analysis'][an.id]['widget'] = an_widget
        #self.data_storage['analysis'][an.id]['tree_widget'] = tree_widget
        #output_widget = 

        edtAnalysisOutput = QPlainTextEdit("")
        font = QFont("Courier", 10)  # You can also use "Monospace", "Consolas", etc.
        font.setStyleHint(QFont.Monospace)  # Hint to use a monospace font
        edtAnalysisOutput.setFont(font)        
        edtAnalysisOutput.setReadOnly(True)
        self.data_storage['analysis'][an.id]['output'] = edtAnalysisOutput
        # if completed, load logfile to output
        if an.completion_percentage == 100:
            log_filename = os.path.join( an.result_directory, "progress.log" )
            if os.path.isfile(log_filename):
                #print("log file exists:", log_filename)
                log_fd = open(log_filename,mode='r',encoding='utf-8')
                log_text = log_fd.read()
                edtAnalysisOutput.setPlainText(log_text)
                log_fd.close()

        an_layout2 = QVBoxLayout()
        an_widget2.setLayout(an_layout2)
        an_layout2.addWidget(edtAnalysisOutput)
        an_tabview.addTab(an_widget, "Analysis Info")
        an_tabview.addTab(an_widget2, "Log")
        an_tabview.addTab(tree_widget, "Trees")
        #print("tree widget:", tree_widget)

        if an.completion_percentage == 100:
            # get concensus tree file
            tree_filename = os.path.join( an.result_directory, "concensus_tree.svg" )
            if os.path.isfile(tree_filename):
                tree_widget.set_tree_image(tree_filename)
                #tree_label = TreeViewer()
                #tree_layout = QVBoxLayout()
                #tree_layout.addWidget(tree_label)
                #tree_widget.setLayout(tree_layout)
                #tree_label.set_analysis(an)
                #tree_label.set_tree_image(tree_filename)

        # show analysis information
        # analysis type, analysis package, analysis status, analysis directory
        edtAnalysisName = QLineEdit()
        edtAnalysisName.setText(an.analysis_name)
        edtAnalysisName.setReadOnly(True)
        edtAnalysisType = QLineEdit()
        edtAnalysisType.setText(an.analysis_type)
        edtAnalysisType.setReadOnly(True)
        edtAnalysisPackage = QLineEdit()
        #edtAnalysisPackage.setText(an.analysis_package)
        edtAnalysisPackage.setReadOnly(True)
        edtAnalysisStatus = QLineEdit()
        edtAnalysisStatus.setText(an.analysis_status)
        edtAnalysisStatus.setReadOnly(True)

        an_layout = QFormLayout()
        an_widget.setLayout(an_layout)
        an_layout.addRow("Analysis Name", edtAnalysisName)
        an_layout.addRow("Analysis Type", edtAnalysisType)
        an_layout.addRow("Analysis Package", edtAnalysisPackage)
        an_layout.addRow("Analysis Status", edtAnalysisStatus)

        if an.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            pass
        elif an.analysis_type == ANALYSIS_TYPE_ML:
            edtBootstrapCount = QLineEdit()
            edtBootstrapCount.setText(str(an.ml_bootstrap))
            edtBootstrapCount.setReadOnly(True)
            edtBootstrapType = QLineEdit()
            edtBootstrapType.setText(an.ml_bootstrap_type)
            edtBootstrapType.setReadOnly(True)
            edtSubstitutionModel = QLineEdit()
            edtSubstitutionModel.setText(an.ml_substitution_model)
            edtSubstitutionModel.setReadOnly(True)
            an_layout.addRow("Bootstrap Count", edtBootstrapCount)
            an_layout.addRow("Bootstrap Type", edtBootstrapType)
            an_layout.addRow("Substitution Model", edtSubstitutionModel)

        elif an.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            edtMCMCBurnin = QLineEdit()
            edtMCMCBurnin.setText(str(an.mcmc_burnin))
            edtMCMCBurnin.setReadOnly(True)
            edtMCMCRelBurnin = QLineEdit()
            edtMCMCRelBurnin.setText(str(an.mcmc_relburnin))
            edtMCMCRelBurnin.setReadOnly(True)
            edtMCMCBurninFrac = QLineEdit()
            edtMCMCBurninFrac.setText(str(an.mcmc_burninfrac))
            edtMCMCBurninFrac.setReadOnly(True)
            edtMCMCNGen = QLineEdit()
            edtMCMCNGen.setText(str(an.mcmc_ngen))
            edtMCMCNGen.setReadOnly(True)
            edtMCMCNRates = QLineEdit()
            edtMCMCNRates.setText(an.mcmc_nrates)
            edtMCMCNRates.setReadOnly(True)
            edtMCMCPrintFreq = QLineEdit()
            edtMCMCPrintFreq.setText(str(an.mcmc_printfreq))
            edtMCMCPrintFreq.setReadOnly(True)                    
            edtMCMCSampleFreq = QLineEdit()
            edtMCMCSampleFreq.setText(str(an.mcmc_samplefreq))
            edtMCMCSampleFreq.setReadOnly(True)
            edtMCMCNRuns = QLineEdit()
            edtMCMCNRuns.setText(str(an.mcmc_nruns))
            edtMCMCNRuns.setReadOnly(True)
            edtMCMCNChains = QLineEdit()
            edtMCMCNChains.setText(str(an.mcmc_nchains))
            edtMCMCNChains.setReadOnly(True)
            an_layout.addRow("MCMC Burnin", edtMCMCBurnin)
            an_layout.addRow("MCMC Rel Burnin", edtMCMCRelBurnin)
            an_layout.addRow("MCMC Burnin Frac", edtMCMCBurninFrac)
            an_layout.addRow("MCMC NGen", edtMCMCNGen)
            an_layout.addRow("MCMC NRates", edtMCMCNRates)
            an_layout.addRow("MCMC Print Freq", edtMCMCPrintFreq)
            an_layout.addRow("MCMC Sample Freq", edtMCMCSampleFreq)
            an_layout.addRow("MCMC NRuns", edtMCMCNRuns)
            an_layout.addRow("MCMC NChains", edtMCMCNChains)                    

        edtAnalysisResultDirectory = QLineEdit()
        edtAnalysisResultDirectory.setText(an.result_directory)
        edtAnalysisResultDirectory.setReadOnly(True)
        dir_widget = QWidget()
        dir_layout = QHBoxLayout()
        dir_widget.setLayout(dir_layout)
        btnOpenDir = QPushButton("Open Directory")
        btnOpenDir.clicked.connect(self.on_btn_open_result_dir_clicked)
        dir_layout.addWidget(edtAnalysisResultDirectory)
        dir_layout.addWidget(btnOpenDir)

        edtAnalysisStartDatetime = QLineEdit()
        edtAnalysisStartDatetime.setText(an.start_datetime.strftime("%Y-%m-%d %H:%M:%S"))
        edtAnalysisStartDatetime.setReadOnly(True)
        edtAnalysisFinishDatetime = QLineEdit()
        if an.finish_datetime is not None:
            edtAnalysisFinishDatetime.setText(an.finish_datetime.strftime("%Y-%m-%d %H:%M:%S"))
        edtAnalysisFinishDatetime.setReadOnly(True)
        edtAnalysisCompletionPercentage = QLineEdit()
        edtAnalysisCompletionPercentage.setText(str(an.completion_percentage))
        edtAnalysisCompletionPercentage.setReadOnly(True)
        self.data_storage['analysis'][an.id]['completion'] = edtAnalysisCompletionPercentage


        #an_layout.addRow("Analysis Output", edtAnalysisOutput)
        an_layout.addRow("Result Directory", dir_widget)
        an_layout.addRow("Start Datetime", edtAnalysisStartDatetime)
        an_layout.addRow("Finish Datetime", edtAnalysisFinishDatetime)
        an_layout.addRow("Completion %", edtAnalysisCompletionPercentage)
        return an_tabview

    def on_btn_open_result_dir_clicked(self):
        if self.selected_analysis is None:
            return
        result_dir = self.selected_analysis.result_directory
        if os.path.isdir(result_dir):
            os.startfile(result_dir)

    def on_treeview_selection_changed(self, selected, deselected):
        #print("project selection changed")
        indexes = selected.indexes()
        #print(indexes)
        if indexes:
            #self.object_model.clear()
            item1 =self.project_model.itemFromIndex(indexes[0])
            data = item1.data()

            if isinstance(data, PfAnalysis):
                #self.selected_analysis = 
                self.selected_analysis = PfAnalysis.get_by_id(data.id)
                self.show_selected_analysis()
                self.selected_datamatrix = self.selected_analysis.datamatrix
                self.selected_project = self.selected_datamatrix.project
                #print(self.data_storage['analysis'][self.selected_analysis.id])
                self.hsplitter.replaceWidget(1, self.data_storage['analysis'][self.selected_analysis.id]['widget'])

            if isinstance(data, PfDatamatrix):
                self.selected_datamatrix = data
                self.selected_project = self.selected_datamatrix.project
                self.hsplitter.replaceWidget(1, self.data_storage['datamatrix'][self.selected_datamatrix.id]['widget'])

            elif isinstance(data, PfProject):
                self.selected_project = data
                self.selected_datamatrix = None
                if len(self.data_storage['project'][data.id]['datamatrices']) > 0 :
                    dm_id = self.data_storage['project'][data.id]['datamatrices'][0]
                    self.selected_datamatrix = self.data_storage['datamatrix'][dm_id]['object']
                    self.hsplitter.replaceWidget(1, self.data_storage['datamatrix'][dm_id]['widget'])
                else:
                    self.hsplitter.replaceWidget(1,self.empty_widget)
            #self.actionAnalyze.setEnabled(True)
            #self.actionNewObject.setEnabled(True)
            #self.actionExport.setEnabled(True)
        else:
            #self.actionAnalyze.setEnabled(False)
            #self.actionNewObject.setEnabled(False)
            #self.actionExport.setEnabled(False)
            pass

    def on_treeView_doubleClicked(self, index):
        self.dlg = ProjectDialog(self, logger=self.logger)
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
            self.logger.debug(f"Selected datamatrix item: {item.text()}")
            #object_id = int(object_id)
            #object = MdObject.get_by_id(object_id)
            #selected_object_list.append(object)

        return selected_object_list

    def load_treeview(self):
        #print("load treeview begins at", datetime.datetime.now())

        self.project_model.clear()
        self.project_model.setHeaderData(0, Qt.Horizontal, "Project")
        self.project_model.setHeaderData(1, Qt.Horizontal, "Status")
        self.selected_project = None

        try:
            project_list = PfProject.select()
        except OperationalError as e:
            self.logger.error(f"Database error while loading projects: {e}")
            QMessageBox.critical(self, "Database Error",
                               f"Failed to load projects:\n{e}")
            return

        for project in project_list:
            #rec.unpack_wireframe()
            item1 = QStandardItem(project.project_name)# + " (" + str(rec.object_list.count()) + ")")
            #item2 = QStandardItem(str(project.id))
            item1.setIcon(QIcon(pu.resource_path(ICON['project'])))
            item1.setData(project)
            item2 = QStandardItem()
            analysis_status = " "            
            item2.setData(analysis_status, Qt.UserRole + 10)
            self.data_storage['project'][project.id] = { 'object': project, 'item': item1, 'datamatrices': []}
            
            self.project_model.appendRow([item1,item2])#,item2,item3] )
            if project.datamatrices.count() > 0:
                dm_list = PfDatamatrix.select().where(PfDatamatrix.project == project)
                for dm in dm_list:
                    item3 = QStandardItem(dm.datamatrix_name)
                    item3.setIcon(QIcon(pu.resource_path(ICON['datamatrix'])))
                    item3.setData(dm)
                    item4 = QStandardItem()
                    item4.setData(dm.datatype, Qt.UserRole + 10)
                    item1.appendRow([item3,item4])
                    self.data_storage['datamatrix'][dm.id] = { 'object': dm, 'item': item3, 'analyses': [], 'widget': None}
                    self.data_storage['project'][project.id]['datamatrices'].append(dm.id)
                    if dm.analyses.count() > 0:
                        for analysis in dm.analyses:
                            analysis = PfAnalysis.get_by_id(analysis.id)
                            item5 = QStandardItem(analysis.analysis_name)
                            item5.setIcon(QIcon(pu.resource_path(ICON['analysis'])))    
                            item5.setData(analysis)
                            item6 = QStandardItem("")
                            analysis_status = { 'status': analysis.analysis_status, 'percentage': analysis.completion_percentage}
                            item6.setData(analysis_status, Qt.UserRole + 10)
                            item3.appendRow([item5,item6])
                            if analysis.id not in self.data_storage['analysis']:
                                self.data_storage['analysis'][analysis.id] = { 'object': analysis, 'tree_item': item6, 'widget': None }
                            self.data_storage['datamatrix'][dm.id]['analyses'].append(analysis.id)

            self.selected_project = project
            self.load_datamatrices(project)

            #if rec.children.count() > 0:
            #    self.load_subproject(item1,item1.data())
        delegate = PfItemDelegate()
        self.treeView.setItemDelegateForColumn(1, delegate)

        #horizontalHeader = self.treeView.horizontalHeader()
        verticalHeader = self.treeView.header()
        verticalHeader.resizeSection(0, 250)
        verticalHeader.resizeSection(1, 100)

        self.treeView.expandAll()
        #self.treeView.hideColumn(1)
        #print("load treeview ends at", datetime.datetime.now())

    def load_datamatrices(self, project=None):
        if project is None:
            return
        self.datamatrix_list = project.datamatrices #PfDatamatrix.select().where(PfDatamatrix.project == self.selected_project)
        #taxa_list = self.selected_project.get_taxa_list()

        self.datamatrix_model_list = []
        self.table_view_list = []
        self.selected_datamatrix = None
        #self.tabView.clear()

        if len(self.datamatrix_list) == 0:
            #self.add_empty_tabview()
            return

        for dm in self.datamatrix_list:
            if self.data_storage['datamatrix'][dm.id]['widget'] is None:

                self.data_storage['datamatrix'][dm.id]['widget'] = self.create_datamatrix_table(dm)
                #dm_widget = self.create_datamatrix_table(dm)
                self.load_analyses(dm)

                #self.tabView.addTab(dm_widget, dm.datamatrix_name)

    def on_btn_add_taxon_clicked(self):
        #print("add taxon")
        if self.selected_datamatrix is None:
            return
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter new taxon name', text="")
        dm = self.selected_datamatrix
        dm.taxa_list = dm.get_taxa_list()
        #print("taxa_list 1", dm.taxa_list)
        dm.taxa_list.append(text)
        dm.taxa_list_json = json.dumps(dm.taxa_list)
        dm.n_taxa = len(dm.taxa_list)
        dm.datamatrix = dm.datamatrix_as_list()
        #print("datamatrix 1:", dm.datamatrix)
        #dm.datamatrix
        dm.datamatrix.append(["0"] * dm.n_chars)
        dm.datamatrix_json = json.dumps(dm.datamatrix,indent=4)
        #print("taxa_list 2", dm.taxa_list)
        #print("datamatrix 2:", dm.datamatrix)
        dm.save()
        self.update_datamatrix_table()
        self.hsplitter.replaceWidget(1, self.data_storage['datamatrix'][self.selected_datamatrix.id]['widget'])
        #self.load_datamatrices(self.selected_project)

    def on_btn_add_character_clicked(self):
        if self.selected_datamatrix is None:
            return
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter new character name', text="")
        dm = self.selected_datamatrix

        dm.characters_list = dm.get_character_list()
        if len(dm.characters_list) == 0:
            dm.characters_list = ['0'] * dm.n_chars
        dm.characters_list.append(text)
        dm.character_list_json = json.dumps(dm.characters_list)
        dm.n_chars = len(dm.characters_list)
        dm.datamatrix = dm.datamatrix_as_list()
        for row in dm.datamatrix:
            row.append("0")
        dm.datamatrix_json = json.dumps(dm.datamatrix,indent=4)
        dm.save()
        self.update_datamatrix_table()
        self.hsplitter.replaceWidget(1, self.data_storage['datamatrix'][self.selected_datamatrix.id]['widget'])

    def load_analyses(self, datamatrix=None):
        if datamatrix is None:
            return
        self.analysis_list = datamatrix.analyses
        if len(self.analysis_list) == 0:
            return
        
        for an in self.analysis_list:
            #analysis_ref = 
            #print("analysis widget:",self.data_storage['analysis'][an.id]['widget'])
            av = self.data_storage['analysis'][an.id]['widget']
            if av is None:
                #self.data_storage['analysis'][an.id]['widget'] = self.create_analysis_widget(an)
                av = self.data_storage['analysis'][an.id]['widget'] = AnalysisViewer(logger=self.logger)
                av.set_analysis(an)
                av.update_info(an)
            #print("analysis widget:",self.data_storage['analysis'][an.id]['widget'])                


        #self.analysis_model.clear()
        #for analysis in self.analysis_list:
        #    item1 = QStandardItem(analysis.analysis_name)
        #    item1.setIcon(QIcon(pu.resource_path(ICON['analysis'])))
        #    item1.setData(analysis)
            #self.analysis_model.appendRow([item1])

    def on_btn_save_dm_clicked(self):
        #idx = self.tabView.selected_index
        #print("save dm", idx)

        #print("selected datamatrix", self.selected_datamatrix.datamatrix_name)
        #print("current table:", self.selected_tableview)
        #return

        #self.selected_datamatrix 
        dm = self.selected_datamatrix

        self.selected_tableview = self.data_storage['datamatrix'][dm.id]['table']
        # iterate through the tableview
        #print("dm:", self.selected_datamatrix.datamatrix_name)

        data_list = []

        self.selected_tableview.model().resetColors()
        for row in range(self.selected_tableview.model().rowCount()):
            data_row = []
            for column in range(self.selected_tableview.model().columnCount()):
                idx = self.selected_tableview.model().index(row, column)
                d = self.selected_tableview.model().data(idx, Qt.DisplayRole)
                if d.find(" ") > -1:
                    data = d.split(" ")
                else:
                    data = d
                data_row.append(data)
                    #print(item.text(),)
                    #print(item.data())
                    #print(item.textAlignment())
                    #print(item.textAlignment())
            data_list.append(data_row)
        #print(data_list)


        #self.tabView.selected_index
        #return
        if self.selected_datamatrix is None:
            self.logger.warning("No datamatrix selected for saving")
            return
        dm = self.selected_datamatrix

        dm.datamatrix_json = json.dumps(data_list,indent=4)
        dm.save()            
    
    def on_btn_analyze_clicked(self):
        if self.selected_datamatrix is None:
            return
        self.add_analysis(self.selected_datamatrix)

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

pyinstaller --onefile --noconsole --add-data "icons/*.png;icons" --add-data "data/*.*;data" --add-data "translations/*.qm;translations" --add-data "migrations/*;migrations" --icon="icons/PhyloForester.png" PhyloForester.py
pyinstaller --onedir --noconsole --add-data "icons/*.png;icons" --add-data "data/*.*;data" --add-data "translations/*.qm;translations" --add-data "migrations/*;migrations" --icon="icons/PhyloForester.png" --noconfirm PhyloForester.py

for MacOS
pyinstaller --onefile --noconsole --add-data "icons/*.png:icons" --add-data "data/*.*:data" --add-data "translations/*.qm:translations" --add-data "migrations/*:migrations" --icon="icons/PhyloForester.png" PhyloForester.py
pyinstaller --onedir --noconsole --add-data "icons/*.png:icons" --add-data "data/*.*:data" --add-data "translations/*.qm:translations" --add-data "migrations/*:migrations" --icon="icons/PhyloForester.png" --noconfirm PhyloForester.py


pylupdate5 PhyloForester.py -ts translations/PhyloForester_en.ts
pylupdate5 PhyloForester.py -ts translations/PhyloForester_ko.ts

linguist

'''