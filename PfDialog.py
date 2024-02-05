from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QFileDialog, QCheckBox, QColorDialog, \
                            QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QProgressBar, QApplication, \
                            QDialog, QLineEdit, QLabel, QPushButton, QAbstractItemView, QStatusBar, QMessageBox, \
                            QTableView, QSplitter, QRadioButton, QComboBox, QTextEdit, QSizePolicy, \
                            QTableWidget, QGridLayout, QAbstractButton, QButtonGroup, QGroupBox, \
                            QTabWidget, QListWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QStandardItemModel, QStandardItem, QImage,\
                        QFont, QPainter, QBrush, QMouseEvent, QWheelEvent, QDoubleValidator
from PyQt5.QtCore import Qt, QRect, QSortFilterProxyModel, QSize, QPoint,\
                         pyqtSlot, QItemSelectionModel, QTimer

from pathlib import Path
import PfUtils as pu
from PfModel import *

class AnalysisDialog(QDialog):
    def __init__(self,parent):
        super().__init__()
        self.setWindowTitle("PhyloForester - Run Analysis")
        self.parent = parent
        self.remember_geometry = True
        self.m_app = QApplication.instance()
        self.read_settings()
        self.edtProjectName = QLineEdit()
        self.edtProjectDesc = QLineEdit()
        self.edtDatamatrixName = QLineEdit()
        self.result_directory_widget = QWidget()
        self.result_directory_layout = QHBoxLayout()
        self.edtResultDirectory = QLineEdit()
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
        self.cbxParsimony.setChecked(True)
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
        result_directory = str(QFileDialog.getExistingDirectory(self, "Select a folder", str(self.result_directory)))
        if result_directory:
            self.result_directory = Path(result_directory).resolve()
            self.edtResultDirectory.setText(result_directory)

    def on_cbxParsimony_clicked(self):
        # add parsimony tab if not exists
        if self.cbxParsimony.isChecked():
            if self.tabView.indexOf(self.tabParsimony) == -1:
                #self.tabParsimony = QWidget()
                self.tabView.addTab(self.tabParsimony, ANALYSIS_TYPE_PARSIMONY)
            self.tabView.setCurrentWidget(self.tabParsimony)
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
                analysis.analysis_name = self.edtAnalysisNameParsimony.text()
            elif analysis_type == ANALYSIS_TYPE_ML:
                analysis.analysis_name = self.edtAnalysisNameML.text()
                analysis.ml_bootstrap_type = self.cbBootstrapType.currentText()
                analysis.ml_bootstrap = int(self.edtBootstrapCount.text())

            elif analysis_type == ANALYSIS_TYPE_BAYESIAN:
                analysis.analysis_name = self.edtAnalysisNameBayesian.text()
                analysis.mcmc_burnin = int(self.edtMCMCBurnin.text())
                analysis.mcmc_relburnin = self.edtMCMCRelBurnin.isChecked()
                analysis.mcmc_burninfrac = float(self.edtMCMCBurninFrac.text())
                analysis.mcmc_ngen = int(self.edtMCMCNGen.text())
                analysis.mcmc_nrates = self.cbMCMCNRates.currentText()
                analysis.mcmc_printfreq = int(self.edtPrintFreq.text())
                analysis.mcmc_samplefreq = int(self.edtSampleFreq.text())
                analysis.mcmc_nruns = int(self.edtNRuns.text())
                analysis.mcmc_nchains = int(self.edtNChains.text())

            analysis.analysis_status = ANALYSIS_STATUS_QUEUED
            analysis.analysis_type = analysis_type
            analysis.result_directory = os.path.join( result_directory_base, analysis.analysis_name )
            analysis.save()

        self.accept()


    def Cancel(self):
        self.reject()

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

        # add listbox for taxa
        self.lstTaxa = QListWidget()
        self.lstTaxa.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.lstTaxa.setSortingEnabled(False)
        self.lstTaxa.setAlternatingRowColors(True)
        #self.lstTaxa.setDragDropMode(QAbstractItemView.InternalMove)
        #self.lstTaxa.setDragEnabled(True)
        #self.lstTaxa.setDropIndicatorShown(True)
        #self.lstTaxa.setAcceptDrops(True)
        #self.lstTaxa.setDragDropOverwriteMode(False)
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

        self.main_layout = QFormLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addRow("Project Name", self.edtProjectName)
        self.main_layout.addRow("Description", self.edtProjectDesc)
        self.main_layout.addRow("Data Type", datatype_layout)
        self.main_layout.addRow("Taxa", self.taxa_layout_widget)

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
        if project.datatype == "Morphology":
            self.rbMorphology.setChecked(True)
        elif project.datatype == "DNA":
            self.rbDNA.setChecked(True)
        elif project.datatype == "RNA":
            self.rbRNA.setChecked(True)
        elif project.datatype == "Combined":
            self.rbCombined.setChecked(True)
        self.lstTaxa.clear()
        if project.taxa_str is not None:
            taxa_list = project.taxa_str.split(",")
            for taxa in taxa_list:
                self.lstTaxa.addItem(taxa)
    
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
        self.project.taxa_str = ""
        for i in range(self.lstTaxa.count()):
            self.project.taxa_str += self.lstTaxa.item(i).text()
            if i < self.lstTaxa.count()-1:
                self.project.taxa_str += ","

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
        self.main_layout.addRow("Softwares", self.gbSoftwarePaths)
        self.main_layout.addRow("", self.btnOkay)

        self.read_settings()

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