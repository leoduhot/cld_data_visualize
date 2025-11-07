# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWin.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QCheckBox, QComboBox,
    QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QMainWindow, QPushButton,
    QScrollArea, QSizePolicy, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1004, 689)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setStyleSheet(u"Fusion")
        self.action1 = QAction(MainWindow)
        self.action1.setObjectName(u"action1")
        self.action2 = QAction(MainWindow)
        self.action2.setObjectName(u"action2")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.centralwidget.setMinimumSize(QSize(0, 451))
        self.centralwidget.setAcceptDrops(True)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setMouseTracking(False)
        self.scrollArea.setTabletTracking(False)
        self.scrollArea.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scrollArea.setAcceptDrops(True)
        self.scrollArea.setFrameShape(QFrame.Shape.StyledPanel)
        self.scrollArea.setFrameShadow(QFrame.Shadow.Raised)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1000, 678))
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy2)
        self.scrollAreaWidgetContents.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scrollAreaWidgetContents.setAcceptDrops(True)
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(6, 6, 6, 6)
        self.fileBrowserFrm = QFrame(self.scrollAreaWidgetContents)
        self.fileBrowserFrm.setObjectName(u"fileBrowserFrm")
        self.fileBrowserFrm.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.fileBrowserFrm.sizePolicy().hasHeightForWidth())
        self.fileBrowserFrm.setSizePolicy(sizePolicy3)
        self.fileBrowserFrm.setAcceptDrops(True)
        self.fileBrowserFrm.setFrameShape(QFrame.Shape.StyledPanel)
        self.fileBrowserFrm.setFrameShadow(QFrame.Shadow.Sunken)
        self.fileBrowserFrm.setLineWidth(1)
        self.horizontalLayout_2 = QHBoxLayout(self.fileBrowserFrm)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.horizontalLayout_2.setContentsMargins(-1, 6, -1, 6)
        self.filaPathLab = QLabel(self.fileBrowserFrm)
        self.filaPathLab.setObjectName(u"filaPathLab")

        self.horizontalLayout_2.addWidget(self.filaPathLab)

        self.fileEntry = QLineEdit(self.fileBrowserFrm)
        self.fileEntry.setObjectName(u"fileEntry")
        self.fileEntry.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.fileEntry.setAcceptDrops(True)
        self.fileEntry.setDragEnabled(True)

        self.horizontalLayout_2.addWidget(self.fileEntry)

        self.browserBtn = QPushButton(self.fileBrowserFrm)
        self.browserBtn.setObjectName(u"browserBtn")
        self.browserBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.browserBtn.setAutoFillBackground(False)

        self.horizontalLayout_2.addWidget(self.browserBtn)


        self.verticalLayout_3.addWidget(self.fileBrowserFrm)

        self.keepFrm = QFrame(self.scrollAreaWidgetContents)
        self.keepFrm.setObjectName(u"keepFrm")
        sizePolicy.setHeightForWidth(self.keepFrm.sizePolicy().hasHeightForWidth())
        self.keepFrm.setSizePolicy(sizePolicy)
        self.keepFrm.setFrameShape(QFrame.Shape.NoFrame)
        self.keepFrm.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_4 = QGridLayout(self.keepFrm)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, -1, 0)
        self.keepParamCkb = QCheckBox(self.keepFrm)
        self.keepParamCkb.setObjectName(u"keepParamCkb")

        self.gridLayout_4.addWidget(self.keepParamCkb, 0, 0, 1, 1)


        self.verticalLayout_3.addWidget(self.keepFrm)

        self.paramFrm = QFrame(self.scrollAreaWidgetContents)
        self.paramFrm.setObjectName(u"paramFrm")
        self.paramFrm.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.paramFrm.sizePolicy().hasHeightForWidth())
        self.paramFrm.setSizePolicy(sizePolicy3)
        self.paramFrm.setFrameShape(QFrame.Shape.StyledPanel)
        self.paramFrm.setFrameShadow(QFrame.Shadow.Sunken)
        self.verticalLayout_5 = QVBoxLayout(self.paramFrm)
#ifndef Q_OS_MAC
        self.verticalLayout_5.setSpacing(-1)
