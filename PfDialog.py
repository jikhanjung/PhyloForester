from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QFileDialog, QCheckBox, QColorDialog, \
                            QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QProgressBar, QApplication, \
                            QDialog, QLineEdit, QLabel, QPushButton, QAbstractItemView, QStatusBar, QMessageBox, \
                            QTableView, QSplitter, QRadioButton, QComboBox, QTextEdit, QSizePolicy, \
                            QTableWidget, QGridLayout, QAbstractButton, QButtonGroup, QGroupBox, \
                            QTabWidget, QListWidget, QSlider, QScrollBar, QPlainTextEdit 
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QStandardItemModel, QStandardItem, QImage,\
                        QFont, QPainter, QBrush, QMouseEvent, QWheelEvent, QDoubleValidator
from PyQt5.QtCore import Qt, QRect, QSortFilterProxyModel, QSize, QPoint,\
                         pyqtSlot, QItemSelectionModel, QTimer

from pathlib import Path
import PfUtils as pu
from PfModel import *
import matplotlib.pyplot as plt
import matplotlib.backends.backend_svg


class AnalysisViewer(QWidget):
    def __init__(self):
        super(AnalysisViewer, self).__init__()
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

        self.layout1 = QFormLayout()
        self.analysis_info_widget.setLayout(self.layout1)
        self.layout1.addRow("Analysis Name", self.edtAnalysisName) # 0
        self.layout1.addRow("Analysis Type", self.edtAnalysisType) # 1
        self.layout1.addRow("Analysis Package", self.edtAnalysisPackage) # 2
        self.layout1.addRow("Analysis Status", self.edtAnalysisStatus) # 3

        self.edtBootstrapCount = QLineEdit()
        self.edtBootstrapCount.setReadOnly(True)
        self.edtBootstrapType = QLineEdit()
        self.edtBootstrapType.setReadOnly(True)
        self.edtSubstitutionModel = QLineEdit()
        self.edtSubstitutionModel.setReadOnly(True)
        self.layout1.addRow("Bootstrap Count", self.edtBootstrapCount) # 4
        self.layout1.addRow("Bootstrap Type", self.edtBootstrapType) # 5
        self.layout1.addRow("Substitution Model", self.edtSubstitutionModel) # 6

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
        self.layout1.addRow("MCMC Burnin", self.edtMCMCBurnin) # 7
        self.layout1.addRow("MCMC Rel Burnin", self.edtMCMCRelBurnin) # 8
        self.layout1.addRow("MCMC Burnin Frac", self.edtMCMCBurninFrac) # 9
        self.layout1.addRow("MCMC NGen", self.edtMCMCNGen) # 10
        self.layout1.addRow("MCMC NRates", self.edtMCMCNRates) # 11
        self.layout1.addRow("MCMC Print Freq", self.edtMCMCPrintFreq) # 12
        self.layout1.addRow("MCMC Sample Freq", self.edtMCMCSampleFreq) # 13
        self.layout1.addRow("MCMC NRuns", self.edtMCMCNRuns) # 14
        self.layout1.addRow("MCMC NChains", self.edtMCMCNChains) # 15

        self.edtAnalysisResultDirectory = QLineEdit()
        self.edtAnalysisResultDirectory.setReadOnly(True)
        self.dir_widget = QWidget()
        self.dir_layout = QHBoxLayout()
        self.dir_widget.setLayout(self.dir_layout)
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

        #an_layout.addRow("Analysis Output", edtAnalysisOutput)
        self.layout1.addRow("Result Directory", self.dir_widget)
        self.layout1.addRow("Start Datetime", self.edtAnalysisStartDatetime)
        self.layout1.addRow("Finish Datetime", self.edtAnalysisFinishDatetime)
        self.layout1.addRow("Completion %", self.edtAnalysisCompletionPercentage)

    def set_analysis(self,analysis):
        self.analysis = analysis
        self.tree_widget.set_analysis(self.analysis)
        
        if analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            for i in range(4,16):
                #print("i:", i)
                self.layout1.itemAt(4,QFormLayout.FieldRole).widget().hide()
                self.layout1.itemAt(4,QFormLayout.LabelRole).widget().hide()
                self.layout1.removeRow(4)
        elif analysis.analysis_type == ANALYSIS_TYPE_ML:
            for i in range(7,16):
                #print("i:", i)
                self.layout1.itemAt(7,QFormLayout.FieldRole).widget().hide()
                self.layout1.itemAt(7,QFormLayout.LabelRole).widget().hide()
                self.layout1.removeRow(7)
        elif analysis.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            for i in range(4,7):
                #print("i:", i)
                self.layout1.itemAt(4,QFormLayout.FieldRole).widget().hide()
                self.layout1.itemAt(4,QFormLayout.LabelRole).widget().hide()
                self.layout1.removeRow(4)
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
        self.edtAnalysisResultDirectory.setText(analysis.result_directory)
        self.tree_widget.update_info(self.analysis)

    def on_btn_open_result_dir_clicked(self):
        if self.analysis is None:
            return
        result_dir = self.analysis.result_directory
        if os.path.isdir(result_dir):
            os.startfile(result_dir)

    def append_output(self, text):
        self.edtAnalysisOutput.appendPlainText(text)

