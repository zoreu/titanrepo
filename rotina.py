import os
import re
import shutil
import zipfile
import requests
import subprocess
import xml.etree.ElementTree as ET

dir_path = os.path.dirname(os.path.realpath(__file__))
pasta_leia = os.path.join(dir_path, "leia")
pasta_matrix = os.path.join(dir_path, "matrix")
pasta_hibrido = os.path.join(dir_path, "hibrido")
temp_hibrido = os.path.join(dir_path, 'temp', "hibrido")
temp_leia = os.path.join(dir_path, 'temp', "leia")
temp_matrix = os.path.join(dir_path, 'temp', "matrix")

def compactar_pasta(pasta):
    # Verificar se a pasta é a "plugin.video.CineRoom"
    # nome_pasta = os.path.basename(pasta)
    # if nome_pasta != 'plugin.video.CineRoom':
    #     print(f"A pasta {pasta} não é a pasta 'plugin.video.CineRoom'. Ignorando.")
    #     return

    # Verificar se existe um arquivo addon.xml na pasta
    arquivo_addon = os.path.join(pasta, 'addon.xml')
    if not os.path.isfile(arquivo_addon):
        print(f"A pasta {pasta} não possui o arquivo addon.xml.")
        return

    # Extrair informações de id e version do arquivo addon.xml
    with open(arquivo_addon, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.read()
        id_match = re.search(r'<addon[^>]*?\bid="([^"]+)"', conteudo)
        version_match = re.search(r'<addon[^>]*?\bversion="([^"]+)"', conteudo)

        if not id_match or not version_match:
            print(f"O arquivo addon.xml na pasta {pasta} está mal formatado.")
            return

        addon_id, addon_version = id_match.group(1), version_match.group(1)

    # Nome do arquivo zip a ser criado
    arquivo_zip = os.path.join(pasta, f'{addon_id}-{addon_version}.zip')

    # Verificar se o arquivo zip já existe na pasta
    if os.path.exists(arquivo_zip):
        print(f"O arquivo zip {arquivo_zip} já existe. Ignorando pasta {pasta}.")
        return

    # Criar o arquivo zip e adicionar apenas os arquivos da pasta
    try:
        with zipfile.ZipFile(arquivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for pasta_raiz, _, arquivos in os.walk(pasta):
                for arquivo in arquivos:
                    if not arquivo_zip == os.path.join(pasta, arquivo):
                        caminho_completo = os.path.join(pasta_raiz, arquivo)
                        rel_path = os.path.relpath(caminho_completo, pasta)
                        zip_path = os.path.join(addon_id, rel_path)
                        zipf.write(caminho_completo, zip_path)

        print(f"Pasta {pasta} compactada para {arquivo_zip}.")
    except Exception as e:
        print(f"Erro ao compactar a pasta {pasta}: {e}")

def copiar_pastas(origem, destino):
    try:
        # Verificar se o diretório de origem existe
        if not os.path.exists(origem):
            print(f"Diretório de origem {origem} não encontrado.")
            return

        # Verificar se o diretório de destino existe
        if not os.path.exists(destino):
            print(f"Diretório de destino {destino} não encontrado.")
            return

        # Listar todas as pastas dentro do diretório de origem
        pastas = [f for f in os.listdir(origem) if os.path.isdir(os.path.join(origem, f))]

        # Copiar cada pasta para o diretório de destino
        for pasta in pastas:
            origem_pasta = os.path.join(origem, pasta)
            destino_pasta = os.path.join(destino, pasta)
            shutil.copytree(origem_pasta, destino_pasta)

        print(f"Pastas copiadas de {origem} para {destino}.")
    except Exception as e:
        print(f"Erro ao copiar pastas: {e}")

def baixar_arquivo_zip(url, pasta_destino):
    try:
        # Fazer a requisição para baixar o arquivo
        resposta = requests.get(url)
        resposta.raise_for_status()  # Verificar se a requisição foi bem-sucedida

        # Extrair o nome do arquivo da URL
        nome_arquivo = os.path.basename(url)

        # Caminho completo para a pasta de destino
        caminho_completo_destino = os.path.join(pasta_destino, nome_arquivo)

        # Salvar o conteúdo do arquivo no disco
        with open(caminho_completo_destino, 'wb') as arquivo:
            arquivo.write(resposta.content)

        print(f"Arquivo zip baixado e salvo em: {caminho_completo_destino}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o arquivo: {e}")
    except Exception as e:
        print(f"Erro durante o processo: {e}")

def executar_script_na_pasta(pasta, nome_script):
    caminho_script = os.path.join(pasta, nome_script)
    try:
        if os.name == 'nt':  # Verifica se está executando no Windows
            subprocess.run(['python', caminho_script], shell=True, check=True)
        else:
            subprocess.run(['python3', caminho_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o script {nome_script}: {e}")
    except Exception as e:
        print(f"Erro durante o processo: {e}")

def extrair_arquivos_zip(pasta_destino):
    try:
        # Verificar se a pasta de destino existe
        if not os.path.exists(pasta_destino):
            print(f"Diretório de destino {pasta_destino} não encontrado.")
            return

        # Percorrer todos os arquivos na pasta de destino
        for arquivo in os.listdir(pasta_destino):
            caminho_arquivo = os.path.join(pasta_destino, arquivo)

            # Verificar se é um arquivo zip
            if zipfile.is_zipfile(caminho_arquivo):
                with zipfile.ZipFile(caminho_arquivo, 'r') as zip_ref:
                    zip_ref.extractall(pasta_destino)
                print(f"Arquivo zip {arquivo} extraído em: {pasta_destino}")
    
    except Exception as e:
        print(f"Erro durante o processo: {e}")

def obter_versao_do_addon(url_do_xml, addon_id):
    try:
        # Fazer a requisição HTTP GET para obter o conteúdo do XML
        resposta = requests.get(url_do_xml)
        resposta.raise_for_status()  # Verificar se a requisição foi bem-sucedida

        # Parsear o XML usando ElementTree
        root = ET.fromstring(resposta.content)

        # Encontrar o elemento com o ID do addon desejado
        for addon in root.findall('.//addon[@id="{}"]'.format(addon_id)):
            versao = addon.get('version')
            return versao

        print(f"Addon com o ID '{addon_id}' não encontrado no XML.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer a requisição: {e}")
        return None
    except ET.ParseError as e:
        print(f"Erro ao parsear o XML: {e}")
        return None
    except Exception as e:
        print(f"Erro durante o processo: {e}")
        return None


# 1 - BAIXAR ARQUIVOS
#### BAIXAR CINE ROOM
try:
    baixar_arquivo_zip('https://cineroom1.github.io/plugin.video.CineRoom.zip', temp_hibrido)
except:
    pass
#### BAIXAR BRAZUCA
try:
    versao_brazuca_leia = obter_versao_do_addon('https://github.com/skyrisk/brazucaplay/raw/master/addons/repo/addons.xml', 'plugin.video.BrazucaPlay')
    url_brazuca_leia = f'https://github.com/skyrisk/brazucaplay/raw/master/addons/repo/Plugins/plugin.video.BrazucaPlay/plugin.video.BrazucaPlay-{versao_brazuca_leia}.zip'
    baixar_arquivo_zip(url_brazuca_leia, temp_leia)
except:
    pass
try:
    versao_brazuca_matrix = obter_versao_do_addon('https://github.com/skyrisk/brazucaplay/raw/master/addons/repo/addons_matrix.xml', 'plugin.video.BrazucaPlay.Matrix')
    url_brazuca_matrix = f'https://github.com/skyrisk/brazucaplay/raw/master/addons/repo/Plugins/plugin.video.BrazucaPlay.Matrix/plugin.video.BrazucaPlay.Matrix-{versao_brazuca_matrix}.zip'
    baixar_arquivo_zip(url_brazuca_matrix, temp_matrix)
except:
    pass

# 2 - EXTRAIR
### EXTRAIR TODOS OS ARQUIVOS DA PASTA
try:
    extrair_arquivos_zip(temp_hibrido)
except:
    pass
try:
    extrair_arquivos_zip(temp_leia)
except:
    pass
try:
    extrair_arquivos_zip(temp_matrix)
except:
    pass
## 3 - COMPACTAR
#### COMPACTAR CADA ADDON ###############
# COMPACTAR CINE ROOM NOVAMENTE
try:
    compactar_pasta(os.path.join(temp_hibrido, 'plugin.video.CineRoom'))
except:
    pass
# COMPACTAR BRAZUCA LEIA
try:
    compactar_pasta(os.path.join(temp_leia, 'plugin.video.BrazucaPlay'))
except:
    pass
try:
    compactar_pasta(os.path.join(temp_matrix, 'plugin.video.BrazucaPlay.Matrix'))
except:
    pass
# ######################################
### 4 COPAR PARA PASTA DE DESTINO
try:
    copiar_pastas(temp_hibrido, pasta_hibrido)
except:
    pass
try:
    copiar_pastas(temp_leia, pasta_leia)
except:
    pass
try:
    copiar_pastas(temp_matrix, pasta_matrix)
except:
    pass
### EXECUTAR SCRIPT CORRESPONDENTE
executar_script_na_pasta(pasta_hibrido, 'addons_xml_generator.py')
executar_script_na_pasta(pasta_leia, 'addons_xml_generator.py')
executar_script_na_pasta(pasta_matrix, 'addons_xml_generator.py')