#endif
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(-1, 6, -1, 6)
        self.frame_2 = QFrame(self.paramFrm)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_8 = QGridLayout(self.frame_2)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.frame_2)
        self.label.setObjectName(u"label")

        self.gridLayout_8.addWidget(self.label, 0, 2, 1, 1)

        self.convertTypeComb = QComboBox(self.frame_2)
        self.convertTypeComb.addItem("")
        self.convertTypeComb.addItem("")
        self.convertTypeComb.setObjectName(u"convertTypeComb")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(1)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.convertTypeComb.sizePolicy().hasHeightForWidth())
        self.convertTypeComb.setSizePolicy(sizePolicy4)

        self.gridLayout_8.addWidget(self.convertTypeComb, 0, 10, 1, 1)

        self.label_2 = QLabel(self.frame_2)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_8.addWidget(self.label_2, 0, 5, 1, 1)

        self.sensorTypeComb = QComboBox(self.frame_2)
        self.sensorTypeComb.setObjectName(u"sensorTypeComb")
        sizePolicy4.setHeightForWidth(self.sensorTypeComb.sizePolicy().hasHeightForWidth())
        self.sensorTypeComb.setSizePolicy(sizePolicy4)
        self.sensorTypeComb.setMinimumSize(QSize(80, 0))

        self.gridLayout_8.addWidget(self.sensorTypeComb, 0, 4, 1, 1)

        self.convertTypeLab = QLabel(self.frame_2)
        self.convertTypeLab.setObjectName(u"convertTypeLab")

        self.gridLayout_8.addWidget(self.convertTypeLab, 0, 9, 1, 1)

        self.projectComb = QComboBox(self.frame_2)
        self.projectComb.setObjectName(u"projectComb")
        sizePolicy4.setHeightForWidth(self.projectComb.sizePolicy().hasHeightForWidth())
        self.projectComb.setSizePolicy(sizePolicy4)
        self.projectComb.setMinimumSize(QSize(40, 0))

        self.gridLayout_8.addWidget(self.projectComb, 0, 1, 1, 1)

        self.projectLab = QLabel(self.frame_2)
        self.projectLab.setObjectName(u"projectLab")

        self.gridLayout_8.addWidget(self.projectLab, 0, 0, 1, 1)

        self.dataTypeLab = QLabel(self.frame_2)
        self.dataTypeLab.setObjectName(u"dataTypeLab")

        self.gridLayout_8.addWidget(self.dataTypeLab, 0, 6, 1, 1)

        self.sensorTypeLab = QLabel(self.frame_2)
        self.sensorTypeLab.setObjectName(u"sensorTypeLab")

        self.gridLayout_8.addWidget(self.sensorTypeLab, 0, 3, 1, 1)

        self.dataTypeComb = QComboBox(self.frame_2)
        self.dataTypeComb.addItem("")
        self.dataTypeComb.addItem("")
        self.dataTypeComb.addItem("")
        self.dataTypeComb.setObjectName(u"dataTypeComb")
        sizePolicy3.setHeightForWidth(self.dataTypeComb.sizePolicy().hasHeightForWidth())
        self.dataTypeComb.setSizePolicy(sizePolicy3)
        self.dataTypeComb.setMinimumSize(QSize(140, 0))

        self.gridLayout_8.addWidget(self.dataTypeComb, 0, 7, 1, 1)

        self.label_3 = QLabel(self.frame_2)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_8.addWidget(self.label_3, 0, 8, 1, 1)


        self.verticalLayout_5.addWidget(self.frame_2)

        self.plotNameFrm = QFrame(self.paramFrm)
        self.plotNameFrm.setObjectName(u"plotNameFrm")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.plotNameFrm.sizePolicy().hasHeightForWidth())
        self.plotNameFrm.setSizePolicy(sizePolicy5)
        self.plotNameFrm.setFrameShape(QFrame.Shape.NoFrame)
        self.plotNameFrm.setFrameShadow(QFrame.Shadow.Sunken)
        self.gridLayout = QGridLayout(self.plotNameFrm)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.plotNameFrm)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 2, 1, 1)

        self.plotNameLab = QLabel(self.plotNameFrm)
        self.plotNameLab.setObjectName(u"plotNameLab")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.plotNameLab.sizePolicy().hasHeightForWidth())
        self.plotNameLab.setSizePolicy(sizePolicy6)

        self.gridLayout.addWidget(self.plotNameLab, 0, 12, 1, 1)

        self.dataDropEndEntry = QLineEdit(self.plotNameFrm)
        self.dataDropEndEntry.setObjectName(u"dataDropEndEntry")
        sizePolicy5.setHeightForWidth(self.dataDropEndEntry.sizePolicy().hasHeightForWidth())
        self.dataDropEndEntry.setSizePolicy(sizePolicy5)
        self.dataDropEndEntry.setMinimumSize(QSize(40, 0))

        self.gridLayout.addWidget(self.dataDropEndEntry, 0, 5, 1, 1)

        self.dataRateLab = QLabel(self.plotNameFrm)
        self.dataRateLab.setObjectName(u"dataRateLab")

        self.gridLayout.addWidget(self.dataRateLab, 0, 0, 1, 1)

        self.dataDropStartEntry = QLineEdit(self.plotNameFrm)
        self.dataDropStartEntry.setObjectName(u"dataDropStartEntry")
        sizePolicy5.setHeightForWidth(self.dataDropStartEntry.sizePolicy().hasHeightForWidth())
        self.dataDropStartEntry.setSizePolicy(sizePolicy5)
        self.dataDropStartEntry.setMinimumSize(QSize(40, 0))

        self.gridLayout.addWidget(self.dataDropStartEntry, 0, 4, 1, 1)

        self.gainEntry = QLineEdit(self.plotNameFrm)
        self.gainEntry.setObjectName(u"gainEntry")
        self.gainEntry.setMinimumSize(QSize(40, 0))

        self.gridLayout.addWidget(self.gainEntry, 0, 10, 1, 1)

        self.plotNameEntry = QLineEdit(self.plotNameFrm)
        self.plotNameEntry.setObjectName(u"plotNameEntry")
        sizePolicy3.setHeightForWidth(self.plotNameEntry.sizePolicy().hasHeightForWidth())
        self.plotNameEntry.setSizePolicy(sizePolicy3)
        self.plotNameEntry.setMinimumSize(QSize(60, 0))

        self.gridLayout.addWidget(self.plotNameEntry, 0, 13, 1, 1)

        self.gainLab = QLabel(self.plotNameFrm)
        self.gainLab.setObjectName(u"gainLab")

        self.gridLayout.addWidget(self.gainLab, 0, 7, 1, 1)

        self.dataDropsLab = QLabel(self.plotNameFrm)
        self.dataDropsLab.setObjectName(u"dataDropsLab")

        self.gridLayout.addWidget(self.dataDropsLab, 0, 3, 1, 1)

        self.dataRateEntry = QLineEdit(self.plotNameFrm)
        self.dataRateEntry.setObjectName(u"dataRateEntry")
        sizePolicy5.setHeightForWidth(self.dataRateEntry.sizePolicy().hasHeightForWidth())
        self.dataRateEntry.setSizePolicy(sizePolicy5)
        self.dataRateEntry.setMinimumSize(QSize(40, 0))

        self.gridLayout.addWidget(self.dataRateEntry, 0, 1, 1, 1)

        self.label_5 = QLabel(self.plotNameFrm)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 0, 6, 1, 1)

        self.label_6 = QLabel(self.plotNameFrm)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 0, 11, 1, 1)


        self.verticalLayout_5.addWidget(self.plotNameFrm)


        self.verticalLayout_3.addWidget(self.paramFrm)

        self.frame_3 = QFrame(self.scrollAreaWidgetContents)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_9 = QGridLayout(self.frame_3)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setContentsMargins(-1, 6, -1, 6)
        self.mspFreqEntry = QLineEdit(self.frame_3)
        self.mspFreqEntry.setObjectName(u"mspFreqEntry")

        self.gridLayout_9.addWidget(self.mspFreqEntry, 0, 3, 1, 1)

        self.mspFreqLab = QLabel(self.frame_3)
        self.mspFreqLab.setObjectName(u"mspFreqLab")

        self.gridLayout_9.addWidget(self.mspFreqLab, 0, 2, 1, 1)

        self.mspChkb = QCheckBox(self.frame_3)
        self.mspChkb.setObjectName(u"mspChkb")

        self.gridLayout_9.addWidget(self.mspChkb, 0, 0, 1, 1)

        self.frame_4 = QFrame(self.frame_3)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout_9.addWidget(self.frame_4, 0, 1, 1, 1)

        self.frame_5 = QFrame(self.frame_3)
        self.frame_5.setObjectName(u"frame_5")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.frame_5.sizePolicy().hasHeightForWidth())
        self.frame_5.setSizePolicy(sizePolicy7)
        self.frame_5.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout_9.addWidget(self.frame_5, 0, 4, 1, 1)


        self.verticalLayout_3.addWidget(self.frame_3)

        self.filterFrm = QFrame(self.scrollAreaWidgetContents)
        self.filterFrm.setObjectName(u"filterFrm")
        sizePolicy3.setHeightForWidth(self.filterFrm.sizePolicy().hasHeightForWidth())
        self.filterFrm.setSizePolicy(sizePolicy3)
        self.filterFrm.setFrameShape(QFrame.Shape.StyledPanel)
        self.filterFrm.setFrameShadow(QFrame.Shadow.Sunken)
        self.gridLayout_2 = QGridLayout(self.filterFrm)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(-1, 6, -1, 6)
        self.hpfChkb = QCheckBox(self.filterFrm)
        self.hpfChkb.setObjectName(u"hpfChkb")

        self.gridLayout_2.addWidget(self.hpfChkb, 0, 0, 1, 1)

        self.hpfTypeComb = QComboBox(self.filterFrm)
        self.hpfTypeComb.addItem("")
        self.hpfTypeComb.addItem("")
        self.hpfTypeComb.addItem("")
        self.hpfTypeComb.setObjectName(u"hpfTypeComb")
        sizePolicy4.setHeightForWidth(self.hpfTypeComb.sizePolicy().hasHeightForWidth())
        self.hpfTypeComb.setSizePolicy(sizePolicy4)
        self.hpfTypeComb.setMinimumSize(QSize(80, 0))

        self.gridLayout_2.addWidget(self.hpfTypeComb, 0, 3, 1, 1)

        self.hpfFreqLab = QLabel(self.filterFrm)
        self.hpfFreqLab.setObjectName(u"hpfFreqLab")

        self.gridLayout_2.addWidget(self.hpfFreqLab, 0, 8, 1, 1)

        self.lpfOrdLab = QLabel(self.filterFrm)
        self.lpfOrdLab.setObjectName(u"lpfOrdLab")

        self.gridLayout_2.addWidget(self.lpfOrdLab, 1, 5, 1, 1)

        self.lpfTypeLab = QLabel(self.filterFrm)
        self.lpfTypeLab.setObjectName(u"lpfTypeLab")

        self.gridLayout_2.addWidget(self.lpfTypeLab, 1, 2, 1, 1)

        self.lpfOrdEntry = QLineEdit(self.filterFrm)
        self.lpfOrdEntry.setObjectName(u"lpfOrdEntry")
        sizePolicy3.setHeightForWidth(self.lpfOrdEntry.sizePolicy().hasHeightForWidth())
        self.lpfOrdEntry.setSizePolicy(sizePolicy3)
        self.lpfOrdEntry.setAcceptDrops(False)

        self.gridLayout_2.addWidget(self.lpfOrdEntry, 1, 6, 1, 1)

        self.hpfOrdEntry = QLineEdit(self.filterFrm)
        self.hpfOrdEntry.setObjectName(u"hpfOrdEntry")
        sizePolicy3.setHeightForWidth(self.hpfOrdEntry.sizePolicy().hasHeightForWidth())
        self.hpfOrdEntry.setSizePolicy(sizePolicy3)
        self.hpfOrdEntry.setAcceptDrops(False)
        self.hpfOrdEntry.setStyleSheet(u"")

        self.gridLayout_2.addWidget(self.hpfOrdEntry, 0, 6, 1, 1)

        self.hpfFreqEntry = QLineEdit(self.filterFrm)
        self.hpfFreqEntry.setObjectName(u"hpfFreqEntry")
        sizePolicy3.setHeightForWidth(self.hpfFreqEntry.sizePolicy().hasHeightForWidth())
        self.hpfFreqEntry.setSizePolicy(sizePolicy3)
        self.hpfFreqEntry.setAcceptDrops(False)

        self.gridLayout_2.addWidget(self.hpfFreqEntry, 0, 9, 1, 1)

        self.hpfOrdLab = QLabel(self.filterFrm)
        self.hpfOrdLab.setObjectName(u"hpfOrdLab")

        self.gridLayout_2.addWidget(self.hpfOrdLab, 0, 5, 1, 1)

        self.lpfFreqLab = QLabel(self.filterFrm)
        self.lpfFreqLab.setObjectName(u"lpfFreqLab")

        self.gridLayout_2.addWidget(self.lpfFreqLab, 1, 8, 1, 1)

        self.lpfChkb = QCheckBox(self.filterFrm)
        self.lpfChkb.setObjectName(u"lpfChkb")

        self.gridLayout_2.addWidget(self.lpfChkb, 1, 0, 1, 1)

        self.hpfTypeLab = QLabel(self.filterFrm)
        self.hpfTypeLab.setObjectName(u"hpfTypeLab")

        self.gridLayout_2.addWidget(self.hpfTypeLab, 0, 2, 1, 1)

        self.pfPadLad2 = QLabel(self.filterFrm)
        self.pfPadLad2.setObjectName(u"pfPadLad2")

        self.gridLayout_2.addWidget(self.pfPadLad2, 1, 1, 1, 1)

        self.pfPadLab1 = QLabel(self.filterFrm)
        self.pfPadLab1.setObjectName(u"pfPadLab1")

        self.gridLayout_2.addWidget(self.pfPadLab1, 0, 1, 1, 1)

        self.lpfFreqEntry = QLineEdit(self.filterFrm)
        self.lpfFreqEntry.setObjectName(u"lpfFreqEntry")
        sizePolicy3.setHeightForWidth(self.lpfFreqEntry.sizePolicy().hasHeightForWidth())
        self.lpfFreqEntry.setSizePolicy(sizePolicy3)
        self.lpfFreqEntry.setAcceptDrops(False)

        self.gridLayout_2.addWidget(self.lpfFreqEntry, 1, 9, 1, 1)

        self.lpfTypeComb = QComboBox(self.filterFrm)
        self.lpfTypeComb.addItem("")
        self.lpfTypeComb.addItem("")
        self.lpfTypeComb.addItem("")
        self.lpfTypeComb.setObjectName(u"lpfTypeComb")
        sizePolicy4.setHeightForWidth(self.lpfTypeComb.sizePolicy().hasHeightForWidth())
        self.lpfTypeComb.setSizePolicy(sizePolicy4)
        self.lpfTypeComb.setMinimumSize(QSize(80, 0))

        self.gridLayout_2.addWidget(self.lpfTypeComb, 1, 3, 1, 1)

        self.label_16 = QLabel(self.filterFrm)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_2.addWidget(self.label_16, 0, 4, 1, 1)

        self.label_17 = QLabel(self.filterFrm)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_2.addWidget(self.label_17, 1, 4, 1, 1)

        self.label_18 = QLabel(self.filterFrm)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_2.addWidget(self.label_18, 0, 7, 1, 1)

        self.label_19 = QLabel(self.filterFrm)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_2.addWidget(self.label_19, 1, 7, 1, 1)


        self.verticalLayout_3.addWidget(self.filterFrm)

        self.filterfFm2 = QFrame(self.scrollAreaWidgetContents)
        self.filterfFm2.setObjectName(u"filterfFm2")
        sizePolicy3.setHeightForWidth(self.filterfFm2.sizePolicy().hasHeightForWidth())
        self.filterfFm2.setSizePolicy(sizePolicy3)
        self.filterfFm2.setFrameShape(QFrame.Shape.StyledPanel)
        self.filterfFm2.setFrameShadow(QFrame.Shadow.Sunken)
        self.gridLayout_6 = QGridLayout(self.filterfFm2)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(-1, 6, -1, 6)
        self.nfPadLab2 = QLabel(self.filterfFm2)
        self.nfPadLab2.setObjectName(u"nfPadLab2")

        self.gridLayout_6.addWidget(self.nfPadLab2, 1, 1, 1, 1)

        self.nf3FreqLab = QLabel(self.filterfFm2)
        self.nf3FreqLab.setObjectName(u"nf3FreqLab")

        self.gridLayout_6.addWidget(self.nf3FreqLab, 2, 2, 1, 1)

        self.nfPadLab1 = QLabel(self.filterfFm2)
        self.nfPadLab1.setObjectName(u"nfPadLab1")

        self.gridLayout_6.addWidget(self.nfPadLab1, 0, 1, 1, 1)

        self.nf1FreqEntry = QLineEdit(self.filterfFm2)
        self.nf1FreqEntry.setObjectName(u"nf1FreqEntry")
        sizePolicy3.setHeightForWidth(self.nf1FreqEntry.sizePolicy().hasHeightForWidth())
        self.nf1FreqEntry.setSizePolicy(sizePolicy3)
        self.nf1FreqEntry.setAcceptDrops(False)

        self.gridLayout_6.addWidget(self.nf1FreqEntry, 0, 3, 1, 1)

        self.nf2QEntry = QLineEdit(self.filterfFm2)
        self.nf2QEntry.setObjectName(u"nf2QEntry")
        sizePolicy3.setHeightForWidth(self.nf2QEntry.sizePolicy().hasHeightForWidth())
        self.nf2QEntry.setSizePolicy(sizePolicy3)
        self.nf2QEntry.setAcceptDrops(False)

        self.gridLayout_6.addWidget(self.nf2QEntry, 1, 6, 1, 1)

        self.nf2QLab = QLabel(self.filterfFm2)
        self.nf2QLab.setObjectName(u"nf2QLab")

        self.gridLayout_6.addWidget(self.nf2QLab, 1, 5, 1, 1)

        self.nf1QLab = QLabel(self.filterfFm2)
        self.nf1QLab.setObjectName(u"nf1QLab")

        self.gridLayout_6.addWidget(self.nf1QLab, 0, 5, 1, 1)

        self.nf3FreqEntry = QLineEdit(self.filterfFm2)
        self.nf3FreqEntry.setObjectName(u"nf3FreqEntry")
        sizePolicy3.setHeightForWidth(self.nf3FreqEntry.sizePolicy().hasHeightForWidth())
        self.nf3FreqEntry.setSizePolicy(sizePolicy3)
        self.nf3FreqEntry.setAcceptDrops(False)

        self.gridLayout_6.addWidget(self.nf3FreqEntry, 2, 3, 1, 1)

        self.nfPadLab3 = QLabel(self.filterfFm2)
        self.nfPadLab3.setObjectName(u"nfPadLab3")

        self.gridLayout_6.addWidget(self.nfPadLab3, 2, 1, 1, 1)

        self.nf3QEntry = QLineEdit(self.filterfFm2)
        self.nf3QEntry.setObjectName(u"nf3QEntry")
        sizePolicy3.setHeightForWidth(self.nf3QEntry.sizePolicy().hasHeightForWidth())
        self.nf3QEntry.setSizePolicy(sizePolicy3)
        self.nf3QEntry.setAcceptDrops(False)

        self.gridLayout_6.addWidget(self.nf3QEntry, 2, 6, 1, 1)

        self.nf1QEntry = QLineEdit(self.filterfFm2)
        self.nf1QEntry.setObjectName(u"nf1QEntry")
        sizePolicy3.setHeightForWidth(self.nf1QEntry.sizePolicy().hasHeightForWidth())
        self.nf1QEntry.setSizePolicy(sizePolicy3)
        self.nf1QEntry.setAcceptDrops(False)

        self.gridLayout_6.addWidget(self.nf1QEntry, 0, 6, 1, 1)

        self.nf2FreqEntry = QLineEdit(self.filterfFm2)
        self.nf2FreqEntry.setObjectName(u"nf2FreqEntry")
        sizePolicy3.setHeightForWidth(self.nf2FreqEntry.sizePolicy().hasHeightForWidth())
        self.nf2FreqEntry.setSizePolicy(sizePolicy3)
        self.nf2FreqEntry.setAcceptDrops(False)

        self.gridLayout_6.addWidget(self.nf2FreqEntry, 1, 3, 1, 1)

        self.nf3Chkb = QCheckBox(self.filterfFm2)
        self.nf3Chkb.setObjectName(u"nf3Chkb")

        self.gridLayout_6.addWidget(self.nf3Chkb, 2, 0, 1, 1)

        self.nf1Chkb = QCheckBox(self.filterfFm2)
        self.nf1Chkb.setObjectName(u"nf1Chkb")

        self.gridLayout_6.addWidget(self.nf1Chkb, 0, 0, 1, 1)

        self.nf2Chkb = QCheckBox(self.filterfFm2)
        self.nf2Chkb.setObjectName(u"nf2Chkb")

        self.gridLayout_6.addWidget(self.nf2Chkb, 1, 0, 1, 1)

        self.nf1FreqLab = QLabel(self.filterfFm2)
        self.nf1FreqLab.setObjectName(u"nf1FreqLab")

        self.gridLayout_6.addWidget(self.nf1FreqLab, 0, 2, 1, 1)

        self.nf3QLab = QLabel(self.filterfFm2)
        self.nf3QLab.setObjectName(u"nf3QLab")

        self.gridLayout_6.addWidget(self.nf3QLab, 2, 5, 1, 1)

        self.nf2FreqLab = QLabel(self.filterfFm2)
        self.nf2FreqLab.setObjectName(u"nf2FreqLab")

        self.gridLayout_6.addWidget(self.nf2FreqLab, 1, 2, 1, 1)

        self.label_13 = QLabel(self.filterfFm2)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_6.addWidget(self.label_13, 0, 4, 1, 1)

        self.label_14 = QLabel(self.filterfFm2)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_6.addWidget(self.label_14, 1, 4, 1, 1)

        self.label_15 = QLabel(self.filterfFm2)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_6.addWidget(self.label_15, 2, 4, 1, 1)


        self.verticalLayout_3.addWidget(self.filterfFm2)

        self.scaleFrm = QFrame(self.scrollAreaWidgetContents)
        self.scaleFrm.setObjectName(u"scaleFrm")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.scaleFrm.sizePolicy().hasHeightForWidth())
        self.scaleFrm.setSizePolicy(sizePolicy8)
        self.scaleFrm.setFrameShape(QFrame.Shape.StyledPanel)
        self.scaleFrm.setFrameShadow(QFrame.Shadow.Sunken)
        self.gridLayout_3 = QGridLayout(self.scaleFrm)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(-1, 6, -1, 6)
        self.fftScaleXEndEntry = QLineEdit(self.scaleFrm)
        self.fftScaleXEndEntry.setObjectName(u"fftScaleXEndEntry")
        sizePolicy3.setHeightForWidth(self.fftScaleXEndEntry.sizePolicy().hasHeightForWidth())
        self.fftScaleXEndEntry.setSizePolicy(sizePolicy3)
        self.fftScaleXEndEntry.setAcceptDrops(False)

        self.gridLayout_3.addWidget(self.fftScaleXEndEntry, 0, 6, 1, 1)

        self.summPlotLimitLowerLab = QLabel(self.scaleFrm)
        self.summPlotLimitLowerLab.setObjectName(u"summPlotLimitLowerLab")

        self.gridLayout_3.addWidget(self.summPlotLimitLowerLab, 2, 2, 1, 1)

        self.fftScaleYStartLab = QLabel(self.scaleFrm)
        self.fftScaleYStartLab.setObjectName(u"fftScaleYStartLab")

        self.gridLayout_3.addWidget(self.fftScaleYStartLab, 1, 2, 1, 1)

        self.fftScaleYStartEntry = QLineEdit(self.scaleFrm)
        self.fftScaleYStartEntry.setObjectName(u"fftScaleYStartEntry")
        sizePolicy3.setHeightForWidth(self.fftScaleYStartEntry.sizePolicy().hasHeightForWidth())
        self.fftScaleYStartEntry.setSizePolicy(sizePolicy3)
        self.fftScaleYStartEntry.setAcceptDrops(False)

        self.gridLayout_3.addWidget(self.fftScaleYStartEntry, 1, 3, 1, 1)

        self.fftScaleXChkb = QCheckBox(self.scaleFrm)
        self.fftScaleXChkb.setObjectName(u"fftScaleXChkb")

        self.gridLayout_3.addWidget(self.fftScaleXChkb, 0, 0, 1, 1)

        self.fftPadLab2 = QLabel(self.scaleFrm)
        self.fftPadLab2.setObjectName(u"fftPadLab2")

        self.gridLayout_3.addWidget(self.fftPadLab2, 1, 1, 1, 1)

        self.summPlotLimitChkb = QCheckBox(self.scaleFrm)
        self.summPlotLimitChkb.setObjectName(u"summPlotLimitChkb")

        self.gridLayout_3.addWidget(self.summPlotLimitChkb, 2, 0, 1, 1)

        self.summPlotLimitUpperLab = QLabel(self.scaleFrm)
        self.summPlotLimitUpperLab.setObjectName(u"summPlotLimitUpperLab")

        self.gridLayout_3.addWidget(self.summPlotLimitUpperLab, 2, 5, 1, 1)

        self.fftPadLab1 = QLabel(self.scaleFrm)
        self.fftPadLab1.setObjectName(u"fftPadLab1")

        self.gridLayout_3.addWidget(self.fftPadLab1, 0, 1, 1, 1)

        self.fftScaleXStartLab = QLabel(self.scaleFrm)
        self.fftScaleXStartLab.setObjectName(u"fftScaleXStartLab")

        self.gridLayout_3.addWidget(self.fftScaleXStartLab, 0, 2, 1, 1)

        self.fftScaleYEndEntry = QLineEdit(self.scaleFrm)
        self.fftScaleYEndEntry.setObjectName(u"fftScaleYEndEntry")
        sizePolicy3.setHeightForWidth(self.fftScaleYEndEntry.sizePolicy().hasHeightForWidth())
        self.fftScaleYEndEntry.setSizePolicy(sizePolicy3)
        self.fftScaleYEndEntry.setAcceptDrops(False)

        self.gridLayout_3.addWidget(self.fftScaleYEndEntry, 1, 6, 1, 1)

        self.summPlotLimitUpperEntry = QLineEdit(self.scaleFrm)
        self.summPlotLimitUpperEntry.setObjectName(u"summPlotLimitUpperEntry")

        self.gridLayout_3.addWidget(self.summPlotLimitUpperEntry, 2, 6, 1, 1)

        self.fftScaleXEndLab = QLabel(self.scaleFrm)
        self.fftScaleXEndLab.setObjectName(u"fftScaleXEndLab")

        self.gridLayout_3.addWidget(self.fftScaleXEndLab, 0, 5, 1, 1)

        self.summPlotLimitLowerEntry = QLineEdit(self.scaleFrm)
        self.summPlotLimitLowerEntry.setObjectName(u"summPlotLimitLowerEntry")

        self.gridLayout_3.addWidget(self.summPlotLimitLowerEntry, 2, 3, 1, 1)

        self.fftScaleYChkb = QCheckBox(self.scaleFrm)
        self.fftScaleYChkb.setObjectName(u"fftScaleYChkb")

        self.gridLayout_3.addWidget(self.fftScaleYChkb, 1, 0, 1, 1)

        self.fftScaleYEndLab = QLabel(self.scaleFrm)
        self.fftScaleYEndLab.setObjectName(u"fftScaleYEndLab")

        self.gridLayout_3.addWidget(self.fftScaleYEndLab, 1, 5, 1, 1)

        self.fftScaleXStartEntry = QLineEdit(self.scaleFrm)
        self.fftScaleXStartEntry.setObjectName(u"fftScaleXStartEntry")
        sizePolicy3.setHeightForWidth(self.fftScaleXStartEntry.sizePolicy().hasHeightForWidth())
        self.fftScaleXStartEntry.setSizePolicy(sizePolicy3)
        self.fftScaleXStartEntry.setAcceptDrops(False)

        self.gridLayout_3.addWidget(self.fftScaleXStartEntry, 0, 3, 1, 1)

        self.label_10 = QLabel(self.scaleFrm)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_3.addWidget(self.label_10, 0, 4, 1, 1)

        self.label_11 = QLabel(self.scaleFrm)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_3.addWidget(self.label_11, 1, 4, 1, 1)

        self.label_12 = QLabel(self.scaleFrm)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_3.addWidget(self.label_12, 2, 4, 1, 1)


        self.verticalLayout_3.addWidget(self.scaleFrm)

        self.frame = QFrame(self.scrollAreaWidgetContents)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_7 = QGridLayout(self.frame)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setContentsMargins(-1, 6, -1, 6)
        self.stationFilterEntry = QLineEdit(self.frame)
        self.stationFilterEntry.setObjectName(u"stationFilterEntry")

        self.gridLayout_7.addWidget(self.stationFilterEntry, 0, 9, 1, 1)

        self.snFilterLab = QLabel(self.frame)
        self.snFilterLab.setObjectName(u"snFilterLab")

        self.gridLayout_7.addWidget(self.snFilterLab, 0, 5, 1, 1)

        self.stationFilterLab = QLabel(self.frame)
        self.stationFilterLab.setObjectName(u"stationFilterLab")

        self.gridLayout_7.addWidget(self.stationFilterLab, 0, 8, 1, 1)

        self.snFilterEntry = QLineEdit(self.frame)
        self.snFilterEntry.setObjectName(u"snFilterEntry")

        self.gridLayout_7.addWidget(self.snFilterEntry, 0, 6, 1, 1)

        self.itemFilterLabel = QLabel(self.frame)
        self.itemFilterLabel.setObjectName(u"itemFilterLabel")

        self.gridLayout_7.addWidget(self.itemFilterLabel, 0, 2, 1, 1)

        self.label_7 = QLabel(self.frame)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_7.addWidget(self.label_7, 0, 1, 1, 1)

        self.refreshDataBtn = QPushButton(self.frame)
        self.refreshDataBtn.setObjectName(u"refreshDataBtn")

        self.gridLayout_7.addWidget(self.refreshDataBtn, 0, 0, 1, 1)

        self.label_8 = QLabel(self.frame)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_7.addWidget(self.label_8, 0, 4, 1, 1)

        self.itemFilterEntry = QLineEdit(self.frame)
        self.itemFilterEntry.setObjectName(u"itemFilterEntry")

        self.gridLayout_7.addWidget(self.itemFilterEntry, 0, 3, 1, 1)

        self.label_9 = QLabel(self.frame)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_7.addWidget(self.label_9, 0, 7, 1, 1)


        self.verticalLayout_3.addWidget(self.frame)

        self.refreshFrm = QFrame(self.scrollAreaWidgetContents)
        self.refreshFrm.setObjectName(u"refreshFrm")
        sizePolicy6.setHeightForWidth(self.refreshFrm.sizePolicy().hasHeightForWidth())
        self.refreshFrm.setSizePolicy(sizePolicy6)
        self.refreshFrm.setFrameShape(QFrame.Shape.NoFrame)
        self.refreshFrm.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_5 = QGridLayout(self.refreshFrm)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, -1, 0)

        self.verticalLayout_3.addWidget(self.refreshFrm)

        self.channelFrm = QFrame(self.scrollAreaWidgetContents)
        self.channelFrm.setObjectName(u"channelFrm")
        sizePolicy9 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy9.setHorizontalStretch(1)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.channelFrm.sizePolicy().hasHeightForWidth())
        self.channelFrm.setSizePolicy(sizePolicy9)
        self.channelFrm.setFrameShape(QFrame.Shape.StyledPanel)
        self.channelFrm.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_3.addWidget(self.channelFrm)

        self.goBtnFrm = QFrame(self.scrollAreaWidgetContents)
        self.goBtnFrm.setObjectName(u"goBtnFrm")
        sizePolicy5.setHeightForWidth(self.goBtnFrm.sizePolicy().hasHeightForWidth())
        self.goBtnFrm.setSizePolicy(sizePolicy5)
        self.goBtnFrm.setFrameShape(QFrame.Shape.NoFrame)
        self.goBtnFrm.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.goBtnFrm)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, -1)
        self.goBtn = QPushButton(self.goBtnFrm)
        self.goBtn.setObjectName(u"goBtn")
        sizePolicy6.setHeightForWidth(self.goBtn.sizePolicy().hasHeightForWidth())
        self.goBtn.setSizePolicy(sizePolicy6)

        self.verticalLayout_2.addWidget(self.goBtn, 0, Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout_3.addWidget(self.goBtnFrm, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.contactFrm = QFrame(self.scrollAreaWidgetContents)
        self.contactFrm.setObjectName(u"contactFrm")
        self.contactFrm.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.contactFrm.sizePolicy().hasHeightForWidth())
        self.contactFrm.setSizePolicy(sizePolicy6)
        self.contactFrm.setFrameShape(QFrame.Shape.NoFrame)
        self.contactFrm.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.contactFrm)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(6, 0, 0, 6)

        self.verticalLayout_3.addWidget(self.contactFrm, 0, Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignBottom)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.fileBrowserFrm.raise_()
        self.paramFrm.raise_()
        self.filterFrm.raise_()
        self.scaleFrm.raise_()
        self.channelFrm.raise_()
        self.keepFrm.raise_()
        self.refreshFrm.raise_()
        self.goBtnFrm.raise_()
        self.filterfFm2.raise_()
        self.contactFrm.raise_()
        self.frame.raise_()
        self.frame_3.raise_()

        self.verticalLayout.addWidget(self.scrollArea)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.action2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.filaPathLab.setText(QCoreApplication.translate("MainWindow", u"File Path", None))
