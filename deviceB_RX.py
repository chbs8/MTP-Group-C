try:

    import RPi.GPIO as GPIO
    from lib_nrf24 import NRF24
    from math import *
    import time
    import spidev

    GPIO.setmode(GPIO.BCM)
    #GPIO.setup(23, GPIO.OUT)
    #GPIO.output(23,1)
    
    print("Receiver")
    pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]
    payloadSize = 32
    channel_RX = 0x60
    channel_TX = 0x65

    #Initializa the radio transceivers with the CE ping connected to the GPIO22 and GPIO24
    radio_Tx = NRF24(GPIO, spidev.SpiDev())
    radio_Rx = NRF24(GPIO, spidev.SpiDev())
    radio_Tx.begin(0, 22)
    radio_Rx.begin(0, 24)

    #We set the Payload Size to the limit which is 32 bytes
    radio_Tx.setPayloadSize(payloadSize)
    radio_Rx.setPayloadSize(payloadSize)

    #We choose the channels to be used for one and the other transceiver
    radio_Tx.setChannel(channel_TX)
    radio_Rx.setChannel(channel_RX)

    #We set the Transmission Rate
    radio_Tx.setDataRate(NRF24.BR_250KBPS)
    radio_Rx.setDataRate(NRF24.BR_250KBPS)

    #Configuration of the power level to be used by the transceiver
    radio_Tx.setPALevel(NRF24.PA_MAX)
    radio_Rx.setPALevel(NRF24.PA_MAX)

    #We disable the Auto Acknowledgement
    radio_Tx.setAutoAck(False)
    radio_Rx.setAutoAck(False)
    radio_Tx.enableDynamicPayloads()
    radio_Rx.enableDynamicPayloads()

    #Open the writing and reading pipe
    radio_Tx.openWritingPipe(pipes[0])
    radio_Rx.openReadingPipe(1, pipes[1])

    #We print the configuration details of both transceivers
    radio_Tx.printDetails()
    print("*------------------------------------------------------------------------------------------------------------*")
    radio_Rx.printDetails()
    print("*------------------------------------------------------------------------------------------------------------*")

    recv_frame = []
    str_recvFrame = ""
    flag = 0
    time_ack = 0.5
    outputFile = open("ReceivedFile.txt", "wb")
    receivedPacket = 0
    while(1):
        timeout = time.time() + time_ack
        radio_Rx.openReadingPipe(1, pipes[1])
        while(!receivedPacket):
            if radio_Rx.available(0):
                radio_Rx.read(frame, radio_Rx.getDynamicPayloadSize())
                print(frame)
                print(str(flag))
                if(char(frame[0]) == flag):
                    for c in range(1, len(frame)):
                        str_frame = str_frame + chr(frame[c])
                    outputFile.write(str_frame)
                    radio_Tx.write(list("ACK") + list(str(flag)))
                    receivedPacket = 1
                else:
                    if flag == 0:
                        radio_Tx.write(list("ACK") + list("9"))
                    else:
                        radio_Tx.write(list("ACK") + list(str(flag-1)))
                    timeout = time.time() + time_ack
            if((time.time() + 0.3) > timeout):
                radio_Rx.openReadingPipe(0, pipes[1])
                radio_Rx.startListening()
                radio_Tx.write(list("ACK") + list(str(flag-1)))
                timeout = time.time() + time_ack
        flag += 1 % 10
   
except KeyboardInterrupt:
    GPIO.output(23,0)
    GPIO.output(24,0)
    GPIO.cleanup()
    