import paramiko

# Liste der IP-Adressen Ihrer Raspberry Pi-Geräte
raspberry_pi_ips = ["192.168.201.251", "192.168.201.250", "192.168.201.229", "192.168.201.167"]

# Benutzername und Passwort für die SSH-Verbindung
ssh_username = "pi"
ssh_password = "12345"

# SSH-Verbindung herstellen und Befehl ausführen
def run_ssh_command(ip, username, password, command):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=username, password=password)
        
        stdin, stdout, stderr = ssh_client.exec_command(command)
        for line in stdout:
            print(line.strip())
        
        ssh_client.close()
        print(f"Command execution on {ip} completed.")
    except paramiko.AuthenticationException:
        print(f"Authentication failed for {ip}.")
    except paramiko.SSHException as e:
        print(f"SSH error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Hauptfunktion, um den Befehl auf allen Raspberry Pi-Geräten auszuführen
def main():
    command = "sudo pip install kafka-python -y"  # Ihr Befehl hier
    
    for ip in raspberry_pi_ips:
        run_ssh_command(ip, ssh_username, ssh_password, command)

if __name__ == "__main__":
    main()
