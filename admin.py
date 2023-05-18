import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import mysql.connector
import mimetypes
import bcrypt
import handle_image

from PyQt5.uic import loadUiType
ui,_=loadUiType('admin_design.ui')

dbname = 'election_database'
regex_integer = QRegExp("[0-9_]+")
validator_integer = QRegExpValidator(regex_integer)

cont_no = QRegExp("[9][8]+[0-9_]+")
contact_no = QRegExpValidator(cont_no)

regex_text = QRegExp("[a-zA-Z_]+( )[a-zA-Z_]+( )[a-zA-Z_]+")
validator_text = QRegExpValidator(regex_text)

class Mainapp_admin(QMainWindow, ui):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Handle_Admin_UI()
        self.Handle_Admin_Buttons() 
        self.Handle_Party_ComboBox()

    def Handle_Admin_Buttons(self):
        #handle Login window
        self.pushButton_5.clicked.connect(self.Open_Login_Window)
        #open main tab
        self.pushButton_6.clicked.connect(self.Open_Main_Window)
        self.pushButton_13.clicked.connect(self.Open_Main_Window)
        self.pushButton_16.clicked.connect(self.Open_Main_Window)
        self.pushButton_17.clicked.connect(self.Open_Main_Window)
        self.pushButton_18.clicked.connect(self.Open_Main_Window)
        #open respective tab
        self.pushButton.clicked.connect(self.Open_Candidate_Registration)
        self.pushButton_3.clicked.connect(self.Open_Party_Registration_Tab)
        self.pushButton_4.clicked.connect(self.Open_Party_Modification_Tab)
        self.pushButton_2.clicked.connect(self.Open_Staff_Tab)
        self.pushButton_11.clicked.connect(self.Open_Admin_Tab)

        #Candidate Registration Operation
        self.pushButton_8.clicked.connect(self.Verify_Candidate)
        self.pushButton_12.clicked.connect(self.Display_Candidate)
        self.pushButton_7.clicked.connect(self.Register_Candidate)
        #Party Registration Operation
        self.pushButton_10.clicked.connect(self.Register_Party)
        self.pushButton_9.clicked.connect(self.Register_Party)

        #add staffs
        self.pushButton_14.clicked.connect(self.Add_Staff)
        self.pushButton_15.clicked.connect(self.Add_Admin)

        self.tableWidget.selectionModel().selectionChanged.connect(self.On_SelectionChanged)
        self.tableWidget_3.selectionModel().selectionChanged.connect(self.On_SelectionChanged)
        self.tableWidget_2.selectionModel().selectionChanged.connect(self.On_SelectionChanged_Party_Delete)
        self.tableWidget_2.selectionModel().selectionChanged.connect(self.On_SelectionChanged_Party_Modify)

        self.pushButton_19.clicked.connect(self.Open_File_Browser)
        self.pushButton_20.clicked.connect(self.Open_File_Browser)


    def Handle_Admin_UI(self):
        self.tabWidget.setCurrentIndex(0)

        #hide tabBars
        self.tabWidget.tabBar().setVisible(False)
        #hide buttons
        self.pushButton_12.setEnabled(False)
        self.pushButton_7.setEnabled(False)

        #disable party comboBox
        self.comboBox.setEnabled(False)

        self.pushButton_3.setToolTip("Party Registration")
        self.pushButton.setToolTip("Candidate Registration")
        self.pushButton_4.setToolTip("Party Modification")
        self.pushButton_2.setToolTip("Staff Settings")
        self.pushButton_11.setToolTip("Admin Settings")

    def Open_File_Browser(self):
        fname=QFileDialog.getOpenFileName(None, 'Open file', '.',  str("Images (*.png *.xpm *.jpg)"))
        if(self.tabWidget.currentIndex()==2):
            self.label_39.setText(str(fname[0]))
        if(self.tabWidget.currentIndex()==3):
            self.label_47.setText(str(fname[0]))        

    def Handle_Party_ComboBox(self):
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = '''SELECT political_party FROM political_party'''
            self.cur.execute(sql)
            party_name = self.cur.fetchall()

            for data in party_name:
                self.comboBox.addItem(data[0])
            
            self.cur.close()
            self.database.close()
        
    def Clear_Registration(self):
        self.label_5.clear()
        self.label_7.clear()
        self.label_11.clear()
        self.label_9.clear()
        self.label_15.clear()
        self.lineEdit.clear()
        self.label_13.clear()
    

    def Open_Candidate_Registration(self):
        self.label_13.clear()
        self.comboBox.setEnabled(False)
        self.lineEdit.setValidator(validator_integer)
        self.Clear_Registration()
        # self.Disable_Registration()
        self.tabWidget.setCurrentIndex(1)


    def Verify_Candidate(self):
        self.label_13.clear()
        # self.Disable_Registration()

        voter = False
        voterId = str(self.lineEdit.text())
        if(len(voterId) == 0):
            self.label_13.setText("Please Enter Voter ID no")
            return
        else:
            voterId = int(voterId)

        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            #validate citizenships
            sql_voterId = '''SELECT voter_id FROM voter_details'''
            self.cur.execute(sql_voterId)
            result_voterId = self.cur.fetchall()

            for data in result_voterId:
                if voterId == data[0]:
                    voter = True        

            if voter:
                self.label_25.setText("Available")
                self.pushButton_12.setEnabled(True)
                
            else:
                self.label_25.setText("Unavailable")
                self.Clear_Registration()

            self.cur.close()
            self.database.close()
    
    def Display_Candidate(self):
        voterId = int(self.lineEdit.text())
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            #validate citizenships
            sql_voterId = '''SELECT name,province,district,local_body,election_area FROM voter_details WHERE voter_id = %s'''
            self.cur.execute(sql_voterId,(voterId,))
            result_candidate = self.cur.fetchone()

            name = str(result_candidate[0])
            province = str(result_candidate[1])
            district = str(result_candidate[2])
            local_body = str(result_candidate[3])
            election_area = str(result_candidate[4])

            self.label_5.setText(name)
            self.label_7.setText(province)
            self.label_9.setText(local_body)
            self.label_11.setText(district)
            self.label_15.setText(election_area)
        
        
        self.comboBox.setEnabled(True)
        self.pushButton_7.setEnabled(True)
        self.cur.close()
        self.database.close()
                 
    def Register_Candidate(self):
        name = str(self.label_5.text())
        district = str(self.label_11.text())
        election_area = int(self.label_15.text())
        party_name = str(self.comboBox.currentText())
        voter_id = int(self.lineEdit.text())
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql4 = '''SELECT COUNT(candidate_id) FROM candidate WHERE voter_id = %s'''
            self.cur.execute(sql4,(voter_id,))
            result = self.cur.fetchone()
            if int(result[0]) == 1:
                self.label_13.setText("You have already been registered.")
                return
            #validate candidate is single in a voting area
            sql1 = '''SELECT count(candidate_id) FROM candidate WHERE political_party = %s and district = %s and election_area = %s'''
            self.cur.execute(sql1,(party_name,district,election_area,))
            result = self.cur.fetchone()
            if int(result[0])==1:
                self.label_13.setText("Already Registered From Respective Political Party")
                return
            else:
                sql2 = '''INSERT INTO candidate(name,political_party,district,election_area,voter_id) VALUES(%s,%s,%s,%s,%s)'''
                self.cur.execute(sql2,(name,party_name,district,election_area,voter_id))
                self.database.commit()
                self.statusBar().showMessage("Candidate Registration Successful.")

                sql3 = '''SELECT candidate_id FROM candidate WHERE name = %s and political_party = %s 
                            and district = %s and election_area = %s'''
                self.cur.execute(sql3,(name,party_name,district,election_area,))
                candidate_id = self.cur.fetchone()
                message_box = QMessageBox(self)
                message_box.setText("Candidate ID :" + str(candidate_id[0]))
                message_box.setWindowTitle("Candidate Registration")
                message_box.setFont(QFont("Segeo UI",14))
                message_box.setIcon(QMessageBox.Information)
                message_box.exec_()      
                self.Open_Candidate_Registration()             
            self.cur.close()
            self.database.close()

    def Open_Party_Registration_Tab(self):
        self.lineEdit_4.setValidator(validator_text)
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        self.label_39.setText("Browse")
        self.label_28.clear()
        self.tabWidget.setCurrentIndex(2)

    def Register_Party(self):
        party = str(self.lineEdit_2.text())
        headoffice = str(self.lineEdit_3.text())
        president = str(self.lineEdit_4.text())
        path = str(self.label_39.text())
        voteCount = int(0)

        if(self.tabWidget.currentIndex() == 3):
            party = self.lineEdit_6.text()
            headoffice = self.lineEdit_7.text()
            president = self.lineEdit_8.text()
            path = self.label_47.text()

        if( len(party)==0 or len(headoffice)==0 or len(president)==0):
            self.label_28.setText("*All field required.")
            return

        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = '''INSERT INTO political_party(political_party,headoffice,president,vote_Count) VALUES (%s,%s,%s,%s)'''
            self.cur.execute(sql,(party,headoffice,president,voteCount))
            self.database.commit()
            sql = '''INSERT INTO party_symbol(political_party) VALUES (%s)'''
            self.cur.execute(sql,(party,))
            self.database.commit()
            self.cur.close()
            self.database.close()
            handle_image.insertBlob(party, path)
            handle_image.readBlob(party)
            self.statusBar().showMessage("Party Registration Successful.")
            self.lineEdit_2.clear()
            self.lineEdit_3.clear()
            self.lineEdit_4.clear()
            self.lineEdit_6.clear()
            self.lineEdit_7.clear()
            self.lineEdit_8.clear()
            self.label_39.setText("Browse Photo")
            self.label_28.clear()
            self.label_47.setText("Browse Photo")
            self.tableWidget_2.clearContents()
            self.Display_Party_inTableWidget()


    def Display_Party_inTableWidget(self):
        self.tableWidget_2.setRowCount(0)
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = '''SELECT political_party,headoffice,president, mime_type FROM political_party NATURAL JOIN party_symbol'''
            self.cur.execute(sql)
            result_party = self.cur.fetchall()
            i = 0 
            table = self.tableWidget_2
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            for data in result_party:
                table.insertRow(i)
                table.setRowHeight(i,100)
                pushbutton1 = QPushButton(table)
                pushbutton1.setText(str(data[0]))
                pushbutton2 = QPushButton(table)
                pushbutton2.setText(str(data[1]))
                pushbutton3 = QPushButton(table)
                pushbutton3.setText(str(data[2]))
                pushbutton4 = QPushButton(table)
                pushbutton4.setIcon(QIcon("icons/{0}{1}".format(data[0], mimetypes.guess_extension(data[3]))))
                pushbutton4.setIconSize(QSize(40,100))
                pushbutton5 = QPushButton(table)
                pushbutton5.setIcon(QIcon("icons/delete.png"))
                pushbutton5.setIconSize(QSize(40,100))
                pushbutton6 = QPushButton(table)
                pushbutton6.setIcon(QIcon("icons/party_modify.png"))
                pushbutton6.setIconSize(QSize(40,100))

                table.setCellWidget(i,0,pushbutton1)
                table.setCellWidget(i,1,pushbutton2)
                table.setCellWidget(i,2,pushbutton3)
                table.setCellWidget(i,3,pushbutton4)
                table.setCellWidget(i,4,pushbutton5)
                table.setCellWidget(i,5,pushbutton6)


    def Open_Party_Modification_Tab(self):
        self.lineEdit_6.setValidator(validator_text)
        self.lineEdit_7.setValidator(validator_text)
        self.lineEdit_8.setValidator(validator_text)
        self.Clear_Party_Modification()
        self.Disable_Party_Modification()
        self.Display_Party_inTableWidget()
        self.tabWidget.setCurrentIndex(3)
    
    def Clear_Party_Modification(self):
        self.lineEdit_6.clear()
        self.lineEdit_7.clear()
        self.lineEdit_8.clear()

    def Disable_Party_Modification(self):
        self.lineEdit_6.setEnabled(False)
        self.lineEdit_7.setEnabled(False)
        self.lineEdit_8.setEnabled(False)
        self.pushButton_20.setEnabled(False)
        self.pushButton_9.setEnabled(False)
    
    def Enable_Party_Modification(self):
        self.lineEdit_6.setEnabled(True)
        self.lineEdit_7.setEnabled(True)
        self.lineEdit_8.setEnabled(True)
        self.pushButton_9.setEnabled(True)
        self.pushButton_20.setEnabled(True)

    def Open_Staff_Tab(self):
        self.lineEdit_15.setValidator(validator_text)
        self.lineEdit_16.setValidator(validator_text)
        self.lineEdit_17.setValidator(validator_text)
        self.lineEdit_18.setValidator(validator_text)
        self.label_37.clear()
        self.lineEdit_15.clear()
        self.lineEdit_16.clear()
        self.lineEdit_17.clear()
        self.lineEdit_18.clear()
        self.Staff_Table()
        self.tabWidget.setCurrentIndex(4)
    
    def Add_Staff(self):
        name = str(self.lineEdit_15.text())
        username = str(self.lineEdit_16.text())
        password = str(self.lineEdit_17.text())
        password_again = str(self.lineEdit_18.text())
        admin = str(self.label_26.text())

        if ( len(name) == 0 or len(username) == 0 or len(password) == 0 or len(password_again) == 0):
            self.label_37.setText("* All Field Required.")
        elif( not password == password_again):
            self.label_37.setText("Password doesn't match")
        else:
            try:
                self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
                self.cur = self.database.cursor()           
            except mysql.connector.Error as err:
                self.statusBar().showMessage("Database Connectivity Error")
            else:
                sql_fetch = '''SELECT id from admin WHERE username = %s'''
                self.cur.execute(sql_fetch,(admin,))
                result = self.cur.fetchone()
                admin_id = int(result[0])

                sql_insert = '''INSERT INTO staff(name,username,password,admin) VALUES(%s,%s,%s,%s)'''
                self.cur.execute(sql_insert,(name,username,bcrypt.hashpw(password.encode(), bcrypt.gensalt()),admin_id,))
                self.database.commit()
                self.statusBar().showMessage("New staff user added.")
                self.Clear_Staff()
                self.Staff_Table()
                self.cur.close()
                self.database.close()

    def Clear_Staff(self):
        self.lineEdit_15.clear()
        self.lineEdit_16.clear()  
        self.lineEdit_17.clear()  
        self.lineEdit_18.clear() 
        self.label_37.clear()  
    
    def Staff_Table(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table = self.tableWidget
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = "SELECT id,name,admin FROM staff"
            self.cur.execute(sql)
            result = self.cur.fetchall()
            i = 0 
            for data in result:
                table.insertRow(i)
                pushbutton1 = QPushButton(table)
                pushbutton1.setText(str(data[0]))
                pushbutton2 = QPushButton(table)
                pushbutton2.setText(str(data[1]))
                pushbutton3 = QPushButton(table)
                pushbutton3.setText(str(data[2]))
                pushbutton4 = QPushButton(table)
                pushbutton4.setIcon(QIcon("icons/delete.png"))
                pushbutton4.setIconSize(QSize(40,40))

                self.tableWidget.setCellWidget(i,0,pushbutton1)
                self.tableWidget.setCellWidget(i,1,pushbutton2)
                self.tableWidget.setCellWidget(i,2,pushbutton3)
                self.tableWidget.setCellWidget(i,3,pushbutton4)

                table.setRowHeight(i,40)
                i = i + 1
        
            self.cur.close()
            self.database.close()
    
    def On_SelectionChanged(self,selected):
        sql = '''DELETE  FROM staff WHERE id = %s'''
        table = self.tableWidget      
        if ( int(self.tabWidget.currentIndex()) == 5 ):
            sql = '''DELETE  FROM admin WHERE id = %s'''
            table = self.tableWidget_3
        for ix in selected.indexes():   
            if (ix.column() == 3):
                try:
                    self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
                    self.cur = self.database.cursor()           
                except mysql.connector.Error as err:
                    self.statusBar().showMessage("Database Connectivity Error")
                else:
                    id = int(table.cellWidget(int(ix.row()),0).text())
                    self.cur.execute(sql,(id,))
                    self.database.commit()
                    table.clearContents()
                    if ( int(self.tabWidget.currentIndex()) == 4 ):
                        self.Staff_Table()
                    if ( int(self.tabWidget.currentIndex()) == 5 ):
                        self.Admin_Table()
                    self.cur.close()
                    self.database.close()

    def On_SelectionChanged_Party_Delete(self,selected):
        table = self.tableWidget_2
        for ix in selected.indexes():
            if (ix.column() == 4):
                try:
                    self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
                    self.cur = self.database.cursor()           
                except mysql.connector.Error as err:
                    self.statusBar().showMessage("Database Connectivity Error")
                else:
                    party = str(table.cellWidget(int(ix.row()),0).text())
                    sql = '''DELETE  FROM party_symbol WHERE political_party = %s'''
                    self.cur.execute(sql,(party,))
                    self.database.commit()
                    sql = '''DELETE  FROM political_party WHERE political_party = %s'''
                    self.cur.execute(sql,(party,))
                    self.database.commit()
                    table.clearContents()
                    self.Display_Party_inTableWidget()
    
    def On_SelectionChanged_Party_Modify(self,selected):
        table = self.tableWidget_2
        for ix in selected.indexes():   
            if (ix.column() == 5):
                try:
                    self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
                    self.cur = self.database.cursor()           
                except mysql.connector.Error as err:
                    self.statusBar().showMessage("Database Connectivity Error")
                else:
                    self.Enable_Party_Modification()
                    party = str(table.cellWidget(int(ix.row()),0).text())
                    sql = '''DELETE  FROM party_symbol WHERE political_party = %s'''
                    self.cur.execute(sql,(party,))
                    self.database.commit()
                    sql = '''DELETE  FROM political_party WHERE political_party = %s'''
                    self.cur.execute(sql,(party,))
                    self.database.commit()
                    self.cur.close()
                    self.database.close()
              

    def Open_Admin_Tab(self):
        self.lineEdit_19.setValidator(validator_text)
        self.lineEdit_20.setValidator(validator_text)
        self.lineEdit_21.setValidator(validator_text)
        self.lineEdit_22.setValidator(validator_text)
        self.lineEdit_19.clear()
        self.lineEdit_20.clear()
        self.lineEdit_21.clear()
        self.lineEdit_22.clear()
        self.label_38.clear()
        self.Admin_Table()
        self.tabWidget.setCurrentIndex(5)
    
    def Clear_Admin(self):
        self.lineEdit_19.clear()
        self.lineEdit_20.clear()  
        self.lineEdit_21.clear()  
        self.lineEdit_22.clear()
        self.label_38.clear()

    def Add_Admin(self):
        name = str(self.lineEdit_19.text())
        username = str(self.lineEdit_20.text())
        password = str(self.lineEdit_21.text())
        password_again = str(self.lineEdit_22.text())
        admin = str(self.label_27.text())

        if ( len(name) == 0 or len(username) == 0 or len(password) == 0 or len(password_again) == 0):
            self.label_38.setText("* All Field Required")
        elif( not password == password_again):
            self.label_38.setText("Password doesn't match")
        else:
            try:
                self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
                self.cur = self.database.cursor()           
            except mysql.connector.Error as err:
                self.statusBar().showMessage("Database Connectivity Error")
            else:
                sql_fetch = '''SELECT id from admin WHERE username = %s'''
                self.cur.execute(sql_fetch,(admin,))
                result = self.cur.fetchone()
                admin_id = int(result[0])
        
                sql_insert = '''INSERT INTO admin(name,username,password,admin) VALUES(%s,%s,%s,%s)'''
                self.cur.execute(sql_insert,(name,username,bcrypt.hashpw(password.encode(), bcrypt.gensalt()),admin_id,))
                self.database.commit()
                self.statusBar().showMessage("New admin user added.")
                self.Clear_Admin()
                self.Admin_Table()
                self.cur.close()
                self.database.close()

    def Admin_Table(self):
        self.tableWidget_3.clearContents()
        self.tableWidget_3.setRowCount(0)
        self.tableWidget_3.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table = self.tableWidget_3
        try:
            self.database = mysql.connector.connect( host='localhost',user='root',password='',database = dbname)
            self.cur = self.database.cursor()           
        except mysql.connector.Error as err:
            self.statusBar().showMessage("Database Connectivity Error")
        else:
            sql = "SELECT id,name,admin FROM admin"
            self.cur.execute(sql)
            result = self.cur.fetchall()
            i = 0 
            for data in result:
                table.insertRow(i)
                pushbutton1 = QPushButton(table)
                pushbutton1.setText(str(data[0]))
                pushbutton2 = QPushButton(table)
                pushbutton2.setText(str(data[1]))
                pushbutton3 = QPushButton(table)
                pushbutton3.setText(str(data[2]))
                pushbutton4 = QPushButton(table)
                pushbutton4.setIcon(QIcon("icons/delete.png"))
                pushbutton4.setIconSize(QSize(40,40))
        
                table.setCellWidget(i,0,pushbutton1)
                table.setCellWidget(i,1,pushbutton2)
                table.setCellWidget(i,2,pushbutton3)
                table.setCellWidget(i,3,pushbutton4)

                table.setRowHeight(i,40)
                i = i + 1
        
            self.cur.close()
            self.database.close()

    def Open_Main_Window(self):
        self.tabWidget.setCurrentIndex(0)
    
    def Open_Login_Window(self):
        from Bmvs_login import Login
        self.LoginWindow = Login()
        self.close()
        self.LoginWindow.show()

