import pymongo
import requests
from datetime import datetime

def conectar_mongo(nome_banco, nome_colecao):
    client = pymongo.MongoClient(" ")
    banco_de_dados = client[nome_banco]
    return banco_de_dados[nome_colecao]


def recuperar_dados_api(url, limite):
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados_json = resposta.json()
        return dados_json[:limite]
    else:
        print(f"Erro ao recuperar dados da API: {resposta.status_code}")
        return None


def inserir_dados_banco_dados(dados, colecao):
    colecao.insert_many(dados)


def listar_dados(colecao, limite):
    cursor = colecao.find()
    for documento in cursor[:limite]:
        print(documento)


def atualizar_dados(colecao, quantidade_documentos):
    campos_possiveis = {
        "titulo": "Título",
        "inicio_execucao": "Data de Início",
        "fim_execucao": "Data de Término",
        "foco_tecnologico": "Foco Tecnológico",
        "area_conhecimento": "Área de Conhecimento",
        "valor_total_executado": "Valor Total Executado",
        "aprovado": "Aprovado (True/False)",
        "resumo": "Resumo",
        "justificativa": "Justificativa",
        "resultados_esperados": "Resultados Esperados"
    }

    while True:
        print("\nCampos Possíveis para Atualização:")
        for campo, descricao in campos_possiveis.items():
            print(f"- {campo} ({descricao})")

        campo_escolhido = input("Digite o campo que deseja atualizar (ou 'sair' para voltar): ").lower()

        if campo_escolhido == "sair":
            break

        if campo_escolhido not in campos_possiveis:
            print(f"Campo inválido: '{campo_escolhido}'. Tente novamente.")
            continue

        novo_valor = input(f"Digite o novo valor para o campo '{campos_possiveis[campo_escolhido]}': ")

        documentos_atualizar = list(colecao.find({}, limit=quantidade_documentos))

        for documento in documentos_atualizar:
            documento[campo_escolhido] = novo_valor
            colecao.update_one({"_id": documento["_id"]}, {"$set": documento})

        print(f"Documentos atualizados com sucesso! Total: {len(documentos_atualizar)}")

        continuar_atualizando = input("Deseja atualizar outro campo? (sim/não): ").lower()
        if continuar_atualizando != "sim":
            break


def excluir_dados(colecao, quantidade):
    total_documentos = colecao.count_documents({})

    if quantidade > total_documentos:
        print(
            f"Erro: A quantidade de documentos a serem excluídos ({quantidade}) excede o total de documentos na coleção ({total_documentos}).")
        return

    confirmar_exclusao = input(f"Tem certeza que deseja excluir {quantidade} documentos? (sim/não): ").lower()

    if confirmar_exclusao != "sim":
        print("Exclusão cancelada.")
        return

    documentos_para_excluir = colecao.find().limit(quantidade)

    for documento in documentos_para_excluir:
        colecao.delete_one({"_id": documento["_id"]})

    print(f"Documentos excluídos com sucesso! Total: {quantidade}")


def contar_projetos_por_area(data_inicio, data_fim, area_conhecimento, colecao):
    try:
        # Converter strings de data para objetos datetime
        data_inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
        data_fim = datetime.strptime(data_fim, "%d/%m/%Y")
    except ValueError as e:
        print(f"Erro ao converter datas: {e}")
        return 0

    # Construir o filtro para a consulta
    filtro = {
        "area_conhecimento": area_conhecimento,
        "inicio_execucao": {"$gte": data_inicio},
        "fim_execucao": {"$lte": data_fim}
    }

    # Debug: Exibir o filtro que está sendo usado
    print(f"Filtro usado na consulta: {filtro}")

    # Executar a consulta e contar os documentos que atendem ao filtro
    contagem = colecao.count_documents(filtro)

    # Debug: Exibir o resultado da contagem
    print(f"Número de documentos encontrados: {contagem}")

    return contagem


def menu_principal():
    while True:
        print("\nMenu Principal:")
        print("1. Iniciar coleta e inserção de dados")
        print("2. Listar dados")
        print("3. Atualizar dados")
        print("4. Excluir Dados")
        print("5. Contar projetos por área de conhecimento")
        print("0. Sair")

        opcao = input("Digite sua opção: ")

        if opcao == "1":
            nome_banco = input("Digite o nome do banco de dados: ")
            nome_colecao = input("Digite o nome da coleção: ")
            limite_dados = int(input("Digite o limite de dados: "))

            colecao_mongo = conectar_mongo(nome_banco, nome_colecao)

            dados_api = recuperar_dados_api(
                "https://dados.ifpb.edu.br/dataset/029b50a4-f50a-422d-867f-b457277b5168/resource/d3b1908b-e6d6-4437-aefb-281b7b1b57ea/download/projetos-extensao.json",
                limite_dados)

            if dados_api:
                inserir_dados_banco_dados(dados_api, colecao_mongo)
                print("Dados coletados e inseridos com sucesso!")
            else:
                print("Erro ao recuperar dados da API.")

        elif opcao == "2":
            nome_banco = input("Digite o nome do banco de dados: ")
            nome_colecao = input("Digite o nome da coleção: ")
            limite_dados = int(input("Digite o limite de dados: "))

            colecao_mongo = conectar_mongo(nome_banco, nome_colecao)

            listar_dados(colecao_mongo, limite_dados)

        elif opcao == "3":
            nome_banco = input("Digite o nome do banco de dados: ")
            nome_colecao = input("Digite o nome da coleção: ")
            quantidade_documentos = int(input("Digite a quantidade de documentos a serem atualizados: "))

            colecao_mongo = conectar_mongo(nome_banco, nome_colecao)

            atualizar_dados(colecao_mongo, quantidade_documentos)

        elif opcao == "4":
            nome_banco = input("Digite o nome do banco de dados: ")
            nome_colecao = input("Digite o nome da coleção: ")
            quantidade_documentos = int(input("Digite a quantidade de documentos a excluir: "))

            colecao_mongo = conectar_mongo(nome_banco, nome_colecao)
            excluir_dados(colecao_mongo, quantidade_documentos)

        elif opcao == "5":
            nome_banco = input("Digite o nome do banco de dados: ")
            nome_colecao = input("Digite o nome da coleção: ")
            area_conhecimento = input("Digite a área de conhecimento: ")
            data_inicio_str = input("Digite a data de início no formato dd/mm/aaaa: ")
            data_fim_str = input("Digite a data de fim no formato dd/mm/aaaa: ")
            colecao_mongo = conectar_mongo(nome_banco, nome_colecao)
            total_projetos = contar_projetos_por_area(data_inicio_str, data_fim_str, area_conhecimento, colecao_mongo)
            print(
                f"Total de projetos na área de conhecimento '{area_conhecimento}' entre {data_inicio_str} e {data_fim_str}: {total_projetos}")


        elif opcao == "0":
            print("Saindo do programa...")
            break

        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu_principal()