#if QT_CONFIG(tooltip)
        self.fileEntry.setToolTip(QCoreApplication.translate("MainWindow", u"Drag and drop the sensor data file to tool window or click Browser", None))
#endif // QT_CONFIG(tooltip)
        self.browserBtn.setText(QCoreApplication.translate("MainWindow", u"Browser", None))
#if QT_CONFIG(tooltip)
        self.keepParamCkb.setToolTip(QCoreApplication.translate("MainWindow", u"Click me to keep parameters when change data file", None))
#endif // QT_CONFIG(tooltip)
        self.keepParamCkb.setText(QCoreApplication.translate("MainWindow", u"Keep Parameters", None))
        self.label.setText("")
        self.convertTypeComb.setItemText(0, QCoreApplication.translate("MainWindow", u"FFT", None))
        self.convertTypeComb.setItemText(1, QCoreApplication.translate("MainWindow", u"PSD", None))

        self.label_2.setText("")
        self.convertTypeLab.setText(QCoreApplication.translate("MainWindow", u"Sig convert type", None))
        self.projectLab.setText(QCoreApplication.translate("MainWindow", u"Project", None))
        self.dataTypeLab.setText(QCoreApplication.translate("MainWindow", u"Data Type", None))
        self.sensorTypeLab.setText(QCoreApplication.translate("MainWindow", u"Sensor Type", None))
        self.dataTypeComb.setItemText(0, QCoreApplication.translate("MainWindow", u"Raw Data", None))
        self.dataTypeComb.setItemText(1, QCoreApplication.translate("MainWindow", u"Tester Data", None))
        self.dataTypeComb.setItemText(2, QCoreApplication.translate("MainWindow", u"Summary Data", None))

        self.label_3.setText("")
        self.label_4.setText("")
