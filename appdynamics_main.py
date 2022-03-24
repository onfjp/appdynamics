"""
Desenvolvido por: Franklin Pereira
Objetivo: Obter informações como: Aplicação, Calls, Policies e Health Rule
Versão: 0.1-beta
Revisão: 1
"""
import requests
import urllib3
import json
import csv
import xmltodict

urllib3.disable_warnings()

def consolidarInfo():
    nomeApp = ""
    conteudo = ""
    callsTotal = ""

    configuracao = lerConfig()

    for config in configuracao:
        controller = config['Controller']
        auth = config['Token']
        token = {'Authorization': 'Bearer %s'%(auth)}

        val_proxy = {
            'http': '',
            'https': ''
            }

        ## OBTER A LISTA DE TODAS APLICAÇÕES DO APPDYNAMICS

        print("Obtendo lista de aplicações")
        obter_aplicacoes = obterApps(controller, token, val_proxy)
        status = obter_aplicacoes[1]

        if status == 200:
            ## OBTER INFORMAÇÕES REFERENTE A MÉTRICA CALL PER MINUTE
            for todas_apps in obter_aplicacoes[0]:
                nomeApp = todas_apps['name']
                ids = todas_apps['id']               

                #idTexto = str(ids)

                metrica = obterMetrica(controller, nomeApp, token, val_proxy)

                if metrica == None:
                    print("Aplicação sem métricas!")
                else:
                    nomeMetrica = metrica['metric-data']['metricName']

                    if nomeMetrica != "METRIC DATA NOT FOUND":
                        callsTotal = metrica['metric-data']['metricValues']['metric-value']['sum']
                        if callsTotal != "0":
                            print("Obtendo métrica da aplicação:"+nomeApp)  
                            conteudo = [controller,nomeApp,callsTotal]
                            exportarCsv(conteudo)

        else:
              print("Algo deu errado!")   

def exportarCsv(resultado):
    with open('relAppDy.csv', 'a', newline='') as f:
        writer = csv.writer(f, delimiter = ",",lineterminator='\n')
        writer.writerow(resultado)

def lerConfig():
    with open('config.json', 'r') as file:
        return json.load(file)

def obterApps(controller, token, proxy,  app = "All"):
    if app == "All":
        api = "/rest/applications/?output=JSON"
    else:
        api = "/rest/applications/"+app+"/?output=JSON"

    urlCompleta = (controller + api)
    req = requests.get(url = urlCompleta , verify = False, headers = token, proxies = proxy)
    status = req.status_code  

    dados = json.loads(req.content)
    return dados, status
    
def obterMetrica(controller, nomeApp, token, proxy ):

    ## Coleta dados de 1 semana atrás
    metrica = "Overall%20Application%20Performance%7CCalls%20per%20Minute&time-range-type=BEFORE_NOW&duration-in-mins=10080"      

    api = "/rest/applications/"+nomeApp+"/metric-data?metric-path="+metrica

    urlCompleta = (controller + api)           

    req = requests.get(url = urlCompleta, verify = False, headers = token, proxies = proxy)   

    conversao =  xmltodict.parse(req.text)           

    jsonRetorno = json.dumps(conversao)

    dados = json.loads(jsonRetorno)  

    metrica = dados['metric-datas']       

    return metrica 

def obterPolicies(controller, token, proxy, ids):

    existePolicies = ""
    url_pol = "/alerting/rest/v1/applications/"+ids+"/policies/?output=JSON"
    urlPol = (controller + url_pol)
    reqPol = requests.get(url = urlPol, verify = False, headers = token, proxies = proxy)
    data_policies = json.loads(reqPol.content)

    if data_policies == []:
        existePolicies = "Não"
    else:
       for vPolicies in data_policies:
           validarPolicies = vPolicies["enabled"]
           if validarPolicies == True:
               existePolicies = "Sim"
    return existePolicies           

 
def obterRegras(controller, token, proxy, ids):
    existeRegra = ""
    url_hel = "/alerting/rest/v1/applications/"+ids+"/health-rules/?output=JSON"
    urlHel = (controller + url_hel)
    reqHel = requests.get(url = urlHel, verify = False, headers = token, proxies = proxy)
    data_health = json.loads(reqHel.content)

    for vRegras in data_health:
        validarRegra = vRegras["enabled"]
        if validarRegra == True:
            existeRegra = "Sim"                                   
        else:
            print("Aplicação sem regra ativa.")

    return existeRegra     

def ExportarDash(controller, token, proxy, idD):
    url_dash ="/CustomDashboardImportExportServlet?dashboardId="+idD
    urlHel = (controller + url_dash)
    reqHel = requests.get(url = urlHel, verify = False, headers = token, proxies = proxy)
    dashboard = json.loads(reqHel.content)
    return dashboard

if __name__ == '__main__':
    #header = "controller,aplicação,calls"
    #exportarCsv(header)
    consolidarInfo()
