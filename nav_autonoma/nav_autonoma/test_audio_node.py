#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import subprocess
import os

class SimpleAudioNode(Node):
    def __init__(self):
        super().__init__('test_audio_node')
        
        # Parámetro para el archivo de audio
        self.declare_parameter('audio_file', '/home/orangepi/sound_ia/test_eleven.mp3')
        self.audio_file = self.get_parameter('audio_file').value
        
        # Verificar que el archivo existe
        if not os.path.exists(self.audio_file):
            self.get_logger().error(f'❌ Archivo de audio no encontrado: {self.audio_file}')
            return
        
        self.get_logger().info(f'🎵 Iniciando reproducción de: {self.audio_file}')
        
        # Reproducir el audio
        self.play_audio()
        
        self.get_logger().info('✅ Nodo de audio inicializado. Presiona Ctrl+C para detener.')

    def play_audio(self):
        """Reproduce el audio continuamente"""
        while True:
            try:
                # Comando que sabemos funciona
                cmd = f"mpg321 -o alsa -a plughw:3,0 '{self.audio_file}'"
                
                # Ejecutar el proceso de audio
                self.audio_process = subprocess.Popen(
                    cmd, 
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                self.get_logger().info('🔊 Audio reproducido exitosamente')
                
            except Exception as e:
                self.get_logger().error(f'❌ Error reproduciendo audio: {str(e)}')

    def destroy_node(self):
        """Limpia recursos al destruir el nodo"""
        self.get_logger().info('🛑 Deteniendo reproducción...')
        
        if hasattr(self, 'audio_process') and self.audio_process:
            self.audio_process.terminate()
            self.audio_process.wait()
        
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    
    node = SimpleAudioNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('👋 Interrupción por teclado recibida')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()