#if QT_CONFIG(tooltip)
        self.plotNameLab.setToolTip(QCoreApplication.translate("MainWindow", u"Specify a string used as plot image name, default use sensor tpye", None))
#endif // QT_CONFIG(tooltip)
        self.plotNameLab.setText(QCoreApplication.translate("MainWindow", u"Plot Name", None))
#if QT_CONFIG(tooltip)
        self.dataDropEndEntry.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>end number of samples, -1 for the end of data</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.dataRateLab.setText(QCoreApplication.translate("MainWindow", u"Data Rate", None))
#if QT_CONFIG(tooltip)
        self.dataDropStartEntry.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>start number of samples</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.plotNameEntry.setToolTip(QCoreApplication.translate("MainWindow", u"Specify a string used as plot image name, default use sensor tpye", None))
#endif // QT_CONFIG(tooltip)
        self.gainLab.setText(QCoreApplication.translate("MainWindow", u"Gain", None))
#if QT_CONFIG(tooltip)
        self.dataDropsLab.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>specify the data to drop, e.g.: start 2, end 100, mean only visulize data from line 2 to line 100</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.dataDropsLab.setText(QCoreApplication.translate("MainWindow", u"Data Drops", None))
        self.label_5.setText("")
        self.label_6.setText("")
        self.mspFreqLab.setText(QCoreApplication.translate("MainWindow", u"Freq", None))
        self.mspChkb.setText(QCoreApplication.translate("MainWindow", u"Manual search peak", None))
