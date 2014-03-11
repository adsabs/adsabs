import smtpd
import asyncore
#python -m smtpd -n -c DebuggingServer localhost:1025
smtpd.PureProxy(('localhost', 25), ('smtp server name', 25))
asyncore.loop()