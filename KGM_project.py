from PyQt5.QtWidgets import *
from KGM_python import Ui_MainWindow
import subprocess
import psycopg2
import configparser
import os

class kgm_project(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton_koUuidAl.setEnabled(False)
        self.ui.lineEdit_koUUID.setEnabled(False)
        self.ui.radioButton_koBuCihazIcin.clicked.connect(self.rdButtonControl)
        self.ui.radioButton_koFarkliBirCihazIcin.clicked.connect(self.rdButtonControl)
        self.ui.pushButton_koUuidAl.clicked.connect(self.getUUID)
        self.ui.pushButton_koKayitOlustur.clicked.connect(self.buttonKayitOlustur)
        self.ui.pushButton_bbSorgula.clicked.connect(self.buttonSorgula)
        self.ui.radioButton_BuCihazIcin.clicked.connect(self.rdButtonControl)
        self.ui.radioButton_FarkliBirCihazIcin.clicked.connect(self.rdButtonControl)
        self.ui.pushButton_TalepFormuEkle.clicked.connect(self.buttonTalepFormuEkle)
        self.ui.pushButton_UUID.clicked.connect(self.getUUID)
        self.ui.lineEdit_Sicil_BuCihazIcin.setEnabled(False)
        self.ui.pushButton_UUID.setEnabled(False)
        self.ui.lineEdit_UUID_BuCihazIcin.setEnabled(False)
        self.ui.lineEdit_Sicil_FarkliBirCihazIcin.setEnabled(False)
        self.ui.lineEdit_UUID_FarkliBirCihazIcin.setEnabled(False)
        self.ui.pushButton_TalepFormuEkle.setEnabled(False)
        self.ui.pushButton_BelgeyiKaydet.setEnabled(False)

    def sicilKontrol(self, sicilNo):
        if sicilNo.isdigit() is False:  # Sicil rakamlardan oluşuyor.
            QMessageBox.information(self, "Uyarı", "Sicil numarasını doğru girdiğinizden emin olun!")
            return False
        else:
            sicilNoIlkDortHane = sicilNo[0]
            sicilNoIlkDortHane += sicilNo[1]
            sicilNoIlkDortHane += sicilNo[2]
            sicilNoIlkDortHane += sicilNo[3]
            sicilNoIlkDortHane = int(sicilNoIlkDortHane)
            if (sicilNoIlkDortHane < 1923 or sicilNoIlkDortHane > 2023):  # Sicillerin ilk 4 hanesi atanılan yıl oluyor. Bunu kontrol ediyoruz
                QMessageBox.information(self, "Uyarı", "Sicil numarasını doğru girdiğinizden emin olun!")
                return False
        return True


    def buttonTalepFormuEkle(self):
        if(self.ui.radioButton_BuCihazIcin.isChecked()):
            if self.sicilKontrol(self.ui.lineEdit_Sicil_BuCihazIcin.text()) is False:
                return

        if(self.ui.radioButton_FarkliBirCihazIcin.isChecked()):
            if self.sicilKontrol(self.ui.radioButton_FarkliBirCihazIcin.text()) is False:
                return
        self.choice_path = QFileDialog.getOpenFileName(filter= '*.pdf *.docx')
        print(self.choice_path)


    def rdButtonControl(self):
        if(self.ui.radioButton_koBuCihazIcin.isChecked()):
            self.ui.pushButton_koUuidAl.setEnabled(True)
            self.ui.lineEdit_koUUID.setEnabled(True)
        if self.ui.radioButton_koFarkliBirCihazIcin.isChecked():
            self.ui.pushButton_koUuidAl.setEnabled(False)
            self.ui.lineEdit_koUUID.setEnabled(True)
    def getUUID(self):
        varb = subprocess.getstatusoutput('wmic csproduct get UUID')
        variable = varb[1]
        variable = variable.split()
        variable = str(variable[1])
        if variable == 'FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF':
            QMessageBox.information(self, "Bilgilendirme", "Cihazın Anakartı UUID için destek vermemektedir!")
        else:
            self.ui.lineEdit_koUUID.setText(variable)
    def buttonKayitOlustur(self):
        personelSicilNo = self.ui.lineEdit_koSicilNo.text()
        cihazUUID = self.ui.lineEdit_koUUID.text()
        cihazAriza = self.ui.plainTextEdit_koAriza.toPlainText()
        select_query = 'select * from kgm_personel where sicil = {}'.format(int(personelSicilNo))
        cursor.execute(select_query)
        control_variable = cursor.fetchall()
        if(len(control_variable) == 0):
            QMessageBox.information(self, "Uyarı", "Personel sicil bilgisini doğru girdiğinizden emin olunuz!")
            return

        else:
            control_variable.clear()
            select_query = 'select * from kgm_ariza where sicil = {} and onaydurumu = false'.format(int(personelSicilNo))
            cursor.execute(select_query)
            control_variable = cursor.fetchall()
            if len(control_variable) != 0:
                QMessageBox.information(self, "Uyarı", "Bu sicil numarası ile oluşturulmuş  ve henüz onaylanmamış bir "
                                                       "arıza kaydı var! Lütfen amirinizin kaydı onaylamasını "
                                                       "bekleyiniz!")
                return
        control_variable.clear()
        select_query = 'select * from kgm_personel where sicil = {} and yetkiduzeyi = 2'.format(personelSicilNo)
        cursor.execute(select_query)
        control_variable = cursor.fetchall()
        if len(control_variable) != 0:
            insert_query = "INSERT INTO kgm_ariza (sicil, cihazuuid, yapilacakislem, onaydurumu, btOnay) values (%s," \
                           "%s,%s,%s, %s)"
            inserted_values = (int(personelSicilNo), cihazUUID, cihazAriza, True, False)
            cursor.execute(insert_query, inserted_values)
        else:
            insert_query = "INSERT INTO kgm_ariza (sicil, cihazuuid, yapilacakislem, onaydurumu, btOnay) values (%s," \
                           "%s,%s,%s, %s)"
            inserted_values = (int(personelSicilNo), cihazUUID, cihazAriza, False, False)
            cursor.execute(insert_query, inserted_values)
        QMessageBox.information(self, "Uyarı", "Kayıt başarıyla eklendi! Arıza bildiriminizi onaylaması için birim "
                                               "amirinizle iletişime geçiniz")

    def buttonSorgula(self):
        personnel_registration_number = self.ui.lineEdit_bbSicilNo.text()
        personnel_password = self.ui.lineEdit_bbParola.text()
        select_query = "select yetkiduzeyi, buro from kgm_personel where sicil = {} and parola = '{}' and yetkiduzeyi " \
                       "IN (2,3)".format(personnel_registration_number, str(personnel_password))
        cursor.execute(select_query)
        control_variable = cursor.fetchall()
        if len(control_variable) != 0:
            authority_level = control_variable[0]
            personnel_unit = authority_level[1]
            authority_level = int(authority_level[0])
            if authority_level == 2:
                # select_query = "select sicil, cihazuuid, yapilacakislem, onaydurumu from kgm_ariza where "
                select_query = "select kgm_ariza.sicil, kgm_personel.adsoyad, cihazuuid, yapilacakislem, onaydurumu " \
                               "from kgm_ariza inner join kgm_personel on kgm_ariza.sicil = kgm_personel.sicil where " \
                               "buro = '{}'".format(personnel_unit)
                cursor.execute(select_query)
                control_variable = cursor.fetchall()
                if len(control_variable) != 0:
                    list_personnel = control_variable[0]
                    self.ui.plainTextEdit_bbArizalar.setPlainText('Sicil No:' + str(list_personnel[0]) + '\nAd Soyad:'
                                                                      +str(list_personnel[1])+'\n----------------------\nCihaz ID:'+
                                                                  str(list_personnel[2])+'\n----------------------\nYapılması istenen işlem:\n'+
                                                                  str(list_personnel[3])+'\n----------------------\nOnayDurumu:'+
                                                                  str(list_personnel[4]))

                    # self.ui.plainTextEdit_bbArizalar.setPlainText(list_personnel[0])

                # self.ui.plainTextEdit_bbArizalar.setPlainText(control_variable)
            if authority_level == 3:
                pass

        else:
            QMessageBox.information(self, "Uyarı", "Girilen sicil veya parola bilgisi hatalı!")


try:
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    database_name = config.get('database', 'db_name')
    host_ip = config.get('database', 'host')
    host_port = config.get('database', 'port')
    user_name = config.get('database', 'username')
    db_password = config.get('database', 'password')
    connection = psycopg2.connect(database=database_name, user=user_name, password=db_password, host=host_ip,
                                port=host_port)
    connection.autocommit = True
    cursor = connection.cursor()
    app = QApplication([])
    window = kgm_project()
    window.show()
    app.exec_()
except Exception:
    cursor.close()

