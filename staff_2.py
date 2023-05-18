import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtTest

import mysql.connector

from re import *
import mimetypes

from driver import * 

from PyQt5.uic import loadUiType
ui,_=loadUiType('staff_design_2.ui')


dbname = 'election_database'

regex_integer = QRegExp("[0-9_]+")
validator_integer = QRegExpValidator(regex_integer)

cont_no = QRegExp("[9][8]+[0-9_]+")
contact_no = QRegExpValidator(cont_no)

regex_text = QRegExp("[a-zA-Z_]+( )[a-zA-Z_]+( )[a-zA-Z_]+")
validator_text = QRegExpValidator(regex_text)

class Mainapp_staff(QMainWindow, ui):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Handle_UI_Changes()
        self.Handle_Buttons()

    def Handle_UI_Changes(self):
        self.tabWidget.setCurrentIndex(0)

        #hide tab bar
        self.tabWidget.tabBar().setVisible(False)
        self.tabWidget_2.tabBar().setVisible(False)
        self.tabWidget_3.tabBar().setVisible(False)

        #disable submit buttons 
        self.pushButton_8.setEnabled(False)
        self.pushButton_6.setEnabled(False)
        self.pushButton_14.setEnabled(False)
        self.pushButton_9.setEnabled(False)

        self.label_59.hide()
        self.label_63.hide()

        self.pushButton_2.setToolTip("Voter Registration")
        self.pushButton.setToolTip("Voter Modification")
        self.pushButton_4.setToolTip("Voting Page")
        self.pushButton_3.setToolTip("Voter List")


    def Handle_Buttons(self):
        #Open specific tab
        self.pushButton_2.clicked.connect(self.Open_Voter_Registration)
        self.pushButton.clicked.connect(self.Open_Voter_Modification)
        self.pushButton_4.clicked.connect(self.Open_Voting)
        self.pushButton_3.clicked.connect(self.Open_Voter_Verification)

        #refresh
        self.pushButton_17.clicked.connect(self.Open_Voter_Verification)
        self.pushButton_13.clicked.connect(self.Open_Voter_Modification)

        #Handle back naviagation
        self.pushButton_5.clicked.connect(self.Open_Main_Tab)
        self.pushButton_11.clicked.connect(self.Open_Main_Tab)
        self.pushButton_16.clicked.connect(self.Open_Main_Tab)
        self.pushButton_21.clicked.connect(self.Open_Main_Tab)

        #open biometrics collection page
        self.pushButton_6.clicked.connect(self.Open_Voter_Registration_Biometrics)
        self.pushButton_8.clicked.connect(self.Biometrics_Registration) ### start biometrics


        #perform modification
        self.pushButton_12.clicked.connect(self.Modification)
        self.pushButton_14.clicked.connect(self.Biometrics_Verification)
        self.pushButton_15.clicked.connect(self.Update_Voter_Details)

        #perform voting
        self.pushButton_18.clicked.connect(self.Biometrics_Verification) 
        self.pushButton_19.clicked.connect(self.Party_Voting)
        self.pushButton_20.clicked.connect(self.Update_Votes)

        #perform voter's list
        self.pushButton_10.clicked.connect(self.VotersList)
        self.pushButton_9.clicked.connect(self.VotersDetail)

        #navigate back and forth between login and main app
        self.pushButton_7.clicked.connect(self.Open_Login_Window) #### navigate back to login window #####

        self.tableWidget.selectionModel().selectionChanged.connect(self.On_SelectionChanged)
        self.tableWidget_2.selectionModel().selectionChanged.connect(self.On_SelectionChanged)
    
    ####################Open Login Window#############################
    def Open_Login_Window(self):
        from Bmvs_login import Login
        self.LoginWindow = Login()
        self.close()
        self.LoginWindow.show()

    ###########open tab when push buttons are clicked##############
    def Open_Main_Tab(self):
        self.statusBar().showMessage("")
        self.tabWidget.setCurrentIndex(0)

    def Open_Voter_Registration(self):
        self.statusBar().showMessage("")
        self.tabWidget.setCurrentIndex(1)
        self.tabWidget_3.setCurrentIndex(0)

        self.label_40.clear()
        self.label_29.clear()
        self.label_38.clear()
        self.label_2.clear()
        self.label_54.clear()
        self.lineEdit_14.clear()
        self.lineEdit.clear()
        self.lineEdit_16.clear()
        self.lineEdit_17.clear()
        self.lineEdit_18.clear()
        self.lineEdit_19.clear()
        self.comboBox_8.clear()
        self.comboBox_7.clear()
        self.comboBox_9.clear()
        self.Handle_Province_ComboBox()


        self.lineEdit_14.setValidator(validator_text)
        self.lineEdit_17.setValidator(validator_text)
        self.lineEdit_19.setValidator(validator_text)

        self.lineEdit.setValidator(contact_no)
        self.lineEdit_18.setValidator(validator_integer)

    def Open_Voter_Registration_Biometrics(self):
        citizenship_repeat = False
        #collect data
        name = str(self.lineEdit_14.text())
        contact_no = self.lineEdit.text()
        if(self.radioButton_5.isChecked()):
            gender = "female"
        if(self.radioButton_6.isChecked()):
            gender = "male"
        citizenship_id = str(self.lineEdit_16.text())
        father_name = str(self.lineEdit_17.text())
        mother_name = str(self.lineEdit_19.text())
        if(self.radioButton.isChecked()):
            marital_status = "unmarried"
        if(self.radioButton_2.isChecked()):
            marital_status = "married"
        province = int(self.comboBox_9.currentText())
        district = str(self.comboBox_8.currentText())
        local_level = str(self.comboBox_7.currentText())
        ward = str(self.lineEdit_18.text())
        dob = self.dateEdit.date()
        date_of_birth = str(dob.toPyDate())
        
        #validate
        if((self.radioButton_5.isChecked()==False and self.radioButton_6.isChecked()==False and 
                self.radioButton_2.isChecked()==False and self.radioButton.isChecked()==False) or 
                len(name)==0 or len(citizenship_id)==0 or len(father_name)==0 or len(mother_name)==0 or len(ward)==0):
            self.label_40.setText("All Field Required")
        else:
             ####### Database Connection#######################
            try:
                self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
                self.cur = self.database.cursor()           
            except mysql.connector.Error as err:
                self.statusBar().showMessage("Database Connectivity Error")
            else:
                #validate citizenships
                sql_citizenship_validate = '''SELECT citizenship_no FROM voter_details'''
                self.cur.execute(sql_citizenship_validate)
                result_citizenship = self.cur.fetchall()

                for data in result_citizenship:
                    if citizenship_id == data[0]:
                        citizenship_repeat = True
                        break
                
                if citizenship_repeat:
                    self.label_40.setText("Already repeated with given Citizenship number")

                else:
                    sql_election_area = '''SELECT election_area from local_body where district = %s and local_body = %s'''
                    self.cur.execute(sql_election_area,(district,local_level,))
                    result = self.cur.fetchone()
                    voting_area = int(result[0])
                    self.label_40.setText(str(voting_area))

                    self.cur.close()
                    self.database.close()

                    self.tabWidget_3.setCurrentIndex(1)
                    self.label_29.setText(name)
                    self.label_38.setText(str(voting_area))
                    self.pushButton_8.setEnabled(True)

        
    
    def Open_Voter_Modification(self):
        self.statusBar().showMessage("")
        self.lineEdit_3.setValidator(validator_integer)
        self.lineEdit_4.setValidator(validator_text)
        self.lineEdit_7.setValidator(validator_text)
        self.lineEdit_8.setValidator(validator_text)
        self.lineEdit_5.setValidator(contact_no)
        self.lineEdit_9.setValidator(validator_integer)
        self.lineEdit_3.clear()
        self.label_52.setText("Status")
        self.pushButton_14.setEnabled(False)
        self.label_23.clear()
        self.label_55.clear()
        self.label_70.clear()
        self.Disable_Modification()
        self.Handle_Province_ComboBox()
        self.tabWidget.setCurrentIndex(2)

    def Modification(self):
        self.label_52.setText("Status")
        self.pushButton_14.setEnabled(False)
        self.label_23.clear()
        self.label_55.clear()
        self.label_70.clear()
        status = False
        # self.label_53.clear()
        voter_id = str(self.lineEdit_3.text())
        if(len(voter_id)==0):
            self.label_60.setText("Please specify Voter Id in given field.")
            return
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = '''SELECT voter_id FROM voter_details'''
            self.cur.execute(sql)
            result = self.cur.fetchall()
            voter_id = int(voter_id)
            for data in result:
                if voter_id == int(data[0]):
                    status = True
                    break
            
            if(status):
                self.label_52.setText("Available")
                self.pushButton_14.setEnabled(True)
            else:
                self.label_52.setText("Unavailable")
                self.pushButton_14.setEnabled(False)
            self.cur.close()
            self.database.close()


    
    def Enable_Modification(self):
        self.lineEdit_4.setEnabled(True)
        self.dateEdit_2.setEnabled(True)
        self.radioButton_3.setEnabled(True)
        self.radioButton_4.setEnabled(True)
        self.radioButton_7.setEnabled(True)
        self.radioButton_8.setEnabled(True)
        self.lineEdit_5.setEnabled(True)
        self.lineEdit_6.setEnabled(True)
        self.lineEdit_7.setEnabled(True)
        self.lineEdit_8.setEnabled(True)
        self.lineEdit_9.setEnabled(True)
        self.comboBox.setEnabled(True)
        self.comboBox_2.setEnabled(True)
        self.comboBox_3.setEnabled(True)

    def Disable_Modification(self):
        self.lineEdit_4.setEnabled(False)
        self.dateEdit_2.setEnabled(False)
        self.radioButton_3.setEnabled(False)
        self.radioButton_4.setEnabled(False)
        self.radioButton_7.setEnabled(False)
        self.radioButton_8.setEnabled(False)
        self.lineEdit_5.setEnabled(False)
        self.lineEdit_6.setEnabled(False)
        self.lineEdit_7.setEnabled(False)
        self.lineEdit_8.setEnabled(False)
        self.lineEdit_9.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.comboBox_2.setEnabled(False)
        self.comboBox_3.setEnabled(False)
        self.pushButton_15.setEnabled(False)

    def Update_Voter_Details(self):
        name = str(self.lineEdit_4.text())
        dob = self.dateEdit_2.date()
        date_of_birth = str(dob.toPyDate())
        if(self.radioButton_3.isChecked()):
            gender = "female"
        else:
            gender = "male"
        if(self.radioButton_7.isChecked()):
            marital_status = "unmarried"
        else:
            marital_status = "married"
        contact = int(self.lineEdit_5.text())
        citizenship = str(self.lineEdit_6.text())
        father_name = str(self.lineEdit_7.text())
        mother_name = str(self.lineEdit_8.text())
        ward = str(self.lineEdit_9.text())
        province = int(self.comboBox.currentText())
        district = str(self.comboBox_2.currentText())
        local_level = str(self.comboBox_3.currentText())

        if((self.radioButton_7.isChecked()==False and self.radioButton_8.isChecked()==False and 
                self.radioButton_3.isChecked()==False and self.radioButton_4.isChecked()==False) or 
                len(name)==0 or len(citizenship)==0 or len(father_name)==0 or len(mother_name)==0 or len(ward)==0):
            self.label_60.setText("All Field Required")
            return

        ward = int(ward)
        voter_id = int(self.lineEdit_3.text())
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = '''UPDATE voter_details SET name = %s, dob = %s, sex = %s, marital_status = %s, fathers_name = %s,
             mothers_name = %s, province = %s, district = %s, local_body = %s, ward_no = %s, citizenship_no = %s
             WHERE voter_id = %s'''
            self.cur.execute(sql,(name,date_of_birth,gender,marital_status,father_name,mother_name,province,district,local_level,ward,citizenship,voter_id,))
            self.database.commit()
            self.statusBar().showMessage("Voter details successfully modified.")
            self.cur.close()
            self.database.close()

            

    def Open_Voting(self): 
        self.statusBar().showMessage("")
        self.lineEdit_10.setValidator(validator_integer)
        self.pushButton_18.setEnabled(True)
        self.lineEdit_10.clear()
        self.label_57.clear()
        self.label_72.clear()
        self.tableWidget.clear()
        self.tableWidget_2.clear()
        self.tabWidget.setCurrentIndex(3)
        self.tabWidget_2.setCurrentIndex(0)  
        
    def DisplayCandidate(self):
        self.tableWidget.clear()
        self.tableWidget.setHorizontalHeaderItem(0,QTableWidgetItem('Candidate'))
        self.tableWidget.setHorizontalHeaderItem(1,QTableWidgetItem('Party'))
        self.tableWidget.setHorizontalHeaderItem(2,QTableWidgetItem('Symbol'))
        self.tableWidget.setHorizontalHeaderItem(3,QTableWidgetItem('Vote'))

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setRowCount(0)

        voter_id = int(self.lineEdit_10.text())
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql1 = '''SELECT district,election_area FROM voter_details WHERE voter_id = %s'''
            self.cur.execute(sql1,(voter_id,))
            result = self.cur.fetchone()
            district = str(result[0])
            election_area = int(result[1])

            sql2 = '''SELECT COUNT(*) FROM candidate WHERE district = %s and election_area = %s'''
            self.cur.execute(sql2,(district,election_area,))
            candidate_result = self.cur.fetchone()
            candidate_no = int(candidate_result[0])
            if candidate_no == 0:
                self.statusBar().showMessage("No candidate in given area")
                self.Party_Voting()
            else:
                sql3 = '''SELECT name,political_party,mime_type FROM candidate NATURAL JOIN 
                                political_party NATURAL JOIN party_symbol WHERE district = %s and election_area = %s'''
                self.cur.execute(sql3,(district,election_area,))
                candidate_list = self.cur.fetchall()
                i = 0

                for data in candidate_list:
                    self.tableWidget.insertRow(i)
                    pushbutton1 = QPushButton(self.tableWidget)
                    pushbutton1.setText(str(data[0]))
                    pushbutton2 = QPushButton(self.tableWidget)
                    pushbutton2.setText(str(data[1]))
                    pushbutton3 = QPushButton(self.tableWidget)
                    pushbutton3.setIcon(QIcon("icons/{0}{1}".format(data[1], mimetypes.guess_extension(data[2]))))
                    pushbutton3.setIconSize(QSize(160,100))

                    self.tableWidget.setCellWidget(i,0,pushbutton1)
                    self.tableWidget.setCellWidget(i,1,pushbutton2)
                    self.tableWidget.setCellWidget(i,2,pushbutton3)

                    self.tableWidget.setRowHeight(i,100)
                    i = i + 1
            self.cur.close()
            self.database.close()      
    
    def On_SelectionChanged(self,selected,deselected):
        table = self.tableWidget
        column = 2
        vote = 3
        party_candidate_name = self.label_59

        if(int(self.tabWidget_2.currentIndex())==2):
            table = self.tableWidget_2
            column = 1
            vote = 2
            party_candidate_name = self.label_63
            
        pushbutton6 = QPushButton(table)

        for ix in deselected.indexes(): 
            if(ix.column()==column):
                pushbutton6.setIcon(QIcon())
                table.setCellWidget(int(ix.row()),vote,pushbutton6)

        for ix in selected.indexes():
            if (ix.column() == column):
                pushbutton6.setIcon(QIcon("icons/vote.png"))
                pushbutton6.setIconSize(QSize(160,100))    
                table.setCellWidget(int(ix.row()),vote,pushbutton6)
                party_candidate_name.setText(str(ix.row()))

    def Party_Voting(self):
        self.tableWidget_2.clear()
        self.tableWidget_2.setHorizontalHeaderItem(0,QTableWidgetItem('Party'))
        self.tableWidget_2.setHorizontalHeaderItem(1,QTableWidgetItem('Symbol'))
        self.tableWidget_2.setHorizontalHeaderItem(2,QTableWidgetItem('Vote'))
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_2.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_2.setRowCount(0)
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = '''SELECT political_party, mime_type FROM political_party NATURAL JOIN party_symbol'''
            self.cur.execute(sql)
            party_list = self.cur.fetchall()

            i = 0
            for data in party_list:
                self.tableWidget_2.insertRow(i)
                pushbutton1 = QPushButton(self.tableWidget_2)
                pushbutton1.setText(str(data[0]))
                pushbutton2 = QPushButton(self.tableWidget_2)
                pushbutton2.setIcon(QIcon("icons/{0}{1}".format(data[0], mimetypes.guess_extension(data[1]))))
                pushbutton2.setIconSize(QSize(40,40))
                self.tableWidget_2.setCellWidget(i,0,pushbutton1)
                self.tableWidget_2.setCellWidget(i,1,pushbutton2)
                self.tableWidget_2.setRowHeight(i,100)
                i = i + 1
            self.cur.close()
            self.database.close()
            self.tabWidget_2.setCurrentIndex(2)

    def Update_Votes(self):
        position_candidate = int(self.label_59.text())
        candidate = str(self.tableWidget.cellWidget(position_candidate,0).text())
        position_party = int(self.label_63.text())
        party = str(self.tableWidget_2.cellWidget(position_party,0).text())
        voter_id = int(self.lineEdit_10.text())
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = '''UPDATE candidate SET voteCount = voteCount + 1 WHERE name = %s'''
            self.cur.execute(sql,(candidate,))
            self.database.commit()

            sql = '''UPDATE political_party SET vote_Count = vote_Count + 1 WHERE political_party = %s'''
            self.cur.execute(sql,(party,))
            self.database.commit()

            sql = '''UPDATE voter_details SET voting_status = %s WHERE voter_id = %s'''
            self.cur.execute(sql,("1",voter_id,))
            self.database.commit()     
            self.cur.close()
            self.database.close()
            message_box = QMessageBox(self)
            message_box.setText("Vote successful")
            message_box.setWindowTitle("Vote Confirmation")
            message_box.setFont(QFont("Segeo UI",14))
            message_box.setIcon(QMessageBox.Information)
            message_box.exec_()
            self.statusBar().showMessage("Vote successful")
            self.tableWidget.clearContents()
            self.tableWidget.clear()
            self.tableWidget_2.clearContents()
            self.tableWidget_2.clear()
            self.Open_Voting()
 

    def Open_Voter_Verification(self):
        self.statusBar().showMessage("")
        self.lineEdit_2.setValidator(validator_integer)
        self.label_12.setText("Status")
        self.lineEdit_2.clear()
        self.pushButton_9.setEnabled(False)
        self.label_13.clear()
        self.label_14.clear()
        self.label_15.clear()
        self.label_18.clear()
        self.label_20.clear()
        self.label_21.clear()
        self.label_51.clear()
        self.tabWidget.setCurrentIndex(4)


    def VotersList(self):
        status = False
        voter_id = str(self.lineEdit_2.text())
        if(len(voter_id)==0):
            self.label_12.setText("Specify Voter Id in given field.")
        else:
            voter_id = int(voter_id)
            self.label_12.setText("Status")
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = '''SELECT voter_id FROM voter_details'''
            self.cur.execute(sql)
            result = self.cur.fetchall()

            for data in result:
                if voter_id == int(data[0]):
                    status = True
                    break
            
            if(status):
                self.label_12.setText("Available")
                self.pushButton_9.setEnabled(True)
            else:
                self.label_12.setText("Unavailable")
                self.pushButton_9.setEnabled(False)
            self.label_13.clear()
            self.label_14.clear()
            self.label_15.clear()
            self.label_18.clear()
            self.label_20.clear()
            self.label_21.clear()
            self.label_51.clear()
            self.cur.close()
            self.database.close()
    
    def VotersDetail(self):
        voter_id = int(self.lineEdit_2.text())

        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = '''SELECT name,citizenship_no,province,district,local_body,ward_no,election_area 
                            FROM voter_details WHERE voter_id = %s'''
            self.cur.execute(sql,(voter_id,))
            result = self.cur.fetchone()

            self.label_13.setText(str(result[0]))
            self.label_14.setText(str(result[1]))
            self.label_15.setText(str(result[2]))
            self.label_18.setText(str(result[3]))
            self.label_20.setText(str(result[4]))
            self.label_21.setText(str(result[5]))
            self.label_51.setText(str(result[6]))

            self.cur.close()
            self.database.close()


    ###############################################################

    def Handle_Province_ComboBox(self):
        province = ['1','2','3','4','5','6','7']
        province_box = self.comboBox_9
        if (int(self.tabWidget.currentIndex())==1):
            province_box = self.comboBox_9
        if (int(self.tabWidget.currentIndex())==2):
            province_box = self.comboBox
        province_box.addItems(province)

        province_box.currentIndexChanged.connect(self.Handle_District_Combobox)
    
    def Handle_District_Combobox(self):
        province_box = self.comboBox_9
        district_box = self.comboBox_8
        if (int(self.tabWidget.currentIndex())==1):
            province_box = self.comboBox_9
            district_box = self.comboBox_8
        if (int(self.tabWidget.currentIndex())==2):
            province_box = self.comboBox
            district_box = self.comboBox_2

        province_no = province_box.currentText()

        try:
            self.database = mysql.connector.connect(host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = ''' SELECT district FROM district WHERE province = %s'''
            self.cur.execute(sql,(province_no,))
            districts_name = self.cur.fetchall()
            district_box.clear()
            for data in districts_name:
                district_box.addItem(data[0])
            self.cur.close()
            self.database.close()
        
        district_box.currentIndexChanged.connect(self.Handle_Local_Level_ComboBox)
    
    def Handle_Local_Level_ComboBox(self):
        local_level_box = self.comboBox_7
        district_box = self.comboBox_8
        if (int(self.tabWidget.currentIndex())==1):
            local_level_box = self.comboBox_7
            district_box = self.comboBox_8
        if (int(self.tabWidget.currentIndex())==2):
            local_level_box = self.comboBox_3
            district_box = self.comboBox_2

        district_name = district_box.currentText()

        try:
            self.database = mysql.connector.connect(host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = ''' SELECT local_body FROM local_body WHERE district = %s'''
            self.cur.execute(sql,(district_name,))
            local_level_name = self.cur.fetchall()
            local_level_box.clear()
            for data in local_level_name:
                local_level_box.addItem(data[0])
            self.cur.close()
            self.database.close()

            # set submit enabled
            if (int(self.tabWidget.currentIndex())==1):
                self.pushButton_6.setEnabled(True)
            if (int(self.tabWidget.currentIndex())==2):
                self.pushButton_15.setEnabled(True)
                
        

    def Biometrics_Registration(self):
        name = str(self.lineEdit_14.text())
        contact_no = self.lineEdit.text()
        if(self.radioButton_5.isChecked()):
            gender = "female"
        if(self.radioButton_6.isChecked()):
            gender = "male"
        citizenship_id = str(self.lineEdit_16.text())
        father_name = str(self.lineEdit_17.text())
        mother_name = str(self.lineEdit_19.text())
        if(self.radioButton.isChecked()):
            marital_status = "unmarried"
        if(self.radioButton_2.isChecked()):
            marital_status = "married"
        province = int(self.comboBox_9.currentText())
        district = str(self.comboBox_8.currentText())
        local_level = str(self.comboBox_7.currentText())
        ward = str(self.lineEdit_18.text())
        dob = self.dateEdit.date()
        date_of_birth = str(dob.toPyDate())
        voting_area = self.label_40.text()
        displayButton = self.pushButton_8
        displayLabelInstr = self.label_2
        displayLabelResult = self.label_54

        displayButton.setEnabled(False)
        displayLabelInstr.setText("Place Your Finger")
        QtTest.QTest.qWait(4000)
        p = -1
        while not p == FINGERPRINT_OK:
            try:
                p = getImage()        
            except ImageError as err:
                pass

        displayLabelInstr.setText("Image Taken")
        QtTest.QTest.qWait(1000)
        try:
            createTemplate(b'\x01')
        except TemplateCreationError as err:
            self.statusBar().showMessage(str(err))
            displayButton.setEnabled(True)
            return 
        displayLabelInstr.setText("Template Creation Successful")
        QtTest.QTest.qWait(1000)

        displayLabelInstr.setText("Remove Finger")
        QtTest.QTest.qWait(1000)
        
        while 1:
            try:
                getImage()
            except ImageError as err:
                if err.code == FINGERPRINT_NOFINGER:
                    break

        displayLabelInstr.setText("Place Your Finger Again")
        QtTest.QTest.qWait(1000)
        p = -1
        while not p == FINGERPRINT_OK:
            try:
                p = getImage()
            except ImageError as err:
                pass
            
        displayLabelInstr.setText("Image Taken")
        QtTest.QTest.qWait(1000)
        try:
            createTemplate(b'\x02')
        except TemplateCreationError as err:
            self.statusBar().showMessage(str(err))
            displayButton.setEnabled(True)
            #print(err)
            return 
        
        displayLabelInstr.setText("Template Creation Successful")
        QtTest.QTest.qWait(1000)

        try:
            createModel()
        except ModelCreationError as err:
            self.statusBar().showMessage(str(err))
            displayButton.setEnabled(True)
            return
        
        displayLabelInstr.setText("Model Creation Successful")

        charSequence = b''
        try:
            generator = downloadTemplate()
            for i in range(TEMPLATE_SIZE):
                charSequence += next(generator)
        except DownloadError as err:
            self.statusBar().showMessage(str(err))
            displayButton.setEnabled(True)
            return
        
        try:
            self.database = mysql.connector.connect(host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql_insert_details = '''INSERT INTO voter_details
                                            (name,dob,sex,marital_status,fathers_name,mothers_name,province,district,
                                            local_body,ward_no,citizenship_no,election_area)
                                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            self.cur.execute(sql_insert_details,(name,date_of_birth,gender,marital_status,father_name,mother_name,
                                                        province,district,local_level,int(ward),citizenship_id,voting_area,))
            self.database.commit()

            sql_fetch_voterid = '''SELECT voter_id from voter_details where citizenship_no = %s'''
            self.cur.execute(sql_fetch_voterid,(citizenship_id,))
            details = self.cur.fetchone()

            voterId = str(details[0])

            sql = '''UPDATE voter_details SET fingerprint = %s WHERE voter_id = %s'''
            self.cur.execute(sql,(charSequence,voterId))

            self.database.commit()
            self.cur.close()
            self.database.close()
            displayLabelResult.setText("Biometrics Collection Successful")
            message_box = QMessageBox(self)
            message_box.setText("Voter ID :" + str(voterId))
            message_box.setWindowTitle("Voter Registration")
            message_box.setFont(QFont("Segeo UI",14))
            message_box.setIcon(QMessageBox.Information)
            message_box.exec_()   
            self.Open_Voter_Registration()
        

    def Biometrics_Verification(self):
        self.label_57.clear()
        self.label_72.clear()
        voterId = self.lineEdit_3.text()
        displayButton = self.pushButton_14
        displayLabelInstr = self.label_23
        displayLabelResult_matched = self.label_55
        displayLabelResult_failed = self.label_70

        
        if (int(self.tabWidget.currentIndex())==2):
            displayButton = self.pushButton_14
            displayLabelInstr = self.label_23
            displayLabelResult_matched = self.label_55
            displayLabelResult_failed = self.label_70


        if (int(self.tabWidget.currentIndex())==3):
            if(len(str(self.lineEdit_10.text()))==0):
                self.label_57.setText("Please enter voter Id no.")
                return
            voterId = self.lineEdit_10.text()
            displayButton = self.pushButton_18
            displayLabelInstr = self.label_57
            displayLabelResult_failed = self.label_72
        
        displayButton.setEnabled(False)
        displayLabelInstr.setText("Place Your Finger")
        QtTest.QTest.qWait(4000)
        p = -1
        while not p == FINGERPRINT_OK:
            try:
                p = getImage()        
            except ImageError as err:
                pass

        displayLabelInstr.setText("Image Taken")
        QtTest.QTest.qWait(1000)
        try:
            createTemplate(b'\x01')
        except TemplateCreationError as err:
            self.statusBar().showMessage(str(err))
            displayButton.setEnabled(True)
            return 
        displayLabelInstr.setText("Template Creation Successful")
        QtTest.QTest.qWait(1000)

        displayLabelInstr.setText("Remove Finger")
        QtTest.QTest.qWait(1000)
        
        while 1:
            try:
                getImage()
            except ImageError as err:
                if err.code == FINGERPRINT_NOFINGER:
                    break
        
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error.")
        else:
            sql = '''SELECT fingerprint FROM voter_details WHERE voter_id = %s'''
            self.cur.execute(sql,(int(voterId),))
            result = self.cur.fetchone()
            fingerprint = result[0]
        try:
            uploadTemplate(fingerprint)
        except UploadError as err:
            self.statusBar.showMessage(str(err))
        else:
            displayLabelInstr.setText("Upload Successful")
        
        try:
            matchTemplate()
        except MatchingError as err:
            displayLabelInstr.clear()
            displayLabelResult_failed.setText("Not Matched")
            displayButton.setEnabled(True)
        else:
            if (int(self.tabWidget.currentIndex())==2):
                displayLabelResult_matched.setText("Matched")
                self.Enable_Modification()
            if (int(self.tabWidget.currentIndex())==3):
                sql = '''SELECT voting_status FROM voter_details WHERE voter_id = %s'''
                self.cur.execute(sql,(voterId,))
                result = self.cur.fetchone()
                if(result[0]==0):
                    self.tabWidget_2.setCurrentIndex(1)
                    self.DisplayCandidate()
                else:
                    displayLabelInstr.setText("Vote already casted from specified voter Id.")
                    displayButton.setEnabled(True)

