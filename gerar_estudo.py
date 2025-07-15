import sys
import os
import subprocess
import argparse
import re

def slugify(text):
    """
    Converte um texto em um formato seguro para nomes de arquivo (slug).
    Ex: "Aula 01 de 19 - A Natureza do Pecado" -> "aula_01_de_19_-_a_natureza_do_pecado"
    """
    text = text.lower()
    text = text.replace(" ", "_")
    text = re.sub(r'[^\w\-_.]', '', text)
    return text

def run_command(command):
    """
    Executa um comando no shell e exibe sua saída em tempo real.
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1
        )

        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
            process.stdout.close()
        
        return_code = process.wait()
        
        if return_code != 0:
            # Imprime uma mensagem de erro mais detalhada
            print(f"\n{'='*20} ERRO AO EXECUTAR COMANDO {'='*20}")
            print(f"O comando abaixo falhou com o código de saída {return_code}:")
            print(f"  {' '.join(command)}")
            print(f"Verifique a saída de erro acima para mais detalhes.")
            print(f"{'='*62}")
            # Retorna False em caso de falha para que o script principal possa parar
            return False
            
    except FileNotFoundError:
        print(f"\nERRO: Comando '{command[0]}' não encontrado. Verifique se o programa está instalado e no PATH do sistema.")
        return False
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Gerador de material de estudo a partir de vídeos do Vimeo.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("main_topic", help="O tema geral do curso (será o nome da pasta).\nEx: \"Teologia Sistemática III\"")
    parser.add_argument("lesson_identifier", help="O identificador da aula.\nEx: \"Aula 01 de 19\"")
    parser.add_argument("url", help="A URL completa do vídeo no Vimeo.")
    parser.add_argument("--password", help="Senha para o vídeo do Vimeo (opcional).", default=None)
    parser.add_argument("--model", help="Modelo do Whisper a ser usado (tiny, base, small, medium, large).", default="medium")


    args = parser.parse_args()

    # --- Configuração dos diretórios ---
    processing_dir = "processing"
    safe_main_topic_folder = slugify(args.main_topic)
    safe_lesson_identifier_name = slugify(args.lesson_identifier)
    
    topic_folder_path = os.path.join("docs", "teologia", "temas", safe_main_topic_folder)
    
    # Cria os diretórios necessários
    os.makedirs(topic_folder_path, exist_ok=True)
    os.makedirs(processing_dir, exist_ok=True)

    # Define os nomes de arquivo
    # Usamos um nome de arquivo consistente para vídeo, áudio e transcrição para facilitar a retomada
    base_filename = f"{safe_main_topic_folder}__{safe_lesson_identifier_name}"
    video_path = os.path.join(processing_dir, f"{base_filename}.mp4")
    audio_path = os.path.join(processing_dir, f"{base_filename}.mp3")
    transcription_path = os.path.join(processing_dir, f"{base_filename}.txt")

    # --- Montagem dos Comandos ---
    commands_to_run = []

    # 1. Comando para baixar o vídeo
    # Só adiciona o comando se o vídeo ainda não existir
    if not os.path.exists(video_path):
        video_command = ["yt-dlp", "-f", "bestvideo+bestaudio/best", "-o", video_path, args.url]
        if args.password:
            video_command.insert(4, "--video-password")
            video_command.insert(5, args.password)
        commands_to_run.append({"name": "Download do Vídeo", "command": video_command, "check_file": video_path})

    # 2. Comando para extrair o áudio
    # Só adiciona se o áudio não existir. O yt-dlp pode extrair de URL ou de arquivo local.
    if not os.path.exists(audio_path):
        source_for_audio = video_path if os.path.exists(video_path) else args.url
        audio_command = ["yt-dlp", "--extract-audio", "--audio-format", "mp3", "-o", audio_path, source_for_audio]
        if not os.path.exists(video_path) and args.password: # Apenas precisa da senha se baixar da URL
             audio_command.insert(5, "--video-password")
             audio_command.insert(6, args.password)
        commands_to_run.append({"name": "Extração de Áudio", "command": audio_command, "check_file": audio_path})
        
    # 3. Comando para transcrever o áudio
    # Só adiciona se a transcrição não existir
    if not os.path.exists(transcription_path):
        transcribe_cmd = ["whisper", audio_path, "--language", "Portuguese", "--model", args.model, "--output_format", "txt", "--output_dir", processing_dir]
        commands_to_run.append({"name": "Transcrição de Áudio (Whisper)", "command": transcribe_cmd, "check_file": transcription_path})

    # --- Log e Execução dos Comandos ---
    if not commands_to_run:
        print("\nTodos os arquivos necessários (vídeo, áudio, transcrição) já existem.")
        print("Pulando para a geração do prompt.")
    else:
        print(f"\n{'='*15} COMANDOS A SEREM EXECUTADOS {'='*15}\n")
        for i, step in enumerate(commands_to_run):
            # Transforma a lista de comando em uma string para exibição
            command_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in step["command"])
            print(f"Passo {i+1}: {step['name']}")
            print(f"  Comando: {command_str}\n")
        
        print(f"\n{'='*20} INICIANDO EXECUÇÃO {'='*21}\n")

        for i, step in enumerate(commands_to_run):
            print(f"\n--- Executando Passo {i+1}: {step['name']} ---\n")
            if not run_command(step['command']):
                print(f"\nO passo '{step['name']}' falhou. O script será interrompido.")
                sys.exit(1)
            # Verifica se o arquivo esperado foi realmente criado
            if not os.path.exists(step['check_file']):
                 print(f"\nERRO: O comando foi executado, mas o arquivo esperado '{step['check_file']}' não foi criado.")
                 sys.exit(1)


    # --- Passo Final: Geração do Prompt ---
    print(f"\n{'='*18} PASSO FINAL: GERANDO PROMPT {'='*17}\n")
    try:
        with open(transcription_path, 'r', encoding='utf-8') as f:
            transcription_content = f.read().strip()
        
        # Renomeia o arquivo de transcrição para um nome mais descritivo
        final_transcription_path = os.path.join(processing_dir, f"{base_filename}_transcricao_final.txt")
        os.rename(transcription_path, final_transcription_path)

    except FileNotFoundError:
        print(f"ERRO: Arquivo de transcrição não encontrado em '{transcription_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"ERRO ao ler ou renomear o arquivo de transcrição: {e}")
        sys.exit(1)

    
    sources_folder = os.path.join("docs", "teologia", "fontes_de_referencia")
    os.makedirs(sources_folder, exist_ok=True)
    sources_file_path = os.path.join(sources_folder, "todas_as_fontes.md")
    if not os.path.exists(sources_file_path):
        with open(sources_file_path, 'w', encoding='utf-8') as f:
            f.write("# Fontes de Referência Teológica\n\nEste arquivo centraliza todas as fontes citadas nas aulas.\n")

    final_prompt = f"""Olá! Sua tarefa é analisar a transcrição de uma aula e gerar o material de estudo consolidado.

