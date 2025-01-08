from confluent_kafka import Consumer
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time


# Funzione per inviare email
def send_email(to_email, subject, body):
    """
    Funzione per inviare un'email con le informazioni fornite.
    :param to_email: Indirizzo email del destinatario
    :param subject: Oggetto dell'email
    :param body: Corpo dell'email
    """
    from_email = 'tickerfinanzalert@gmail.com'
    password = 'hcrg jhti uabu qimk'  

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, password)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            print(f'Email inviata a {to_email}')
    except Exception as e:
        print(f'Errore nell\'invio dell\'email: {e}')
        
        

def listen_for_alerts():
    # Iniziamo ad ascoltare i messaggi dal topic 'to-notifier'
    consumer.subscribe([topic_alert])

    while True:
        # Poll per i nuovi messaggi
        msg = consumer.poll(1.0)
        if msg is None:
            continue  # Nessun messaggio ricevuto, continua a fare polling
        if msg.error():
            print(f"Errore del consumer: {msg.error()}")  # Logga eventuali errori
            continue

        # Parsing del messaggio ricevuto
        data = json.loads(msg.value().decode('utf-8'))
        print(f"Messaggio ricevuto: {data}")
        
        consumer.commit(asynchronous=False)  # Commit dell'offset per il messaggio
        # Estraggo i parametri dal messaggio
        email = data.get('email')
        ticker = data.get('ticker')
        condition = data.get('condition')

        # Creo il corpo dell'email
        subject = f'Alert: {ticker}'
        body = f'La condizione per il ticker {ticker} è stata soddisfatta.\n\nCondizione: {condition}'
        
        # Invia l'email
        if email:
            send_email(email, subject, body)
            
        
if __name__ =="__main__":
        # Kafka configuration for consumer
    time.sleep(20)
    consumer_config = {
        'bootstrap.servers': 'kafka:9092',  # Kafka broker address
        'group.id': 'alert-notifier-group',  # Consumer group ID
        'auto.offset.reset': 'latest',  # Start reading from the latest message
        'enable.auto.commit': False,  # Automatically commit offsets periodically
    }

    consumer = Consumer(consumer_config)

    topic_alert = 'to-notifier'  # Topic for receiving alert messages
    listen_for_alerts()

