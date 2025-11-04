from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QFileDialog, QCheckBox, QColorDialog, \
                            QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QProgressBar, QApplication, \
                            QDialog, QLineEdit, QLabel, QPushButton, QAbstractItemView, QStatusBar, QMessageBox, \
                            QTableView, QSplitter, QRadioButton, QComboBox, QTextEdit, QSizePolicy, \
                            QTableWidget, QGridLayout, QAbstractButton, QButtonGroup, QGroupBox, \
                            QTabWidget, QListWidget, QListWidgetItem, QSlider, QScrollBar, QPlainTextEdit, QInputDialog, QItemDelegate
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QResizeEvent, QStandardItemModel, QStandardItem, QImage,\
                        QFont, QPainter, QBrush, QMouseEvent, QWheelEvent, QDoubleValidator, QFontMetrics
from PyQt5.QtCore import Qt, QRect, QSortFilterProxyModel, QSize, QPoint,\
                         pyqtSlot, QItemSelectionModel, QTimer, pyqtSignal, QModelIndex, QAbstractTableModel

from PyQt5.QtSvg import QSvgGenerator  # For PyQt5
# from PyQt6.QtSvg import QSvgGenerator  # For PyQt6, adjust import as needed

from pathlib import Path
import PfUtils as pu
from PfModel import *
import PfLogger
import matplotlib.pyplot as plt
import matplotlib.backends.backend_svg
import sys
import os
import subprocess 

class PfInputDialog(QDialog):
    def __init__(self, parent=None):
        super(PfInputDialog, self).__init__(parent)
        self.setWindowTitle("Input")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.edtInput1 = QLineEdit()
        self.layout.addWidget(self.edtInput1)
        self.edtInput2 = QLineEdit()
        self.layout.addWidget(self.edtInput2)
        self.btnOK = QPushButton("OK")
        self.btnOK.clicked.connect(self.on_btn_ok_clicked)
        self.btnCancel = QPushButton("Cancel")
        self.btnCancel.clicked.connect(self.on_btn_cancel_clicked)
        self.layout.addWidget(self.btnOK)
        self.layout.addWidget(self.btnCancel)

    def on_btn_ok_clicked(self):
        self.accept()

    def on_btn_cancel_clicked(self):
        self.reject()

class AnalysisViewer(QWidget):
    def __init__(self, logger=None):
        super(AnalysisViewer, self).__init__()
        self.logger = logger or PfLogger.get_logger(__name__)
        self.setMinimumSize(400,300)
        self.bgcolor = "#000000"

        self.tabview = QTabWidget()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.tabview)

        self.analysis_info_widget = QWidget()
        self.analysis_log_widget = QWidget()
        self.tree_widget = TreeViewer()
        #self.tree_widget.set_analysis(self.analysis)

        self.edtAnalysisOutput = QPlainTextEdit("")
        font = QFont("Courier", 10)  # You can also use "Monospace", "Consolas", etc.
        font.setStyleHint(QFont.Monospace)  # Hint to use a monospace font
        self.edtAnalysisOutput.setFont(font)        
        self.edtAnalysisOutput.setReadOnly(True)
        #self.data_storage['analysis'][an.id]['output'] = edtAnalysisOutput
        # if completed, load logfile to output

        self.layout2 = QVBoxLayout()
        self.analysis_log_widget.setLayout(self.layout2)
        self.layout2.addWidget(self.edtAnalysisOutput)
        self.tabview.addTab(self.analysis_info_widget, "Analysis Info")
        self.tabview.addTab(self.analysis_log_widget, "Log")
        self.tabview.addTab(self.tree_widget, "Trees")
        #print("tree widget:", tree_widget)

        # show analysis information
        # analysis type, analysis package, analysis status, analysis directory
        self.edtAnalysisName = QLineEdit()
        self.edtAnalysisName.setReadOnly(True)
        self.edtAnalysisType = QLineEdit()
        self.edtAnalysisType.setReadOnly(True)
        self.edtAnalysisPackage = QLineEdit()
        #edtAnalysisPackage.setText(an.analysis_package)
        self.edtAnalysisPackage.setReadOnly(True)
        self.edtAnalysisStatus = QLineEdit()
        self.edtAnalysisStatus.setReadOnly(True)
        #self.edtCompletionPer = QLineEdit()
        #self.edtAnalysisStatus.setReadOnly(True)

        self.layout0 = QGridLayout()
        self.layout1 = QFormLayout()
        self.analysis_info_widget.setLayout(self.layout0)
        self.layout0.addWidget(QLabel("Analysis Name"), 0, 0 )
        self.layout0.addWidget(self.edtAnalysisName, 0, 1 ) # 0
        self.layout0.addWidget(QLabel("Analysis Type"), 1, 0 )
        self.layout0.addWidget(self.edtAnalysisType, 1, 1 ) # 1
        self.layout0.addWidget(QLabel("Analysis Package"), 2, 0 )
        self.layout0.addWidget(self.edtAnalysisPackage, 2, 1 )
        self.layout0.addWidget(QLabel("Analysis Status"), 3, 0 )
        self.layout0.addWidget(self.edtAnalysisStatus, 3, 1 )

        #self.layout1.addRow(QLabel("Analysis Type"), self.edtAnalysisType) # 1
        #self.layout1.addRow(QLabel("Analysis Package"), self.edtAnalysisPackage) # 2
        #self.layout1.addRow(QLabel("Analysis Status"), self.edtAnalysisStatus) # 3

        self.edtBootstrapCount = QLineEdit()
        self.edtBootstrapCount.setReadOnly(True)
        self.edtBootstrapType = QLineEdit()
        self.edtBootstrapType.setReadOnly(True)
        self.edtSubstitutionModel = QLineEdit()
        self.edtSubstitutionModel.setReadOnly(True)

        self.layout0.addWidget(QLabel("Bootstrap Count"), 4, 0 )
        self.layout0.addWidget(self.edtBootstrapCount, 4, 1 )
        self.layout0.addWidget(QLabel("Bootstrap Type"), 5, 0 )
        self.layout0.addWidget(self.edtBootstrapType, 5, 1 )
        self.layout0.addWidget(QLabel("Substitution Model"), 6, 0 )
        self.layout0.addWidget(self.edtSubstitutionModel, 6, 1 )

        #self.layout1.addRow("Bootstrap Count", self.edtBootstrapCount) # 4
        #self.layout1.addRow("Bootstrap Type", self.edtBootstrapType) # 5
        #self.layout1.addRow("Substitution Model", self.edtSubstitutionModel) # 6

        self.edtMCMCBurnin = QLineEdit()
        self.edtMCMCBurnin.setReadOnly(True)
        self.edtMCMCRelBurnin = QLineEdit()
        self.edtMCMCRelBurnin.setReadOnly(True)
        self.edtMCMCBurninFrac = QLineEdit()
        self.edtMCMCBurninFrac.setReadOnly(True)
        self.edtMCMCNGen = QLineEdit()
        self.edtMCMCNGen.setReadOnly(True)
        self.edtMCMCNRates = QLineEdit()
        self.edtMCMCNRates.setReadOnly(True)
        self.edtMCMCPrintFreq = QLineEdit()
        self.edtMCMCPrintFreq.setReadOnly(True)                    
        self.edtMCMCSampleFreq = QLineEdit()
        self.edtMCMCSampleFreq.setReadOnly(True)
        self.edtMCMCNRuns = QLineEdit()
        self.edtMCMCNRuns.setReadOnly(True)
        self.edtMCMCNChains = QLineEdit()
        self.edtMCMCNChains.setReadOnly(True)

        self.layout0.addWidget(QLabel("MCMC Burnin"), 7, 0 )
        self.layout0.addWidget(self.edtMCMCBurnin, 7, 1 )
        self.layout0.addWidget(QLabel("MCMC Rel Burnin"), 8, 0 )
        self.layout0.addWidget(self.edtMCMCRelBurnin, 8, 1 )
        self.layout0.addWidget(QLabel("MCMC Burnin Frac"), 9, 0 )
        self.layout0.addWidget(self.edtMCMCBurninFrac, 9, 1 )
        self.layout0.addWidget(QLabel("MCMC NGen"), 10, 0 )
        self.layout0.addWidget(self.edtMCMCNGen, 10, 1 )
        self.layout0.addWidget(QLabel("MCMC NRates"), 11, 0 )
        self.layout0.addWidget(self.edtMCMCNRates, 11, 1 )
        self.layout0.addWidget(QLabel("MCMC Print Freq"), 12, 0 )
        self.layout0.addWidget(self.edtMCMCPrintFreq, 12, 1 )
        self.layout0.addWidget(QLabel("MCMC Sample Freq"), 13, 0 )
        self.layout0.addWidget(self.edtMCMCSampleFreq, 13, 1 )
        self.layout0.addWidget(QLabel("MCMC NRuns"), 14, 0 )
        self.layout0.addWidget(self.edtMCMCNRuns, 14, 1 )
        self.layout0.addWidget(QLabel("MCMC NChains"), 15, 0 )
        self.layout0.addWidget(self.edtMCMCNChains, 15, 1 )
        '''
        self.layout1.addRow("MCMC Burnin", self.edtMCMCBurnin) # 7
        self.layout1.addRow("MCMC Rel Burnin", self.edtMCMCRelBurnin) # 8
        self.layout1.addRow("MCMC Burnin Frac", self.edtMCMCBurninFrac) # 9
        self.layout1.addRow("MCMC NGen", self.edtMCMCNGen) # 10
        self.layout1.addRow("MCMC NRates", self.edtMCMCNRates) # 11
        self.layout1.addRow("MCMC Print Freq", self.edtMCMCPrintFreq) # 12
        self.layout1.addRow("MCMC Sample Freq", self.edtMCMCSampleFreq) # 13
        self.layout1.addRow("MCMC NRuns", self.edtMCMCNRuns) # 14
        self.layout1.addRow("MCMC NChains", self.edtMCMCNChains) # 15
        '''

        self.edtAnalysisResultDirectory = QLineEdit()
        self.edtAnalysisResultDirectory.setReadOnly(True)
        self.dir_widget = QWidget()
        self.dir_layout = QHBoxLayout()
        self.dir_widget.setLayout(self.dir_layout)
        self.dir_widget.setFixedHeight(40)
        self.btnOpenDir = QPushButton("Open Directory")
        self.btnOpenDir.clicked.connect(self.on_btn_open_result_dir_clicked)
        self.dir_layout.addWidget(self.edtAnalysisResultDirectory)
        self.dir_layout.addWidget(self.btnOpenDir)

        self.edtAnalysisStartDatetime = QLineEdit()
        self.edtAnalysisStartDatetime.setReadOnly(True)
        self.edtAnalysisFinishDatetime = QLineEdit()
        self.edtAnalysisFinishDatetime.setReadOnly(True)
        self.edtAnalysisCompletionPercentage = QLineEdit()
        self.edtAnalysisCompletionPercentage.setReadOnly(True)

        row_num = 16
        self.layout0.addWidget(QLabel("Result Directory"), row_num, 0 )
        self.layout0.addWidget(self.dir_widget, row_num, 1 )
        row_num += 1
        self.layout0.addWidget(QLabel("Start Datetime"), row_num, 0 )
        self.layout0.addWidget(self.edtAnalysisStartDatetime, row_num, 1 )
        row_num += 1
        self.layout0.addWidget(QLabel("Finish Datetime"), row_num, 0 )
        self.layout0.addWidget(self.edtAnalysisFinishDatetime, row_num, 1 )
        row_num += 1
        self.layout0.addWidget(QLabel("Completion %"), row_num, 0 )
        self.layout0.addWidget(self.edtAnalysisCompletionPercentage, row_num, 1 )
        row_num += 1
        self.layout0.addWidget(QLabel(""), row_num, 0 )
        self.layout0.setRowStretch(row_num, 1)
        #self.layout0.addWidget(self.edtAnalysisFinishDatetime, row_num, 1 )

        #self.layout1.addRow("Start Datetime", self.edtAnalysisStartDatetime)
        #self.layout1.addRow("Result Directory", self.dir_widget)
        #self.layout1.addRow("Start Datetime", self.edtAnalysisStartDatetime)
        #self.layout1.addRow("Finish Datetime", self.edtAnalysisFinishDatetime)
        #self.layout1.addRow("Completion %", self.edtAnalysisCompletionPercentage)

    def set_analysis(self,analysis):
        self.analysis = analysis
        self.tree_widget.set_analysis(self.analysis)
        
        if analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            for i in range(4,16):
                #print("i:", i)
                self.layout0.itemAtPosition(i,0).widget().hide()
                self.layout0.itemAtPosition(i,1).widget().hide()
                #self.layout0.itemAt(4,QFormLayout.LabelRole).widget().hide()
                #self.layout0.removeRow(4)
        elif analysis.analysis_type == ANALYSIS_TYPE_ML:
            for i in range(7,16):
                #print("i:", i)
                self.layout0.itemAtPosition(i,0).widget().hide()
                self.layout0.itemAtPosition(i,1).widget().hide()
                #self.layout1.itemAt(7,QFormLayout.FieldRole).widget().hide()
                #self.layout1.itemAt(7,QFormLayout.LabelRole).widget().hide()
                #self.layout1.removeRow(7)
        elif analysis.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            for i in range(4,7):
                #print("i:", i)
                self.layout0.itemAtPosition(i,0).widget().hide()
                self.layout0.itemAtPosition(i,1).widget().hide()
                #self.layout1.itemAt(4,QFormLayout.FieldRole).widget().hide()
                #self.layout1.itemAt(4,QFormLayout.LabelRole).widget().hide()
                #self.layout1.removeRow(4)
        #    for i in range(5,8):
        #        self.layout1.itemAt(i).widget().hide()
            #for i in range(13,17):
            #    self.layout1.itemAt(i).widget().hide()
            
        #self.update_info()

    def update_info(self, analysis):
        #analysis = self.analysis
        #print("update analysis info", analysis.analysis_name, analysis.analysis_status)
        self.analysis = analysis
        if analysis.completion_percentage == 100:
            log_filename = os.path.join( analysis.result_directory, "progress.log" )
            if os.path.isfile(log_filename):
                #print("log file exists:", log_filename)
                log_fd = open(log_filename,mode='r',encoding='utf-8')
                log_text = log_fd.read()
                self.edtAnalysisOutput.setPlainText(log_text)
                log_fd.close()
        #if analysis.completion_percentage == 100:
        #    # get concensus tree file
        #    tree_filename = os.path.join( analysis.result_directory, "concensus_tree.svg" )
        #    if os.path.isfile(tree_filename):
        #        self.tree_widget.set_tree_image(tree_filename)
        self.edtAnalysisName.setText(analysis.analysis_name)
        self.edtAnalysisType.setText(analysis.analysis_type)
        self.edtAnalysisStatus.setText(analysis.analysis_status)
        if analysis.finish_datetime is not None:
            self.edtAnalysisFinishDatetime.setText(analysis.finish_datetime.strftime("%Y-%m-%d %H:%M:%S"))

        self.edtAnalysisStartDatetime.setText(analysis.start_datetime.strftime("%Y-%m-%d %H:%M:%S"))
        self.edtAnalysisCompletionPercentage.setText(str(analysis.completion_percentage))

        if analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            pass
        elif analysis.analysis_type == ANALYSIS_TYPE_ML:

            self.edtBootstrapCount.setText(str(analysis.ml_bootstrap))
            self.edtBootstrapType.setText(analysis.ml_bootstrap_type)
            self.edtSubstitutionModel.setText(analysis.ml_substitution_model)
        elif analysis.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            self.edtMCMCBurnin.setText(str(analysis.mcmc_burnin))
            self.edtMCMCRelBurnin.setText(str(analysis.mcmc_relburnin))
            self.edtMCMCBurninFrac.setText(str(analysis.mcmc_burninfrac))
            self.edtMCMCNGen.setText(str(analysis.mcmc_ngen))
            self.edtMCMCNRates.setText(analysis.mcmc_nrates)
            self.edtMCMCPrintFreq.setText(str(analysis.mcmc_printfreq))
            self.edtMCMCSampleFreq.setText(str(analysis.mcmc_samplefreq))
            self.edtMCMCNRuns.setText(str(analysis.mcmc_nruns))
            self.edtMCMCNChains.setText(str(analysis.mcmc_nchains))
        # Normalize path for OS-appropriate display
        self.edtAnalysisResultDirectory.setText(os.path.normpath(analysis.result_directory))
        self.tree_widget.update_info(self.analysis)

    def on_btn_open_result_dir_clicked(self):
        if self.analysis is None:
            return
        result_dir = self.analysis.result_directory
        if os.path.isdir(result_dir):
            #os.startfile(result_dir)
            try:
                if sys.platform == "win32":
                    os.startfile(result_dir)
                elif sys.platform == "darwin":
                    subprocess.run(["open", result_dir])
                elif sys.platform == "linux":
                    subprocess.run(["xdg-open", result_dir])
            except Exception as e:
                print(f"Error opening {result_dir}: {e}")
    def append_output(self, text):
        self.edtAnalysisOutput.appendPlainText(text)

MODE = { 'NONE': 0, 'PAN': 1, 'ZOOM': 2, 'EDIT': 3 }

class CheckboxTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data  # Data is a list of tuples (bool, str)

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 1  # Assuming 2 columns: checkbox and some text

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if index.column() == 0 and role == Qt.CheckStateRole:
            return Qt.Checked if self._data[index.row()] else Qt.Unchecked
        if index.column() == 1 and role == Qt.DisplayRole:
            return self._data[index.row()][1]
        return None

    def flags(self, index):
        flags = super().flags(index)
        if index.column() == 0:
            flags |= Qt.ItemIsUserCheckable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.CheckStateRole:
            return False
        self._data[index.row()] = (value == Qt.Checked)
        self.dataChanged.emit(index, index, [role])
        return True

    def get_selected_indices(self):
        selected_indices = []
        for i, value in enumerate(self._data):
            if value:  # Assuming checkbox state is at index 0 in the tuple
                selected_indices.append(i)
        return selected_indices

