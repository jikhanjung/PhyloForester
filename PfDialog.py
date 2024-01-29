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

class DatasetDialog(QDialog):
    # NewDatasetDialog shows new dataset dialog.
    def __init__(self,parent):
        super().__init__()
        self.setWindowTitle("PhyloForester - Dataset Information")
        self.parent = parent
        #print(self.parent.pos())
        #self.setGeometry(QRect(100, 100, 600, 400))
        self.remember_geometry = True
        self.m_app = QApplication.instance()
        self.read_settings()
        #self.move(self.parent.pos()+QPoint(100,100))

        self.edtDatasetName = QLineEdit()
        self.edtDatasetDesc = QLineEdit()

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

        self.main_layout = QFormLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addRow("Dataset Name", self.edtDatasetName)
        self.main_layout.addRow("Description", self.edtDatasetDesc)
        self.main_layout.addRow("Data Type", datatype_layout)

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

        self.dataset = None

    def read_settings(self):
        self.remember_geometry = pu.value_to_bool(self.m_app.settings.value("WindowGeometry/RememberGeometry", True))
        if self.remember_geometry is True:
            self.setGeometry(self.m_app.settings.value("WindowGeometry/DatasetDialog", QRect(100, 100, 600, 400)))
        else:
            self.setGeometry(QRect(100, 100, 600, 400))
            self.move(self.parent.pos()+QPoint(100,100))


    def write_settings(self):
        if self.remember_geometry is True:
            self.m_app.settings.setValue("WindowGeometry/DatasetDialog", self.geometry())

    def closeEvent(self, event):
        self.write_settings()
        event.accept()

    def read_dataset(self, dataset_id):
        try:
            dataset = PfDataset.get(dataset.id == dataset_id)
        except:
            dataset = None
        self.dataset = dataset

    def set_dataset(self, dataset):
        if dataset is None:
            self.dataset = None
            self.cbxParent.setCurrentIndex(-1)
            return

        self.dataset = dataset

        self.edtDatasetName.setText(dataset.dataset_name)
        self.edtDatasetDesc.setText(dataset.dataset_desc)
        if dataset.datatype == "Morphology":
            self.rbMorphology.setChecked(True)
        elif dataset.datatype == "DNA":
            self.rbDNA.setChecked(True)
        elif dataset.datatype == "RNA":
            self.rbRNA.setChecked(True)
        elif dataset.datatype == "Combined":
            self.rbCombined.setChecked(True)
        #print(dataset.dimension,self.dataset.objects)
    
    def Okay(self):
        if self.dataset is None:
            self.dataset = PfDataset()
        self.dataset.dataset_name = self.edtDatasetName.text()
        self.dataset.dataset_desc = self.edtDatasetDesc.text()
        if self.rbMorphology.isChecked():
            self.dataset.datatype = "Morphology"
        elif self.rbDNA.isChecked():
            self.dataset.datatype = "DNA"
        elif self.rbRNA.isChecked():
            self.dataset.datatype = "RNA"
        elif self.rbCombined.isChecked():
            self.dataset.datatype = "Combined"

        #self.data
        #print(self.dataset.dataset_desc, self.dataset.dataset_name)
        self.dataset.save()
        self.accept()

    def Delete(self):
        ret = QMessageBox.question(self, "", "Are you sure to delete this dataset?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        #print("ret:", ret)
        if ret == QMessageBox.Yes:
            self.dataset.delete_instance()
            self.parent.selected_dataset = None
            #self.dataset.delete_dataset()
        #self.delete_dataset()
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
        self.main_layout.addRow("", self.btnOkay)

        self.read_settings()

    def comboLangIndexChanged(self, index):
        if index == 0:
            self.m_app.language = "en"
        elif index == 1:
            self.m_app.language = "ko"

    def read_settings(self):
        self.m_app.remember_geometry = pu.value_to_bool(self.m_app.settings.value("WindowGeometry/RememberGeometry", True))
        self.m_app.toolbar_icon_size = self.m_app.settings.value("ToolbarIconSize", "Medium")
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