MODE = { 'NONE': 0, 'PAN': 1, 'ZOOM': 2, 'EDIT': 3 }
class TreeViewer(QWidget):
    def __init__(self):
        super(TreeViewer, self).__init__()
        self.setMinimumSize(400,300)
        self.bgcolor = "#000000"
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.m_app = QApplication.instance()
        self.newick_tree_list = []
        self.treeobj_hash = {}
        self.stored_newick_tree_list = []
        self.stored_treeobj_hash = {}

        self.tree_type_widget = QWidget()        
        self.tree_type_layout = QHBoxLayout()
        self.tree_type_widget.setLayout(self.tree_type_layout)
        self.layout.addWidget(self.tree_type_widget)
        self.rb_tree_type1 = QRadioButton("Trees")
        self.rb_tree_type2 = QRadioButton("Stored Trees")
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
        self.lbl_tree_number = QLabel()
        self.lbl_tree_number.setText("Tree Index")
        self.tree_info_layout.addWidget(self.lbl_tree_number)
        self.edt_tree_index = QLineEdit()
        self.edt_tree_index.setReadOnly(True)
        self.tree_info_layout.addWidget(self.edt_tree_index)
        self.lbl_total_trees = QLabel()
        self.tree_info_layout.addWidget(self.lbl_total_trees)
        #self.lbl_total_trees.setText("Total Trees: 0")

        self.tree_info_widget2 = QWidget()
        self.tree_info_layout2 = QHBoxLayout()
        self.tree_info_widget2.setFixedHeight(50)
        self.tree_info_widget2.setLayout(self.tree_info_layout2)
        self.layout.addWidget(self.tree_info_widget2)
        self.lbl_tree_info = QLabel()
        self.lbl_tree_info.setText("Consensus tree")
        self.tree_info_layout2.addWidget(self.lbl_tree_info)
        self.edt_tree_index2 = QLineEdit()
        self.edt_tree_index2.setReadOnly(True)
        self.tree_info_layout2.addWidget(self.edt_tree_index2)
        self.lbl_total_trees2 = QLabel()
        self.tree_info_layout2.addWidget(self.lbl_total_trees2)

        self.tree_label = TreeLabel()
        self.layout.addWidget(self.tree_label)
        self.tree_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tree_list = []
        self.consensus_tree = None
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.setPageStep(10)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self.on_slider_valueChanged)
        self.layout.addWidget(self.slider)
        self.curr_tree_index = 0
        self.tree_type = 1

    def update_info(self, analysis):
        self.analysis = analysis
        #print("treeview update_info", analysis.analysis_name, analysis.analysis_status, analysis.completion_percentage)
        if analysis.completion_percentage == 100:
            self.load_trees()


    def on_rb_tree_type1_clicked(self):
        #print("on_rb_tree_type1_clicked")
        self.tree_type = 1
        #self.current_treeobj_hash = self.treeobj_hash
        #self.current_newick_tree_list = self.newick_tree_list
        self.slider.setRange(0, len(self.newick_tree_list) - 1)
        self.slider.setValue(0)
        self.on_slider_valueChanged(0)
        self.lbl_total_trees.setText("/" + str(len(self.newick_tree_list)))

    def on_rb_tree_type2_clicked(self):
        #print("on_rb_tree_type2_clicked")
        self.tree_type = 2
        self.slider.setRange(0, len(self.stored_newick_tree_list) - 1)
        self.slider.setValue(0)
        self.on_slider_valueChanged(0)
        self.lbl_total_trees.setText("/" + str(len(self.stored_newick_tree_list)))

        #self.current_treeobj_hash = self.stored_treeobj_hash
        #self.current_newick_tree_list = self.stored_newick_tree_list

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
            else:
                tree = self.treeobj_hash[self.tree_current_index]
        elif self.tree_type == 2:
            if self.tree_current_index < len(self.newick_tree_list):
            #self.stored_tree_list = PfTree.select().where(PfTree.analysis == self.analysis)        
            #self.stored_newick_tree_list = [tree.newick_text for tree in self.stored_tree_list]
                tree = Phylo.read(io.StringIO(self.stored_newick_tree_list[self.tree_current_index]), "newick")

        if tree is None:
            return

        self.tree_label.set_tree(tree)
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

    def load_trees(self):
        #print("load trees")
        tree_dir = self.analysis.result_directory
        if not os.path.exists(tree_dir):
            return
        
        if self.analysis.analysis_type == ANALYSIS_TYPE_ML:
            tf = pu.PhyloTreefile()
            filename = os.path.join(tree_dir, self.analysis.datamatrix.datamatrix_name + ".phy.boottrees")
            #print("ML tree filename:", filename)
            tf.readtree(filename, 'treefile')
            self.newick_tree_list = tf.tree_list

        elif self.analysis.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            tf = pu.PhyloTreefile()
            tf.readtree(os.path.join(tree_dir, "tmp.tre"), 'tre')
            self.newick_tree_list = tf.tree_list

        elif self.analysis.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            tf = pu.PhyloTreefile()
            tf.readtree(os.path.join(tree_dir, self.analysis.datamatrix.datamatrix_name.replace(" ","_") + ".nex1.t"), 'Nexus')
            self.newick_tree_list = tf.tree_list

        self.slider.setRange(0, len(self.newick_tree_list) - 1)
        self.slider.setValue(0)
        self.slider.setPageStep(10)
        self.slider.setSingleStep(1)
        self.lbl_total_trees.setText("/" + str(len(self.newick_tree_list)))
        self.edt_tree_index.setText("1")
        self.on_slider_valueChanged(0)

        self.stored_tree_list = PfTree.select().where(PfTree.analysis == self.analysis)        
        self.stored_newick_tree_list = [tree.newick_text for tree in self.stored_tree_list]
        #for tree in stored_tree_list:
        #    self.add_stored_tree(tree.newick_text)

    def set_tree_image(self, tree_image):
        self.tree_label.set_tree_image( tree_image)


