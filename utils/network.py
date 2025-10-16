import socket
import time

def test_service(ip_or_domain, port=443):
    """
    Teste si un service est accessible
    Retourne (statut: bool, ping: int ou None)
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        start_time = time.time()
        sock.connect((ip_or_domain, port))
        ping = int((time.time() - start_time) * 1000)
        sock.close()
        
        return True, ping
    except socket.gaierror:
        # Domaine invalide
        return False, None
    except socket.timeout:
        # Timeout
        return False, None
    except ConnectionRefusedError:
        # Connexion refusée
        return False, None
    except Exception as e:
        # Autre erreur
        return False, None