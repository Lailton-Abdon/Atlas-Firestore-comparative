import requests
import firebase_admin

from firebase_admin import credentials, firestore
from datetime import datetime

# Configuração do Firebase
def inicializar_firebase(cred_caminho: str):
    cred = credentials.Certificate(cred_caminho)
    firebase_admin.initialize_app(cred)
    return firestore.client()

db = inicializar_firebase(
    " ")

# Função para gerenciar a coleção
def criar_collection(db, collection_name: str):
    collection_ref = db.collection(collection_name)
    docs = collection_ref.limit(1).stream()

    if not list(docs):  # Se não houver documentos na coleção
        collection_ref.document('temp_doc').set({'created': True})  # Cria um documento temporário
        collection_ref.document('temp_doc').delete()  # Exclui o documento temporário imediatamente
        print(f'Coleção "{collection_name}" criada.')
    else:
        print(f'Coleção "{collection_name}" já existe.')

    return collection_ref

# Função para obter dados da API
def obter_dados_da_api(api_url: str, limit: int):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()[:limit]
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a API: {e}")
        return []

def ajustar_justificativa(item):
    if 'justificativa' in item and item['justificativa']:  # Verifica se não é None ou vazio
        justificativa_bytes = item['justificativa'].encode('utf-8')
        if len(justificativa_bytes) > 1048576:  # Verifica se ultrapassa 1 MB
            item['justificativa'] = "Limite"
    return item

# Função para inserir documentos no Firebase
def insert_doc(collection_ref, dado):
    for item in dado:
        # Ajustar justificativa caso exceda o limite de 1000 caracteres
        item = ajustar_justificativa(item)

        collection_ref.add(item)

    print(f'{len(dado)} documentos inseridos com sucesso.')
# Função para excluir documentos em lote
def delete_doc(collection_ref, quant: int):
    docs = collection_ref.order_by("inicio_execucao").limit(quant).stream()
    delete_count = sum(1 for doc in docs if doc.reference.delete())
    print(f'{delete_count} documentos excluídos com sucesso.')

# Função para listar documentos
def list_doc(collection_ref, quant: int):
    docs = collection_ref.order_by("inicio_execucao")  # Ordena os documentos pela data de início
    total_docs = 0  # Contador para o total de documentos listados

    print(f"\nListagem dos documentos (máximo de {quant}):")
    print("=" * 50)  # Separador para visualização

    # Loop para listar documentos
    for doc in docs.stream():
        doc_data = doc.to_dict()  # Converte o documento para um dicionário
        print(f"ID: {doc.id}")
        for key, value in doc_data.items():
            print(f"  {key}: {value}")  # Exibe cada campo e seu valor
        print("-" * 50)  # Separador entre documentos
        total_docs += 1
        if total_docs >= quant:  # Para se certificar de não exceder a quantidade solicitada
            break

    print(f'\nTotal de documentos listados: {total_docs}.')

# Função para atualizar documentos em lote
def update_doc(collection_ref, quant: int):
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

    print("\nCampos disponíveis para atualização:")
    for campo, descricao in campos_possiveis.items():
        print(f"{campo}: {descricao}")

    campo = input("Digite o campo que deseja atualizar: ").lower()

    if campo not in campos_possiveis:
        print(f"Campo '{campo}' não encontrado. Tente novamente.")
        return

    novo_valor = input(f"Digite o novo valor para o campo '{campo}': ")

    docs = collection_ref.order_by("inicio_execucao").limit(quant).stream()
    update_count = 0

    for doc in docs:
        doc_data = doc.to_dict()
        if campo == "justificativa" and not doc_data.get("justificativa"):
            print(f"Documento {doc.id} ignorado por não ter justificativa.")
            continue

        try:
            doc.reference.update({campo: novo_valor})
            update_count += 1
        except Exception as e:
            print(f"Erro ao atualizar documento {doc.id}: {e}")

    print(f'{update_count} documentos atualizados com sucesso.')

# Função para contar participantes em todos os projetos ativos no período especificado
def contar_participants_por_data(collection_ref, data_inicio, data_fim):
    # Converter as datas de string para datetime
    data_inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
    data_fim = datetime.strptime(data_fim, "%d/%m/%Y")

    # Buscar documentos e filtrar pelo período
    docs = collection_ref.stream()
    total_participantes_acumulado = 0
    documentos_no_periodo = []

    for doc in docs:
        doc_data = doc.to_dict()

        # Converter as datas de execução para datetime
        inicio_execucao = datetime.strptime(doc_data["inicio_execucao"], "%d/%m/%Y")
        fim_execucao = datetime.strptime(doc_data["fim_execucao"], "%d/%m/%Y")

        # Verificar sobreposição com o período especificado
        if (inicio_execucao <= data_fim and fim_execucao >= data_inicio):
            # Contar o número de participantes no documento e acumular no total
            total_participantes_acumulado += len(doc_data.get("participantes", []))
            # Adicionar o documento à lista para atualização posterior
            documentos_no_periodo.append(doc.reference)

    # Atualizar cada documento do período com o total acumulado
    if total_participantes_acumulado > 0:
        for doc_ref in documentos_no_periodo:
            try:
                doc_ref.update({"total_participantes_periodo": total_participantes_acumulado})
                print(
                    f"Documento {doc_ref.id} atualizado com o total acumulado de participantes: {total_participantes_acumulado}")
            except Exception as e:
                print(f"Erro ao atualizar o documento {doc_ref.id}: {e}")
    else:
        print("Nenhum participante encontrado no período especificado.")

# Menu Principal
def main():
    api_url = "https://dados.ifpb.edu.br/dataset/029b50a4-f50a-422d-867f-b457277b5168/resource/d3b1908b-e6d6-4437-aefb-281b7b1b57ea/download/projetos-extensao.json"
    collection_name = input("Digite o nome da coleção: ")
    collection_ref = criar_collection(db, collection_name)

    while True:
        print("\nMenu Principal:")
        print("1. Inserção de dados")
        print("2. Excluir Dados em Lote")
        print("3. Listar Dados")
        print("4. Atualizar Dados em Lote")
        print("5. Contar Participantes por período de tempo")
        print("0. Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            limit = int(input("Quantos documentos você deseja inserir? "))
            data = obter_dados_da_api(api_url, limit)
            if data:
                insert_doc(collection_ref, data)

        elif escolha == "2":
            quantity = int(input("Quantos documentos deseja excluir? "))
            delete_doc(collection_ref, quantity)

        elif escolha == "3":
            quantity = int(input("Quantos documentos deseja listar? "))
            list_doc(collection_ref, quantity)

        elif escolha == "4":
            quantity = int(input("Quantos documentos deseja atualizar? "))
            update_doc(collection_ref, quantity)

        elif escolha == "5":
            # Opção para contar participantes dentro de um período específico
            start_date_str = input("Digite a data de início (dd/mm/aaaa): ")
            end_date_str = input("Digite a data de fim (dd/mm/aaaa): ")
            contar_participants_por_data(collection_ref, start_date_str, end_date_str)

        elif escolha == "0":
            print("Saindo...")
            break

        else:
            print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    main()
