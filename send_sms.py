import re
import subprocess
import pathlib
import os
import time

from PyQt5.QtGui import QIcon, QValidator
from PyQt5.QtWidgets import QMessageBox, \
    QPlainTextEdit, QVBoxLayout, QHBoxLayout, QLabel, QProgressDialog, QPushButton


from maindialog import Dialog
from utilities import SendTextSMS
from utilities import connect_android_device


class SendSMSDialog(Dialog):
    cancel_sms = False

    def __init__(self, parent=None):
        super(SendSMSDialog, self).__init__(parent, titulo="Envio de SMS", imagem='img/smartphone.png')

        self.recipients = QPlainTextEdit()
        self.message = QPlainTextEdit()
        self.cell_serial_number = ""
        self.sms_time_sleep = 2

        self.message.textChanged.connect(lambda: self.conta_caracters(self.message.toPlainText()))
        self.caracteres_label = QLabel('Caracteres: 0')

        self.num_caracteres = 0

        vlay = QVBoxLayout()
        vlay.setContentsMargins(10, 10, 10, 10)
        vlay.addWidget(QLabel('Receptores (Entre contactos separados por ;)'))
        vlay.addWidget(self.recipients)
        vlay.addWidget(QLabel('Mensagem (160 Caracteres por SMS)'))
        vlay.addWidget(self.message)
        vlay.addWidget(self.caracteres_label)

        enviar = QPushButton('Enviar')
        enviar.clicked.connect(lambda: self.send_sms(self.recipients.toPlainText(), self.message.toPlainText()))
        enviar.setIcon(QIcon('img/next.png'))
        cancelar = QPushButton('Cancelar')
        cancelar.clicked.connect(self.close)
        cancelar.setIcon(QIcon('img/remove.ico'))
        conectar = QPushButton('Reconectar')
        conectar.setIcon(QIcon('img/edit.png'))
        conectar.clicked.connect(self.recconect_device)

        desconectar = QPushButton('Desconectar')
        desconectar.setIcon(QIcon('img/delete.png'))
        desconectar.clicked.connect(self.desconectar_despositivo)

        hlay = QHBoxLayout()
        hlay.addWidget(desconectar)
        hlay.addWidget(conectar)
        hlay.addStretch()
        hlay.addWidget(enviar)
        hlay.addWidget(cancelar)

        vlay.addWidget(self.add_line())
        vlay.addLayout(hlay)
        self.layout().addLayout(vlay)

        self.resize(400, 200)

    def desconectar_despositivo(self):
        # Inicia adb ou lista dispositivos
        # Caminho real do adb
        caminho = os.path.realpath("android/adb.exe")

        subprocess.run([caminho, 'kill-server'])

        time.sleep(self.sms_time_sleep)

        QMessageBox.information(self, 'Dispositivo desconectado', 'O dispositivo Android foi desconectado!')

    def recconect_device(self):
        try:
            adb_command_1 = "devices"

            # Caminho real do adb
            caminho = os.path.realpath("android/adb.exe")

            subprocess.run([caminho, adb_command_1])

            self.android_device = connect_android_device(self.cell_serial_number)

            if self.android_device is not  None:

                print(self.android_device.get_state())

                time.sleep(self.sms_time_sleep)

                QMessageBox.information(self, 'sucesso',
                                        'Dispositivo {} reconectado com sucesso!'.format(self.cell_serial_number))
            else:
                QMessageBox.warning(self, 'Sem sucesso',
                                        '''Não foi possível connectar o dispositivo.
                                        \n 1. Desconecta e reconecta o cabo USB; e
                                        \n 2. Ponha o telefone no modo MTP (Transferência dispositivo.); 
                                        \n 3. Ponha o Disposivo no modo developer e activa depuração USB.
                                        '''.format(self.cell_serial_number))
        except Exception as e:
            QMessageBox.warning(self, 'Sem sucesso',
                                    '''Não foi possível connectar o dispositivo.
                                    \n 1. Desconecta e reconecta o cabo USB; e
                                    \n 2. Ponha o telefone no modo MTP (Transferência dispositivo.)
                                    
                                    \n Erro: {}. 
                                    '''.format(e))
            return False

        return True

    def connect_android_devices(self):
        try:
            self.android_device = connect_android_device(self.cell_serial_number)

            if self.android_device is None:
                QMessageBox.warning(self, 'Sem Telefone', '''O telefone com o Serial number {} não foi encontrado.\n
                Se o telefone estiver conectado veja o seguinte:
                1. O telefone deve estar em modo de Programador (Developer mode);\n
                2. No Modo de Programador a Depuração USB deve estar activa; e\n
                3. A conexão USB deve ser 'Transferência de Ficheiro (File Transfer USB mode)'.\n\n
                Se o problema persistir contacte o suporte.
                           '''.format(self.cell_serial_number))

                return False

        except RuntimeError as e:
            QMessageBox.warning(self, 'Erro de Conexão', '''O ADB não está a correr. \n{}.
            \n Tentando Correr o ADB. \n Reabra SMS. No caso do problema persistir corra o ADB manualmente.
            '''.format(e))
            adb_command_1 = "devices"

            # Caminho real do adb
            caminho = os.path.realpath("android/adb.exe")

            # Inicia adb ou lista dispositivos
            subprocess.run([caminho, adb_command_1])

            return False
        except Exception as e:
            QMessageBox.warning(self, 'Erro', 'Erro {}.'.format(e))

            return False

        return True

    def conta_caracters(self, text: str):
        caracteres = len(text)
        num_sms = caracteres // 160 + 1

        self.caracteres_label.setText('Caracteres: {} :: {} SMS(s) por contacto.'.format(str(caracteres), num_sms))
        return num_sms

    def cancelar(self):
        self.cancel_sms = True

        return self.cancel_sms

    def send_sms(self, to: str, msg: str):
        from scripts.utilities import divide_sms

        if to == "":
            QMessageBox.warning(self, "Entre o Receptor",
                                "Entre pelomenos 1 receptor.")
            self.recipients.setFocus()

            return False

        if msg == "":
            QMessageBox.warning(self, "Entre a Mensagem",
                                "O Corpo da Mensagem não pode ser estar em branco." )
            self.message.setFocus()

            return False

        num_sms = int(self.conta_caracters(self.message.toPlainText()))
        numbers = to.split(';')

        progress = QProgressDialog(self)
        progress.setMaximum(len(numbers)*num_sms)
        progress.setModal(True)
        progress.resize(100, 50)
        progress.show()

        count = 0

        cancel_button = QPushButton('Cancelar')
        progress.setCancelButton(cancel_button)
        cancel_button.clicked.connect(self.cancelar)

        progress_label = QLabel("")
        progress.setLabel(progress_label)

        lista_sms = divide_sms(msg, 160)

        for sms in lista_sms:
            for number in numbers:
                if number != "":
                    if self.cancel_sms is True:
                        QMessageBox.warning(self, 'Cancelamento!',
                                            "Envio de SMS's cancelado!")
                        progress.close()
                        self.cancel_sms = False
                        return False

                    progress_label.setText('Enviando  SMS {} de {} para:\n{}'.format(count,
                                                                                     progress.maximum(),
                                                                                     number))
                    try:
                        # Envia sms
                        self.envia_mensagem(number, r'{}'.format(sms))

                        count += 1
                        progress.setValue(count)

                    except Exception as e:
                        QMessageBox.warning(self, 'Falha', 'Não foi possivel enviar SMS. \nErro: {}'.format(e))
                        progress.close()
                        return False

        progress.close()
        QMessageBox.information(self, 'Sucesso!', "Todas SMS's foram enviadas com Sucesso!")


    def envia_mensagem(self, numero, msg):
        '''
        Envia SMS usando Telefone Android
        O MTP MODE deve estar activo
        '''
        print(numero, ':', msg )
        service = '''service call isms  7 i32 0 s16  "com.android.mms.service"  s16 "{n}" s16  "null" s16 "{m}" s16  "null"  s16 "null"
                                '''.format(n=numero, m=msg)
        # Put device in MTP mode
        # self.android_device.shell('svc usb setFunctions mtp true')
        # Send SMS through ADB
        self.android_device.shell(service)
        # Waits some time
        time.sleep(self.sms_time_sleep)


class Validator(QValidator):
    def __init__(self, parent=None):
        super(Validator, self).__init__(parent)

        regex = "@£$¥èéùìòÇ\fØø\nÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./[0-9]:;<=>\?¡[A-Z]ÄÖÑÜ§¿[a-z]äöñüà\^\{\}\[~\]\|€"
        self._replace = re.compile(r'[{}]'.format(regex)).sub

    def validate(self, string, pos):
        string = self._replace('_', string)
        prefix = string[:3].upper()
        if len(string) > 3 and not string[3] == '_':
            prefix += '_'
            pos += 1
        string = prefix + string[3:]
        return QValidator.Acceptable, string, pos