class TreeViewer(QWidget):
    def __init__(self, logger=None):
        super(TreeViewer, self).__init__()
        self.logger = logger or PfLogger.get_logger(__name__)
        self.setMinimumSize(400,300)
        self.bgcolor = "#000000"
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.m_app = QApplication.instance()
        self.newick_tree_list = []
        self.treeobj_hash = {}
        self.bookmarked_newick_tree_list = []
        self.bookmarked_treeobj_hash = {}
        #self.scroll_area = QScrollArea()
        #self.scroll_area.setWidgetResizable(True)
        #self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        #self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)


        self.tree_type_widget = QWidget()        
        self.tree_type_layout = QHBoxLayout()
        self.tree_type_widget.setLayout(self.tree_type_layout)
        self.layout.addWidget(self.tree_type_widget)
        self.rb_tree_type1 = QRadioButton("Trees")
        self.rb_tree_type2 = QRadioButton("Bookmarked Trees")
        self.tree_type_layout.addWidget(self.rb_tree_type1)
        self.tree_type_layout.addWidget(self.rb_tree_type2)
        self.rb_tree_type1.setChecked(True)
        self.rb_tree_type1.clicked.connect(self.on_rb_tree_type1_clicked)
        self.rb_tree_type2.clicked.connect(self.on_rb_tree_type2_clicked)

        self.tree_info_widget1 = QWidget()
        # set tree_info_widget height to 30
        #self.tree_info_widget1.setFixedHeight(50)
        self.tree_info_layout = QHBoxLayout()
        self.tree_info_widget1.setLayout(self.tree_info_layout)
        self.layout.addWidget(self.tree_info_widget1)

        self.lbl_tree_name = QLabel()
        self.lbl_tree_name.setText("Tree Name")
        self.tree_info_layout.addWidget(self.lbl_tree_name)
        self.edt_tree_name = QLineEdit()
        #self.edt_tree_name.setReadOnly(True)
        #self.edt_tree_name.setFixedWidth(50)
        self.tree_info_layout.addWidget(self.edt_tree_name)


        self.lbl_tree_number = QLabel()
        self.lbl_tree_number.setText("Tree Index")
        self.tree_info_layout.addWidget(self.lbl_tree_number)
        self.edt_tree_index = QLineEdit()
        self.edt_tree_index.setReadOnly(True)
        self.edt_tree_index.setFixedWidth(50)

        self.tree_info_layout.addWidget(self.edt_tree_index)
        self.lbl_total_trees = QLabel()
        self.tree_info_layout.addWidget(self.lbl_total_trees)
        #self.lbl_total_trees.setText("Total Trees: 0")

        self.options_widget = QWidget()
        self.options_layout = QHBoxLayout()
        self.options_widget.setLayout(self.options_layout)
        self.layout.addWidget(self.options_widget)

        self.lbl_tree_style = QLabel("Style")
        self.combo_tree_style = QComboBox()
        self.combo_tree_style.addItem("Topology")
        self.combo_tree_style.addItem("Branch length")
        self.combo_tree_style.addItem("Timetree")
        self.combo_tree_style.currentIndexChanged.connect(self.on_combo_tree_style_currentIndexChanged)

        ''' topology option: character mapping, align taxa names'''
        self.cbx_char_mapping = QCheckBox()
        self.cbx_char_mapping.setText("Char. Mapping")
        self.cbx_char_mapping.setChecked(False)
        self.cbx_char_mapping.clicked.connect(self.on_cbx_char_mapping_clicked)

        self.cbx_align_taxa = QCheckBox()
        self.cbx_align_taxa.setText("Align Names")
        self.cbx_align_taxa.setChecked(False)
        self.cbx_align_taxa.clicked.connect(self.on_cbx_align_taxa_clicked)

        ''' branch length options: none '''

        ''' timetree options: node minimum offset '''
        self.lbl_node_minimum_offset = QLabel()
        self.lbl_node_minimum_offset.setText("Min.offset(Ma)")

        self.edt_node_minimum_offset = QLineEdit()
        self.edt_node_minimum_offset.setFixedWidth(40)
        self.edt_node_minimum_offset.setValidator(QDoubleValidator())
        self.edt_node_minimum_offset.setText("0.1")
        #self.edt_node_minimum_offset.setPlaceholderText("Node Min Offset")
        self.edt_node_minimum_offset.editingFinished.connect(self.on_edt_node_minimum_offset_change)
        #self.edt_tree_width.editingFinished.connect(self.on_edt_tree_width_change)

        #self.cbx_apply_branch_length = QCheckBox()
        #self.cbx_apply_branch_length.setText("Branch Length")
        #self.cbx_apply_branch_length.setChecked(False)
        #self.options_layout.addWidget(self.cbx_apply_branch_length)
        #self.cbx_apply_branch_length.clicked.connect(self.on_cbx_show_branch_length_clicked)

        #self.timetree_widget = QWidget()
        #self.timetree_widget.setFixedWidth(220)
        #self.timetree_layout = QHBoxLayout()
        #self.timetree_widget.setLayout(self.timetree_layout)
        #self.options_layout.addWidget(self.timetree_widget)

        #self.cbx_timetree = QCheckBox()
        #self.cbx_timetree.setText("Timetree")
        #self.cbx_timetree.setFixedWidth(75)
        #self.cbx_timetree.setChecked(False)
        #self.timetree_layout.addWidget(self.cbx_timetree)
        #self.cbx_timetree.clicked.connect(self.on_cbx_timetree_clicked)

        self.cbx_show_axis = QCheckBox()
        self.cbx_show_axis.setText("Show axis")
        self.cbx_show_axis.setChecked(False)
        self.cbx_show_axis.clicked.connect(self.on_cbx_show_axis_clicked)
        
        self.font_option_widget = QWidget()
        #self.font_option_widget.setFixedWidth(150)
        self.font_option_layout = QHBoxLayout()
        self.font_option_widget.setLayout(self.font_option_layout)

        self.lbl_font = QLabel()
        self.lbl_font.setText("Font")
        self.font_option_layout.addWidget(self.lbl_font)

        self.cbx_italic_taxa_name = QCheckBox()
        self.cbx_italic_taxa_name.setText("Italic")
        self.cbx_italic_taxa_name.setChecked(False)
        self.font_option_layout.addWidget(self.cbx_italic_taxa_name)
        self.cbx_italic_taxa_name.clicked.connect(self.on_cbx_italic_taxa_name_clicked)

        self.combo_font_size = QComboBox()
        for i in [ 6, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28 ]:
            self.combo_font_size.addItem(str(i))
        #self.combo_font_size.addItem("8")
        #self.combo_font_size.setFixedWidth(50)
        self.font_option_layout.addWidget(self.combo_font_size)
        self.combo_font_size.setCurrentIndex(3)
        self.combo_font_size.currentIndexChanged.connect(self.on_combo_font_size_currentIndexChanged)

        self.fit_widget = QWidget()
        #self.fit_widget.setFixedWidth(210)
        self.fit_layout = QHBoxLayout()
        self.fit_widget.setLayout(self.fit_layout)

        self.cbx_fit_to_window = QCheckBox()
        self.cbx_fit_to_window.setText("Fit to window")
        #self.cbx_fit_to_window.setFixedWidth(120)
        self.cbx_fit_to_window.setChecked(True)
        self.fit_layout.addWidget(self.cbx_fit_to_window)
        self.cbx_fit_to_window.clicked.connect(self.on_cbx_fit_to_window_clicked)
        
        self.edt_tree_width = QLineEdit()
        self.edt_tree_width.setReadOnly(True)
        self.edt_tree_width.setEnabled(False)
        self.edt_tree_width.setFixedWidth(40)
        # change event
        self.edt_tree_width.editingFinished.connect(self.on_edt_tree_width_change)
        #self.edt_tree_width.changeEvent = self.on_edt_tree_width_change
        #self.edt_tree_width.setText("0")
        self.fit_layout.addWidget(self.edt_tree_width)
        self.lbl_tree_x = QLabel()
        self.lbl_tree_x.setText("x")
        self.lbl_tree_x.setFixedWidth(10)
        self.fit_layout.addWidget(self.lbl_tree_x)        
        self.edt_tree_height = QLineEdit()
        self.edt_tree_height.setReadOnly(True)
        self.edt_tree_height.setEnabled(False)
        self.edt_tree_height.setFixedWidth(40)
        # change event
        self.edt_tree_height.editingFinished.connect(self.on_edt_tree_height_change)
        #self.edt_tree_height.changeEvent = self.on_edt_tree_height_change
        #self.edt_tree_height.setText("0")
        self.fit_layout.addWidget(self.edt_tree_height)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.on_btn_reset_clicked)
        #self.btn_reset.setFixedWidth(80)

        ''' options layout '''
        self.options_layout.addWidget(self.lbl_tree_style)
        self.options_layout.addWidget(self.combo_tree_style)
        self.options_layout.addWidget(self.cbx_char_mapping)
        self.options_layout.addWidget(self.cbx_align_taxa)
        self.options_layout.addWidget(self.lbl_node_minimum_offset)
        self.options_layout.addWidget(self.edt_node_minimum_offset)
        self.options_layout.addStretch(1)
        self.options_layout.addWidget(self.cbx_show_axis)
        self.options_layout.addWidget(self.font_option_widget)
        self.options_layout.addWidget(self.fit_widget)
        self.options_layout.addWidget(self.btn_reset)


        self.buttons_widget = QWidget()
        self.buttons_layout = QHBoxLayout()
        self.buttons_widget.setLayout(self.buttons_layout)

        self.btn_characters = QPushButton("Show Characters")
        self.btn_characters.clicked.connect(self.on_btn_characters_clicked)
        #self.btn_characters.setFixedWidth(80)
        self.buttons_layout.addWidget(self.btn_characters)

        self.btn_timetable = QPushButton("Edit Timetable")
        self.btn_timetable.clicked.connect(self.on_btn_timetable_clicked)
        #self.btn_reset.setFixedWidth(80)
        self.buttons_layout.addWidget(self.btn_timetable)

        self.btn_bookmark = QPushButton("Add Bookmark")
        self.btn_bookmark.clicked.connect(self.on_btn_bookmark_clicked)
        #self.btn_save.setFixedWidth(80)
        self.buttons_layout.addWidget(self.btn_bookmark)

        self.btn_copy_image = QPushButton("Copy image")
        self.btn_copy_image.clicked.connect(self.on_btn_copy_image_clicked)
        #self.btn_export.setFixedWidth(80)
        self.buttons_layout.addWidget(self.btn_copy_image)

        self.btn_export = QPushButton("Export")
        self.btn_export.clicked.connect(self.on_btn_export_clicked)
        #self.btn_export.setFixedWidth(80)
        self.buttons_layout.addWidget(self.btn_export)

        self.combo_image_type = QComboBox()
        self.combo_image_type.addItem("SVG")
        self.combo_image_type.addItem("PNG")
        #self.combo_image_type.addItem("PDF")
        self.combo_image_type.setFixedWidth(80)
        self.buttons_layout.addWidget(self.combo_image_type)

        self.tree_info_widget2 = QWidget()
        self.tree_info_layout2 = QHBoxLayout()
        self.tree_info_widget2.setFixedHeight(50)
        self.tree_info_widget2.setLayout(self.tree_info_layout2)
        #self.layout.addWidget(self.tree_info_widget2)
        self.lbl_tree_info = QLabel()
        self.lbl_tree_info.setText("Consensus tree")
        self.tree_info_layout2.addWidget(self.lbl_tree_info)
        self.edt_tree_index2 = QLineEdit()
        self.edt_tree_index2.setReadOnly(True)
        self.tree_info_layout2.addWidget(self.edt_tree_index2)
        self.lbl_total_trees2 = QLabel()
        self.tree_info_layout2.addWidget(self.lbl_total_trees2)

        self.tree_widget = QWidget()
        self.tree_layout = QHBoxLayout()
        self.tree_widget.setLayout(self.tree_layout)
        self.layout.addWidget(self.tree_widget)

        ''' char list widget '''
        self.character_list_widget = QWidget()
        self.character_list_layout = QVBoxLayout()
        self.character_list_widget.setLayout(self.character_list_layout)
        self.tree_layout.addWidget(self.character_list_widget)
        self.tbl_character_list = QTableView()
        self.character_list_widget.setFixedWidth(150)
        #self.tbl_character_list.setFixedWidth(100)
        self.tbl_character_list.setMaximumWidth(150)
        self.tbl_character_list.verticalHeader().setFixedWidth(75)
        self.tbl_character_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_character_list.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        #self.tbl_character_list.dataChanged.connect(self.on_tbl_character_list_dataChanged)
        self.character_list_layout.addWidget(self.tbl_character_list)

        self.cbx_all_characters = QCheckBox()
        self.cbx_all_characters.setText("All")
        self.cbx_all_characters.setChecked(False)
        self.cbx_all_characters.clicked.connect(self.on_cbx_all_characters_clicked)
        self.character_list_layout.addWidget(self.cbx_all_characters)

        self.timetable_widget = QWidget()
        self.timetable_widget.setFixedWidth(285)
        self.timetable_layout = QVBoxLayout()
        self.timetable_widget.setLayout(self.timetable_layout)
        self.tree_layout.addWidget(self.timetable_widget)

        self.tbl_timetable = QTableWidget()
        self.tbl_timetable.setFixedWidth(265)
        self.tbl_timetable.verticalHeader().setFixedWidth(150)
        self.tbl_timetable.setRowCount(10)
        self.tbl_timetable.setColumnCount(2)
        self.tbl_timetable.setHorizontalHeaderLabels([ "FAD", "LAD"])
        self.tbl_timetable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #self.tbl_timetree.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_timetable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        #self.tbl_timetree.verticalHeader().hide()#
        self.timetable_layout.addWidget(self.tbl_timetable)

        self.btn_save_tiemtable = QPushButton("Save")
        self.btn_save_tiemtable.setFixedWidth(265)
        self.timetable_layout.addWidget(self.btn_save_tiemtable)
        self.btn_save_tiemtable.clicked.connect(self.on_btn_save_timetable_clicked)

        self.timetable_widget.hide()
        self.character_list_widget.hide()

        self.tree_label = TreeLabel()
        #self.scroll_area.setWidget(self.tree_label)
        self.tree_layout.addWidget(self.tree_label)
        self.tree_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tree_label.resized.connect(self.handle_label_resize)

        self.layout.addWidget(self.buttons_widget)

        self.tree_list = []
        self.consensus_tree = None
        self.current_tree = None
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.setPageStep(10)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self.on_slider_valueChanged)
        self.tree_info_layout.addWidget(self.slider)
        self.curr_tree_index = 0
        self.tree_type = 1
        self.tree_style = 0
        self.combo_tree_style.setCurrentIndex(0)
        self.tree_style_changed(self.combo_tree_style.currentIndex())

    def on_cbx_all_characters_clicked(self):
        if self.cbx_all_characters.isChecked():
            for i in range(self.character_model.rowCount()):
                # set all characters to checked
                self.character_model.setData(self.character_model.index(i,0), Qt.Checked, Qt.CheckStateRole)
        else:
            for i in range(self.character_model.rowCount()):
                # set all characters to unchecked
                self.character_model.setData(self.character_model.index(i,0), Qt.Unchecked, Qt.CheckStateRole)
                
        self.update_selected_character_index()
        self.tree_label.repaint()

    def on_cbx_char_mapping_clicked(self):
        char_mapping = self.cbx_char_mapping.isChecked()
        self.tree_label.char_mapping = char_mapping
        if char_mapping:
            self.character_list_widget.show()
            self.btn_characters.setText("Hide Characters")
        else:
            self.character_list_widget.hide()
            self.btn_characters.setText("Show Characters")

        self.tree_label.repaint()

    def on_tbl_character_list_dataChanged(self):
        print("on_tbl_character_list_dataChanged")
        #print("on_tbl_character_list_dataChanged")
        self.tree_label.repaint()

    def on_combo_tree_style_currentIndexChanged(self, index):
        self.tree_style_changed(index)

    def tree_style_changed(self, index):
        # hide all options
        if index == pu.TREE_STYLE_TIMETREE and not self.analysis.datamatrix.is_timetable_valid():
            self.combo_tree_style.setCurrentIndex(self.tree_style)
            self.lbl_node_minimum_offset.hide()
            self.edt_node_minimum_offset.hide()
            return

        self.tree_style = index

        self.cbx_char_mapping.hide()
        self.cbx_align_taxa.hide()
        self.lbl_node_minimum_offset.hide()
        self.edt_node_minimum_offset.hide()

        self.tree_label.topology_only = False
        self.tree_label.timetree = False
        self.tree_label.apply_branch_length = False
        self.tree_label.align_taxa = False

        if index == pu.TREE_STYLE_TOPOLOGY:
            self.tree_label.tree_style = pu.TREE_STYLE_TOPOLOGY
            self.tree_label.apply_branch_length = True
            self.cbx_char_mapping.show()
            self.cbx_align_taxa.show()
        elif index == pu.TREE_STYLE_BRANCH_LENGTH:
            self.tree_label.tree_style = pu.TREE_STYLE_BRANCH_LENGTH
            self.tree_label.apply_branch_length = True
        elif index == pu.TREE_STYLE_TIMETREE:
            #timetree = self.cbx_timetree.isChecked()
            #timetable = json.loads(self.analysis.taxa_timetable_json)
            if self.analysis.datamatrix.is_timetable_valid():
                self.tree_label.tree_style = pu.TREE_STYLE_TIMETREE
                self.tree_label.timetree = True
                # check if timetree is available
                # if yes
                self.lbl_node_minimum_offset.show()
                self.edt_node_minimum_offset.show()
            else:
                self.combo_tree_style.setCurrentIndex(self.tree_label.tree_style)
                self.tree_label.tree_style = pu.TREE_STYLE_TOPOLOGY
                self.tree_label.apply_branch_length = True
                self.cbx_char_mapping.show()
                self.cbx_align_taxa.show()

        self.tree_label.repaint()

    def on_cbx_show_axis_clicked(self):
        self.tree_label.show_axis = self.cbx_show_axis.isChecked()
        self.tree_label.repaint()

    def on_edt_node_minimum_offset_change(self):
        #print("on_edt_node_minimum_offset_change", self.edt_node_minimum_offset.text())
        self.tree_label.node_minimum_offset = float(self.edt_node_minimum_offset.text())
        self.tree_label.repaint()

    def on_btn_save_timetable_clicked(self):
        # get data from timetable widget
        # save to analysis
        timetable = []
        for i in range(self.tbl_timetable.rowCount()):
            fad = self.tbl_timetable.item(i,0).text()
            lad = self.tbl_timetable.item(i,1).text()
            #print(fad, lad)
            timetable.append( [fad, lad] )
        self.analysis.datamatrix.taxa_timetable_json = json.dumps(timetable)
        self.analysis.datamatrix.save()
        #if self.analysis.datamatrix.is_timetable_valid():
        #    self.combo_tree_style.setItemEnabled(2, True)
        #    self.tree_label.timetree = True
        #    self.tree_label.repaint()
        #else:
        #    self.combo_tree_style.setItemEnabled(2, False)
        #self.
        self.tree_label.repaint()
        return

    def on_btn_characters_clicked(self):
        if self.character_list_widget.isHidden():
            self.character_list_widget.show()
            self.btn_characters.setText("Hide Characters")
        else:
            self.character_list_widget.hide()
            self.btn_characters.setText("Show Characters")

    def on_btn_timetable_clicked(self):
        if self.timetable_widget.isHidden():
            self.timetable_widget.show()
            self.btn_timetable.setText("Hide Timetable")
        else:
            self.timetable_widget.hide()
            self.btn_timetable.setText("Edit Timetable")

    def on_combo_font_size_currentIndexChanged(self, index):
        font_size = int(self.combo_font_size.currentText())
        self.tree_label.font_size = font_size
        self.tree_label.repaint()

    def on_btn_export_clicked(self):
        if self.current_tree is None:
            return
        if self.combo_image_type.currentText() == "SVG":
            filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Scalable Vector Graphics (*.svg)")
            if filename:
                #print("export to svg:", filename)
                self.tree_label.export_tree_as_svg(filename)

        else:
            if self.combo_image_type.currentText() == "PNG":
                filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Portable Network Graphics (*.png)")
            #elif self.combo_image_type.currentText() == "PDF":
            #    filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Portable Document Format (*.pdf)")
            if filename:
                #print("export to png:", filename)
                # get pixmap from tree_label
                self.tree_label.export_tree_as_png(filename)                

    def on_btn_copy_image_clicked(self):
        if self.current_tree is None:
            return
        self.tree_label.copy_tree_image()

    def on_btn_bookmark_clicked(self):
        if self.current_tree is None:
            return
        if self.tree_type == 1:
            # get tree name via messagebox
            #tree_name, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter tree name', text="")
            #if ok:
            #    pass
            #else:
            #    return
            tree_to_save = PfTree()
            #tree_to_save.tree_name = tree_name

            #consensus_tree.project = analysis.project
            tree_to_save.analysis = self.analysis
            if self.analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
                tree_to_save.tree_type = TREE_TYPE_MPT
                tree_to_save.tree_name = TREE_TYPE_MPT + " " + str(self.tree_current_index+1)
            elif self.analysis.analysis_type == ANALYSIS_TYPE_ML:
                tree_to_save.tree_type = TREE_TYPE_BOOTSTRAP
                tree_to_save.tree_name = TREE_TYPE_BOOTSTRAP + " " + str(self.tree_current_index+1)
            elif self.analysis.analysis_type == ANALYSIS_TYPE_BAYESIAN:
                tree_to_save.tree_type = TREE_TYPE_POSTERIOR
                tree_to_save.tree_name = TREE_TYPE_POSTERIOR + " " + str(self.tree_current_index+1)
            string_io = io.StringIO()
            # Write the tree in Newick format to the text stream
            Phylo.write(self.current_tree, string_io, "newick")
            # Get the Newick string from the text stream
            newick_string = string_io.getvalue()
            # Close the StringIO object if it's not needed anymore
            string_io.close()
            
            tree_to_save.newick_text = newick_string
            tree_options = {}
            tree_options['tree_style'] = self.tree_label.tree_style
            tree_options['align_taxa'] = self.tree_label.align_taxa
            tree_options['italic_taxa_name'] = self.tree_label.italic_taxa_name
            tree_options['font_size'] = self.tree_label.font_size
            #tree_options['timetree'] = self.tree_label.timetree
            tree_options['show_axis'] = self.tree_label.show_axis
            tree_options['node_minimum_offset'] = self.tree_label.node_minimum_offset
            tree_to_save.tree_options_json = json.dumps(tree_options)

            tree_to_save.save()
            #self.add_stored_tree(newick_string)
            self.bookmarked_tree_list = PfTree.select().where(PfTree.analysis == self.analysis)
            self.bookmarked_newick_tree_list = [tree.newick_text for tree in self.bookmarked_tree_list]
            #self.bookmarked_newick_tree_list = []
            for i, tree in enumerate(self.bookmarked_tree_list):
                self.bookmarked_treeobj_hash[i] = tree


        else:
            # save bookmark
            tree = self.bookmarked_treeobj_hash[self.tree_current_index]
            tree_options = {}
            tree_options['tree_style'] = self.tree_label.tree_style
            tree_options['align_taxa'] = self.tree_label.align_taxa
            tree_options['italic_taxa_name'] = self.tree_label.italic_taxa_name
            tree_options['font_size'] = self.tree_label.font_size
            #tree_options['timetree'] = self.tree_label.timetree
            tree_options['show_axis'] = self.tree_label.show_axis
            tree_options['node_minimum_offset'] = self.tree_label.node_minimum_offset
            tree.tree_name = self.edt_tree_name.text()
            tree.tree_options_json = json.dumps(tree_options)
            tree.save()

    
    def on_btn_reset_clicked(self):
        self.set_analysis(self.analysis)
        self.combo_tree_style.setCurrentIndex(0)
        self.tree_style_changed(0)

        self.cbx_char_mapping.setChecked(False)
        self.on_cbx_char_mapping_clicked()
        #if self.rb_tree_type1.isChecked():
        #    self.on_rb_tree_type1_clicked()
        #else:
        #    self.on_rb_tree_type2_clicked() 
        #self.cbx_timetree.setChecked(False)
        #self.on_cbx_timetree_clicked()
        self.cbx_show_axis.setChecked(False)
        self.on_cbx_show_axis_clicked()
        self.cbx_fit_to_window.setChecked(True)
        self.on_cbx_fit_to_window_clicked()
        self.cbx_align_taxa.setChecked(False)
        self.on_cbx_align_taxa_clicked()
        self.cbx_italic_taxa_name.setChecked(False)
        self.on_cbx_italic_taxa_name_clicked()
        self.tree_label.scale = 1.0
        self.tree_label.pan_x = 0
        self.tree_label.pan_y = 0
        self.tree_label.temp_pan_x = 0
        self.tree_label.temp_pan_y = 0
        self.tree_label.repaint()
        
    def on_edt_tree_width_change(self):
        #print("on_edt_tree_width_change", self.edt_tree_width.text())
        self.tree_label.tree_image_width = int(self.edt_tree_width.text())
        self.tree_label.repaint()
    
    def on_edt_tree_height_change(self):
        #print("on_edt_tree_height_change", self.edt_tree_height.text())
        self.tree_label.tree_image_height = int(self.edt_tree_height.text())
        self.tree_label.repaint()

    def on_cbx_fit_to_window_clicked(self):
        fit_to_window = self.cbx_fit_to_window.isChecked()
        self.tree_label.fit_to_window = fit_to_window
        if fit_to_window:
            self.edt_tree_width.setText(str(self.tree_label.width()))
            self.edt_tree_height.setText(str(self.tree_label.height()))
            self.edt_tree_width.setEnabled(False)
            self.edt_tree_height.setEnabled(False)
            self.edt_tree_width.setReadOnly(True)
            self.edt_tree_height.setReadOnly(True)
        else:
            #print("not fit to window, edit width and height manually.")
            self.edt_tree_width.setEnabled(True)
            self.edt_tree_height.setEnabled(True)
            self.edt_tree_width.setReadOnly(False)
            self.edt_tree_height.setReadOnly(False)
        self.tree_label.repaint()

    def on_cbx_timetree_clicked(self):
        timetree = self.cbx_timetree.isChecked()
        #timetable = json.loads(self.analysis.taxa_timetable_json)
        if timetree and self.analysis.datamatrix.is_timetable_valid():
            self.tree_label.timetree = timetree
            #self.cbx_apply_branch_length.setChecked(False)
            self.tree_label.apply_branch_length = False
            self.cbx_align_taxa.setChecked(False)
            self.tree_label.align_taxa = False
        else:
            #self.cbx_timetree.setChecked(False)
            self.tree_label.timetree = False
        self.tree_label.repaint()

    def on_cbx_italic_taxa_name_clicked(self):
        self.tree_label.italic_taxa_name = self.cbx_italic_taxa_name.isChecked()
        self.tree_label.repaint()

    def on_cbx_show_branch_length_clicked(self):
        return
        self.tree_label.apply_branch_length = self.cbx_apply_branch_length.isChecked()
        if self.tree_label.apply_branch_length:
            #self.cbx_align_taxa.setEnabled(False)
            self.cbx_align_taxa.setChecked(False)
            self.cbx_timetree.setChecked(False)
            self.tree_label.align_taxa = False
            self.tree_label.timetree = False
        self.tree_label.repaint()
    
    def on_cbx_align_taxa_clicked(self):
        self.tree_label.align_taxa = self.cbx_align_taxa.isChecked()
        if self.tree_label.align_taxa:
            #self.cbx_show_branch_length.setEnabled(False)
            #self.cbx_apply_branch_length.setChecked(False)
            self.tree_label.apply_branch_length = False
            #self.cbx_timetree.setChecked(False)
            self.tree_label.timetree = False
        self.tree_label.repaint()

    def update_info(self, analysis):
        self.analysis = analysis
        #print("treeview update_info", analysis.analysis_name, analysis.analysis_status, analysis.completion_percentage)
        if analysis.completion_percentage == 100:
            self.load_trees()


    def on_rb_tree_type1_clicked(self):
        #print("on_rb_tree_type1_clicked")
        self.btn_bookmark.setText("Add Bookmark")

        self.tree_type = 1
        #self.current_treeobj_hash = self.treeobj_hash
        #self.current_newick_tree_list = self.newick_tree_list
        self.slider.setRange(0, len(self.newick_tree_list) - 1)
        self.slider.setValue(0)
        self.on_slider_valueChanged(0)
        self.lbl_total_trees.setText("/" + str(len(self.newick_tree_list)))
        self.lbl_tree_name.hide()
        self.edt_tree_name.hide()        

    def on_rb_tree_type2_clicked(self):
        #print("on_rb_tree_type2_clicked")
        self.btn_bookmark.setText("Save Bookmark")

        self.tree_type = 2
        self.slider.setRange(0, len(self.bookmarked_newick_tree_list) - 1)
        self.slider.setValue(0)
        self.on_slider_valueChanged(0)
        self.lbl_total_trees.setText("/" + str(len(self.bookmarked_newick_tree_list)))

        #self.current_treeobj_hash = self.stored_treeobj_hash
        #self.current_newick_tree_list = self.stored_newick_tree_list
        self.lbl_tree_name.show()
        self.edt_tree_name.show()

    def on_slider_valueChanged(self, value):
        #print("scrollbar valueChanged", value)
        self.tree_current_index = value
        self.edt_tree_index.setText(str(self.tree_current_index+1))

        tree = None

        if self.tree_type == 1:
            if self.tree_current_index not in self.treeobj_hash.keys():
                if self.tree_current_index < len(self.newick_tree_list):
                    tree = Phylo.read(io.StringIO(self.newick_tree_list[self.tree_current_index-1]), "newick")
                    self.treeobj_hash[self.tree_current_index] = tree
                    for clade in tree.find_clades():
                        if clade.name:
                            try:
                                taxon_index = int(clade.name) - 1
                                taxa_list = self.analysis.datamatrix.get_taxa_list()
                                clade.name = taxa_list[taxon_index]
                            except:
                                pass
                    if self.analysis and self.analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
                        self.combo_tree_style.setCurrentIndex(0)
                    else:
                        self.combo_tree_style.setCurrentIndex(1)
            else:
                tree = self.treeobj_hash[self.tree_current_index]
        elif self.tree_type == 2:
            if self.tree_current_index < len(self.bookmarked_newick_tree_list):
            #self.stored_tree_list = PfTree.select().where(PfTree.analysis == self.analysis)        
            #self.stored_newick_tree_list = [tree.newick_text for tree in self.stored_tree_list]
                #print("tree_current_index:", self.tree_current_index, len(self.bookmarked_newick_tree_list),self.bookmarked_treeobj_hash.keys())
                treeobj = self.bookmarked_treeobj_hash[self.tree_current_index]
                tree = Phylo.read(io.StringIO(self.bookmarked_newick_tree_list[self.tree_current_index]), "newick")
                tree_options = treeobj.get_tree_options()
                #self.cbx_apply_branch_length.setChecked(tree_options['apply_branch_length'])
                self.combo_tree_style.setCurrentIndex(tree_options['tree_style'])
                self.cbx_align_taxa.setChecked(tree_options['align_taxa'])
                self.cbx_italic_taxa_name.setChecked(tree_options['italic_taxa_name'])
                self.combo_font_size.setCurrentText(str(tree_options['font_size']))
                #self.cbx_timetree.setChecked(tree_options['timetree'])
                #self.tree_label.apply_branch_length = tree_options['apply_branch_length']
                self.tree_label.tree_style = tree_options['tree_style']
                self.tree_label.align_taxa = tree_options['align_taxa']
                self.tree_label.italic_taxa_name = tree_options['italic_taxa_name']
                self.tree_label.font_size = tree_options['font_size']
                self.tree_label.timetree = tree_options['timetree']
                self.edt_tree_name.setText(treeobj.tree_name)
                self.edt_node_minimum_offset.setText(str(tree_options['node_minimum_offset']))


        if tree is None:
            self.tree_label.set_tree(tree)
            #self.tree_label.clear()
            self.tree_label.repaint()
            return
        self.current_tree = tree
        #print("selection changed. tree:", tree)
        #self.edt_tree_width.setText(str(self.tree_label.width()))
        #self.edt_tree_height.setText(str(self.tree_label.height()))
        self.tree_label.set_tree(tree)
        self.tree_label.set_analysis(self.analysis)
        self.tree_label.update()
        return
    
        #tree = self.tree_list[value]
        fig = plt.figure(figsize=(10, 20), dpi=100)
        axes = fig.add_subplot(1, 1, 1)
        Phylo.draw(tree, axes=axes,do_show=False)

        buf = io.BytesIO()
        plt.savefig(buf, format='svg')
        buf.seek(0)  # Go to the beginning of the BytesIO object
        self.set_tree_image_buf(buf)
        plt.close(fig)

    def set_tree_image_buf(self, buf):
        #print("set_tree_image in treelabel", tree_image)
        self.tree_label.orig_pixmap = QPixmap()
        self.tree_label.orig_pixmap.loadFromData(buf.read())
        self.tree_label.curr_pixmap = self.tree_label.orig_pixmap.scaled(int(self.tree_label.orig_pixmap.width() * self.tree_label.scale / self.tree_label.image_canvas_ratio), int(self.tree_label.orig_pixmap.height() * self.tree_label.scale / self.tree_label.image_canvas_ratio))
        self.tree_label.repaint()

    def set_analysis(self, analysis):
        self.analysis = analysis
        self.load_trees()
        #if self.analysis.datamatrix.is_timetable_valid():
        #    self.combo_tree_style.setItemEnabled(2, True)
        #else:
        #    self.combo_tree_style.setItemEnabled(2, False)
        self.tree_label.set_analysis_type(self.analysis.analysis_type)
        if self.analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            self.cbx_align_taxa.setEnabled(True)
            #self.cbx_show_branch_length.setEnabled(False)
            #self.cbx_apply_branch_length.setChecked(False)
        elif self.analysis.analysis_type == ANALYSIS_TYPE_ML:
            #self.cbx_align_taxa.setEnabled(False)
            #self.cbx_apply_branch_length.setEnabled(True)
            #self.cbx_apply_branch_length.setChecked(True)
            pass
        elif self.analysis.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            #self.cbx_align_taxa.setEnabled(False)
            #self.cbx_apply_branch_length.setEnabled(True)
            #self.cbx_apply_branch_length.setChecked(True)
            pass
        self.on_cbx_show_branch_length_clicked()
        self.on_cbx_align_taxa_clicked()
        self.on_cbx_fit_to_window_clicked()
        #print("load trees tree label size", self.tree_label.width(), self.tree_label.height())

        dm = self.analysis.datamatrix
        taxa_list = dm.get_taxa_list()
        self.tbl_timetable.setRowCount(len(taxa_list))
        timetable = dm.get_taxa_timetable()
        #print("timetable:", timetable)
        #print("taxa_list:", taxa_list)

        for row, taxon in enumerate(taxa_list):
            if row >= len(timetable):
                continue
            #print( row, taxon, str(timetable[row][0]), str(timetable[row][1]))
            # reset table and add taxon to table
            #row = self.tbl_timetable.rowCount()
            #self.tbl_timetable.setRowCount(row+1)
            #self.tbl_timetree.setItem(row, 0, QTableWidgetItem(taxon))
            self.tbl_timetable.setItem(row, 0, QTableWidgetItem(str(timetable[row][0])))
            self.tbl_timetable.setItem(row, 1, QTableWidgetItem(str(timetable[row][1])))
        self.tbl_timetable.setVerticalHeaderLabels(taxa_list)

        character_list = dm.get_character_list()
        data = [False]*len(character_list)
        #table_view = QTableView()
        self.character_model = CheckboxTableModel(data)
        self.character_model.dataChanged.connect(self.on_character_data_changed)
        self.tbl_character_list.setModel(self.character_model)

    def on_character_data_changed(self, top_left, bottom_right, roles):
        #print(f"Data changed: Top Left: {top_left}, Bottom Right: {bottom_right}, Roles: {roles}")
        #print(f"Data changed: Top Left: {top_left.row()}, {top_left.column()}")
        #character_index_list = 
        self.update_selected_character_index()

    def update_selected_character_index(self):
        self.tree_label.character_index_list = self.character_model.get_selected_indices()
        self.tree_label.repaint()

    def load_trees(self):
        #print("load trees")
        tree_dir = self.analysis.result_directory
        if not os.path.exists(tree_dir):
            return
        
        if self.analysis.analysis_type == ANALYSIS_TYPE_ML:
            tf = pu.PhyloTreefile()
            filename = os.path.join(tree_dir, self.analysis.datamatrix.datamatrix_name.replace(" ","_") + ".phy.boottrees")
            #print("ML tree filename:", filename)
            tf.readtree(filename, 'treefile')
            self.newick_tree_list = tf.tree_list
            #print("tree list:", self.newick_tree_list)
    
        elif self.analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            tf = pu.PhyloTreefile()
            tf.readtree(os.path.join(tree_dir, "tmp.tre"), 'tre')
            self.newick_tree_list = tf.tree_list

        elif self.analysis.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            tf = pu.PhyloTreefile()
            tf.readtree(os.path.join(tree_dir, self.analysis.datamatrix.datamatrix_name.replace(" ","_") + ".nex.t"), 'Nexus')
            self.newick_tree_list = tf.tree_list

        self.slider.setRange(0, len(self.newick_tree_list) - 1)
        self.slider.setValue(0)
        self.slider.setPageStep(10)
        self.slider.setSingleStep(1)
        self.lbl_total_trees.setText("/" + str(len(self.newick_tree_list)))
        self.edt_tree_index.setText("1")
        self.on_slider_valueChanged(0)
        self.edt_tree_name.hide()
        self.lbl_tree_name.hide()

        self.bookmarked_tree_list = PfTree.select().where(PfTree.analysis == self.analysis)
        self.bookmarked_newick_tree_list = [tree.newick_text for tree in self.bookmarked_tree_list]
        for i, tree in enumerate(self.bookmarked_tree_list):
            self.bookmarked_treeobj_hash[i] = tree
        #for tree in stored_tree_list:
        #    self.add_stored_tree(tree.newick_text)

    def set_tree_image(self, tree_image):
        self.tree_label.set_tree_image( tree_image)

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        #print("treeViewer resizeEvent")
        super().resizeEvent(a0)
        #print("tree label size:", self.tree_label.width(), self.tree_label.height())
        if self.cbx_fit_to_window.isChecked():
            self.edt_tree_width.setText(str(self.tree_label.width()))
            self.edt_tree_height.setText(str(self.tree_label.height()))
        return
    def handle_label_resize(self, new_size: QSize):
        #print("handle_label_resize")
        if self.cbx_fit_to_window.isChecked():
            self.edt_tree_width.setText(str(self.tree_label.width()))
            self.edt_tree_height.setText(str(self.tree_label.height()))
        return

