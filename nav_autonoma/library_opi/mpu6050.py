import wiringpi
import time
import math

class MPU6050:
    def __init__(self, address=0x68, i2cbus=2, node=None):
        self.address = address
        self.i2cbus = i2cbus
        self.node = node
        self.angular_velocity_z = 0.0
        self.angle_z = 0.0  # Ángulo integrado
        self.accel_x = 0.0
        self.accel_y = 0.0
        self.linear_velocity_x = 0.0  # Velocidad lineal estimada en X
        self.linear_velocity_y = 0.0  # Velocidad lineal estimada en Y
        self.last_time = time.time()

        self.fd = wiringpi.wiringPiI2CSetupInterface(f"/dev/i2c-{self.i2cbus}", self.address)
        if self.fd < 0:
            if self.node:
                self.node.get_logger().error(f"Error I2C MPU6050 - Bus: {i2cbus}, Addr: {address}")
            return False

        # 1. Reset
        wiringpi.wiringPiI2CWriteReg8(self.fd, 0x6B, 0x80)
        time.sleep(0.1)

        # 2. Wake up y configurar
        wiringpi.wiringPiI2CWriteReg8(self.fd, 0x6B, 0x00)
        time.sleep(0.1)
        
        # Configurar giroscopio ±250°/s
        wiringpi.wiringPiI2CWriteReg8(self.fd, 0x1B, 0x00)
        
        # Configurar acelerómetro ±2g
        wiringpi.wiringPiI2CWriteReg8(self.fd, 0x1C, 0x00)
        
        if self.node:
            self.node.get_logger().info('MPU6050 inicializado correctamente')

    def read_all_data(self):
        """Lee todos los datos del MPU6050 para odometría"""
        try:
            current_time = time.time()
            dt = current_time - self.last_time
            
            # LEER ACELERÓMETRO (ejes X e Y)
            # Registros del acelerómetro
            accel_x_h = wiringpi.wiringPiI2CReadReg8(self.fd, 0x3B)
            accel_x_l = wiringpi.wiringPiI2CReadReg8(self.fd, 0x3C)
            accel_y_h = wiringpi.wiringPiI2CReadReg8(self.fd, 0x3D)
            accel_y_l = wiringpi.wiringPiI2CReadReg8(self.fd, 0x3E)
            accel_z_h = wiringpi.wiringPiI2CReadReg8(self.fd, 0x3F)
            accel_z_l = wiringpi.wiringPiI2CReadReg8(self.fd, 0x40)
            
            # Convertir a valores signed (complemento a 2)
            accel_x_raw = (accel_x_h << 8) | accel_x_l
            accel_y_raw = (accel_y_h << 8) | accel_y_l
            accel_z_raw = (accel_z_h << 8) | accel_z_l
            
            if accel_x_raw > 32767: accel_x_raw -= 65536
            if accel_y_raw > 32767: accel_y_raw -= 65536
            if accel_z_raw > 32767: accel_z_raw -= 65536
            
            # Convertir a g's (escala ±2g = 16384 LSB/g)
            self.accel_x = accel_x_raw / 16384.0
            self.accel_y = accel_y_raw / 16384.0
            accel_z = accel_z_raw / 16384.0
            
            # LEER GIROSCOPIO (solo eje Z para orientación)
            gz_h = wiringpi.wiringPiI2CReadReg8(self.fd, 0x47)
            gz_l = wiringpi.wiringPiI2CReadReg8(self.fd, 0x48)
            gz_raw = (gz_h << 8) | gz_l
            if gz_raw > 32767: gz_raw -= 65536
            
            # Convertir a °/s (escala ±250°/s = 131 LSB/°/s)
            self.angular_velocity_z = gz_raw / 131.0
            
            # INTEGRAR PARA OBTENER ÁNGULO (simple)
            self.angle_z += self.angular_velocity_z * dt
            
            # ESTIMAR VELOCIDAD LINEAL (integrando aceleración, con corrección por gravedad)
            # Asumimos que el robot está en superficie plana
            gravity_correction = 1.0  # Ajustar según calibración
            
            # Integrar aceleración para obtener velocidad (filtro simple)
            alpha = 0.8  # Factor de filtro
            self.linear_velocity_x = (alpha * self.linear_velocity_x + 
                                    (1 - alpha) * (self.accel_x - gravity_correction) * dt)
            self.linear_velocity_y = (alpha * self.linear_velocity_y + 
                                    (1 - alpha) * (self.accel_y - gravity_correction) * dt)
            
            # Limitar la deriva (velocidad tiende a cero si no hay aceleración)
            if abs(self.accel_x) < 0.1:  # Umbral de ruido
                self.linear_velocity_x *= 0.95
            if abs(self.accel_y) < 0.1:
                self.linear_velocity_y *= 0.95
                
            self.last_time = current_time
            return True
            
        except Exception as e:
            if self.node:
                self.node.get_logger().error(f'Error lectura MPU6050: {e}')
            return False

    def get_odometry_data(self):
        """Retorna datos formateados para odometría"""
        return {
            'angular_velocity_z': self.angular_velocity_z,
            'angle_z': self.angle_z,
            'linear_velocity_x': self.linear_velocity_x,
            'linear_velocity_y': self.linear_velocity_y,
            'accel_x': self.accel_x,
            'accel_y': self.accel_y
        }

    def reset_orientation(self, angle=0.0):
        """Resetear ángulo de orientación"""
        self.angle_z = angle

    def calibrate_gyro_drift(self, duration=5.0):
        """Calibración simple de deriva del giroscopio"""
        if self.node:
            self.node.get_logger().info('Calibrando giroscopio... (mantener robot quieto)')
        
        samples = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            if self.read_all_data():
                samples.append(self.angular_velocity_z)
            time.sleep(0.01)
        
        if samples:
            drift_bias = sum(samples) / len(samples)
            self.angular_velocity_z -= drift_bias
            if self.node:
                self.node.get_logger().info(f'Deriva calibrada: {drift_bias:.3f} °/s')
            return drift_bias
        return 0.0