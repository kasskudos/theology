#!/usr/bin/env python3
"""
Script para buscar comentários de um post do Instagram usando a Instagram Graph API.

REQUISITOS:
- Conta Business ou Creator no Instagram
- App criado no Facebook Developers
- Access Token com permissões adequadas
- ID do post do Instagram (Media ID)

LIMITAÇÕES:
- Só é possível acessar comentários de posts da SUA PRÓPRIA conta
- Ou de contas que você gerencia/possui permissão
- Não é possível acessar comentários de posts públicos de outras pessoas
"""

import requests
import json
import argparse
import sys
from typing import Dict, List, Optional


class InstagramAPI:
    """Classe para interagir com a Instagram Graph API."""
    
    def __init__(self, access_token: str):
        """
        Inicializa a API do Instagram.
        
        Args:
            access_token: Token de acesso do Instagram Graph API
        """
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def get_post_comments(self, media_id: str, limit: int = 100) -> List[Dict]:
        """
        Busca comentários de um post específico.
        
        Args:
            media_id: ID do post (Media ID) do Instagram
            limit: Número máximo de comentários a retornar (padrão: 100)
            
        Returns:
            Lista de comentários com informações completas
        """
        endpoint = f"{self.base_url}/{media_id}/comments"
        
        params = {
            'access_token': self.access_token,
            'fields': 'id,text,username,timestamp,like_count,replies',
            'limit': limit
        }
        
        all_comments = []
        
        try:
            while True:
                response = requests.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if 'data' in data:
                    all_comments.extend(data['data'])
                    
                    # Verifica se há mais páginas
                    if 'paging' in data and 'next' in data['paging']:
                        endpoint = data['paging']['next']
                        params = {}  # O next já contém todos os parâmetros
                    else:
                        break
                else:
                    break
            
            return all_comments
            
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            error_msg = error_data.get('error', {}).get('message', str(e))
            raise Exception(f"Erro ao buscar comentários: {error_msg}")
        except Exception as e:
            raise Exception(f"Erro inesperado: {str(e)}")
    
    def get_post_info(self, media_id: str) -> Dict:
        """
        Busca informações básicas de um post.
        
        Args:
            media_id: ID do post (Media ID) do Instagram
            
        Returns:
            Dicionário com informações do post
        """
        endpoint = f"{self.base_url}/{media_id}"
        
        params = {
            'access_token': self.access_token,
            'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count'
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            error_msg = error_data.get('error', {}).get('message', str(e))
            raise Exception(f"Erro ao buscar informações do post: {error_msg}")


def format_comment(comment: Dict, index: int) -> str:
    """Formata um comentário para exibição."""
    text = comment.get('text', '(sem texto)')
    username = comment.get('username', 'desconhecido')
    timestamp = comment.get('timestamp', '')
    likes = comment.get('like_count', 0)
    
    formatted = f"\n--- Comentário #{index} ---\n"
    formatted += f"Usuário: @{username}\n"
    formatted += f"Data: {timestamp}\n"
    formatted += f"Curtidas: {likes}\n"
    formatted += f"Texto: {text}\n"
    
    # Verifica se há respostas
    if 'replies' in comment and 'data' in comment['replies']:
        replies = comment['replies']['data']
        if replies:
            formatted += f"\n  Respostas ({len(replies)}):\n"
            for reply in replies:
                reply_username = reply.get('username', 'desconhecido')
                reply_text = reply.get('text', '(sem texto)')
                formatted += f"    - @{reply_username}: {reply_text}\n"
    
    return formatted


def save_comments_to_file(comments: List[Dict], output_file: str):
    """Salva comentários em um arquivo JSON."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Comentários salvos em: {output_file}")


def save_comments_to_markdown(comments: List[Dict], post_info: Optional[Dict], output_file: str):
    """Salva comentários em formato Markdown."""
    with open(output_file, 'w', encoding='utf-8') as f:
        if post_info:
            caption = post_info.get('caption', 'N/A')
            f.write(f"# Análise de Comentários - Post do Instagram\n\n")
            f.write(f"**Legenda do Post:** {caption}\n\n")
            f.write(f"**Total de Comentários:** {len(comments)}\n\n")
            f.write("---\n\n")
        
        for i, comment in enumerate(comments, 1):
            text = comment.get('text', '(sem texto)')
            username = comment.get('username', 'desconhecido')
            timestamp = comment.get('timestamp', '')
            likes = comment.get('like_count', 0)
            
            f.write(f"## Comentário #{i}\n\n")
            f.write(f"- **Usuário:** @{username}\n")
            f.write(f"- **Data:** {timestamp}\n")
            f.write(f"- **Curtidas:** {likes}\n\n")
            f.write(f"{text}\n\n")
            
            # Respostas
            if 'replies' in comment and 'data' in comment['replies']:
                replies = comment['replies']['data']
                if replies:
                    f.write(f"### Respostas ({len(replies)})\n\n")
                    for reply in replies:
                        reply_username = reply.get('username', 'desconhecido')
                        reply_text = reply.get('text', '(sem texto)')
                        f.write(f"- **@{reply_username}:** {reply_text}\n\n")
            
            f.write("---\n\n")
    
    print(f"\n✅ Comentários salvos em Markdown: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Busca comentários de um post do Instagram usando a Graph API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLOS DE USO:

1. Buscar comentários e exibir no terminal:
   python comentar_post.py --token SEU_TOKEN --post-id POST_ID

2. Salvar comentários em arquivo JSON:
   python comentar_post.py --token SEU_TOKEN --post-id POST_ID --output comentarios.json

3. Salvar comentários em Markdown:
   python comentar_post.py --token SEU_TOKEN --post-id POST_ID --output comentarios.md --format markdown

COMO OBTER O MEDIA ID:
- O Media ID não é o mesmo que a URL do post
- Você pode usar ferramentas online como: https://www.instagram.com/p/{shortcode}/?__a=1
- Ou usar a API para listar seus posts e encontrar o ID
- O Media ID geralmente é um número longo (ex: 1234567890123456789)

IMPORTANTE:
- Você só pode acessar comentários de posts da SUA PRÓPRIA conta
- Não é possível acessar comentários de posts públicos de outras pessoas
- É necessário ter uma conta Business ou Creator no Instagram
        """
    )
    
    parser.add_argument(
        '--token',
        required=True,
        help='Access Token do Instagram Graph API'
    )
    
    parser.add_argument(
        '--post-id',
        required=True,
        dest='post_id',
        help='Media ID do post do Instagram'
    )
    
    parser.add_argument(
        '--output',
        help='Arquivo para salvar os comentários (JSON ou Markdown)'
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'markdown'],
        default='json',
        help='Formato do arquivo de saída (padrão: json)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Número máximo de comentários a buscar (padrão: 100)'
    )
    
    parser.add_argument(
        '--show-post-info',
        action='store_true',
        help='Exibe informações do post antes dos comentários'
    )
    
    args = parser.parse_args()
    
    # Inicializa a API
    api = InstagramAPI(args.token)
    
    try:
        # Busca informações do post (opcional)
        post_info = None
        if args.show_post_info or (args.output and args.format == 'markdown'):
            print("📋 Buscando informações do post...")
            post_info = api.get_post_info(args.post_id)
            if args.show_post_info:
                print("\n" + "="*50)
                print("INFORMAÇÕES DO POST")
                print("="*50)
                print(f"ID: {post_info.get('id')}")
                print(f"Legenda: {post_info.get('caption', 'N/A')[:100]}...")
                print(f"Curtidas: {post_info.get('like_count', 0)}")
                print(f"Comentários: {post_info.get('comments_count', 0)}")
                print(f"URL: {post_info.get('permalink', 'N/A')}")
                print("="*50 + "\n")
        
        # Busca comentários
        print(f"🔍 Buscando comentários do post {args.post_id}...")
        comments = api.get_post_comments(args.post_id, limit=args.limit)
        
        print(f"✅ Encontrados {len(comments)} comentários\n")
        
        # Exibe comentários no terminal
        if not args.output:
            for i, comment in enumerate(comments, 1):
                print(format_comment(comment, i))
        
        # Salva em arquivo se especificado
        if args.output:
            if args.format == 'json':
                save_comments_to_file(comments, args.output)
            elif args.format == 'markdown':
                save_comments_to_markdown(comments, post_info, args.output)
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