class TreeLabel(QLabel):
    resized = pyqtSignal(QSize)
    def __init__(self):
        super(TreeLabel, self).__init__()
        self.setMinimumSize(400,300)
        self.bgcolor = "#888888"
        self.m_app = QApplication.instance()

        #self.read_settings()
        self.tree = None
        self.orig_pixmap = None
        self.curr_pixmap = None
        self.scale = 1.0
        self.pan_mode = MODE['NONE']
        self.edit_mode = MODE['NONE']
        self.pan_x = 0
        self.pan_y = 0
        self.temp_pan_x = 0
        self.temp_pan_y = 0
        self.mouse_down_x = 0
        self.mouse_down_y = 0
        self.mouse_curr_x = 0
        self.mouse_curr_y = 0
        self.image_canvas_ratio = 1.0
        self.orig_width = -1
        self.orig_height = -1
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.tree_leaf_height = 30
        self.tree_y_offset = 30
        self.tree_unit_width = 50
        self.text_offset = 5
        #self.set_mode(MODE['EDIT_LANDMARK'])
        self.tree_node_parents = {}
        self.analysis_type = None

        self.tree_style = pu.TREE_STYLE_TOPOLOGY
        #self.apply_branch_length = False
        #self.timetree = False
        self.char_mapping = False
        self.align_taxa = False
        self.node_minimum_offset = 0.1

        self.tree_image_width = 0
        self.tree_image_height = 0
        self.fit_to_window = True
        self.italic_taxa_name = False
        self.font_size = 10
        self.show_axis = False
        self.character_index_list = []

        self.leaf_count = 0
        self.min_clade_depth = 0
        self.x_padding = 50
        self.y_padding = 25

    def _2canx(self, coord):
        return round((float(coord) / self.image_canvas_ratio) * self.scale) + self.pan_x + self.temp_pan_x
    def _2cany(self, coord):
        return round((float(coord) / self.image_canvas_ratio) * self.scale) + self.pan_y + self.temp_pan_y
    def _2imgx(self, coord):
        return round(((float(coord) - self.pan_x) / self.scale) * self.image_canvas_ratio)
    def _2imgy(self, coord):
        return round(((float(coord) - self.pan_y) / self.scale) * self.image_canvas_ratio)

    def wheelEvent(self, event):
        return
        #if self.orig_pixmap is None:
        #    return
        we = QWheelEvent(event)
        scale_delta = 0
        if we.angleDelta().y() > 0:
            scale_delta = 0.1
        else:
            scale_delta = -0.1
        if self.scale <= 0.8 and scale_delta < 0:
            return
        if self.scale > 1:
            scale_delta *= math.floor(self.scale)
        
        prev_scale = self.scale
        self.scale += scale_delta
        self.scale = round(self.scale * 10) / 10
        scale_proportion = self.scale / prev_scale
        if self.orig_pixmap is not None:
            self.curr_pixmap = self.orig_pixmap.scaled(int(self.orig_pixmap.width() * self.scale / self.image_canvas_ratio), int(self.orig_pixmap.height() * self.scale / self.image_canvas_ratio))

        self.pan_x = int( we.pos().x() - (we.pos().x() - self.pan_x) * scale_proportion )
        self.pan_y = int( we.pos().y() - (we.pos().y() - self.pan_y) * scale_proportion )

        self.repaint()

        QLabel.wheelEvent(self, event)

    def mouseMoveEvent(self, event):
        me = QMouseEvent(event)
        self.mouse_curr_x = me.x()
        self.mouse_curr_y = me.y()
        curr_pos = [self.mouse_curr_x, self.mouse_curr_y]
        #print("self.edit_mode", self.edit_mode, "curr pos:", curr_pos)
    
        if self.pan_mode == MODE['PAN']:
            self.temp_pan_x = int(self.mouse_curr_x - self.mouse_down_x)
            self.temp_pan_y = int(self.mouse_curr_y - self.mouse_down_y)
            self.repaint()
        QLabel.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):

        me = QMouseEvent(event)
        if me.button() == Qt.RightButton:
            self.pan_mode = MODE['PAN']
            self.mouse_down_x = me.x()
            self.mouse_down_y = me.y()
            self.repaint()
        QLabel.mousePressEvent(self, event)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        me = QMouseEvent(ev)
        if self.pan_mode == MODE['PAN']:
            self.pan_mode = MODE['NONE']
            self.pan_x += self.temp_pan_x
            self.pan_y += self.temp_pan_y
            self.temp_pan_x = 0
            self.temp_pan_y = 0
            self.repaint()
        return super().mouseReleaseEvent(ev)
    '''
    svgGenerator = QSvgGenerator()
    svgGenerator.setFileName("test_output.svg")
    svgGenerator.setSize(QSize(400, 400))
    svgGenerator.setViewBox(QRect(0, 0, 400, 400))
    svgGenerator.setTitle("SVG Test")
    svgGenerator.setDescription("An SVG drawing example.")

    painter = QPainter(svgGenerator)
    painter.setPen(QColor(0, 0, 0))
    painter.drawText(10, 20, "Hello, World!")
    painter.drawRect(10, 30, 100, 100)
    painter.end()
    '''
    def export_tree_as_svg(self, filename):
        svgGenerator = QSvgGenerator()
        svgGenerator.setFileName(filename)
        svgGenerator.setSize(QSize(self.tree_image_width, self.tree_image_height))
        svgGenerator.setViewBox(QRect(0, 0, self.tree_image_width, self.tree_image_height))
        svgGenerator.setTitle("Phylogenetic Tree")
        svgGenerator.setDescription("An SVG drawing of a phylogenetic tree")

        painter = QPainter(svgGenerator)
        self.draw_tree(painter)
        painter.end()

    def copy_tree_image(self):
        clipboard = QApplication.clipboard()

        pixmap = QPixmap(self.tree_image_width, self.tree_image_height)
        pixmap.fill(QColor(QColor("#FFFFFF")))
        painter = QPainter(pixmap)
        # store pan_x, pan_y
        pan_x, pan_y = self.pan_x, self.pan_y
        self.pan_x = self.pan_y = 0
        self.draw_tree(painter)
        clipboard.setPixmap(pixmap)
        painter.end()
        self.pan_x, self.pan_y = pan_x, pan_y

    def export_tree_as_png(self, filename):

        #painter = Q
        pixmap = QPixmap(self.tree_image_width, self.tree_image_height)
        pixmap.fill(QColor(QColor("#FFFFFF")))
        painter = QPainter(pixmap)
        # store pan_x, pan_y
        pan_x, pan_y = self.pan_x, self.pan_y
        self.pan_x = self.pan_y = 0
        self.draw_tree(painter)
        pixmap.save(filename)
        painter.end()


    def draw_tree(self, painter):
        #node_minimum_offset = 0.1
        if self.tree is None:
            return
        #print("draw_tree", self.tree)
        #Phylo.draw_ascii(self.tree)

        clade_list = [ c for c in self.tree.find_clades() ]
        root = clade_list[0]
        self.leaf_count = root.count_terminals()
        #print("leaf_count", self.leaf_count)

        self.min_clade_depth = 0
        tree_length = 0

        ''' calculate depths '''
        if self.tree_style == pu.TREE_STYLE_BRANCH_LENGTH and self.analysis_type != ANALYSIS_TYPE_PARSIMONY:
            self.clade_depths = self.tree.depths()
        elif self.tree_style == pu.TREE_STYLE_TOPOLOGY and self.char_mapping:
            #self.clade_depths = self.tree.depths(unit_branch_lengths=True)
            self.clade_depths = self.map_characters_to_nodes()
            #print("clade_depths", self.clade_depths)
            ''' adjust clade depths (apply minimum node offset) '''
            #self.min_clade_depth = 999999
            for clade in [ c for c in self.tree.find_clades(order='postorder') ]:
                tree_length += len(clade.changed_characters)
                if clade.is_terminal():
                    continue
                for child in clade:
                    if self.clade_depths[child] - self.clade_depths[clade] < self.node_minimum_offset:
                        self.clade_depths[clade] = self.clade_depths[child] - self.node_minimum_offset
                #self.min_clade_depth = min(self.min_clade_depth, self.clade_depths[clade])

        else:
            self.clade_depths = self.tree.depths(unit_branch_lengths=True)
        #print("clade_depths", self.clade_depths)
        self.max_depth = max(self.clade_depths.values())

        taxa_list = [ clade.name for clade in clade_list if clade.name is not None ]
        if self.tree_style == pu.TREE_STYLE_TOPOLOGY and self.char_mapping:
            character_states_list = [ clade.character_states for clade in clade_list if clade.name is not None ]
        # get font
        font = painter.font()
        fontMetrics = QFontMetrics(font)
        max_text_width = 0
        max_text = ''
        for idx, taxon in enumerate(taxa_list):
            taxon_text = taxon
            if self.tree_style == pu.TREE_STYLE_TOPOLOGY and self.char_mapping:
                taxon_text = "".join( [ character_states_list[idx][i] for i in self.character_index_list ] ) + " " + taxon
            textWidth = fontMetrics.width( taxon_text )
            if textWidth > max_text_width:
                max_text_width = textWidth
                max_text = taxon_text


        if self.tree_style == pu.TREE_STYLE_TIMETREE:
            taxa_list = self.analysis.datamatrix.get_taxa_list()
            self.timetable = self.analysis.datamatrix.get_taxa_timetable()
            
            ''' max_depth setting '''
            total_max_fad = 0
            total_min_lad = 999999
            for row in self.timetable:
                total_max_fad = max(total_max_fad, float(row[0]))
                total_min_lad = min(total_min_lad, float(row[1]))
            self.max_depth = total_max_fad - total_min_lad
            self.max_fad = total_max_fad
            self.min_lad = total_min_lad

            ''' timetable setting '''
            self.taxa_timetable = {}
            for i in range(len(taxa_list)):
                self.taxa_timetable[taxa_list[i]] = [float(self.timetable[i][0]), float(self.timetable[i][1])]
                #self.clade_depths[taxa_list[i]] = max_fad - int(timetable[i][0])

            ''' clade depths setting '''
            clade_list = [ c for c in self.tree.find_clades() ]
            for clade in clade_list:
                if clade.is_terminal():
                    self.clade_depths[clade] = total_max_fad - self.taxa_timetable[clade.name][1]
                    #clade.branch_length = self.max_fad - self.taxa_timetable[clade.name][1]
                else:
                    max_fad = 0
                    for leaf in clade.find_clades(terminal=True):
                        max_fad = max(max_fad, self.taxa_timetable[leaf.name][0])
                        #min_lad = min(min_lad, self.taxa_timetable[leaf.name][1])
                    self.clade_depths[clade] = total_max_fad - max_fad

            ''' adjust clade depths (apply minimum node offset) '''
            self.min_clade_depth = 999999
            for clade in [ c for c in self.tree.find_clades(order='postorder') ]:
                if clade.is_terminal():
                    continue
                for child in clade:
                    if self.clade_depths[child] - self.clade_depths[clade] < self.node_minimum_offset:
                        self.clade_depths[clade] = self.clade_depths[child] - self.node_minimum_offset
                self.min_clade_depth = min(self.min_clade_depth, self.clade_depths[clade])


                #print(" "*int(self.clade_depths[clade]),"clade:", clade, clade.name, clade.branch_length, self.clade_depths[clade])

        #print("clade depths", self.clade_depths)
        #print("max_depth", self.max_depth)
        #print("max text width", max_text, max_text_width)
        self.branch_length_scale = ( self.tree_image_width * 0.9 - max_text_width ) / (self.max_depth - self.min_clade_depth)
        self.row_height = int( ( self.tree_image_height - self.y_padding * 2 ) * 0.9 / self.leaf_count )
        #print("row_height", self.row_height, "tree_image_height", self.tree_image_height, "leaf_count", self.leaf_count)
        self.tree_unit_width = int( self.tree_image_width * 0.05 )
        #self.

        ''' row height adjustment based on text height
        font = painter.font()
        font.setPointSize(self.font_size)
        fontMetrics = QFontMetrics(font)
        textHeight = fontMetrics.height()
        self.row_height = max(self.row_height, textHeight)
        '''

        ''' set text font '''
        font = painter.font()
        if self.italic_taxa_name:
            font.setItalic(True)
        font.setPointSize(self.font_size)
        painter.setFont(font)

        v_pos = self.draw_node(painter, root, 0, 0)

        ''' set axis font '''
        if self.show_axis:
            self.draw_axis(painter)

        if self.tree_style == pu.TREE_STYLE_TOPOLOGY and self.char_mapping:
            #self.draw_character_mapping(painter, tree_length)
            self.draw_text( painter, 0, self.leaf_count - 1, "Tree Length: " + str(tree_length) )

    def map_characters_to_nodes(self):
        #return
        pu.reconstruct_ancestral_states(self.tree, self.analysis.datamatrix.datamatrix_as_list(), self.analysis.datamatrix.get_taxa_list())

        clade_depths = {}
        self.calculate_depths(self.tree.root, clade_depths)
        return clade_depths
        #clade_depths = {}

    def calculate_depths(self, node, clade_depths, depth=0):
        clade_depths[node] = depth + len(node.changed_characters)
        for child in node:
            self.calculate_depths(child, clade_depths, clade_depths[node])
            '''
            def print_character_states(node, depth=0):

                print(" "*4*depth,node.name, node.character_states, node.changed_characters, len(node.changed_characters) )
                for child in node:
                    print_character_states(child, depth + 1)
            '''


        #pu.print_character_states(self.tree.root)
        #print("character_index_list", self.character_index_list)

    def draw_axis(self, painter):
        #print("draw_axis")
        axis_offset = 5

        # draw x-axis
        self.draw_line(painter, 0, self.max_depth - self.min_clade_depth, self.leaf_count, self.leaf_count, thickness=1)

        # set axis font 
        font = painter.font()
        font.setItalic(False)
        font.setPointSize(10)
        painter.setFont(font)

        # draw x-axis ticks
        for i in range(0, int(self.max_depth)+1):
            x, y = self.convert_coords(i - self.min_clade_depth, self.leaf_count)
            painter.drawLine(x, y, x, y+axis_offset)
            if self.tree_style == pu.TREE_STYLE_TIMETREE:
                tick_number = str(self.min_lad + self.max_depth - i)
            else:
                tick_number = str(i)
            fontMetrics = QFontMetrics(font)
            textWidth = fontMetrics.width(tick_number)
            painter.drawText(x-int(textWidth/2), y+axis_offset+15, str(tick_number))
        
        # draw y-axis if needed
        #painter.drawLine(self.tree_unit_width-axis_offset, self.row_height, self.tree_unit_width-axis_offset, self.tree_image_height - self.row_height)

    def draw_node(self, painter, node, begin_row, depth ):
        #print(" "*depth*4, "draw_node", node, begin_row, depth, node.is_terminal())
        if node.is_terminal():
            text = node.name
            if self.align_taxa:
                depth = self.max_depth
            if self.tree_style == pu.TREE_STYLE_BRANCH_LENGTH:
                depth = self.clade_depths[node]
            elif self.tree_style == pu.TREE_STYLE_TIMETREE:
                depth = self.max_fad - self.taxa_timetable[node.name][1] - self.min_clade_depth
            elif self.tree_style == pu.TREE_STYLE_TOPOLOGY and self.char_mapping:
                depth = self.clade_depths[node]
                text = "".join([ str(node.character_states[x]) for x in self.character_index_list]) + " " + text
            self.draw_text( painter, depth, begin_row, text )
            return begin_row
        else:
            #print("non-terminal:", node)
            traversed_row_count = 0
            v_pos_sum = 0
            v_pos_list = []

            ''' current node to children '''
            for child in node:
                v_pos = self.draw_node(painter, child, begin_row + traversed_row_count, depth+1)
                #print("child:", child, depth, v_pos)
                v_pos_list.append(v_pos)
                v_pos_sum += v_pos
                #self.draw_node(painter, child, begin_row + traversed_row_count, depth+1)
                from_depth = depth
                to_depth = depth +1
                if self.align_taxa and child.is_terminal():
                    to_depth = self.max_depth
                if self.tree_style == pu.TREE_STYLE_BRANCH_LENGTH:
                    from_depth = self.clade_depths[node]
                    to_depth = self.clade_depths[child]
                elif self.tree_style == pu.TREE_STYLE_TOPOLOGY and self.char_mapping:
                    from_depth = self.clade_depths[node]
                    to_depth = self.clade_depths[child]
                elif self.tree_style == pu.TREE_STYLE_TIMETREE:
                    if child.is_terminal():
                        terminal_from_depth = self.max_fad - self.taxa_timetable[child.name][0] - self.min_clade_depth
                        terminal_to_depth = self.max_fad - self.taxa_timetable[child.name][1] - self.min_clade_depth
                        if terminal_from_depth != terminal_to_depth:
                            self.draw_line(painter, terminal_from_depth, terminal_to_depth, v_pos, v_pos, thickness=3)
                    from_depth = self.clade_depths[node] - self.min_clade_depth
                    to_depth = self.clade_depths[child] - self.min_clade_depth
                    #print("node:",node,"from_depth", from_depth, "to_depth", to_depth)
                self.draw_line(painter, from_depth, to_depth, v_pos, v_pos )

                ''' if char_mapping, write changed character num '''
                if self.tree_style == pu.TREE_STYLE_TOPOLOGY and self.char_mapping:
                    transition_list = []
                    for i in child.changed_characters:
                        #print(i, node.character_states[i], child.character_states[i])
                        transition_list.append( [ i, node.character_states[i], child.character_states[i] ])
                    self.draw_transition_text(painter, ( from_depth + to_depth ) / 2, v_pos, transition_list)

                traversed_row_count += child.count_terminals()
            #print(v_pos_list)
            if self.tree_style == pu.TREE_STYLE_BRANCH_LENGTH:
                depth = self.clade_depths[node]
            elif self.tree_style == pu.TREE_STYLE_TIMETREE:
                depth = self.clade_depths[node] - self.min_clade_depth
            elif self.tree_style == pu.TREE_STYLE_TOPOLOGY and self.char_mapping:
                depth = self.clade_depths[node]
            self.draw_line(painter, depth, depth, v_pos_list[0], v_pos_list[-1])
            average_v_pos = v_pos_sum / len(node)
            if self.tree_style == pu.TREE_STYLE_TOPOLOGY and self.char_mapping:
                self.draw_text(painter, from_depth, average_v_pos, "".join([ str(node.character_states[x]) for x in self.character_index_list]))
            return average_v_pos

    def convert_coords(self, x, y):
        new_x = self.x_padding + int( x * self.branch_length_scale ) + self.pan_x + self.temp_pan_x
        new_y = self.y_padding + int( ( y + 0.5 ) * self.row_height ) + self.pan_y + self.temp_pan_y
        return new_x, new_y

    def draw_line(self, painter, x1, x2, y1, y2,thickness=1):
        x1, y1 = self.convert_coords(x1, y1)
        x2, y2 = self.convert_coords(x2, y2)
        #x1 = int( x1 * self.branch_length_scale ) + self.tree_unit_width + self.pan_x + self.temp_pan_x
        #x2 = int( x2 * self.branch_length_scale ) + self.tree_unit_width + self.pan_x + self.temp_pan_x
        #y1 = int( ( y1 + 1.5 ) * self.row_height ) - int(self.row_height / 2) + self.pan_y + self.temp_pan_y
        #y2 = int( ( y2 + 1.5 ) * self.row_height ) - int(self.row_height / 2) + self.pan_y + self.temp_pan_y

        # adjust thickness
        #painter.drawRect(x1, y1-thickness, x2, y2+thickness)
        #print("draw_line", x1, y1, x2, y2, thickness)
        #painter.drawLine(x1, y1, x2, y2)

        if thickness == 1:
            painter.drawLine(x1, y1, x2, y2)
        else:
            painter.fillRect(x1, y1-int(thickness/2), x2-x1+1, thickness, QColor("#000000"))

    def draw_transition_text(self, painter, x, y, transition_list ):
        selected_character_index_list = self.character_index_list
        text_list = []
        for transition in transition_list:
            idx, from_state, to_state = transition
            if idx in selected_character_index_list:
                text_list.append( str(idx+1) + "(" + str(from_state) + "→" + str(to_state) + ")" )
        text = " ".join(text_list)
        x1, y1 = self.convert_coords(x, y)
        fontMetrics = QFontMetrics(painter.font())
        textWidth = fontMetrics.width(text)
        textHeight = fontMetrics.height()

        painter.drawText(x1-int(textWidth/2), y1-int(textHeight/2), text)

    def draw_text(self, painter, x, y, text):

        x1, y1 = self.convert_coords(x, y)
        fontMetrics = QFontMetrics(painter.font())
        textWidth = fontMetrics.width(text)
        textHeight = fontMetrics.height()

        painter.drawText(x1+5, y1+int(textHeight/2), text)

    def paintEvent(self, event):
        #print("tree paint", self.curr_pixmap)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QBrush(QColor(self.bgcolor)))#as_qt_color(COLOR['BACKGROUND'])))
        if self.fit_to_window:
            self.tree_image_width = self.width()
            self.tree_image_height = self.height()
        
        image_rect = QRect(self.pan_x+self.temp_pan_x, self.pan_y+self.temp_pan_y,self.tree_image_width, self.tree_image_height)
        #print(self.rect(), self.pan_x+self.temp_pan_x, self.pan_y+self.temp_pan_y,self.tree_image_width, self.tree_image_height)
        #image_pos = QPoint()
        #print(self.rect(), image_rect)

        painter.fillRect(image_rect, QBrush(QColor("#FFFFFF")))

        self.draw_tree(painter)

        #self.setPixmap(self.pixmap)

        #if self.curr_pixmap is not None:
        #    painter.drawPixmap(self.pan_x+self.temp_pan_x, self.pan_y+self.temp_pan_y,self.curr_pixmap)
        

    def calculate_resize(self):
        #print("calculate_resize", self.orig_pixmap, self.width(), self.height(), self)
        if self.orig_pixmap is not None:
            self.orig_width = self.orig_pixmap.width()
            self.orig_height = self.orig_pixmap.height()
            image_wh_ratio = self.orig_width / self.orig_height
            label_wh_ratio = self.width() / self.height()
            if image_wh_ratio > label_wh_ratio:
                self.image_canvas_ratio = self.orig_width / self.width()
            else:
                self.image_canvas_ratio = self.orig_height / self.height()
            self.curr_pixmap = self.orig_pixmap.scaled(int(self.orig_width*self.scale/self.image_canvas_ratio),int(self.orig_height*self.scale/self.image_canvas_ratio), Qt.KeepAspectRatio)
            self.setPixmap(self.curr_pixmap)
        self.repaint()


    def resizeEvent(self, event):
        #print("tree label resizeEvent", self, self.size())
        self.calculate_resize()
        #QLabel.resizeEvent(self, event)
        super(TreeLabel, self).resizeEvent(event)
        self.resized.emit(self.size())

    '''
    def updatePixmapSize(self):
        print("updatePixmapSize", self.size())
        print("scale", self.scale, "image_canvas_ratio", self.image_canvas_ratio, "orig_width", self.orig_width, "orig_height", self.orig_height, "curr_pixmap", self.curr_pixmap, "orig_pixmap", self.orig_pixmap)

        if self.orig_pixmap and not self.size().isNull():
            self.orig_width = self.orig_pixmap.width()
            self.orig_height = self.orig_pixmap.height()
            image_wh_ratio = self.orig_width / self.orig_height
            label_wh_ratio = self.width() / self.height()
            if image_wh_ratio > label_wh_ratio:
                self.image_canvas_ratio = self.orig_width / self.width()
            else:
                self.image_canvas_ratio = self.orig_height / self.height()
            self.scale = 1.0
            self.curr_pixmap = self.orig_pixmap.scaled(int(self.orig_width*self.scale/self.image_canvas_ratio),int(self.orig_width*self.scale/self.image_canvas_ratio), Qt.KeepAspectRatio)
            self.setPixmap(self.curr_pixmap)
            self.repaint()


    def showEvent(self, event):
        print("showEvent", self, self.size())
        print("scale", self.scale, "image_canvas_ratio", self.image_canvas_ratio, "orig_width", self.orig_width, "orig_height", self.orig_height, "curr_pixmap", self.curr_pixmap, "orig_pixmap", self.orig_pixmap)
        self.updatePixmapSize()
        super(TreeLabel, self).showEvent(event)
    '''

    def set_tree_image(self, tree_image):
        #print("set_tree_image in treelabel", tree_image)

        self.tree_image = tree_image
        #self.orig_pixmap = QPixmap(self.tree_image)
        self.orig_pixmap = QPixmap(self.tree_image)
        #print("orig_pixmap", self.orig_pixmap)
        #self.update()

    def set_analysis_type(self, analysis_type):
        self.analysis_type = analysis_type

    def set_analysis(self, analysis):
        self.analysis = analysis

    def set_tree(self, tree):
        if tree is None:
            # clear label
            self.tree = None
            self.repaint()
            return

        self.tree = tree
        #parents = {}
        for clade in tree.find_clades(order="level"):
            for child in clade:
                self.tree_node_parents[child] = clade
        return self.tree_node_parents
        #for clade in tree.find_clades():
        #for child in root:
            #print("child:", child)
        #for clade in cldes:
        #    print("clade:", clade) 
        #print("set_tree in treelabel", tree.BaseTree)
        #fig = plt.figure(figsize=(10, 20), dpi=100)
        #axes = fig.add_subplot(1, 1, 1)
        #Phylo.draw(tree, axes=axes,do_show=False)

        #buf = io.BytesIO()
        #plt.savefig(buf, format='svg')
        #buf.seek(0)