#if QT_CONFIG(tooltip)
        self.hpfChkb.setToolTip(QCoreApplication.translate("MainWindow", u"b, a = butter(<order>, <freq>/(0.5x<data rate>), btype='high')\n"
"new_data = lfilter(b, a, <data>, axis=-1)\n"
"new_data = filtfilt(b, a, <data>, axis=-1)", None))
#endif // QT_CONFIG(tooltip)
        self.hpfChkb.setText(QCoreApplication.translate("MainWindow", u"High Pass Filter", None))
        self.hpfTypeComb.setItemText(0, "")
        self.hpfTypeComb.setItemText(1, QCoreApplication.translate("MainWindow", u"lfilter", None))
        self.hpfTypeComb.setItemText(2, QCoreApplication.translate("MainWindow", u"filtfilt", None))

        self.hpfFreqLab.setText(QCoreApplication.translate("MainWindow", u"Freq", None))
        self.lpfOrdLab.setText(QCoreApplication.translate("MainWindow", u"Order", None))
        self.lpfTypeLab.setText(QCoreApplication.translate("MainWindow", u"Type", None))
        self.hpfOrdLab.setText(QCoreApplication.translate("MainWindow", u"Order", None))
        self.lpfFreqLab.setText(QCoreApplication.translate("MainWindow", u"Freq", None))