class TreeLabel(QLabel):
    def __init__(self):
        super(TreeLabel, self).__init__()
        self.setMinimumSize(400,300)
        self.bgcolor = "#FFFFFF"
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
        #self.set_mode(MODE['EDIT_LANDMARK'])
        self.tree_node_parents = {}

    def _2canx(self, coord):
        return round((float(coord) / self.image_canvas_ratio) * self.scale) + self.pan_x + self.temp_pan_x
    def _2cany(self, coord):
        return round((float(coord) / self.image_canvas_ratio) * self.scale) + self.pan_y + self.temp_pan_y
    def _2imgx(self, coord):
        return round(((float(coord) - self.pan_x) / self.scale) * self.image_canvas_ratio)
    def _2imgy(self, coord):
        return round(((float(coord) - self.pan_y) / self.scale) * self.image_canvas_ratio)

    def wheelEvent(self, event):
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

    def draw_tree(self, painter):
        if self.tree is None:
            return
        print("draw_tree", self.tree)
        Phylo.draw_ascii(self.tree)

        clade_list = [ c for c in self.tree.find_clades() ]
        root = clade_list[0]
        returned_row = self.draw_node(painter, root, 0, 1)

        print("root:", root, root.count_terminals(), returned_row)
        for child in root:
            print("child:", child, child.count_terminals())

    def draw_node(self, painter, node, begin_row, depth ):
        #pass
        if node.is_terminal():
            self.draw_text( painter, depth, begin_row, node.name )
            return begin_row + 0.5
        else:
            #print("non-terminal:", node)
            traversed_row_count = 0
            returned_row = 0
            for child in node:
                #print("child:", child)
                returned_row += self.draw_node(painter, child, begin_row + traversed_row_count, depth+1)
                traversed_row_count += child.count_terminals()
            return returned_row / len(node)
        

    def draw_text(self, painter, x, y, text):
        painter.drawText(x * 50, y * 30 + 100, text)

    def paintEvent(self, event):
        #print("tree paint", self.curr_pixmap)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QBrush(QColor(self.bgcolor)))#as_qt_color(COLOR['BACKGROUND'])))

        self.draw_tree(painter)

        if self.curr_pixmap is not None:
            painter.drawPixmap(self.pan_x+self.temp_pan_x, self.pan_y+self.temp_pan_y,self.curr_pixmap)

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
        #print("resizeEvent", self, self.size())
        self.calculate_resize()
        #QLabel.resizeEvent(self, event)
        super(TreeLabel, self).resizeEvent(event)

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

    def set_tree(self, tree):
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
    def __init__(self,parent):
        super().__init__()
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
        self.result_directory = Path(pu.USER_PROFILE_DIRECTORY).resolve()
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

        self.cbxML = QCheckBox()
        self.cbxML.setText(ANALYSIS_TYPE_ML)
        self.cbxML.setChecked(False)
        self.cbxML.clicked.connect(self.on_cbxML_clicked)

        self.cbxBayesian = QCheckBox()
        self.cbxBayesian.setText(ANALYSIS_TYPE_BAYESIAN)
        self.cbxBayesian.setChecked(False)
        self.cbxBayesian.clicked.connect(self.on_cbxBayesian_clicked)

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

        self.tabParsimony.setLayout(QFormLayout())
        self.tabML.setLayout(QFormLayout())
        self.tabBayesian.setLayout(QFormLayout())

        
        #self.lblAnalysisNameParsimony = QLabel("Analysis Name")
        #self.lblAnalysisNameML = QLabel("Analysis Name")
        #self.lblAnalysisNameBayesian = QLabel("Analysis Name")
        
        self.edtAnalysisNameParsimony = QLineEdit(ANALYSIS_TYPE_PARSIMONY)
        # bootstrap type: normal, ultrafast
        self.tabParsimony.layout().addRow("Name",self.edtAnalysisNameParsimony)

        self.edtAnalysisNameML = QLineEdit(ANALYSIS_TYPE_ML)
        self.cbBootstrapType = QComboBox()
        self.cbBootstrapType.addItem(BOOTSTRAP_TYPE_NORMAL)
        self.cbBootstrapType.addItem(BOOTSTRAP_TYPE_ULTRAFAST)
        self.edtBootstrapCount = QLineEdit("1000")
        self.tabML.layout().addRow("Name",self.edtAnalysisNameML)
        self.tabML.layout().addRow("Bootstrap Type",self.cbBootstrapType)
        self.tabML.layout().addRow("Bootstrap Count",self.edtBootstrapCount)

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
        
        self.on_cbxParsimony_clicked()

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btnRun)
        btn_layout.addWidget(self.btnCancel)
        self.main_layout.addRow(btn_layout)

    def select_result_directory(self):
        result_directory = str(QFileDialog.getExistingDirectory(self, "Select a folder", str(self.edtResultDirectory.text())))
        if result_directory:
            self.result_directory = Path(result_directory).resolve()
            self.edtResultDirectory.setText(result_directory)

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
            analysis.project = self.parent.selected_project
            if analysis.project is None:
                return
            analysis.datamatrix = self.parent.selected_datamatrix
            if analysis.datamatrix is None:
                return
            
            if analysis_type == ANALYSIS_TYPE_PARSIMONY:
                analysis.analysis_name = self.edtAnalysisNameParsimony.text() #.replace(" ", "_") 
                # add current time to the name
                directory_name = analysis.datamatrix.datamatrix_name + " " + analysis.analysis_name + " " + datetime.datetime.now().strftime("%H%M%S")
                analysis.result_directory = os.path.join( result_directory_base, directory_name.replace(" ","_") ) # TNT does not like space in file name
            elif analysis_type == ANALYSIS_TYPE_ML:
                analysis.analysis_name = self.edtAnalysisNameML.text()
                analysis.ml_bootstrap_type = self.cbBootstrapType.currentText()
                analysis.ml_bootstrap = int(self.edtBootstrapCount.text())
                directory_name = analysis.datamatrix.datamatrix_name + " " + analysis.analysis_name + " " + datetime.datetime.now().strftime("%H%M%S")
                analysis.result_directory = os.path.join( result_directory_base, directory_name )

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
                analysis.result_directory = os.path.join( result_directory_base, directory_name.replace(" ","_") )
                #analysis.result_directory = os.path.join( result_directory_base, directory_name )

            analysis.analysis_status = ANALYSIS_STATUS_QUEUED
            analysis.analysis_type = analysis_type
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
        self.result_directory_base = self.m_app.settings.value("ResultPath", pu.USER_PROFILE_DIRECTORY)


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
    def __init__(self,parent):
        super().__init__()
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
        self.lstCharacters.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.lstCharacters.setSortingEnabled(False)
        self.lstCharacters.setAlternatingRowColors(True)

        self.edtCharacter = QLineEdit()
        self.edtCharacter.setPlaceholderText("Enter character name")
        self.btnAddCharacter = QPushButton()
        self.btnAddCharacter.setText("Add")
        self.btnAddCharacter.clicked.connect(self.on_btnAddCharacter_clicked)
        self.btnRemoveCharacter = QPushButton()
        self.btnRemoveCharacter.setText("Remove")
        self.btnRemoveCharacter.clicked.connect(self.on_btnRemoveCharacter_clicked)

        self.character_input_layout = QHBoxLayout()
        self.character_input_layout.addWidget(self.edtCharacter)
        self.character_input_layout.addWidget(self.btnAddCharacter)
        self.character_input_layout.addWidget(self.btnRemoveCharacter)
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



        self.main_layout = QFormLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addRow("Project Name", self.edtProjectName)
        self.main_layout.addRow("Datamatrix Name", self.edtDatamatrixName)
        self.main_layout.addRow("Description", self.edtDatamatrixDesc)
        self.main_layout.addRow("Data Type", datatype_layout)
        self.main_layout.addRow("Characters", self.characters_layout_widget)
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
        self.main_layout.addRow(btn_layout)

    def on_btnAddCharacter_clicked(self):
        character_name = self.edtCharacter.text()
        if character_name == "":
            return
        self.edtCharacter.setText("")
        self.lstCharacters.addItem(character_name)

    def on_btnRemoveCharacter_clicked(self):
        items = self.lstCharacters.selectedItems()
        for item in items:
            self.lstCharacters.takeItem(self.lstCharacters.row(item))

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
            for character in character_list:
                self.lstCharacters.addItem(character)
    
    def Okay(self):
        if self.datamatrix is None:
            self.datamatrix = PfDatamatrix()
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
        self.datamatrix.characters_str = ""
        for i in range(self.lstCharacters.count()):
            self.datamatrix.characters_str += self.lstCharacters.item(i).text()
            if i < self.lstCharacters.count()-1:
                self.datamatrix.characters_str += ","

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
    def __init__(self,parent):
        super().__init__()
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

        self.main_layout = QFormLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addRow("Project Name", self.edtProjectName)
        self.main_layout.addRow("Description", self.edtProjectDesc)
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
        self.main_layout.addRow(btn_layout)

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
    def __init__(self,parent):
        super().__init__()
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
        self.gbResultPath = QGroupBox("IQTree")
        self.gbResultPath.setLayout(QHBoxLayout())
        self.gbResultPath.layout().addWidget(self.edtResultPath)
        self.gbResultPath.layout().addWidget(self.btnResultPath)
        self.btnResultPath.clicked.connect(self.select_result_path)

        self.lang_layout = QHBoxLayout()
        self.comboLang = QComboBox()
        self.comboLang.addItem(self.tr("English"))
        self.comboLang.addItem(self.tr("Korean"))
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
        self.m_app.tnt_path = Path(self.m_app.settings.value("SoftwarePath/TNT", ""))
        self.m_app.iqtree_path = Path(self.m_app.settings.value("SoftwarePath/IQTree", ""))
        self.m_app.mrbayes_path = Path(self.m_app.settings.value("SoftwarePath/MrBayes", ""))
        self.m_app.result_path = Path(self.m_app.settings.value("ResultPath", ""))
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
        self.m_app.settings.setValue("SoftwarePath/TNT", str(self.m_app.tnt_path))
        self.m_app.settings.setValue("SoftwarePath/IQTree", str(self.m_app.iqtree_path))
        self.m_app.settings.setValue("SoftwarePath/MrBayes", str(self.m_app.mrbayes_path))
        self.m_app.settings.setValue("ResultPath", str(self.m_app.result_path))
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