class AnalysisDialog(QDialog):
    def __init__(self,parent, logger=None):
        super().__init__()
        self.logger = logger or PfLogger.get_logger(__name__)
        self.setWindowTitle("PhyloForester - Run Analysis")
        self.parent = parent
        self.remember_geometry = True
        self.m_app = QApplication.instance()
        self.read_settings()
        self.datamatrix = None
        self.edtProjectName = QLineEdit()
        self.edtProjectDesc = QLineEdit()
        self.edtDatamatrixName = QLineEdit()
        self.result_directory_widget = QWidget()
        self.result_directory_layout = QHBoxLayout()
        self.edtResultDirectory = QLineEdit(self.result_directory_base)
        self.edtResultDirectory.setReadOnly(True)
        self.btnResultDirectory = QPushButton()
        self.btnResultDirectory.setText("Select")
        self.btnResultDirectory.clicked.connect(self.select_result_directory)
        self.result_directory = Path(pu.DEFAULT_RESULT_DIRECTORY).resolve()
        self.result_directory_layout.addWidget(self.edtResultDirectory)
        self.result_directory_layout.addWidget(self.btnResultDirectory)
        self.result_directory_widget.setLayout(self.result_directory_layout)


        self.main_layout = QFormLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addRow("Project Name", self.edtProjectName)
        self.main_layout.addRow("Description", self.edtProjectDesc)
        self.main_layout.addRow("Datamatrix Name", self.edtDatamatrixName)
        self.main_layout.addRow("Result Directory", self.result_directory_widget)

        self.btnRun = QPushButton()
        self.btnRun.setText("Run")
        self.btnRun.clicked.connect(self.Run)

        self.btnCancel = QPushButton()
        self.btnCancel.setText("Cancel")
        self.btnCancel.clicked.connect(self.Cancel)

        self.cbxParsimony = QCheckBox()
        self.cbxParsimony.setText(ANALYSIS_TYPE_PARSIMONY)
        self.cbxParsimony.setChecked(False)
        self.cbxParsimony.clicked.connect(self.on_cbxParsimony_clicked)
        # Disable if TNT path not configured
        if not self.m_app.tnt_path:
            self.cbxParsimony.setEnabled(False)
            self.cbxParsimony.setToolTip("TNT software path not configured.\nPlease set TNT path in Preferences.")

        self.cbxML = QCheckBox()
        self.cbxML.setText(ANALYSIS_TYPE_ML)
        self.cbxML.setChecked(False)
        self.cbxML.clicked.connect(self.on_cbxML_clicked)
        # Disable if IQTree path not configured
        if not self.m_app.iqtree_path:
            self.cbxML.setEnabled(False)
            self.cbxML.setToolTip("IQTree software path not configured.\nPlease set IQTree path in Preferences.")

        self.cbxBayesian = QCheckBox()
        self.cbxBayesian.setText(ANALYSIS_TYPE_BAYESIAN)
        self.cbxBayesian.setChecked(False)
        self.cbxBayesian.clicked.connect(self.on_cbxBayesian_clicked)
        # Disable if MrBayes path not configured
        if not self.m_app.mrbayes_path:
            self.cbxBayesian.setEnabled(False)
            self.cbxBayesian.setToolTip("MrBayes software path not configured.\nPlease set MrBayes path in Preferences.")

        self.cbx_layout = QHBoxLayout()
        self.cbx_layout.addWidget(self.cbxParsimony)
        self.cbx_layout.addWidget(self.cbxML)
        self.cbx_layout.addWidget(self.cbxBayesian)
        self.cbx_widget = QWidget()
        self.cbx_widget.setLayout(self.cbx_layout)
        self.main_layout.addRow(self.cbx_widget)

        self.tabView = QTabWidget()
        self.main_layout.addRow(self.tabView)
        self.tabParsimony = QWidget()
        self.tabML = QWidget()
        self.tabBayesian = QWidget()

        self.parsimony_layout = QGridLayout()
        self.tabParsimony.setLayout(self.parsimony_layout)
        self.ml_layout = QGridLayout()
        self.tabML.setLayout(self.ml_layout)
        self.bayesian_layout = QGridLayout()
        self.tabBayesian.setLayout(self.bayesian_layout)

        
        #self.lblAnalysisNameParsimony = QLabel("Analysis Name")
        #self.lblAnalysisNameML = QLabel("Analysis Name")
        #self.lblAnalysisNameBayesian = QLabel("Analysis Name")
        
        self.edtAnalysisNameParsimony = QLineEdit(ANALYSIS_TYPE_PARSIMONY)
        # bootstrap type: normal, ultrafast
        self.parsimony_layout.addWidget(QLabel("Name"),0,0)
        self.parsimony_layout.addWidget(self.edtAnalysisNameParsimony,0,1)

        self.edtAnalysisNameML = QLineEdit(ANALYSIS_TYPE_ML)
        self.cbBootstrapType = QComboBox()
        self.cbBootstrapType.addItem(BOOTSTRAP_TYPE_NORMAL)
        self.cbBootstrapType.addItem(BOOTSTRAP_TYPE_ULTRAFAST)
        self.edtBootstrapCount = QLineEdit("1000")
        row_idx = 0
        self.ml_layout.addWidget(QLabel("Name"),row_idx,1)
        self.ml_layout.addWidget(self.edtAnalysisNameML,row_idx,2)
        row_idx += 1
        self.ml_layout.addWidget(QLabel("Bootstrap Type"),row_idx,1)
        self.ml_layout.addWidget(self.cbBootstrapType,row_idx,2)
        row_idx += 1
        self.ml_layout.addWidget(QLabel("Bootstrap Count"),row_idx,1)
        self.ml_layout.addWidget(self.edtBootstrapCount,row_idx,2)
        #self.tabML.layout().addRow("Bootstrap Type",self.cbBootstrapType)
        #self.tabML.layout().addRow("Bootstrap Count",self.edtBootstrapCount)

        '''
            mcmc_burnin = IntegerField(default=1000)
            mcmc_relburnin = FloatField(default=0.25)
            mcmc_burninfrac = FloatField(default=0.25)
            mcmc_ngen = IntegerField(default=1000000)
            mcmc_nrates = CharField(default='gamma')
            mcmc_printfreq = IntegerField(default=1000)
            mcmc_samplefreq = IntegerField(default=100)
            mcmc_nruns = IntegerField(default=1)
            mcmc_nchains = IntegerField(default=1)
        '''
        self.edtAnalysisNameBayesian = QLineEdit(ANALYSIS_TYPE_BAYESIAN)
        self.edtMCMCBurnin = QLineEdit("1000")
        self.edtMCMCRelBurnin = QCheckBox("Relative Burnin")
        self.edtMCMCBurninFrac = QLineEdit("0.25")
        self.edtMCMCNGen = QLineEdit("1000000")
        self.edtMCMCNst = QLineEdit("6")
        self.cbMCMCNRates = QComboBox()
        self.cbMCMCNRates.addItem("gamma")
        self.cbMCMCNRates.addItem("invgamma")
        self.cbMCMCNRates.addItem("lognormal")
        self.cbMCMCNRates.addItem("normal")
        self.cbMCMCNRates.addItem("poisson")
        self.cbMCMCNRates.addItem("uniform")
        self.cbMCMCNRates.addItem("exponential")
        self.edtPrintFreq = QLineEdit("1000")
        self.edtSampleFreq = QLineEdit("100")
        self.edtNRuns = QLineEdit("1")
        self.edtNChains = QLineEdit("1")

        row_idx = 0
        self.bayesian_layout.addWidget(QLabel("Name"),row_idx,0)
        self.bayesian_layout.addWidget(self.edtAnalysisNameBayesian,row_idx,1)
        row_idx += 1
        self.bayesian_layout.addWidget(QLabel("Burnin"),row_idx,0)
        self.bayesian_layout.addWidget(self.edtMCMCBurnin,row_idx,1)
        row_idx += 1
        self.bayesian_layout.addWidget(QLabel("Relative Burnin"),row_idx,0)
        self.bayesian_layout.addWidget(self.edtMCMCRelBurnin,row_idx,1)
        row_idx += 1
        self.bayesian_layout.addWidget(QLabel("Burnin Fraction"),row_idx,0)
        self.bayesian_layout.addWidget(self.edtMCMCBurninFrac,row_idx,1)
        row_idx += 1
        self.bayesian_layout.addWidget(QLabel("NGen"),row_idx,0)
        self.bayesian_layout.addWidget(self.edtMCMCNGen,row_idx,1)
        row_idx += 1
        self.bayesian_layout.addWidget(QLabel("NSt"),row_idx,0)
        self.bayesian_layout.addWidget(self.edtMCMCNst,row_idx,1)
        row_idx += 1
        self.bayesian_layout.addWidget(QLabel("NRates"),row_idx,0)
        self.bayesian_layout.addWidget(self.cbMCMCNRates,row_idx,1)
        row_idx += 1
        self.bayesian_layout.addWidget(QLabel("Print Freq"),row_idx,0)
        self.bayesian_layout.addWidget(self.edtPrintFreq,row_idx,1)
        row_idx += 1
        self.bayesian_layout.addWidget(QLabel("Sample Freq"),row_idx,0)
        self.bayesian_layout.addWidget(self.edtSampleFreq,row_idx,1)
        row_idx += 1
        self.bayesian_layout.addWidget(QLabel("NRuns"),row_idx,0)
        self.bayesian_layout.addWidget(self.edtNRuns,row_idx,1)
        row_idx += 1
        self.bayesian_layout.addWidget(QLabel("NChains"),row_idx,0)
        self.bayesian_layout.addWidget(self.edtNChains,row_idx,1)

        '''
        self.tabBayesian.layout().addRow("Name",self.edtAnalysisNameBayesian)
        self.tabBayesian.layout().addRow("Burnin",self.edtMCMCBurnin)
        self.tabBayesian.layout().addRow("Relative Burnin",self.edtMCMCRelBurnin)
        self.tabBayesian.layout().addRow("Burnin Fraction",self.edtMCMCBurninFrac)
        self.tabBayesian.layout().addRow("NGen",self.edtMCMCNGen)
        self.tabBayesian.layout().addRow("NSt",self.edtMCMCNst)
        self.tabBayesian.layout().addRow("NRates",self.cbMCMCNRates)
        self.tabBayesian.layout().addRow("Print Freq",self.edtPrintFreq)
        self.tabBayesian.layout().addRow("Sample Freq",self.edtSampleFreq)
        self.tabBayesian.layout().addRow("NRuns",self.edtNRuns)
        self.tabBayesian.layout().addRow("NChains",self.edtNChains)
        '''
        
        self.on_cbxParsimony_clicked()

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btnRun)
        btn_layout.addWidget(self.btnCancel)
        self.main_layout.addRow(btn_layout)

    def select_result_directory(self):
        result_directory = str(QFileDialog.getExistingDirectory(self, "Select a folder", str(self.edtResultDirectory.text())))
        if result_directory:
            self.result_directory = Path(result_directory).resolve()
            # Normalize path for OS-appropriate separators
            self.edtResultDirectory.setText(os.path.normpath(str(self.result_directory)))

    def on_cbxParsimony_clicked(self):
        if self.datamatrix is None:
            return

        # add parsimony tab if not exists
        if self.cbxParsimony.isChecked():
            if self.tabView.indexOf(self.tabParsimony) == -1:
                #self.tabParsimony = QWidget()
                self.tabView.addTab(self.tabParsimony, ANALYSIS_TYPE_PARSIMONY)
            self.tabView.setCurrentWidget(self.tabParsimony)
            analysis_name = self.edtAnalysisNameParsimony.text() #.replace(" ", "_")
            analysis_name_list = [analysis.analysis_name for analysis in self.datamatrix.analyses]
            if analysis_name in analysis_name_list:
                analysis_name = pu.get_unique_name(analysis_name, analysis_name_list)
            self.edtAnalysisNameParsimony.setText(analysis_name)
        else:
            if self.tabView.indexOf(self.tabParsimony) != -1:
                self.tabView.removeTab(self.tabView.indexOf(self.tabParsimony))
        #pass

    def on_cbxML_clicked(self):
        #pass
        if self.cbxML.isChecked():
            if self.tabView.indexOf(self.tabML) == -1:
                #self.tabML = QWidget()
                self.tabView.addTab(self.tabML, ANALYSIS_TYPE_ML)
            self.tabView.setCurrentWidget(self.tabML)
            analysis_name = self.edtAnalysisNameML.text()
            analysis_name_list = [analysis.analysis_name for analysis in self.datamatrix.analyses]
            if analysis_name in analysis_name_list:
                analysis_name = pu.get_unique_name(analysis_name, analysis_name_list)
            self.edtAnalysisNameML.setText(analysis_name)
        else:
            if self.tabView.indexOf(self.tabML) != -1:
                self.tabView.removeTab(self.tabView.indexOf(self.tabML))

    def on_cbxBayesian_clicked(self):
        #pass
        if self.cbxBayesian.isChecked():
            if self.tabView.indexOf(self.tabBayesian) == -1:
                #self.tabBayesian = QWidget()
                self.tabView.addTab(self.tabBayesian, ANALYSIS_TYPE_BAYESIAN)
            self.tabView.setCurrentWidget(self.tabBayesian)
            analysis_name = self.edtAnalysisNameBayesian.text()
            analysis_name_list = [analysis.analysis_name for analysis in self.datamatrix.analyses]
            if analysis_name in analysis_name_list:
                analysis_name = pu.get_unique_name(analysis_name, analysis_name_list)
            self.edtAnalysisNameBayesian.setText(analysis_name)
        else:
            if self.tabView.indexOf(self.tabBayesian) != -1:
                self.tabView.removeTab(self.tabView.indexOf(self.tabBayesian))


    def Run (self):
        analysis_type_list = []

        result_directory_base = self.edtResultDirectory.text()
        if result_directory_base == "":
            # show warning
            QMessageBox.warning(self, "Result Directory", "Please select a result directory.")
            return

        if self.cbxParsimony.isChecked():
            # check if the directory contains space
            # tnt specific. so if package is not tnt, this should not be applied.            
            if result_directory_base.find(" ") != -1:
                QMessageBox.warning(self, "Result Directory", "Result directory should not contain space.")
                return
            analysis_type_list.append(ANALYSIS_TYPE_PARSIMONY)
        if self.cbxML.isChecked():
            analysis_type_list.append(ANALYSIS_TYPE_ML)
        if self.cbxBayesian.isChecked():
            analysis_type_list.append(ANALYSIS_TYPE_BAYESIAN)

        for analysis_type in analysis_type_list:
            analysis = PfAnalysis()
            #analysis.project = self.parent.selected_project
            #if analysis.project is None:
            #    return
            analysis.datamatrix = self.parent.selected_datamatrix
            if analysis.datamatrix is None:
                return
            
            if analysis_type == ANALYSIS_TYPE_PARSIMONY:
                analysis.analysis_name = self.edtAnalysisNameParsimony.text() #.replace(" ", "_")
                # add current time to the name
                directory_name = analysis.datamatrix.datamatrix_name + " " + analysis.analysis_name + " " + datetime.datetime.now().strftime("%H%M%S")
                # Normalize path for OS-appropriate separators
                analysis.result_directory = os.path.normpath(os.path.join( result_directory_base, directory_name.replace(" ","_") )) # TNT does not like space in file name
            elif analysis_type == ANALYSIS_TYPE_ML:
                analysis.analysis_name = self.edtAnalysisNameML.text()
                analysis.ml_bootstrap_type = self.cbBootstrapType.currentText()
                analysis.ml_bootstrap = int(self.edtBootstrapCount.text())
                directory_name = analysis.datamatrix.datamatrix_name + " " + analysis.analysis_name + " " + datetime.datetime.now().strftime("%H%M%S")
                # Normalize path for OS-appropriate separators
                analysis.result_directory = os.path.normpath(os.path.join( result_directory_base, directory_name ))

            elif analysis_type == ANALYSIS_TYPE_BAYESIAN:
                analysis.analysis_name = self.edtAnalysisNameBayesian.text()
                analysis.mcmc_burnin = int(self.edtMCMCBurnin.text())
                analysis.mcmc_relburnin = self.edtMCMCRelBurnin.isChecked()
                analysis.mcmc_burninfrac = float(self.edtMCMCBurninFrac.text())
                analysis.mcmc_ngen = int(self.edtMCMCNGen.text())
                analysis.mcmc_nst = int(self.edtMCMCNst.text())
                analysis.mcmc_nrates = self.cbMCMCNRates.currentText()
                analysis.mcmc_printfreq = int(self.edtPrintFreq.text())
                analysis.mcmc_samplefreq = int(self.edtSampleFreq.text())
                analysis.mcmc_nruns = int(self.edtNRuns.text())
                analysis.mcmc_nchains = int(self.edtNChains.text())
                directory_name = analysis.datamatrix.datamatrix_name + " " + analysis.analysis_name + " " + datetime.datetime.now().strftime("%H%M%S")
                # Normalize path for OS-appropriate separators
                analysis.result_directory = os.path.normpath(os.path.join( result_directory_base, directory_name.replace(" ","_") ))
                #analysis.result_directory = os.path.join( result_directory_base, directory_name )

            analysis.analysis_status = ANALYSIS_STATUS_READY
            analysis.analysis_type = analysis_type
            analysis.taxa_list_json = analysis.datamatrix.taxa_list_json
            analysis.character_list_json = analysis.datamatrix.character_list_json
            analysis.datamatrix_json = analysis.datamatrix.datamatrix_json
            analysis.save()

        self.accept()


    def Cancel(self):
        self.reject()

    def read_settings(self):
        self.remember_geometry = pu.value_to_bool(self.m_app.settings.value("WindowGeometry/RememberGeometry", True))
        if self.remember_geometry is True:
            self.setGeometry(self.m_app.settings.value("WindowGeometry/AnalysisDialog", QRect(100, 100, 600, 400)))
        else:
            self.setGeometry(QRect(100, 100, 600, 400))
            self.move(self.parent.pos()+QPoint(100,100))
        # Normalize path for OS-appropriate separators
        # Use DEFAULT_RESULT_DIRECTORY for short paths to avoid TNT command line length issues
        self.result_directory_base = os.path.normpath(self.m_app.settings.value("ResultPath", pu.DEFAULT_RESULT_DIRECTORY))


    def write_settings(self):
        if self.remember_geometry is True:
            self.m_app.settings.setValue("WindowGeometry/AnalysisDialog", self.geometry())

    def closeEvent(self, event):
        self.write_settings()
        event.accept()

    def set_datamatrix(self, datamatrix):
        self.datamatrix = datamatrix
        self.project = datamatrix.project
        self.edtProjectName.setText(self.project.project_name)
        self.edtProjectDesc.setText(self.project.project_desc)
        self.edtProjectName.setReadOnly(True)
        self.edtProjectDesc.setReadOnly(True)
        self.edtDatamatrixName.setText(self.datamatrix.datamatrix_name)

