import sys
import os
import subprocess
import argparse
import re
import shutil
import shlex

def slugify(text):
    """
    Converte um texto em um formato seguro para nomes de arquivo (slug).
    Ex: "Meu Título Incrível" -> "meu_titulo_incrivel"
    """
    text = text.lower()
    text = re.sub(r'[\s\.]+', '_', text)  # Substitui espaços e pontos por underscore
    text = re.sub(r'[^\w\-_]', '', text) # Remove caracteres não-alfanuméricos
    return text

def print_step(message):
    """Exibe uma mensagem de passo formatada."""
    print(f"\n--- {message} ---\n")

def print_error(message):
    """Exibe uma mensagem de erro formatada."""
    print(f"\n{'='*20} ERRO {'='*20}")
    print(message)
    print(f"{'='*46}\n")

def handle_existing_file(filepath):
    """
    Verifica se um arquivo existe. Se sim, pergunta ao usuário como proceder.
    Retorna a ação a ser tomada: 'skip', 'overwrite', ou 'abort'.
    Se o arquivo não existir, retorna 'generate'.
    """
    if not os.path.exists(filepath):
        return 'generate'

    filename = os.path.basename(filepath)
    while True:
        try:
            print(f"AVISO: O arquivo '{filename}' já existe.")
            action = input("Deseja [S]obrescrever, [P]ular ou [A]bortar? ").lower()
            if action in ['s', 'sobrescrever']:
                return 'overwrite'
            if action in ['p', 'pular']:
                return 'skip'
            if action in ['a', 'abortar']:
                return 'abort'
            print("Opção inválida. Por favor, escolha 's', 'p' ou 'a'.")
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
            return 'abort'

def run_command(command, capture_output=False):
    """
    Executa um comando no shell.
    Retorna uma tupla: (sucesso: bool, saida: str | None)
    """
    try:
        if capture_output:
            # Usado para capturar a saída de texto
            result = subprocess.run(
                command, capture_output=True, text=True, encoding='utf-8', errors='replace'
            )
            if result.returncode != 0:
                print(f"\n{'='*20} ERRO AO EXECUTAR COMANDO {'='*20}")
                print(f"O comando abaixo falhou com o código de saída {result.returncode}:")
                print(f"  {' '.join(command)}")
                print(f"Saída: {result.stderr or result.stdout}")
                return False, None
            return True, result.stdout
        else:
            # Usado para exibir a saída em tempo real
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
            return return_code == 0, None

    except FileNotFoundError:
        print(f"\nERRO: Comando '{command[0]}' não encontrado. Verifique se o programa está instalado e no PATH do sistema.")
        return False, None
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
        return False, None

def is_tool(name):
    """Verifica se um programa existe no PATH do sistema."""
    return shutil.which(name) is not None

def get_transcription_source(url, password=None):
    """
    Verifica se há legendas disponíveis ou se deve usar Whisper.
    Retorna um dicionário com o método ('subtitle' ou 'whisper'), idioma e tipo ('manual' ou 'auto').
    """
    print("\nVerificando a disponibilidade de legendas...")
    # Opções para tornar o download mais robusto
    robust_dl_options = [
        "--no-cache-dir",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    ]
    # Inicializa com valores padrão
    transcription_info = {
        'method': 'whisper',
        'lang': 'pt',
        'sub_type': None
    }

    list_subs_command = ["yt-dlp", "--list-subs", url]
    list_subs_command.extend(robust_dl_options)
    if password:
        list_subs_command.extend(["--video-password", password])

    success, output = run_command(list_subs_command, capture_output=True)

    if not success:
        print("Não foi possível verificar as legendas. Prosseguindo com Whisper.")
        return transcription_info

    # Lógica para encontrar legendas manuais
    manual_subs_section_match = re.search(r'Available subtitles for .*?:\n(.*?)(?:\n\nAvailable automatic captions|$)', output, re.DOTALL)
    if manual_subs_section_match:
        for line in manual_subs_section_match.group(1).strip().split('\n'):
            if line.strip().startswith('pt'):
                print(">>> Legenda em português encontrada. Usando-a para transcrição.")
                transcription_info['method'] = 'subtitle'
                transcription_info['lang'] = 'pt'
                transcription_info['sub_type'] = 'manual'
                return transcription_info

    # Lógica para encontrar legendas automáticas
    auto_subs_section_match = re.search(r'Available automatic captions for .*?:\n(.*)', output, re.DOTALL)
    if auto_subs_section_match:
        # Pula a linha do cabeçalho "Language Name..." e verifica as outras
        for line in auto_subs_section_match.group(1).strip().split('\n')[1:]:
            if line.strip().startswith('pt'):
                try:
                    choice = input("? Encontrei apenas uma legenda gerada automaticamente. A qualidade pode ser inferior.\n  Deseja usar esta legenda ou transcrever com o Whisper? (usar/whisper): ").lower()
                    use_auto_sub = choice in ['usar', 'u']
                except KeyboardInterrupt:
                    print("\n\nOperação cancelada.")
                    sys.exit(0)

                if use_auto_sub:
                    print(">>> Usando a legenda automática conforme solicitado.")
                    transcription_info['method'] = 'subtitle'
                    transcription_info['lang'] = 'pt'
                    transcription_info['sub_type'] = 'auto'
                else:
                    print(">>> Prosseguindo com a transcrição via Whisper.")
                    transcription_info['method'] = 'whisper'
                return transcription_info

    print(">>> Nenhuma legenda em português encontrada. Prosseguindo com Whisper.")
    transcription_info['method'] = 'whisper'
    return transcription_info

