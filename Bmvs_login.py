from PyQt5.QtWidgets import *

import mysql.connector
import bcrypt

from staff_2 import Mainapp_staff
from admin import Mainapp_admin

from PyQt5.uic import loadUiType
login,_=loadUiType('login_window.ui')
dbname = "election_database"

class Login(QWidget, login):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)

        ### Handle login when login button clicked####################
        self.pushButton_3.clicked.connect(self.Handle_Login)
        #############################################################

    def Handle_Login(self):  
        ############### Take username and password#########################
        username = self.lineEdit_2.text()
        password = self.lineEdit.text()
        
        ########### Check if any field is empty###########################
        if ( len(username)==0 or len(password)==0 or (self.radioButton_4.isChecked()==False and self.radioButton_3.isChecked()==False)):
            self.label.setText("All Field Required")
        else:
            ####### Database Connection#######################
            try:
                self.database = mysql.connector.connect( host='localhost',user='root',password='',database=dbname)
                self.cur = self.database.cursor()           
            except mysql.connector.Error as err:
                self.label.setText("Database Connectivity Error")
            else:
                ##################For handling Admin Login###############################
                if(self.radioButton_4.isChecked()):
                    sql = '''SELECT username,password FROM admin'''
                    self.cur.execute(sql)
                    data = self.cur.fetchall()
                    for row in data:
                        if username == row[0] and bcrypt.checkpw(password.encode(), bytes(row[1])):
                            self.label.setText("Login successfull")
                            self.MainWindow = Mainapp_admin()
                            self.close()
                            self.MainWindow.showMaximized()
                            self.MainWindow.show()
                            self.MainWindow.label_2.setText(username)
                            self.MainWindow.label.setText(username)
                            self.MainWindow.label_12.setText(username)
                            self.MainWindow.label_24.setText(username)
                            self.MainWindow.label_26.setText(username)
                            self.MainWindow.label_27.setText(username)
                            break
                    else:
                            self.label.setText("No Login found")
                    
                if(self.radioButton_3.isChecked()):
                    #####################For handling Staff Login###########################
                    sql = '''SELECT username,password FROM staff'''
                    self.cur.execute(sql)
                    data = self.cur.fetchall()
                    for row in data:
                        if username == row[0] and bcrypt.checkpw(password.encode(), bytes(row[1])):
                            self.label.setText("Login successfull")
                            self.MainWindow = Mainapp_staff()
                            self.close()
                            self.MainWindow.showMaximized()
                            self.MainWindow.show()
                            self.MainWindow.label_62.setText(username)
                            self.MainWindow.label_67.setText(username)
                            self.MainWindow.label_69.setText(username)
                            self.MainWindow.label_65.setText(username)
                            self.MainWindow.label.setText(username)
                            break
                    else:
                        self.label.setText("No Login found")
                self.cur.close()
                self.database.close()        

