#!/usr/bin/env python3
"""
Script para extrair comentários de qualquer post público do Instagram.

Este script:
1. Faz login na sua conta (necessário para acessar posts)
2. Pega TODOS os comentários de um post público
3. Salva em JSON ou Markdown

REQUISITOS:
- instagrapi: pip install instagrapi
- Suas credenciais do Instagram (usuário e senha)
"""

import json
import argparse
import sys
from datetime import datetime
from typing import Dict, List
from pathlib import Path
import re

try:
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired, TwoFactorRequired
except ImportError:
    print("❌ Erro: instagrapi não está instalado.")
    print("📦 Instale com: pip install instagrapi")
    sys.exit(1)


def extract_shortcode_from_url(url: str) -> str:
    """
    Extrai o shortcode de uma URL do Instagram.
    
    Exemplos:
    - https://www.instagram.com/p/ABC123/ -> ABC123
    - https://instagram.com/p/ABC123/ -> ABC123
    - instagram.com/p/ABC123/?utm_source=... -> ABC123
    """
    # Remove espaços e quebras de linha
    url = url.strip()
    
    # Padrões comuns de URL do Instagram
    patterns = [
        r'instagram\.com/p/([A-Za-z0-9_-]+)',
        r'instagram\.com/reel/([A-Za-z0-9_-]+)',
        r'/p/([A-Za-z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # Se não encontrou padrão, assume que já é o shortcode
    return url.split('/')[-1].split('?')[0]


class InstagramCommentExtractor:
    """Extrai comentários de posts do Instagram."""
    
    def __init__(self, username: str = None, password: str = None, session_file: str = "instagram_session.json"):
        """
        Inicializa o extrator.
        
        Args:
            username: Seu usuário do Instagram (opcional se já tiver sessão)
            password: Sua senha do Instagram (opcional se já tiver sessão)
            session_file: Arquivo para salvar/carregar a sessão
        """
        self.username = username
        self.password = password
        self.session_file = Path(session_file)
        self.client = Client()
        self.authenticated = False
    
    def login(self) -> bool:
        """
        Faz login no Instagram. Tenta usar sessão salva primeiro.
        
        Returns:
            True se login bem-sucedido, False caso contrário
        """
        # Tenta carregar sessão salva
        if self.session_file.exists():
            try:
                print("🔐 Tentando restaurar sessão salva...")
                self.client.load_settings(self.session_file)
                if self.username and self.password:
                    self.client.login(self.username, self.password)
                else:
                    # Tenta fazer login apenas com a sessão
                    # Se a sessão for válida, não precisa de credenciais
                    try:
                        # Testa se a sessão ainda é válida tentando buscar seu perfil
                        self.client.account_info()
                        print("✅ Sessão válida restaurada")
                        self.authenticated = True
                        return True
                    except:
                        print("⚠️  Sessão expirada, precisa fazer login completo")
                        if not self.username or not self.password:
                            return False
                        self.client.login(self.username, self.password)
                
                # Salva a sessão
                self.client.dump_settings(self.session_file)
                print("✅ Login bem-sucedido (sessão restaurada)")
                self.authenticated = True
                return True
            except Exception as e:
                print(f"⚠️  Sessão inválida, fazendo login completo... ({e})")
        
        # Login completo (só se tiver credenciais)
        if not self.username or not self.password:
            print("❌ Erro: Credenciais necessárias para fazer login.")
            return False
        
        try:
            print(f"🔐 Fazendo login como @{self.username}...")
            self.client.login(self.username, self.password)
            
            # Salva a sessão
            self.client.dump_settings(self.session_file)
            print("✅ Login bem-sucedido")
            self.authenticated = True
            return True
            
        except TwoFactorRequired:
            print("\n🔐 Autenticação de dois fatores necessária.")
            code = input("Digite o código de verificação: ")
            try:
                self.client.two_factor_login(code)
                self.client.dump_settings(self.session_file)
                print("✅ Login bem-sucedido (2FA)")
                self.authenticated = True
                return True
            except Exception as e:
                print(f"❌ Erro na autenticação 2FA: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            return False
    
    def get_post_comments(self, shortcode: str, amount: int = 0) -> Dict:
        """
        Busca todos os comentários de um post.
        
        Args:
            shortcode: Shortcode do post (ou URL completa)
            amount: Número de comentários (0 = todos)
            
        Returns:
            Dicionário com informações do post e comentários
        """
        if not self.authenticated:
            raise Exception("Não autenticado. Faça login primeiro.")
        
        # Extrai shortcode da URL se necessário
        shortcode = extract_shortcode_from_url(shortcode)
        
        print(f"🔍 Buscando comentários do post: {shortcode}...")
        
        try:
            # Obtém informações do post
            media_id = self.client.media_id(shortcode=shortcode)
            media_info = self.client.media_info(media_id)
            
            print(f"📌 Post: {media_info.caption[:100] if media_info.caption else 'Sem legenda'}...")
            
            # Busca comentários (amount=0 busca todos)
            print("📥 Carregando comentários (isso pode levar um tempo)...")
            comments = self.client.media_comments(media_id, amount=amount)
            
            print(f"✅ Encontrados {len(comments)} comentários")
            
            # Processa comentários
            comments_data = []
            for comment in comments:
                comment_data = {
                    'id': comment.pk,
                    'user': comment.user.username,
                    'user_id': comment.user.pk,
                    'full_name': comment.user.full_name,
                    'text': comment.text,
                    'created_at': comment.created_at_utc.isoformat() if comment.created_at_utc else None,
                    'like_count': comment.comment_like_count,
                    'is_reply': comment.parent_comment_pk is not None,
                    'parent_comment_id': comment.parent_comment_pk,
                    'child_comment_count': comment.child_comment_count,
                }
                
                comments_data.append(comment_data)
            
            # Organiza comentários e respostas
            organized_comments = self._organize_comments(comments_data)
            
            return {
                'post': {
                    'shortcode': shortcode,
                    'media_id': media_id,
                    'url': f"https://www.instagram.com/p/{shortcode}/",
                    'caption': media_info.caption,
                    'like_count': media_info.like_count,
                    'comment_count': media_info.comment_count,
                    'username': media_info.user.username,
                    'timestamp': media_info.taken_at.isoformat() if media_info.taken_at else None,
                },
                'comments': organized_comments,
                'total_comments': len(comments_data),
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erro ao buscar comentários: {e}")
            raise
    
    def _organize_comments(self, comments: List[Dict]) -> List[Dict]:
        """
        Organiza comentários agrupando respostas com seus comentários pais.
        """
        # Separa comentários principais e respostas
        main_comments = {c['id']: c for c in comments if not c['is_reply']}
        replies = [c for c in comments if c['is_reply']]
        
        # Adiciona respostas aos comentários principais
        for reply in replies:
            parent_id = reply['parent_comment_id']
            if parent_id in main_comments:
                if 'replies' not in main_comments[parent_id]:
                    main_comments[parent_id]['replies'] = []
                main_comments[parent_id]['replies'].append(reply)
        
        # Retorna lista ordenada
        return list(main_comments.values())


def save_to_json(data: Dict, filename: str):
    """Salva dados em arquivo JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Dados salvos em JSON: {filename}")


def save_to_markdown(data: Dict, filename: str):
    """Salva comentários em formato Markdown."""
    post = data['post']
    comments = data['comments']
    
    with open(filename, 'w', encoding='utf-8') as f:
        # Cabeçalho
        f.write(f"# Comentários do Post do Instagram\n\n")
        f.write(f"**Post:** [{post['shortcode']}]({post['url']})\n\n")
        f.write(f"**Autor:** @{post['username']}\n\n")
        f.write(f"**Legenda:** {post['caption'] or 'Sem legenda'}\n\n")
        f.write(f"**Curtidas:** {post['like_count']}\n\n")
        f.write(f"**Total de Comentários:** {data['total_comments']}\n\n")
        f.write(f"**Extraído em:** {data['extracted_at']}\n\n")
        f.write("---\n\n")
        
        # Comentários
        for i, comment in enumerate(comments, 1):
            f.write(f"## Comentário #{i}\n\n")
            f.write(f"- **Usuário:** @{comment['user']} ({comment['full_name']})\n")
            f.write(f"- **Data:** {comment['created_at']}\n")
            f.write(f"- **Curtidas:** {comment['like_count']}\n\n")
            f.write(f"{comment['text']}\n\n")
            
            # Respostas
            if 'replies' in comment and comment['replies']:
                f.write(f"### Respostas ({len(comment['replies'])})\n\n")
                for reply in comment['replies']:
                    f.write(f"- **@{reply['user']}** ({reply['full_name']}): {reply['text']}\n")
                    f.write(f"  _Curtidas: {reply['like_count']} | Data: {reply['created_at']}_\n\n")
            
            f.write("---\n\n")


def main():
    parser = argparse.ArgumentParser(
        description='Extrai comentários de qualquer post público do Instagram',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLOS DE USO:

1. Extrair comentários usando URL completa:
   python pegar_comentarios.py --url "https://www.instagram.com/p/ABC123/" --user SEU_USUARIO --password SUA_SENHA

2. Extrair comentários usando shortcode:
   python pegar_comentarios.py --shortcode ABC123 --user SEU_USUARIO --password SUA_SENHA

3. Salvar em Markdown:
   python pegar_comentarios.py --shortcode ABC123 --output comentarios.md --format markdown --user SEU_USUARIO --password SUA_SENHA

4. Se já tiver sessão salva, pode omitir credenciais:
   python pegar_comentarios.py --shortcode ABC123 --output comentarios.json

NOTAS:
- Você precisa fazer login pelo menos uma vez
- A sessão é salva automaticamente
- Funciona com posts públicos
- Pode levar tempo para posts com muitos comentários
        """
    )
    
    parser.add_argument('--url', help='URL completa do post do Instagram')
    parser.add_argument('--shortcode', help='Shortcode do post (parte da URL após /p/)')
    parser.add_argument('--user', help='Seu usuário do Instagram (necessário na primeira vez)')
    parser.add_argument('--password', help='Sua senha do Instagram (necessário na primeira vez)')
    parser.add_argument('--output', help='Arquivo de saída (JSON ou Markdown)')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json', help='Formato de saída')
    parser.add_argument('--session-file', default='instagram_session.json', help='Arquivo de sessão')
    parser.add_argument('--limit', type=int, default=0, help='Limitar número de comentários (0 = todos)')
    
    args = parser.parse_args()
    
    # Validação
    if not args.url and not args.shortcode:
        print("❌ Erro: Você deve fornecer --url ou --shortcode")
        parser.print_help()
        sys.exit(1)
    
    shortcode = args.shortcode or extract_shortcode_from_url(args.url)
    
    # Inicializa extrator
    extractor = InstagramCommentExtractor(
        username=args.user,
        password=args.password,
        session_file=args.session_file
    )
    
    # Login (tenta usar sessão salva primeiro)
    if not extractor.login():
        print("❌ Falha no login. Verifique suas credenciais.")
        sys.exit(1)
    
    try:
        # Extrai comentários
        data = extractor.get_post_comments(shortcode, amount=args.limit)
        
        # Salva ou exibe
        if args.output:
            if args.format == 'json':
                save_to_json(data, args.output)
            else:
                save_to_markdown(data, args.output)
        else:
            # Exibe resumo no terminal
            print("\n" + "="*60)
            print("RESUMO")
            print("="*60)
            print(f"Post: {data['post']['url']}")
            print(f"Autor: @{data['post']['username']}")
            print(f"Total de comentários: {data['total_comments']}")
            print(f"Curtidas: {data['post']['like_count']}")
            print("\n💡 Use --output para salvar os comentários completos")
            print("="*60)
    
    except Exception as e:
        print(f"\n❌ Erro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

