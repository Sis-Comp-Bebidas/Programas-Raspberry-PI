#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import Adafruit_DHT
import RPi.GPIO as GPIO
import socket
import subprocess

# Configurações do GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Configurações do sensor
sensor = Adafruit_DHT.DHT22     # Ou DHT11
DHT_PIN = 11                    # Pino físico 11 (correspondente ao GPIO17)

def ler_temperatura_umidade():
    umidade, temperatura = Adafruit_DHT.read_retry(sensor, DHT_PIN)
    if umidade is not None and temperatura is not None:
        return f'Temperatura: {temperatura:.1f}°C\nUmidade: {umidade:.1f}%'
    else:
        return 'Falha ao ler os dados do sensor. Tente novamente!'

def get_ip_address(interface):
    try:
        result = subprocess.run(['ip', '-4', 'addr', 'show', interface], stdout=subprocess.PIPE)
        ip_address = result.stdout.decode('utf-8').strip().split("inet ")[1].split('/')[0]
    except Exception as e:
        print(f"Erro ao obter o IP para a interface {interface}: {e}")
        ip_address = None
    return ip_address

# Configurações da comunicação TCP/IP
TCP_IP = get_ip_address('usb0')
TCP_PORT = 2222  # Escolher uma porta que esteja disponível e não conflite com outros serviços

if TCP_IP is None:
    print("Não foi possível determinar o IP da interface de rede.")
    exit(1)

try:
    # Cria o socket TCP/IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((TCP_IP, TCP_PORT))
    sock.listen()
    print(f"Escutando em {TCP_IP}:{TCP_PORT}...")

    while True:
        conn, addr = sock.accept()
        print(f"Conectado por {addr}")
        with conn:
            while True:
                data = conn.recv(1024).decode('utf-8').strip()
                if data:
                    if data == 'ler_sensor':
                        resultado = ler_temperatura_umidade()
                        conn.sendall(resultado.encode())
                    else:
                        conn.sendall('Comando desconhecido.'.encode())
                else:
                    break

except KeyboardInterrupt:
    print("\nEncerrando o programa.")

finally:
    sock.close()
    print("Programa encerrado.")