#if QT_CONFIG(tooltip)
        self.lpfChkb.setToolTip(QCoreApplication.translate("MainWindow", u"b, a = butter(<order>, <freq>/(0.5x<data rate>), btype=\u2018low\u2019)\n"
"new_data = lfilter(b, a, <data>, axis=-1)\n"
"new_data = filtfilt(b, a, <data>, axis=-1)", None))
#endif // QT_CONFIG(tooltip)
        self.lpfChkb.setText(QCoreApplication.translate("MainWindow", u"Low Pass Filter", None))
        self.hpfTypeLab.setText(QCoreApplication.translate("MainWindow", u"Type", None))
        self.pfPadLad2.setText("")
        self.pfPadLab1.setText("")
        self.lpfTypeComb.setItemText(0, "")
        self.lpfTypeComb.setItemText(1, QCoreApplication.translate("MainWindow", u"lfilter", None))
        self.lpfTypeComb.setItemText(2, QCoreApplication.translate("MainWindow", u"filtfilt", None))

        self.label_16.setText("")
        self.label_17.setText("")
        self.label_18.setText("")
        self.label_19.setText("")
        self.nfPadLab2.setText("")
        self.nf3FreqLab.setText(QCoreApplication.translate("MainWindow", u"Freq", None))
        self.nfPadLab1.setText("")
        self.nf2QLab.setText(QCoreApplication.translate("MainWindow", u"Q value", None))
        self.nf1QLab.setText(QCoreApplication.translate("MainWindow", u"Q value", None))
        self.nfPadLab3.setText("")