class DatamatrixDialog(QDialog):
    # DatamatrixDialog shows new project dialog.
    def __init__(self,parent, logger=None):
        super().__init__()
        self.logger = logger or PfLogger.get_logger(__name__)
        self.setWindowTitle("PhyloForester - Datamatrix Information")
        self.parent = parent

        self.remember_geometry = True
        self.m_app = QApplication.instance()
        self.read_settings()

        self.edtProjectName = QLineEdit()
        self.edtDatamatrixName = QLineEdit()
        self.edtDatamatrixDesc = QLineEdit()
        self.rbMorphology = QRadioButton(DATATYPE_MORPHOLOGY)
        self.rbMorphology.setChecked(True)
        self.rbDNA = QRadioButton(DATATYPE_DNA)
        self.rbRNA = QRadioButton(DATATYPE_RNA)
        self.rbCombined = QRadioButton(DATATYPE_COMBINED)
        datatype_layout = QHBoxLayout()
        datatype_layout.addWidget(self.rbMorphology)
        datatype_layout.addWidget(self.rbDNA)
        datatype_layout.addWidget(self.rbRNA)
        datatype_layout.addWidget(self.rbCombined)

        self.lstCharacters = QListWidget()
        self.lstCharacters.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lstCharacters.setSortingEnabled(False)
        self.lstCharacters.setAlternatingRowColors(True)
        self.lstCharacters.itemSelectionChanged.connect(self.on_lstCharacters_itemSelectionChanged)

        self.edtCharacter = QLineEdit()
        self.edtCharacter.setPlaceholderText("Enter character name")
        self.btnAddCharacter = QPushButton()
        self.btnAddCharacter.setText("Add")
        self.btnAddCharacter.clicked.connect(self.on_btnAddCharacter_clicked)
        self.btnSaveCharacter = QPushButton()
        self.btnSaveCharacter.setText("Save")
        self.btnSaveCharacter.clicked.connect(self.on_btnSaveCharacter_clicked)
        self.btnRemoveCharacter = QPushButton()
        self.btnRemoveCharacter.setText("Remove")
        self.btnRemoveCharacter.clicked.connect(self.on_btnRemoveCharacter_clicked)
        self.btnMoveUpCharacter = QPushButton()
        self.btnMoveUpCharacter.setText("↑")
        self.btnMoveUpCharacter.clicked.connect(self.on_btnMoveUpCharacter_clicked)
        self.btnMoveDownCharacter = QPushButton()
        self.btnMoveDownCharacter.setText("↓")
        self.btnMoveDownCharacter.clicked.connect(self.on_btnMoveDownCharacter_clicked)

        # Character input: lineedit on top, buttons below
        self.character_button_layout = QHBoxLayout()
        self.character_button_layout.addWidget(self.btnAddCharacter)
        self.character_button_layout.addWidget(self.btnSaveCharacter)
        self.character_button_layout.addWidget(self.btnRemoveCharacter)
        self.character_button_layout.addWidget(self.btnMoveUpCharacter)
        self.character_button_layout.addWidget(self.btnMoveDownCharacter)

        self.character_input_layout = QVBoxLayout()
        self.character_input_layout.addWidget(self.edtCharacter)
        self.character_input_layout.addLayout(self.character_button_layout)
        self.character_input_widget = QWidget()
        self.character_input_widget.setLayout(self.character_input_layout)

        self.characters_layout_widget = QWidget()
        self.characters_layout_widget.setLayout(QVBoxLayout())
        self.characters_layout_widget.layout().addWidget(self.lstCharacters)
        self.characters_layout_widget.layout().addWidget(self.character_input_widget)
        self.characters_layout_widget.layout().setContentsMargins(0,0,0,0)
        self.characters_layout_widget.layout().setSpacing(0)
        self.characters_layout_widget.layout().setAlignment(Qt.AlignTop)
        self.characters_layout_widget.layout().setStretch(0,1)
        self.characters_layout_widget.layout().setStretch(1,0)

        self.lstTaxa = QListWidget()
        # set single selection mode

        self.lstTaxa.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lstTaxa.setSortingEnabled(False)
        self.lstTaxa.setAlternatingRowColors(True)
        
        # selection changed event to update
        self.lstTaxa.itemSelectionChanged.connect(self.on_lstTaxa_itemSelectionChanged)

        self.edtTaxon = QLineEdit()
        self.edtTaxon.setPlaceholderText("Enter taxon name")
        self.btnAddTaxon = QPushButton()
        self.btnAddTaxon.setText("Add")
        self.btnAddTaxon.clicked.connect(self.on_btnAddTaxon_clicked)
        self.btnSaveTaxon = QPushButton()
        self.btnSaveTaxon.setText("Save")
        self.btnSaveTaxon.clicked.connect(self.on_btnSaveTaxon_clicked)
        self.btnRemoveTaxon = QPushButton()
        self.btnRemoveTaxon.setText("Remove")
        self.btnRemoveTaxon.clicked.connect(self.on_btnRemoveTaxon_clicked)
        self.btnMoveUpTaxon = QPushButton()
        self.btnMoveUpTaxon.setText("↑")
        self.btnMoveUpTaxon.clicked.connect(self.on_btnMoveUpTaxon_clicked)
        self.btnMoveDownTaxon = QPushButton()
        self.btnMoveDownTaxon.setText("↓")
        self.btnMoveDownTaxon.clicked.connect(self.on_btnMoveDownTaxon_clicked)

        # Taxon input: lineedit on top, buttons below
        self.taxon_button_layout = QHBoxLayout()
        self.taxon_button_layout.addWidget(self.btnAddTaxon)
        self.taxon_button_layout.addWidget(self.btnSaveTaxon)
        self.taxon_button_layout.addWidget(self.btnRemoveTaxon)
        self.taxon_button_layout.addWidget(self.btnMoveUpTaxon)
        self.taxon_button_layout.addWidget(self.btnMoveDownTaxon)

        self.taxon_input_layout = QVBoxLayout()
        self.taxon_input_layout.addWidget(self.edtTaxon)
        self.taxon_input_layout.addLayout(self.taxon_button_layout)
        self.taxon_input_widget = QWidget()
        self.taxon_input_widget.setLayout(self.taxon_input_layout)

        self.taxa_layout_widget = QWidget()
        self.taxa_layout_widget.setLayout(QVBoxLayout())
        self.taxa_layout_widget.layout().addWidget(self.lstTaxa)
        self.taxa_layout_widget.layout().addWidget(self.taxon_input_widget)
        self.taxa_layout_widget.layout().setContentsMargins(0,0,0,0)
        self.taxa_layout_widget.layout().setSpacing(0)
        self.taxa_layout_widget.layout().setAlignment(Qt.AlignTop)
        self.taxa_layout_widget.layout().setStretch(0,1)
        self.taxa_layout_widget.layout().setStretch(1,0)

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        row_idx = 0
        self.main_layout.addWidget(QLabel("Project Name"),row_idx,0)
        self.main_layout.addWidget(self.edtProjectName,row_idx,1)
        row_idx += 1
        self.main_layout.addWidget(QLabel("Datamatrix Name"),row_idx,0)
        self.main_layout.addWidget(self.edtDatamatrixName,row_idx,1)
        row_idx += 1
        self.main_layout.addWidget(QLabel("Description"),row_idx,0)
        self.main_layout.addWidget(self.edtDatamatrixDesc,row_idx,1)
        row_idx += 1
        self.main_layout.addWidget(QLabel("Data Type"),row_idx,0)
        self.main_layout.addLayout(datatype_layout,row_idx,1)
        row_idx += 1
        self.main_layout.addWidget(QLabel("Characters"),row_idx,0)
        self.main_layout.addWidget(self.characters_layout_widget,row_idx,1)
        row_idx += 1
        self.main_layout.addWidget(QLabel("Taxa"),row_idx,0)
        self.main_layout.addWidget(self.taxa_layout_widget,row_idx,1)
        row_idx += 1
        '''
        self.main_layout.addRow("Project Name", self.edtProjectName)
        self.main_layout.addRow("Datamatrix Name", self.edtDatamatrixName)
        self.main_layout.addRow("Description", self.edtDatamatrixDesc)
        self.main_layout.addRow("Data Type", datatype_layout)
        self.main_layout.addRow("Taxa", self.taxa_layout_widget)
        self.main_layout.addRow("Characters", self.characters_layout_widget)
        '''
        self.btnOkay = QPushButton()
        self.btnOkay.setText("Save")
        self.btnOkay.clicked.connect(self.Okay)

        self.btnDelete = QPushButton()
        self.btnDelete.setText("Delete")
        self.btnDelete.clicked.connect(self.Delete)

        self.btnCancel = QPushButton()
        self.btnCancel.setText("Cancel")
        self.btnCancel.clicked.connect(self.Cancel)

        btn_widget = QWidget()

        btn_layout = QHBoxLayout()
        btn_widget.setLayout(btn_layout)
        btn_layout.addWidget(self.btnOkay)
        btn_layout.addWidget(self.btnDelete)
        btn_layout.addWidget(self.btnCancel)
        self.main_layout.addWidget(btn_widget,row_idx,1,1,2)

    def on_lstCharacters_itemSelectionChanged(self):
        items = self.lstCharacters.selectedItems()
        if len(items) == 0:
            return
        item = items[0]
        self.edtCharacter.setText(item.text())

    def on_btnAddCharacter_clicked(self):
        character_name = self.edtCharacter.text()
        if character_name == "":
            return
        self.edtCharacter.setText("")

        # Create new item with metadata marking it as new
        item = QListWidgetItem(character_name)
        item.setData(Qt.UserRole, {
            'original_name': None,  # No original name (new item)
            'original_index': None,  # No original index
            'is_new': True
        })
        self.lstCharacters.addItem(item)

    def on_btnSaveCharacter_clicked(self):
        character_name = self.edtCharacter.text()
        if character_name == "":
            return
        items = self.lstCharacters.selectedItems()
        if len(items) == 0:
            return
        item = items[0]

        # Update text only, preserve metadata
        item.setText(character_name)
        # Metadata (original_name, original_index, is_new) is preserved automatically

    def on_btnRemoveCharacter_clicked(self):
        items = self.lstCharacters.selectedItems()
        for item in items:
            self.lstCharacters.takeItem(self.lstCharacters.row(item))

    def on_btnMoveUpCharacter_clicked(self):
        """Move selected character up in the list"""
        items = self.lstCharacters.selectedItems()
        if len(items) == 0:
            return
        item = items[0]
        current_row = self.lstCharacters.row(item)
        if current_row == 0:
            return  # Already at the top

        # Take item and re-insert at previous position
        taken_item = self.lstCharacters.takeItem(current_row)
        self.lstCharacters.insertItem(current_row - 1, taken_item)
        self.lstCharacters.setCurrentItem(taken_item)

    def on_btnMoveDownCharacter_clicked(self):
        """Move selected character down in the list"""
        items = self.lstCharacters.selectedItems()
        if len(items) == 0:
            return
        item = items[0]
        current_row = self.lstCharacters.row(item)
        if current_row == self.lstCharacters.count() - 1:
            return  # Already at the bottom

        # Take item and re-insert at next position
        taken_item = self.lstCharacters.takeItem(current_row)
        self.lstCharacters.insertItem(current_row + 1, taken_item)
        self.lstCharacters.setCurrentItem(taken_item)

    def on_lstTaxa_itemSelectionChanged(self):
        items = self.lstTaxa.selectedItems()
        if len(items) == 0:
            return
        item = items[0]
        self.edtTaxon.setText(item.text())

    def on_btnAddTaxon_clicked(self):
        taxon_name = self.edtTaxon.text()
        if taxon_name == "":
            return
        self.edtTaxon.setText("")

        # Create new item with metadata marking it as new
        item = QListWidgetItem(taxon_name)
        item.setData(Qt.UserRole, {
            'original_name': None,  # No original name (new item)
            'original_index': None,  # No original index
            'is_new': True
        })
        self.lstTaxa.addItem(item)

    def on_btnSaveTaxon_clicked(self):
        taxon_name = self.edtTaxon.text()
        if taxon_name == "":
            return
        items = self.lstTaxa.selectedItems()
        if len(items) == 0:
            return
        item = items[0]

        # Update text only, preserve metadata
        item.setText(taxon_name)
        # Metadata (original_name, original_index, is_new) is preserved automatically

    def on_btnRemoveTaxon_clicked(self):
        items = self.lstTaxa.selectedItems()
        for item in items:
            self.lstTaxa.takeItem(self.lstTaxa.row(item))

    def on_btnMoveUpTaxon_clicked(self):
        """Move selected taxon up in the list"""
        items = self.lstTaxa.selectedItems()
        if len(items) == 0:
            return
        item = items[0]
        current_row = self.lstTaxa.row(item)
        if current_row == 0:
            return  # Already at the top

        # Take item and re-insert at previous position
        taken_item = self.lstTaxa.takeItem(current_row)
        self.lstTaxa.insertItem(current_row - 1, taken_item)
        self.lstTaxa.setCurrentItem(taken_item)

    def on_btnMoveDownTaxon_clicked(self):
        """Move selected taxon down in the list"""
        items = self.lstTaxa.selectedItems()
        if len(items) == 0:
            return
        item = items[0]
        current_row = self.lstTaxa.row(item)
        if current_row == self.lstTaxa.count() - 1:
            return  # Already at the bottom

        # Take item and re-insert at next position
        taken_item = self.lstTaxa.takeItem(current_row)
        self.lstTaxa.insertItem(current_row + 1, taken_item)
        self.lstTaxa.setCurrentItem(taken_item)

    def read_settings(self):
        self.remember_geometry = pu.value_to_bool(self.m_app.settings.value("WindowGeometry/RememberGeometry", True))
        if self.remember_geometry is True:
            self.setGeometry(self.m_app.settings.value("WindowGeometry/DatamatrixDialog", QRect(100, 100, 600, 400)))
        else:
            self.setGeometry(QRect(100, 100, 600, 400))
            self.move(self.parent.pos()+QPoint(100,100))

    def write_settings(self):
        if self.remember_geometry is True:
            self.m_app.settings.setValue("WindowGeometry/DatamatrixDialog", self.geometry())

    def closeEvent(self, event):
        self.write_settings()
        event.accept()

    def set_datamatrix(self, datamatrix):
        if datamatrix is None:
            self.datamatrix = None
            return

        self.datamatrix = datamatrix

        self.edtProjectName.setText(datamatrix.project.project_name)

        self.edtDatamatrixName.setText(datamatrix.datamatrix_name)
        self.edtDatamatrixDesc.setText(datamatrix.datamatrix_desc)
        if datamatrix.datatype == DATATYPE_MORPHOLOGY:
            self.rbMorphology.setChecked(True)
        elif datamatrix.datatype == DATATYPE_DNA:
            self.rbDNA.setChecked(True)
        elif datamatrix.datatype == DATATYPE_RNA:
            self.rbRNA.setChecked(True)
        elif datamatrix.datatype == DATATYPE_COMBINED:
            self.rbCombined.setChecked(True)
        self.lstCharacters.clear()
        character_list = datamatrix.get_character_list()
        if len( character_list ) != 0:
            for idx, character in enumerate(character_list):
                item = QListWidgetItem(character)
                # Store metadata: original name, index, and whether it's new
                item.setData(Qt.UserRole, {
                    'original_name': character,
                    'original_index': idx,
                    'is_new': False
                })
                self.lstCharacters.addItem(item)
        taxa_list = datamatrix.get_taxa_list()
        if len( taxa_list ) != 0:
            for idx, taxon in enumerate(taxa_list):
                item = QListWidgetItem(taxon)
                # Store metadata: original name, index, and whether it's new
                item.setData(Qt.UserRole, {
                    'original_name': taxon,
                    'original_index': idx,
                    'is_new': False
                })
                self.lstTaxa.addItem(item)
    
    def Okay(self):
        if self.datamatrix is None:
            self.datamatrix = PfDatamatrix()

        # Update basic information
        self.datamatrix.datamatrix_name = self.edtDatamatrixName.text()
        self.datamatrix.datamatrix_desc = self.edtDatamatrixDesc.text()
        if self.rbMorphology.isChecked():
            self.datamatrix.datatype = DATATYPE_MORPHOLOGY
        elif self.rbDNA.isChecked():
            self.datamatrix.datatype = DATATYPE_DNA
        elif self.rbRNA.isChecked():
            self.datamatrix.datatype = DATATYPE_RNA
        elif self.rbCombined.isChecked():
            self.datamatrix.datatype = DATATYPE_COMBINED

        # Load old datamatrix
        old_datamatrix = self.datamatrix.datamatrix_as_list()

        # Collect new taxa with metadata
        new_taxa_list = []
        taxa_metadata = []
        for i in range(self.lstTaxa.count()):
            item = self.lstTaxa.item(i)
            new_taxa_list.append(item.text())
            metadata = item.data(Qt.UserRole)
            if metadata is None:
                # No metadata (shouldn't happen, but handle gracefully)
                metadata = {'original_name': None, 'original_index': None, 'is_new': True}
            taxa_metadata.append(metadata)

        # Collect new characters with metadata
        new_char_list = []
        char_metadata = []
        for i in range(self.lstCharacters.count()):
            item = self.lstCharacters.item(i)
            new_char_list.append(item.text())
            metadata = item.data(Qt.UserRole)
            if metadata is None:
                # No metadata (shouldn't happen, but handle gracefully)
                metadata = {'original_name': None, 'original_index': None, 'is_new': True}
            char_metadata.append(metadata)

        # Create new datamatrix with proper dimensions
        new_datamatrix = []
        for new_row_idx in range(len(new_taxa_list)):
            row = []
            for new_col_idx in range(len(new_char_list)):
                # Default value for new cells
                cell_value = "?"

                # Check if this taxon and character are both from old datamatrix
                taxon_meta = taxa_metadata[new_row_idx]
                char_meta = char_metadata[new_col_idx]

                if not taxon_meta['is_new'] and not char_meta['is_new']:
                    # Both are existing items, try to copy old value
                    old_row_idx = taxon_meta['original_index']
                    old_col_idx = char_meta['original_index']

                    if old_row_idx is not None and old_col_idx is not None:
                        if old_row_idx < len(old_datamatrix):
                            if old_col_idx < len(old_datamatrix[old_row_idx]):
                                cell_value = old_datamatrix[old_row_idx][old_col_idx]

                row.append(cell_value)
            new_datamatrix.append(row)

        # Update datamatrix
        self.datamatrix.taxa_list_json = json.dumps(new_taxa_list)
        self.datamatrix.character_list_json = json.dumps(new_char_list)
        self.datamatrix.n_taxa = len(new_taxa_list)
        self.datamatrix.n_chars = len(new_char_list)
        self.datamatrix.datamatrix_json = json.dumps(new_datamatrix)

        # Save
        self.datamatrix.save()
        self.accept()

    def Delete(self):
        ret = QMessageBox.question(self, "", "Are you sure to delete this matamatrix?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        #print("ret:", ret)
        if ret == QMessageBox.Yes:
            self.datamatrix.delete_instance()
            self.parent.selected_datamatrix = None
        self.accept()

    def Cancel(self):
        self.reject()


class ProjectDialog(QDialog):
    # ProjectDialog shows new project dialog.
    def __init__(self,parent, logger=None):
        super().__init__()
        self.logger = logger or PfLogger.get_logger(__name__)
        self.setWindowTitle("PhyloForester - Project Information")
        self.parent = parent
        #print(self.parent.pos())
        #self.setGeometry(QRect(100, 100, 600, 400))
        self.remember_geometry = True
        self.m_app = QApplication.instance()
        self.read_settings()
        #self.move(self.parent.pos()+QPoint(100,100))

        self.edtProjectName = QLineEdit()
        self.edtProjectDesc = QLineEdit()

        self.rbMorphology = QRadioButton("Morphology")
        self.rbMorphology.setChecked(True)
        self.rbDNA = QRadioButton("DNA")
        self.rbRNA = QRadioButton("RNA")
        self.rbCombined = QRadioButton("Combined")
        datatype_layout = QHBoxLayout()
        datatype_layout.addWidget(self.rbMorphology)
        datatype_layout.addWidget(self.rbDNA)
        datatype_layout.addWidget(self.rbRNA)
        datatype_layout.addWidget(self.rbCombined)

        '''
        # add listbox for taxa
        self.lstTaxa = QListWidget()
        self.lstTaxa.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.lstTaxa.setSortingEnabled(False)
        self.lstTaxa.setAlternatingRowColors(True)

        # add textbox for taxa
        self.edtTaxa = QLineEdit()
        self.edtTaxa.setPlaceholderText("Enter taxa name")
        self.btnAddTaxa = QPushButton()
        self.btnAddTaxa.setText("Add")
        self.btnAddTaxa.clicked.connect(self.on_btnAddTaxa_clicked)
        self.btnRemoveTaxa = QPushButton()
        self.btnRemoveTaxa.setText("Remove")
        self.btnRemoveTaxa.clicked.connect(self.on_btnRemoveTaxa_clicked)
        self.taxa_layout = QHBoxLayout()
        self.taxa_layout.addWidget(self.edtTaxa)
        self.taxa_layout.addWidget(self.btnAddTaxa)
        self.taxa_layout.addWidget(self.btnRemoveTaxa)
        self.taxa_widget = QWidget()
        self.taxa_widget.setLayout(self.taxa_layout)
        self.taxa_layout_widget = QWidget()
        self.taxa_layout_widget.setLayout(QVBoxLayout())
        self.taxa_layout_widget.layout().addWidget(self.lstTaxa)
        self.taxa_layout_widget.layout().addWidget(self.taxa_widget)
        self.taxa_layout_widget.layout().setContentsMargins(0,0,0,0)
        self.taxa_layout_widget.layout().setSpacing(0)
        self.taxa_layout_widget.layout().setAlignment(Qt.AlignTop)
        self.taxa_layout_widget.layout().setStretch(0,1)
        self.taxa_layout_widget.layout().setStretch(1,0)
        '''

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(QLabel("Project Name"),0,0)
        self.main_layout.addWidget(self.edtProjectName,0,1)
        self.main_layout.addWidget(QLabel("Description"),1,0)
        self.main_layout.addWidget(self.edtProjectDesc,1,1)

        #self.main_layout.addRow("Project Name", self.edtProjectName)
        #self.main_layout.addRow("Description", self.edtProjectDesc)
        #self.main_layout.addRow("Data Type", datatype_layout)
        #self.main_layout.addRow("Taxa", self.taxa_layout_widget)

        self.btnOkay = QPushButton()
        self.btnOkay.setText("Save")
        self.btnOkay.clicked.connect(self.Okay)

        self.btnDelete = QPushButton()
        self.btnDelete.setText("Delete")
        self.btnDelete.clicked.connect(self.Delete)

        self.btnCancel = QPushButton()
        self.btnCancel.setText("Cancel")
        self.btnCancel.clicked.connect(self.Cancel)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btnOkay)
        btn_layout.addWidget(self.btnDelete)
        btn_layout.addWidget(self.btnCancel)
        # merge two cells for buttons
        self.main_layout.addLayout(btn_layout,2,0,1,2)

        

        self.project = None
    
    def on_btnAddTaxa_clicked(self):
        taxa_name = self.edtTaxa.text()
        if taxa_name == "":
            return
        self.edtTaxa.setText("")
        self.lstTaxa.addItem(taxa_name)
    
    def on_btnRemoveTaxa_clicked(self):
        items = self.lstTaxa.selectedItems()
        for item in items:
            self.lstTaxa.takeItem(self.lstTaxa.row(item))


    def read_settings(self):
        self.remember_geometry = pu.value_to_bool(self.m_app.settings.value("WindowGeometry/RememberGeometry", True))
        if self.remember_geometry is True:
            self.setGeometry(self.m_app.settings.value("WindowGeometry/ProjectDialog", QRect(100, 100, 600, 400)))
        else:
            self.setGeometry(QRect(100, 100, 600, 400))
            self.move(self.parent.pos()+QPoint(100,100))


    def write_settings(self):
        if self.remember_geometry is True:
            self.m_app.settings.setValue("WindowGeometry/ProjectDialog", self.geometry())

    def closeEvent(self, event):
        self.write_settings()
        event.accept()

    def read_project(self, project_id):
        try:
            project = PfProject.get(project.id == project_id)
        except:
            project = None
        self.project = project

    def set_project(self, project):
        if project is None:
            self.project = None
            self.cbxParent.setCurrentIndex(-1)
            return

        self.project = project

        self.edtProjectName.setText(project.project_name)
        self.edtProjectDesc.setText(project.project_desc)
        #if project.datatype == "Morphology":
        #    self.rbMorphology.setChecked(True)
        #elif project.datatype == "DNA":
        #    self.rbDNA.setChecked(True)
        #elif project.datatype == "RNA":
        #    self.rbRNA.setChecked(True)
        #elif project.datatype == "Combined":
        #    self.rbCombined.setChecked(True)
        #self.lstTaxa.clear()
        #if project.taxa_str is not None:
        #    taxa_list = project.taxa_str.split(",")
        #    for taxa in taxa_list:
        #        self.lstTaxa.addItem(taxa)
    
    def Okay(self):
        if self.project is None:
            self.project = PfProject()
        self.project.project_name = self.edtProjectName.text()
        self.project.project_desc = self.edtProjectDesc.text()
        if self.rbMorphology.isChecked():
            self.project.datatype = "Morphology"
        elif self.rbDNA.isChecked():
            self.project.datatype = "DNA"
        elif self.rbRNA.isChecked():
            self.project.datatype = "RNA"
        elif self.rbCombined.isChecked():
            self.project.datatype = "Combined"
        #self.project.taxa_str = ""
        #for i in range(self.lstTaxa.count()):
        #    self.project.taxa_str += self.lstTaxa.item(i).text()
        #    if i < self.lstTaxa.count()-1:
        #        self.project.taxa_str += ","

        self.project.save()
        self.accept()

    def Delete(self):
        ret = QMessageBox.question(self, "", "Are you sure to delete this project?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        #print("ret:", ret)
        if ret == QMessageBox.Yes:
            self.project.delete_instance()
            self.parent.selected_project = None
        self.accept()

    def Cancel(self):
        self.reject()

class PreferencesDialog(QDialog):
    '''
    PreferencesDialog shows preferences.

    Args:
        None

    Attributes:
        well..
    '''
    def __init__(self,parent, logger=None):
        super().__init__()
        self.logger = logger or PfLogger.get_logger(__name__)
        self.parent = parent
        self.m_app = QApplication.instance()

        self.m_app.remember_geometry = True
        self.toolbar_icon_small = False
        self.toolbar_icon_medium = False
        self.toolbar_icon_large = False

        self.read_settings()
        self.setWindowTitle("Preferences")
        #self.lbl_main_view.setMinimumSize(400, 300)
        #print("landmark_pref:", self.landmark_pref)
        #print("wireframe_pref:", self.wireframe_pref)

        self.rbRememberGeometryYes = QRadioButton("Yes")
        self.rbRememberGeometryYes.setChecked(self.m_app.remember_geometry)
        self.rbRememberGeometryYes.clicked.connect(self.on_rbRememberGeometryYes_clicked)
        self.rbRememberGeometryNo = QRadioButton("No")
        self.rbRememberGeometryNo.setChecked(not self.m_app.remember_geometry)
        self.rbRememberGeometryNo.clicked.connect(self.on_rbRememberGeometryNo_clicked)

        self.gbRememberGeomegry = QGroupBox()
        self.gbRememberGeomegry.setLayout(QHBoxLayout())
        self.gbRememberGeomegry.layout().addWidget(self.rbRememberGeometryYes)
        self.gbRememberGeomegry.layout().addWidget(self.rbRememberGeometryNo)

        self.toolbar_icon_large = True if self.m_app.toolbar_icon_size.lower() == "large" else False
        self.rbToolbarIconLarge = QRadioButton("Large")
        self.rbToolbarIconLarge.setChecked(self.toolbar_icon_large)
        self.rbToolbarIconLarge.clicked.connect(self.on_rbToolbarIconLarge_clicked)
        self.rbToolbarIconSmall = QRadioButton("Small")
        self.rbToolbarIconSmall.setChecked(self.toolbar_icon_small)
        self.rbToolbarIconSmall.clicked.connect(self.on_rbToolbarIconSmall_clicked)
        self.rbToolbarIconMedium = QRadioButton("Medium")
        self.rbToolbarIconMedium.setChecked(self.toolbar_icon_medium)
        self.rbToolbarIconMedium.clicked.connect(self.on_rbToolbarIconMedium_clicked)

        self.gbToolbarIconSize = QGroupBox()
        self.gbToolbarIconSize.setLayout(QHBoxLayout())
        self.gbToolbarIconSize.layout().addWidget(self.rbToolbarIconSmall)
        self.gbToolbarIconSize.layout().addWidget(self.rbToolbarIconMedium)
        self.gbToolbarIconSize.layout().addWidget(self.rbToolbarIconLarge)


        self.edtTNTPath = QLineEdit()
        self.edtTNTPath.setText(str(self.m_app.tnt_path))

        self.btnTNTPath = QPushButton("Select Path")
        self.gbTNTPath = QGroupBox("TNT")
        self.gbTNTPath.setLayout(QHBoxLayout())
        self.gbTNTPath.layout().addWidget(self.edtTNTPath)
        self.gbTNTPath.layout().addWidget(self.btnTNTPath)
        self.btnTNTPath.clicked.connect(self.select_tnt_path)

        self.edtIQTreePath = QLineEdit()
        self.edtIQTreePath.setText(str(self.m_app.iqtree_path))
        self.btnIQTreePath = QPushButton("Select Path")
        self.gbIQTreePath = QGroupBox("IQTree")
        self.gbIQTreePath.setLayout(QHBoxLayout())
        self.gbIQTreePath.layout().addWidget(self.edtIQTreePath)
        self.gbIQTreePath.layout().addWidget(self.btnIQTreePath)
        self.btnIQTreePath.clicked.connect(self.select_iqtree_path)

        self.edtMrBayesPath = QLineEdit()
        self.edtMrBayesPath.setText(str(self.m_app.mrbayes_path))
        self.btnMrBayesPath = QPushButton("Select Path")
        self.gbMrBayesPath = QGroupBox("Mr.Bayes")
        self.gbMrBayesPath.setLayout(QHBoxLayout())
        self.gbMrBayesPath.layout().addWidget(self.edtMrBayesPath)
        self.gbMrBayesPath.layout().addWidget(self.btnMrBayesPath)
        self.btnMrBayesPath.clicked.connect(self.select_mrbayes_path)

        self.gbSoftwarePaths = QGroupBox()
        self.gbSoftwarePaths.setLayout(QVBoxLayout())
        self.gbSoftwarePaths.layout().addWidget(self.gbTNTPath)
        self.gbSoftwarePaths.layout().addWidget(self.gbIQTreePath)
        self.gbSoftwarePaths.layout().addWidget(self.gbMrBayesPath)

        self.edtResultPath = QLineEdit()
        self.edtResultPath.setText(str(self.m_app.result_path))
        self.btnResultPath = QPushButton("Select Path")
        self.gbResultPath = QGroupBox("")
        self.gbResultPath.setLayout(QHBoxLayout())
        self.gbResultPath.layout().addWidget(self.edtResultPath)
        self.gbResultPath.layout().addWidget(self.btnResultPath)
        self.btnResultPath.clicked.connect(self.select_result_path)

        self.lang_layout = QHBoxLayout()
        self.comboLang = QComboBox()
        self.comboLang.addItem(self.tr("English"))
        #self.comboLang.addItem(self.tr("Korean"))
        self.comboLang.currentIndexChanged.connect(self.comboLangIndexChanged)
        self.lang_layout.addWidget(self.comboLang)
        self.lang_widget = QWidget()
        self.lang_widget.setLayout(self.lang_layout)

        self.btnOkay = QPushButton()
        self.btnOkay.setText("Close")
        self.btnOkay.clicked.connect(self.Okay)

        self.btnCancel = QPushButton()
        self.btnCancel.setText("Cancel")
        self.btnCancel.clicked.connect(self.Cancel)

        self.main_layout = QFormLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addRow("Remember Geometry", self.gbRememberGeomegry)
        self.main_layout.addRow("Toolbar Icon Size", self.gbToolbarIconSize)
        self.main_layout.addRow("Language", self.lang_widget)
        self.main_layout.addRow("Result Path", self.gbResultPath)
        self.main_layout.addRow("Softwares", self.gbSoftwarePaths)
        self.main_layout.addRow("", self.btnOkay)

        self.read_settings()

    def select_result_path(self):
        result_path = str(QFileDialog.getExistingDirectory(self, "Select a folder", str(self.m_app.result_path)))
        if result_path:
            self.edtResultPath.setText(result_path)
            self.m_app.result_path = Path(result_path).resolve()

    def select_tnt_path(self):
        tnt_path = str(QFileDialog.getOpenFileName(self, "Select TNT", str(self.m_app.tnt_path))[0])
        if tnt_path:
            self.edtTNTPath.setText(tnt_path)
            self.m_app.tnt_path = Path(tnt_path).resolve()

    def select_iqtree_path(self):
        iqtree_path = str(QFileDialog.getOpenFileName(self, "Select IQTree", str(self.m_app.iqtree_path))[0])
        if iqtree_path:
            self.edtIQTreePath.setText(iqtree_path)
            self.m_app.iqtree_path = Path(iqtree_path).resolve()

    def select_mrbayes_path(self):
        mrbayes_path = str(QFileDialog.getOpenFileName(self, "Select Mr.Bayes", str(self.m_app.mrbayes_path))[0])
        if mrbayes_path:
            self.edtMrBayesPath.setText(mrbayes_path)
            self.m_app.mrbayes_path = Path(mrbayes_path).resolve()

    def comboLangIndexChanged(self, index):
        if index == 0:
            self.m_app.language = "en"
        elif index == 1:
            self.m_app.language = "ko"

    def read_settings(self):
        self.m_app.remember_geometry = pu.value_to_bool(self.m_app.settings.value("WindowGeometry/RememberGeometry", True))
        self.m_app.toolbar_icon_size = self.m_app.settings.value("ToolbarIconSize", "Medium")
        # Normalize paths when reading from settings for OS-appropriate separators
        # Software paths (TNT, IQTree, MrBayes) default to empty string (user must configure)
        tnt_value = self.m_app.settings.value("SoftwarePath/TNT", "")
        self.m_app.tnt_path = os.path.normpath(tnt_value) if tnt_value else ""
        iqtree_value = self.m_app.settings.value("SoftwarePath/IQTree", "")
        self.m_app.iqtree_path = os.path.normpath(iqtree_value) if iqtree_value else ""
        mrbayes_value = self.m_app.settings.value("SoftwarePath/MrBayes", "")
        self.m_app.mrbayes_path = os.path.normpath(mrbayes_value) if mrbayes_value else ""
        result_value = self.m_app.settings.value("ResultPath", "")
        # Use DEFAULT_RESULT_DIRECTORY if ResultPath is not set in settings
        self.m_app.result_path = os.path.normpath(result_value) if result_value else pu.DEFAULT_RESULT_DIRECTORY
        self.m_app.language = self.m_app.settings.value("Language", "en")

        #print("toolbar_icon_size:", self.m_app.toolbar_icon_size)
        if self.m_app.toolbar_icon_size.lower() == "small":
            self.toolbar_icon_small = True
            self.toolbar_icon_large = False
            self.toolbar_icon_medium = False
        elif self.m_app.toolbar_icon_size.lower() == "medium":
            self.toolbar_icon_small = False
            self.toolbar_icon_medium = True
            self.toolbar_icon_large = False
        elif self.m_app.toolbar_icon_size.lower() == "large":
            self.toolbar_icon_small = False
            self.toolbar_icon_medium = False
            self.toolbar_icon_large = True

        if self.m_app.remember_geometry is True:
            self.setGeometry(self.m_app.settings.value("WindowGeometry/PreferencesDialog", QRect(100, 100, 600, 400)))
        else:
            self.setGeometry(QRect(100, 100, 600, 400))
            self.move(self.parent.pos()+QPoint(100,100))

    def write_settings(self):
        self.m_app.settings.setValue("ToolbarIconSize", self.m_app.toolbar_icon_size)
        self.m_app.settings.setValue("WindowGeometry/RememberGeometry", self.m_app.remember_geometry)
        # Normalize paths for OS-appropriate separators before saving
        # Software paths save as-is if empty (no normalization of empty string)
        self.m_app.settings.setValue("SoftwarePath/TNT", os.path.normpath(self.m_app.tnt_path) if self.m_app.tnt_path else "")
        self.m_app.settings.setValue("SoftwarePath/IQTree", os.path.normpath(self.m_app.iqtree_path) if self.m_app.iqtree_path else "")
        self.m_app.settings.setValue("SoftwarePath/MrBayes", os.path.normpath(self.m_app.mrbayes_path) if self.m_app.mrbayes_path else "")
        self.m_app.settings.setValue("ResultPath", os.path.normpath(self.m_app.result_path) if self.m_app.result_path else "")
        self.m_app.settings.setValue("Language", self.m_app.language)

        if self.m_app.remember_geometry is True:
            self.m_app.settings.setValue("WindowGeometry/PreferencesDialog", self.geometry())

    def closeEvent(self, event):
        self.write_settings()
        self.parent.update_settings()
        event.accept()

    def on_rbToolbarIconLarge_clicked(self):
        self.toolbar_icon_large = True
        self.toolbar_icon_medium = False
        self.toolbar_icon_small = False
        self.m_app.toolbar_icon_size = "Large"
        self.parent.update_settings()

    def on_rbToolbarIconSmall_clicked(self):
        self.toolbar_icon_small = True
        self.toolbar_icon_medium = False
        self.toolbar_icon_large = False
        self.m_app.toolbar_icon_size = "Small"
        self.parent.update_settings()

    def on_rbToolbarIconMedium_clicked(self):
        self.toolbar_icon_small = False
        self.toolbar_icon_medium = True
        self.toolbar_icon_large = False
        self.m_app.toolbar_icon_size = "Medium"
        self.parent.update_settings()

    def on_rbRememberGeometryYes_clicked(self):
        self.m_app.remember_geometry = True

    def on_rbRememberGeometryNo_clicked(self):
        self.m_app.remember_geometry = False        

    def Okay(self):
        self.write_settings()
        self.close()

    def Cancel(self):
        self.close()

    def select_folder(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select a folder", str(self.data_folder)))
        if folder:
            self.data_folder = Path(folder).resolve()
            self.edtDataFolder.setText(folder)

class ProgressDialog(QDialog):
    def __init__(self,parent):
        super().__init__()
        #self.setupUi(self)
        #self.setGeometry(200, 250, 400, 250)
        self.setWindowTitle("PhyloForester - Progress Dialog")
        self.parent = parent
        self.setGeometry(QRect(100, 100, 320, 180))
        self.move(self.parent.pos()+QPoint(100,100))

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(50,50, 50, 50)

        self.lbl_text = QLabel(self)
        #self.lbl_text.setGeometry(50, 50, 320, 80)
        #self.pb_progress = QProgressBar(self)
        self.pb_progress = QProgressBar(self)
        #self.pb_progress.setGeometry(50, 150, 320, 40)
        self.pb_progress.setValue(0)
        self.stop_progress = False
        self.btnStop = QPushButton(self)
        #self.btnStop.setGeometry(175, 200, 50, 30)
        self.btnStop.setText("Stop")
        self.btnStop.clicked.connect(self.set_stop_progress)
        self.layout.addWidget(self.lbl_text)
        self.layout.addWidget(self.pb_progress)
        self.layout.addWidget(self.btnStop)
        self.setLayout(self.layout)

    def set_stop_progress(self):
        self.stop_progress = True

    def set_progress_text(self,text_format):
        self.text_format = text_format

    def set_max_value(self,max_value):
        self.max_value = max_value

    def set_curr_value(self,curr_value):
        self.curr_value = curr_value
        self.pb_progress.setValue(int((self.curr_value/float(self.max_value))*100))
        self.lbl_text.setText(self.text_format.format(self.curr_value, self.max_value))
        #self.lbl_text.setText(label_text)
        self.update()
        QApplication.processEvents()