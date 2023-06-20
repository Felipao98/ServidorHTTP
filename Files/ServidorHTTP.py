import os
import socket
from flask import Flask, request

class FileServer:
    DIRECTORY = r"/home/acog24/acog24/Documentos/Files"

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(1)
        server_socket.settimeout(1)  # Definindo um timeout de 1 segundo

        print(f"Servidor rodando em {self.ip}:{self.port}")

        while True:
            try:
                client_socket, client_address = server_socket.accept()
                self.handle_request(client_socket)
            except socket.timeout:
                pass

    def handle_request(self, client_socket):
        request = client_socket.recv(1024).decode("utf-8")
        request_lines = request.split("\r\n")

        if len(request_lines) >= 1:
            method, path, version = request_lines[0].split()

            try:
                if path == "/":
                    self.send_response(client_socket, 200, "OK", "text/html")
                    file_list = self.get_file_list()
                    file_links = ''.join(f'<a href="/{file}">{file}</a><br>' for file in file_list)
                    html_content = f"""
                    <html>
                    <head>
                        <title>File Server</title>
                    </head>
                    <body>
                        <h1>Arquivos Disponiveis:</h1>
                        {file_links}
                    </body>
                    </html>
                    """
                    client_socket.sendall(html_content.encode("utf-8"))
                elif path == "/header":
                    self.send_response(client_socket, 200, "OK", "text/html")
                    headers = request_lines[1:]
                    header_lines = "\r\n".join(headers)
                    client_socket.sendall(header_lines.encode("utf-8"))
                else:
                    file_path = os.path.join(self.DIRECTORY, path[1:])
                    if os.path.isfile(file_path):
                        self.send_response(client_socket, 200, "OK", "application/octet-stream")
                        self.send_file(client_socket, file_path)
                    else:
                        self.send_error(client_socket, 404, "Arquivo nao encontrado")

            except Exception as e:
                self.send_error(client_socket, 500, str(e))
        else:
            self.send_error(client_socket, 400, "Solicitação inválida")

        client_socket.close()

    def send_response(self, client_socket, code, message, content_type):
        response = f"HTTP/1.1 {code} {message}\r\n"
        response += f"Content-type: {content_type}\r\n"
        response += "\r\n"
        client_socket.sendall(response.encode("utf-8"))

    def send_file(self, client_socket, file_path):
        with open(file_path, "rb") as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                client_socket.sendall(data)

    def send_error(self, client_socket, code, message):
        self.send_response(client_socket, code, "Error", "text/html")
        error_content = f"""
        <html>
        <head>
            <title>{code} - Error</title>
        </head>
        <body>
            <h1>Error {code}</h1>
            <p>{message}</p>
        </body>
        </html>
        """
        client_socket.sendall(error_content.encode("utf-8"))

    def get_file_list(self):
        file_list = []
        for file in os.listdir(self.DIRECTORY):
            if os.path.isfile(os.path.join(self.DIRECTORY, file)):
                file_list.append(file)
        return file_list

app = Flask(__name__)

@app.route('/header')
def show_header():
    headers = request.headers
    header_list = "<br>".join([f"{header}: {value}" for header, value in headers.items()])
    return header_list


if __name__ == '__main__':
    IP = "172.18.1.50"  # IP do servidor
    PORT = 8000  # Porta do servidor
    DIRECTORY = r"/home/acog24/acog24/Documentos/Files"  # Diretório a ser listado e servido

    file_server = FileServer(IP, PORT)
    file_server.start()