def vtt_to_txt(vtt_path, txt_path):
    """
    Converte um arquivo de legenda VTT para um arquivo de texto limpo.
    """
    print(f"Convertendo legenda de '{vtt_path}' para texto puro...")
    try:
        with open(vtt_path, 'r', encoding='utf-8') as f_in:
            lines = f_in.readlines()
        
        content = []
        for line in lines:
            # Ignora cabeçalhos, timestamps, e linhas vazias
            if "WEBVTT" in line or "->" in line or line.strip() == "":
                continue
            # Remove tags de formatação VTT
            clean_line = re.sub(r'<[^>]+>', '', line)
            content.append(clean_line.strip())
        
        # Junta linhas que foram quebradas e remove duplicatas
        full_text = ' '.join(content)
        
        with open(txt_path, 'w', encoding='utf-8') as f_out:
            f_out.write(full_text)
        print(f"Arquivo de texto salvo em: {txt_path}")
        return True
    except Exception as e:
        print(f"ERRO ao converter VTT para TXT: {e}")
        return False

def setup_paths(args, mode):
    """
    Configura os caminhos de arquivo com base no modo ('aula' ou 'avulso').
    """
    processing_dir = "processing"
    os.makedirs(processing_dir, exist_ok=True)

    if mode == 'aula':
        safe_main_topic = slugify(args.main_topic)
        safe_lesson_id = slugify(args.lesson_identifier)
        base_filename = f"{safe_main_topic}__{safe_lesson_id}"
        output_dir = os.path.join("docs", "teologia", "temas", safe_main_topic)
    else: # modo 'avulso'
        safe_title = slugify(args.title)
        base_filename = safe_title
        output_dir = os.path.join("docs", "estudos")

    os.makedirs(output_dir, exist_ok=True)
    
    paths = {
        'processing_dir': processing_dir,
        'output_dir': output_dir,
        'base_filename': base_filename,
        'video': os.path.join(processing_dir, f"{base_filename}.mp4"),
        'audio': os.path.join(processing_dir, f"{base_filename}.mp3"),
        'subtitle_vtt': os.path.join(processing_dir, f"{base_filename}.pt.vtt"),
        'transcription_txt': os.path.join(processing_dir, f"{base_filename}.txt"),
    }
    return paths

