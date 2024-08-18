import subprocess
import socket
import RPi.GPIO as GPIO

# Configurações do GPIO
GPIO.setmode(GPIO.BOARD)        # Utiliza a numeração física dos pinos
GPIO.setwarnings(False)         # Desativa os warnings do GPIO
VALVE_PIN = 7                   # Define o pino físico 7 (GPIO 4)
GPIO.setup(VALVE_PIN, GPIO.OUT) # Configura o pino como saída

def get_ip_address(interface):
    try:
        # Executa o comando para obter o IP da interface especificada
        result = subprocess.run(['ip', '-4', 'addr', 'show', interface], stdout=subprocess.PIPE)
        ip_address = result.stdout.decode('utf-8').strip().split("inet ")[1].split('/')[0]
    except Exception as e:
        print(f"Erro ao obter o IP para a interface {interface}: {e}")
        ip_address = None
    return ip_address

# Especifica a interface "ethernet usb 0", que geralmente é chamada de 'usb0'
TCP_IP = get_ip_address('usb0')
TCP_PORT = 22  # Esta porta pode funcionar para todos os IPs?
SERIAL_BAUDRATE = 19200  # Defina a taxa de transmissão de dados em bauds

if TCP_IP is None:
    print("Não foi possível determinar o IP da interface de rede.")
    exit(1)
else:
    print(f"IP da interface de rede (usb0): {TCP_IP}")

try:
    # Cria o socket TCP/IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
    print(f"Conectado ao servidor TCP/IP {TCP_IP}:{TCP_PORT} com sucesso.")
except socket.error as e:
    print(f"Erro ao conectar ao servidor TCP/IP {TCP_IP}:{TCP_PORT}: {e}")
    exit(1)

def control_valve(command):
    if command == 'OPEN':
        GPIO.output(VALVE_PIN, GPIO.HIGH)  # Abre a válvula
        print("Válvula aberta.")
    elif command == 'CLOSE':
        GPIO.output(VALVE_PIN, GPIO.LOW)   # Fecha a válvula
        print("Válvula fechada.")
    else:
        print(f"Comando desconhecido: {command}")

try:
    while True:
        # Recebe dados do servidor
        data = sock.recv(1024).decode('utf-8').strip()
        if data:
            control_valve(data)

except KeyboardInterrupt:
    print("\nEncerrando o programa.")

finally:
    GPIO.cleanup()  # Limpa os pinos GPIO
    sock.close()    # Fecha a conexão TCP/IP corretamente
    print("Programa encerrado.")
