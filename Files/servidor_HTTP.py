import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class FileServerHandler(BaseHTTPRequestHandler):
    DIRECTORY = r"C:\Users\user\Documents\CC2023\Redes\Files"

    def do_GET(self):
        try:
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

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
                self.wfile.write(html_content.encode("utf-8"))
            else:
                file_path = os.path.join(self.DIRECTORY, self.path[1:])
                if os.path.isfile(file_path):
                    self.send_response(200)
                    self.send_header("Content-type", "application/octet-stream")
                    self.send_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                    self.end_headers()
                    with open(file_path, "rb") as file:
                        self.wfile.write(file.read())
                else:
                    self.send_error(404, "Arquivo não encontrado")

        except Exception as e:
            self.send_error(500, str(e))

    def get_file_list(self):
        file_list = []
        for file in os.listdir(self.DIRECTORY):
            if os.path.isfile(os.path.join(self.DIRECTORY, file)):
                file_list.append(file)
        return file_list


def run_server(port, directory):
    server_address = ("", port)
    FileServerHandler.DIRECTORY = directory

    httpd = HTTPServer(server_address, FileServerHandler)
    print(f"Servidor rodando na porta {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    PORT = 8000  # Porta do servidor
    DIRECTORY = r"C:\Users\user\Documents\CC2023\Redes\Files"  # Diretório a ser listado e servido

    run_server(PORT, DIRECTORY)
