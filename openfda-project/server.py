
import http.server
import http.client
import json
import socketserver

PORT=8000

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):


    def get_main_page(self):
        html = """
            <html>
                <head>
                    <title>OpenFDA App</title>
                </head>
                <body>
                    <h1>OpenFDA Client </h1>
                    <form method="get" action="listDrugs">
                        <input type = "submit" value="Drug List">
                        </input>
                    </form>
                    **************************************************
                    <form method="get" action="searchDrug">
                        <input type = "submit" value="Drug Search">
                        <input type = "text" name="drug"></input>
                        </input>
                    </form>
                    **************************************************
                    <form method="get" action="listCompanies">
                        <input type = "submit" value="Company List">
                        </input>
                    </form>
                    **************************************************
                    <form method="get" action="searchCompany">
                        <input type = "submit" value="Company Search">
                        <input type = "text" name="company"></input>
                        </input>
                    </form>
                    **************************************************
                    <form method="get" action="listWarnings">
                        <input type = "submit" value="Warnings List">
                        </input>
                    </form>
                </body>
            </html>
                """
        return html
    def dame_web (self, lista):
        list_html = """
                                <html>
                                    <head>
                                        <title>OpenFDA Cool App</title>
                                    </head>
                                    <body>
                                        <ul>
                            """
        for item in lista:
            list_html += "<li>" + item + "</li>"

        list_html += """
                                        </ul>
                                    </body>
                                </html>
                            """
        return list_html
    def dame_resultados_genericos (self, limit=10):
        conn = http.client.HTTPSConnection("api.fda.gov")
        conn.request("GET", "/drug/label.json" + "?limit="+str(limit))
        print ("/drug/label.json" + "?limit="+str(limit))
        r1 = conn.getresponse()
        resp_des = r1.read().decode("utf8")
        resp = json.loads(resp_des)
        resultados = resp['results']
        return resultados
    def do_GET(self):
        recurso_list = self.path.split("?")
        if len(recurso_list) > 1: #En primer lugar averiguamos si se nos está pasando algún recurso, en caso de que si,
            parametros = recurso_list[1] #llamamos a parametros lo que está después de la interrogación (los parámetros).
        else:
            parametros = ""

        limit = 1 #ponemos por defecto que el límite sea igual a 1

        if parametros:
            parse_limit = parametros.split("=") #aquí vemos si se nos pasa algún limit, para darle un nuevo valor, o dejar el
            if parse_limit[0] == "limit":   #predeterminado.
                limit = int(parse_limit[1])
                print("Limit: {}".format(limit))
        else:
            print("SIN PARAMETROS")



        if self.path=='/':

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            pagina_html=self.get_main_page()
            self.wfile.write(bytes(pagina_html, "utf8"))
        elif 'listDrugs' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            lista_medicamentos = []
            resultados = self.dame_resultados_genericos(limit)
            for resultado in resultados:
                if ('generic_name' in resultado['openfda']):
                    lista_medicamentos.append (resultado['openfda']['generic_name'][0])
                else:
                    lista_medicamentos.append('Desconocido')
            pagina_html = self.dame_web (lista_medicamentos)

            self.wfile.write(bytes(pagina_html, "utf8"))
        elif 'listCompanies' in self.path:
            self.send_response(200)

            self.send_header('Content-type', 'text/html')
            self.end_headers()
            list_companies = []
            resultados = self.dame_resultados_genericos (limit)
            for resultado in resultados:
                if ('manufacturer_name' in resultado['openfda']):
                    list_companies.append (resultado['openfda']['manufacturer_name'][0])
                else:
                    list_companies.append('Desconocido')
            pagina_html = self.dame_web(list_companies)

            self.wfile.write(bytes(pagina_html, "utf8"))
        elif 'listWarnings' in self.path:

            self.send_response(200)


            self.send_header('Content-type', 'text/html')
            self.end_headers()
            lista_warnings = []
            resultados = self.dame_resultados_genericos (limit)
            for resultado in resultados:
                if ('warnings' in resultado):
                    lista_warnings.append (resultado['warnings'][0])
                else:
                    lista_warnings.append('Desconocido')
            pagina_html = self.dame_web(lista_warnings)

            self.wfile.write(bytes(pagina_html, "utf8"))
        elif 'searchDrug' in self.path:

            self.send_response(200)

            self.send_header('Content-type', 'text/html')
            self.end_headers()

            limit = 10 #establecemos límite por defecto =10
            drug=self.path.split('=')[1]

            drugs = []
            conn = http.client.HTTPSConnection("api.fda.gov")
            conn.request("GET", "/drug/label.json" + "?limit="+str(limit) + '&search=active_ingredient:' + drug)
            r1 = conn.getresponse()
            resp_des = r1.read().decode("utf8")
            resp = json.loads(resp_des)
            resultado_busqueda = resp['results']
            for resultado in resultado_busqueda:
                if ('generic_name' in resultado['openfda']):
                    drugs.append(resultado['openfda']['generic_name'][0])
                else:
                    drugs.append('Desconocido')

            pagina_html = self.dame_web(drugs)
            self.wfile.write(bytes(pagina_html, "utf8"))
        elif 'searchCompany' in self.path:

            self.send_response(200)


            self.send_header('Content-type', 'text/html')
            self.end_headers()

            limit = 10
            company=self.path.split('=')[1]
            companies = []
            conn = http.client.HTTPSConnection("api.fda.gov")
            conn.request("GET", "/drug/label.json" + "?limit=" + str(limit) + '&search=openfda.manufacturer_name:' + company)
            r1 = conn.getresponse()
            resp_des = r1.read().decode("utf8")
            res = json.loads(resp_des)
            resultado_busqueda = res['results']

            for event in resultado_busqueda:
                companies.append(event['openfda']['manufacturer_name'][0])
            pagina_html = self.dame_web(companies)
            self.wfile.write(bytes(pagina_html, "utf8"))
        elif 'redirect' in self.path:
            self.send_response(301)
            self.send_header('Location', 'http://localhost:'+str(PORT))
            self.end_headers()
        elif 'secret' in self.path:
            self.send_error(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')
            self.end_headers()
        else:
            self.send_error(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("I don't know '{}'.".format(self.path).encode())
        return



socketserver.TCPServer.allow_reuse_address= True

Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()