def main():
    # --- Configuração dos Argumentos ---
    parser = argparse.ArgumentParser(
        description="Gerador de material de estudo a partir de vídeos (YouTube, Vimeo, etc.).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="mode", required=True, help="O modo de operação: 'aula' ou 'avulso'.")

    # Parser Pai para argumentos globais
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--password", help="Senha para o vídeo (principalmente para Vimeo).", default=None)
    parent_parser.add_argument("--model", help="Modelo do Whisper (tiny, base, small, medium, large).", default="large")
    parent_parser.add_argument("--no-video", action="store_true", help="Não baixa o arquivo de vídeo .mp4 (apenas áudio ou legenda).")

    # Sub-comando 'aula'
    parser_aula = subparsers.add_parser('aula', help="Para vídeos que são parte de um curso estruturado.", parents=[parent_parser])
    parser_aula.add_argument("main_topic", help="O tema geral do curso. Ex: \"Teologia Sistemática III\"")
    parser_aula.add_argument("lesson_identifier", help="O identificador da aula. Ex: \"Aula 01 de 19\"")
    parser_aula.add_argument("url", help="A URL completa do vídeo.")
    
    # Sub-comando 'avulso'
    parser_avulso = subparsers.add_parser('avulso', help="Para vídeos únicos ou não-estruturados.", parents=[parent_parser])
    parser_avulso.add_argument("title", help="O título do estudo que você quer gerar. Ex: \"A Importância da Oração\"")
    parser_avulso.add_argument("url", help="A URL completa do vídeo.")
    
    args = parser.parse_args()

    # Limpa a URL de caracteres de escape (\) desnecessários do shell
    if hasattr(args, 'url') and args.url:
        args.url = args.url.replace('\\', '')
    
    # --- Validações Iniciais ---
    if not is_tool('yt-dlp'):
        print("ERRO: O comando 'yt-dlp' não foi encontrado no PATH do sistema. Certifique-se de que o programa está instalado e no PATH do sistema.")
        sys.exit(1)

    # --- Lógica Principal ---
    paths = setup_paths(args, args.mode)
    transcription_info = get_transcription_source(args.url, args.password)

    # Pergunta sobre o download do vídeo se uma legenda for encontrada
    download_video = not args.no_video
    if transcription_info['method'] == 'subtitle' and not args.no_video:
        try:
            choice = input("\n? Legenda encontrada. Deseja baixar o arquivo de vídeo (.mp4) ou apenas a legenda? (video/legenda): ").lower().strip()
            if choice in ['legenda', 'l']:
                download_video = False
                print(">>> OK, baixando apenas a legenda.")
            else:
                print(">>> OK, baixando o vídeo e a legenda.")

        except KeyboardInterrupt:
            print("\n\nOperação cancelada.")
            sys.exit(0)

    # --- Montagem dos Comandos ---
    commands_to_run = []
    # O template de saída base para yt-dlp (sem extensão)
    output_template = os.path.join(paths['processing_dir'], paths['base_filename'])
    
    robust_dl_options = [
        "--no-cache-dir",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    ]

    # Passo de Transcrição/Legenda
    if transcription_info['method'] == 'subtitle':
        sub_flag = "--write-auto-sub" if transcription_info['sub_type'] == 'auto' else "--write-sub"
        format_selection = ["-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"]

        if not download_video:
            # Download de legenda apenas
            if not os.path.exists(paths['subtitle_vtt']):
                cmd = ["yt-dlp", sub_flag, "--sub-lang", transcription_info['lang'], "--skip-download", "-o", f"{output_template}.%(ext)s", args.url]
                cmd.extend(robust_dl_options)
                if args.password: cmd.extend(["--video-password", args.password])
                commands_to_run.append({"name": "Download da Legenda", "command": cmd})
        else:
            # Comportamento padrão: baixa vídeo e legenda
            if not os.path.exists(paths['subtitle_vtt']) or not os.path.exists(paths['video']):
                cmd = ["yt-dlp", sub_flag, "--sub-lang", transcription_info['lang'], "-o", output_template, args.url]
                cmd.extend(format_selection)
                cmd.extend(robust_dl_options)
                if args.password: cmd.extend(["--video-password", args.password])
                commands_to_run.append({"name": "Download do Vídeo e Legenda", "command": cmd})
    else: # Whisper
        if args.no_video:
            if not os.path.exists(paths['audio']):
                cmd = ["yt-dlp", "--extract-audio", "--audio-format", "mp3", "-o", f"{output_template}.%(ext)s", args.url]
                cmd.extend(robust_dl_options)
                if args.password: cmd.extend(["--video-password", args.password])
                commands_to_run.append({"name": "Extração de Áudio", "command": cmd})
        else: # Comportamento padrão: extrai áudio e mantém o vídeo
            if not os.path.exists(paths['audio']) or not os.path.exists(paths['video']):
                cmd = ["yt-dlp", "--extract-audio", "--audio-format", "mp3", "--keep-video", "-o", output_template, args.url]
                cmd.extend(["-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"])
                cmd.extend(robust_dl_options)
                if args.password: cmd.extend(["--video-password", args.password])
                commands_to_run.append({"name": "Download do Vídeo e Extração de Áudio", "command": cmd})

    # Comando do Whisper (só é adicionado se o método for whisper e o .txt não existir)
    if transcription_info['method'] == 'whisper':
        if not os.path.exists(paths['transcription_txt']):
            cmd = ["whisper", paths['audio'], "--language", "Portuguese", "--model", args.model, "--output_format", "txt", "--output_dir", paths['processing_dir']]
            commands_to_run.append({"name": "Transcrição (Whisper)", "command": cmd})

    # --- Log e Execução ---
    if not commands_to_run:
        print("\nTodos os arquivos intermediários necessários já existem. Pulando para a geração do prompt.")
    else:
        print(f"\n{'='*15} COMANDOS A SEREM EXECUTADOS {'='*15}\n")
        for i, step in enumerate(commands_to_run):
            command_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in step["command"])
            print(f"Passo {i+1}: {step['name']}")
            print(f"  Comando: {command_str}\n")
        
        try:
            confirmation = input("? Deseja continuar com a execução? (s/n): ")
            if confirmation.lower() not in ['s', 'sim']:
                print("\nOperação cancelada pelo usuário.")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário.")
            sys.exit(0)
        
        print(f"\n{'='*20} INICIANDO EXECUÇÃO {'='*21}\n")
        # --- Etapa de Execução ---
        for step in commands_to_run:
            print_step(f"Executando: {step['name']}")
            
            command_to_execute = step["command"]

            # NOTA: A lógica de aceleração por GPU (MPS) foi removida intencionalmente
            # devido a um bug de incompatibilidade persistente com o PyTorch no Mac,
            # que causa o erro 'NotImplementedError: aten::_sparse_coo_tensor_with_dims_and_tensors'.
            # O script agora usará a CPU para transcrição, o que é mais lento, porém mais estável.

            success, _ = run_command(command_to_execute)

            if not success:
                print_error(f"O passo '{step['name']}' falhou. Abortando.")
                sys.exit(1)

    # --- Pós-processamento e Geração do Prompt Final ---
    
    # Se usamos legenda, precisamos convertê-la para txt
    if transcription_info['method'] == 'subtitle' and not os.path.exists(paths['transcription_txt']):
        if not vtt_to_txt(paths['subtitle_vtt'], paths['transcription_txt']):
             sys.exit(1) # Sai se a conversão falhar

    # Leitura do conteúdo final da transcrição
    try:
        with open(paths['transcription_txt'], 'r', encoding='utf-8') as f:
            transcription_content = f.read().strip()
    except FileNotFoundError:
        print(f"ERRO: Arquivo de transcrição final não encontrado em '{paths['transcription_txt']}'")
        sys.exit(1)

    # Lógica para gerar o prompt final
    if args.mode == 'aula':
        title = f"{args.lesson_identifier}: {{tema_identificado_pela_ia}}"
        filename_template = f"{slugify(args.lesson_identifier)}_-_{{tema_em_slug}}.md"
        header = f"""**Tema Geral do Curso:** {args.main_topic}
**Identificador da Aula:** {args.lesson_identifier}"""
    else: # avulso
        title = args.title
        filename_template = f"{slugify(args.title)}.md"
        header = f"**Título do Estudo:** {args.title}"


    final_prompt = f"""Olá! Sua tarefa é analisar a transcrição de um vídeo e gerar o material de estudo consolidado.

{header}

**--- SUA TAREFA EM 3 PASSOS ---**

**PASSO 1: ANALISAR O CONTEÚDO**
- Leia a transcrição abaixo. 
- Para o modo 'aula', determine o tema específico e conciso desta aula.

**PASSO 2: CRIAR O ARQUIVO DE ESTUDO CONSOLIDADO**
- Use o tema que você identificou (para o modo 'aula') ou o título fornecido (para o modo 'avulso') para criar o nome do arquivo.
- Nome do arquivo a ser criado: `{filename_template}`
- **Ação:** Crie um NOVO e ÚNICO arquivo no seguinte caminho: `{paths['output_dir']}/{filename_template}`
- **Conteúdo do Arquivo:** O arquivo deve ser bem estruturado e conter as 3 seções abaixo, nesta ordem:

    ---
    
    # {title}

    ## 1. Artigo
    Gere um artigo **aprofundado e detalhado** sobre o tema. A estrutura deve ser rica, contendo:
    *   Uma **introdução** que apresenta o tema central.
    *   **Seções principais (###)** para cada sub-tópico abordado.
    *   **Definições formais** para termos teológicos ou técnicos importantes.
    *   Incorpore **citações diretas da transcrição**.
    *   Finalize com uma **conclusão** que resume os principais aprendizados.

    ## 2. Perguntas reflexivas e Respostas para Fixação
    Elabore de 3 a 5 perguntas pertinentes sobre o conteúdo que causem reflexão sobre o tema. Para **cada pergunta**, forneça uma **resposta detalhada** com pelo menos dois parágrafos, baseando-se exclusivamente na transcrição.

    ## 3. Prova Rápida
    Crie uma prova curta (4 a 6 perguntas) com uma mistura de **múltipla escolha** e **dissertativas curtas** para avaliar a compreensão do material. Indique a resposta correta para as de múltipla escolha.
    
    ## 4. Conteúdos Relacionados
    Faça uma lista com próximos conteúdos relacionados ao tema estudado, que poderiam ser uteis, ou que completem o estudo.

    ---

**PASSO 3: ATUALIZAR O ARQUIVO DE FONTES CENTRAL (SE APLICÁVEL)**
- **Ação:** Verifique a transcrição em busca de qualquer citação de livros, autores ou outras fontes.
- Se encontrar uma fonte nova, edite o arquivo `docs/teologia/fontes_de_referencia/todas_as_fontes.md` para adicioná-la.
- Se nenhuma fonte nova for citada, não faça nada neste passo e me avise.

---
**TRANSCRIÇÃO COMPLETA PARA ANÁLISE:**

{transcription_content}
"""
    print("\n" + "="*58)
    print("PROMPT FINAL GERADO. COPIE TODO O TEXTO ABAIXO E COLE PARA O ASSISTENTE:")
    print("="*58 + "\n")
    print(final_prompt)

if __name__ == "__main__":
    main() 