**Tema Geral do Curso:** {args.main_topic}
**Identificador da Aula:** {args.lesson_identifier}

**--- SUA TAREFA EM 3 PASSOS ---**

**PASSO 1: IDENTIFICAR O TEMA DA AULA**
- Leia a transcrição abaixo e determine o tema específico e conciso desta aula.
- Exemplo de tema: "A Natureza do Pecado", "A Doutrina da Trindade", "Os Atributos de Deus".

**PASSO 2: CRIAR O ARQUIVO DE ESTUDO CONSOLIDADO**
- Use o tema que você identificou para criar um nome de arquivo. O formato deve ser: `{safe_lesson_identifier_name}_-_{{tema_identificado_em_slug}}`.md
- Exemplo de nome de arquivo final: `aula_01_de_19_-_a_natureza_do_pecado.md`
- **Ação:** Crie um NOVO e ÚNICO arquivo no seguinte caminho: `{topic_folder_path}/{{nome_do_arquivo_que_voce_criou}}`
- **Conteúdo do Arquivo:** O arquivo deve ser bem estruturado e conter as 3 seções abaixo, nesta ordem:

    ---
    
    # [Substitua por: {args.lesson_identifier}: Tema que você identificou]

    ## 1. Artigo da Aula
    Gere um artigo **aprofundado e detalhado** sobre o tema. A estrutura deve ser rica, contendo:
    *   Uma **introdução** que apresenta o tema central.
    *   **Seções principais (###)** para cada sub-tópico abordado.
    *   **Definições formais** para termos teológicos importantes.
    *   Incorpore **citações diretas da transcrição**.
    *   Finalize com uma **conclusão** que resume os principais aprendizados.

    ## 2. Perguntas e Respostas para Fixação
    Elabore de 3 a 5 perguntas pertinentes sobre a aula. Para **cada pergunta**, forneça uma **resposta detalhada** em um ou dois parágrafos, baseando-se exclusivamente no conteúdo da transcrição.

    ## 3. Prova Rápida
    Crie uma prova curta (4 a 6 perguntas) com uma mistura de **múltipla escolha** e **dissertativas curtas** para avaliar a compreensão do material. Indique a resposta correta para as de múltipla escolha.

    ---

**PASSO 3: ATUALIZAR O ARQUIVO DE FONTES CENTRAL**
- **Ação:** Verifique a transcrição em busca de qualquer citação de livros, autores ou outras fontes.
- Se encontrar uma fonte que ainda não esteja listada, edite o arquivo `{sources_file_path}` para adicioná-la. Use um formato de lista (`* `) para cada fonte.
- Se nenhuma fonte nova for citada, não faça nada neste passo e me avise.

---
**TRANSCRIÇÃO COMPLETA PARA ANÁLISE (de {final_transcription_path}):**

{transcription_content}
"""
    print("\n" + "="*58)
    print("PROMPT FINAL GERADO. COPIE TODO O TEXTO ABAIXO E COLE PARA O ASSISTENTE:")
    print("="*58 + "\n")
    print(final_prompt)

if __name__ == "__main__":
    main() 