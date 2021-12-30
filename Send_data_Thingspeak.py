from machine import Pin, I2C, UART
import utime
import pmsa003
import bme280

from ssd1306 import SSD1306_I2C

WiFi_SSID='WiFi_SSID'  # Wifi_SSID
WiFi_password = 'WiFi_Password'      # WiFi Password
TCP_ServerIP = "184.106.153.149"   # Thingspeak IP address
Port = '80'                    # Thingspeak port
API_KEY = "FPJBGCLY9V0HNI82"

uart = UART(1, 9600)           # Default Baud rate

######## Function to send or receive commands and data

def sendCMD(cmd,ack,timeout=2000):
    uart.write(cmd+'\r\n')
    t = utime.ticks_ms()
    while (utime.ticks_ms() - t) < timeout:
        s=uart.read()
        if(s != None):
            s=s.decode("utf-8")
            print(s)
            if(s.find(ack) >= 0):
                return True
    return False
#####################################################


WIDTH  = 128                                            # oled display width
HEIGHT = 32                                             # oled display height

#i2c = I2C(0)                                            # Init I2C using I2C0 defaults, SCL=Pin(GP9), SDA=Pin(GP8), freq=400000
i2c = I2C(0, sda=Pin(20), scl=Pin(21))
print(i2c)
print("I2C Address      : "+hex(i2c.scan()[0]).upper()) # Display device address
print("I2C Configuration: "+str(i2c))                   # Display I2C config


oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)                  # Init oled display

oled.fill(0)

# Methods
# ---------------------------------------------------------------------------
def read_value(sensor):
    oled.fill(0)
    oled.text("A",120,0)
    """Read a sensor value and store it in the database."""
    # Read the value from the sensor.
    reading = sensor.read()
    #now = datetime.utcnow()
    bme = bme280.BME280(i2c=i2c, address=0x76)
    
    print(" pm10: {:d} pm25: {:d} pm100: {:d} Temp: {temp} Pressure: {pre} Hum: {hum} " .format(reading.pm10_cf1, reading.pm25_cf1, reading.pm100_cf1,
                                                                                                temp=bme.values[0],pre=bme.values[1],hum=bme.values[2]))
    #print("Temp: {temp} Pressure: {pre} Hum: {hum}".format(temp=bme.values[0],pre=bme.values[1],hum=bme.values[2]))
    oled.text("PM1.0= {:2d}".format(reading.pm10_cf1),5,5)
    oled.show()
    oled.text("PM2.5= {:2d}".format(reading.pm25_cf1),5,15)
    oled.show()
    oled.text("PM10.0= {:2d}".format(reading.pm100_cf1),5,25)
    oled.show()
    
    
    
    
    #data="GET /update?key="+API_KEY+"&field1="+str(reading.pm10_cf1)+"\r\n";
    data="GET /update?key="+API_KEY+"&field1=%s&field2=%s&field3=%s&field4=%s"%(reading.pm10_cf1,
                                                                           reading.pm25_cf1,
                                                                           reading.pm100_cf1,
                                                                                     bme.values[0])+"\r\n";
    
    final=len(data)
    reading=0
    
    sendCMD("AT+CIPSTART=\"TCP\",\""+TCP_ServerIP+"\","+Port,"OK",10000)
    
    sendCMD("AT+CIPSEND="+str(final)+"\r\n","OK")
    
    utime.sleep(0.5)
    uart.write(data)
    print(data)
    #utime.sleep(2)
    sendCMD('AT+CIPCLOSE'+'\r\n',"OK")
    #utime.sleep(0.3)
    oled.text("S",120,0)
    oled.show()
    
    utime.sleep(20)
    
def main():
    """The main method"""
    # Access the sensor over the serial line.
    sensor = pmsa003.Sensor("0")
    # Reading sensor data until terminated
    
    


    #print(bme.values[2])
    
    sendCMD("AT","OK")
    sendCMD("AT+CWMODE=1","OK")
    sendCMD("AT+CWJAP=\""+WiFi_SSID+"\",\""+WiFi_password+"\"","OK",20000)
    sendCMD("AT+CIFSR","OK")
    #sendCMD("AT+CIPSTART=\"TCP\",\""+TCP_ServerIP+"\","+Port,"OK",10000)
    
    
    while True:
        read_value(sensor)
        utime.sleep(2)
        
        
if __name__ == '__main__':
    main()
# EOF
