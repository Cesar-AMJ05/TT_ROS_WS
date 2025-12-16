
"""
Este archivo es para centralizar las connfiguraciones de TODO el robot
pARA PODER TENER UN CONTROL COMPLETO CON ROS2
"""

from library_opi.audio_player import AudioPlayer

class Config:

#Pagina Web
    #Ojo cambiar despues "udp://192.168.0.200:1235"
    Emisor_UDP_ADDR = "udp://192.168.0.200:1235" #"udp://192.168.1.17:1235"
    

    ROBOT_START_PROCESS = False
    ROBOT_STop_PROCESS = False
    ROBOT_UVCLAMPS_ACTIVATE = False
    ROBOT_IS_ONLINE =  False
    


    get_out_audio = '/home/orangepi/sound_ia/resource/desalojo.mp3'