#if QT_CONFIG(tooltip)
        self.nf3Chkb.setToolTip(QCoreApplication.translate("MainWindow", u"b1, a1 = signal.iirnotch(w0=float(<freq>), Q=float(<q value>), fs=<data rate>)\n"
"new_data = signal.lfilter(b1, a1, <data>)", None))
#endif // QT_CONFIG(tooltip)
        self.nf3Chkb.setText(QCoreApplication.translate("MainWindow", u"Notch Filter 3", None))
#if QT_CONFIG(tooltip)
        self.nf1Chkb.setToolTip(QCoreApplication.translate("MainWindow", u"b1, a1 = signal.iirnotch(w0=float(<freq>), Q=float(<q value>), fs=<data rate>)\n"
"new_data = signal.lfilter(b1, a1, <data>)", None))
#endif // QT_CONFIG(tooltip)
        self.nf1Chkb.setText(QCoreApplication.translate("MainWindow", u"Notch Filter 1", None))
#if QT_CONFIG(tooltip)
        self.nf2Chkb.setToolTip(QCoreApplication.translate("MainWindow", u"b1, a1 = signal.iirnotch(w0=float(<freq>), Q=float(<q value>), fs=<data rate>)\n"
"new_data = signal.lfilter(b1, a1, <data>)", None))
#endif // QT_CONFIG(tooltip)
        self.nf2Chkb.setText(QCoreApplication.translate("MainWindow", u"Notch Filter 2", None))
        self.nf1FreqLab.setText(QCoreApplication.translate("MainWindow", u"Freq", None))
        self.nf3QLab.setText(QCoreApplication.translate("MainWindow", u"Q value", None))
        self.nf2FreqLab.setText(QCoreApplication.translate("MainWindow", u"Freq", None))
        self.label_13.setText("")
        self.label_14.setText("")
        self.label_15.setText("")
        self.summPlotLimitLowerLab.setText(QCoreApplication.translate("MainWindow", u"Lower", None))
        self.fftScaleYStartLab.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.fftScaleXChkb.setText(QCoreApplication.translate("MainWindow", u"FFT Scale(X-axis)", None))
        self.fftPadLab2.setText("")
        self.summPlotLimitChkb.setText(QCoreApplication.translate("MainWindow", u"Summary Plot Scale(Y-axis)", None))
        self.summPlotLimitUpperLab.setText(QCoreApplication.translate("MainWindow", u"Upper", None))
        self.fftPadLab1.setText("")
        self.fftScaleXStartLab.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.fftScaleXEndLab.setText(QCoreApplication.translate("MainWindow", u"End", None))
        self.fftScaleYChkb.setText(QCoreApplication.translate("MainWindow", u"FFT Scale(Y-axis)", None))
        self.fftScaleYEndLab.setText(QCoreApplication.translate("MainWindow", u"End", None))
        self.label_10.setText("")
        self.label_11.setText("")
        self.label_12.setText("")
        self.snFilterLab.setText(QCoreApplication.translate("MainWindow", u"SN Filter", None))
        self.stationFilterLab.setText(QCoreApplication.translate("MainWindow", u"Station Filter", None))
