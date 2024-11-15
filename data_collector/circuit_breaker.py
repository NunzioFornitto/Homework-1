import time
import threading

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30, expected_exception=Exception):
        """
        Inizializza una nuova istanza della classe CircuitBreaker.

        Parametri:
        - failure_threshold (int): Numero di fallimenti consecutivi consentiti prima di aprire il circuito.
        - recovery_timeout (int): Tempo in secondi da attendere prima di tentare di ripristinare il circuito.
        - expected_exception (Exception): Tipo di eccezione che incrementa il contatore dei fallimenti.
        """
        self.failure_threshold = failure_threshold          # Soglia di fallimenti per aprire il circuito
        self.recovery_timeout = recovery_timeout            # Timeout prima di tentare di ripristinare il circuito
        self.expected_exception = expected_exception        # Tipo di eccezione da monitorare
        self.failure_count = 0                              # Contatore dei fallimenti consecutivi
        self.last_failure_time = None                       # Timestamp dell'ultimo fallimento
        self.state = 'CLOSED'                               # Stato iniziale del circuito
        self.lock = threading.Lock()                        # Lock per garantire operazioni sicure tra i thread

    def call(self, func, *args, **kwargs):
        """
        Esegue la funzione fornita nel contesto del Circuit Breaker.

        Parametri:
        - func (callable): La funzione da eseguire.
        - *args: Lista di argomenti variabili per la funzione.
        - **kwargs: Argomenti arbitrari per la funzione.

        Ritorna:
        - Il risultato della chiamata alla funzione se è riuscita.

        Solleva:
        - CircuitBreakerOpenException: Se il circuito è aperto e le chiamate non sono consentite.
        - Exception: Rilancia eventuali eccezioni sollevate dalla funzione.
        """
        with self.lock:  # Garantisce l'accesso sicuro ai variabili condivise
            if self.state == 'OPEN':
                # Calcola il tempo trascorso dall'ultimo fallimento
                time_since_failure = time.time() - self.last_failure_time
                if time_since_failure > self.recovery_timeout:
                    # Passa allo stato HALF_OPEN dopo il timeout di recupero
                    self.state = 'HALF_OPEN'
                else:
                    # Il circuito è ancora aperto; nega la chiamata
                    raise CircuitBreakerOpenException("Il circuito è aperto. Chiamata negata.")
            
            try:
                # Tentativo di eseguire la funzione
                result = func(*args, **kwargs)
            except self.expected_exception as e:
                # La funzione ha sollevato un'eccezione prevista; incrementa il contatore dei fallimenti
                self.failure_count += 1
                self.last_failure_time = time.time()  # Aggiorna il timestamp dell'ultimo fallimento
                if self.failure_count >= self.failure_threshold:
                    # La soglia di fallimenti è stata raggiunta; apre il circuito
                    self.state = 'OPEN'
                raise e  # Rilancia l'eccezione al chiamante
            else:
                # La funzione è stata eseguita con successo
                if self.state == 'HALF_OPEN':
                    # Successo nello stato HALF_OPEN; ripristina il circuito a CLOSED
                    self.state = 'CLOSED'
                    self.failure_count = 0  # Resetta il contatore dei fallimenti
                return result  # Ritorna il risultato della chiamata riuscita

class CircuitBreakerOpenException(Exception):
    """Eccezione personalizzata sollevata quando il circuito è aperto."""
    pass