#if QT_CONFIG(tooltip)
        self.itemFilterLabel.setToolTip(QCoreApplication.translate("MainWindow", u"regular expression to fliter the items when press \"ENTER\" key or press \"Refresh\" button:\n"
"e.g. (?i)emg.*ch03.*noise: this regexp will search items which:\n"
"1. ignores case (?i) \n"
"2. and include \"emg\"\n"
"3. and then follows with any number of characters \n"
"3. and then follows with \"ch03\"\n"
"4. and then follows with any number of characters \n"
"5. and then follows with \"noise\"", None))
#endif // QT_CONFIG(tooltip)
        self.itemFilterLabel.setText(QCoreApplication.translate("MainWindow", u"Item Filter", None))
        self.label_7.setText("")
#if QT_CONFIG(tooltip)
        self.refreshDataBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Click me to refresh the items' checkbox", None))
#endif // QT_CONFIG(tooltip)
        self.refreshDataBtn.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.label_8.setText("")
#if QT_CONFIG(tooltip)
        self.itemFilterEntry.setToolTip(QCoreApplication.translate("MainWindow", u"regular expression to fliter the items when press \"ENTER\" key or press \"Refresh\" button:\n"
"e.g. (?i)emg.*ch03.*noise: this regexp will search items which:\n"
"1. ignores case (?i) \n"
"2. and include \"emg\"\n"
"3. and then follows with any number of characters \n"
"3. and then follows with \"ch03\"\n"
"4. and then follows with any number of characters \n"
"5. and then follows with \"noise\"", None))
#endif // QT_CONFIG(tooltip)
        self.label_9.setText("")
        self.goBtn.setText(QCoreApplication.translate("MainWindow", u"GO", None))
    # retranslateUi

