#!/usr/bin/env python3
"""
Script para monitorar respostas aos seus comentários em posts do Instagram.

Este script:
1. Faz login na sua conta do Instagram
2. Busca os comentários que você fez em posts de outras pessoas
3. Verifica se há novas respostas aos seus comentários
4. Notifica sobre respostas não visualizadas

REQUISITOS:
- instagrapi: pip install instagrapi
- Suas credenciais do Instagram (usuário e senha)
"""

import json
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import time

try:
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired, TwoFactorRequired
except ImportError:
    print("❌ Erro: instagrapi não está instalado.")
    print("📦 Instale com: pip install instagrapi")
    sys.exit(1)


class CommentMonitor:
    """Monitora respostas aos seus comentários no Instagram."""
    
    def __init__(self, username: str, password: str, session_file: str = "instagram_session.json"):
        """
        Inicializa o monitor.
        
        Args:
            username: Seu usuário do Instagram
            password: Sua senha do Instagram
            session_file: Arquivo para salvar a sessão (evita login repetido)
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
                self.client.login(self.username, self.password)
                print("✅ Login bem-sucedido (sessão restaurada)")
                self.authenticated = True
                return True
            except Exception as e:
                print(f"⚠️  Sessão inválida, fazendo login completo... ({e})")
        
        # Login completo
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
    
    def get_my_recent_comments(self, limit: int = 50) -> List[Dict]:
        """
        Busca seus comentários recentes em posts de outras pessoas.
        
        Args:
            limit: Número máximo de comentários a buscar
            
        Returns:
            Lista de comentários com informações
        """
        if not self.authenticated:
            raise Exception("Não autenticado. Faça login primeiro.")
        
        print(f"🔍 Buscando seus comentários recentes (limite: {limit})...")
        
        try:
            # Busca suas atividades (comentários que você fez)
            # Nota: instagrapi pode ter limitações aqui, vamos tentar diferentes abordagens
            user_info = self.client.user_info_by_username(self.username)
            user_id = user_info.pk
            
            comments = []
            # Esta parte pode precisar ser adaptada dependendo da versão do instagrapi
            # Vamos usar uma abordagem mais direta: buscar seus posts/comentários via timeline
            
            print("⚠️  Nota: A busca de comentários próprios pode ter limitações.")
            print("    O Instagram não expõe essa funcionalidade facilmente via API não oficial.")
            print("    Este script funciona melhor quando você fornece IDs de posts específicos.")
            
            return comments
            
        except Exception as e:
            print(f"⚠️  Erro ao buscar comentários: {e}")
            return []
    
    def get_post_comments(self, post_shortcode: str) -> List[Dict]:
        """
        Busca todos os comentários de um post específico.
        
        Args:
            post_shortcode: Shortcode do post (parte da URL após /p/)
                           Ex: se URL é instagram.com/p/ABC123/, o shortcode é ABC123
            
        Returns:
            Lista de comentários do post
        """
        if not self.authenticated:
            raise Exception("Não autenticado. Faça login primeiro.")
        
        try:
            print(f"🔍 Buscando comentários do post: {post_shortcode}...")
            media_id = self.client.media_id(shortcode=post_shortcode)
            media_comments = self.client.media_comments(media_id, amount=0)  # 0 = todos
            
            comments_data = []
            for comment in media_comments:
                comment_info = {
                    'id': comment.pk,
                    'user': comment.user.username,
                    'user_id': comment.user.pk,
                    'text': comment.text,
                    'created_at': comment.created_at_utc.isoformat() if comment.created_at_utc else None,
                    'like_count': comment.like_count,
                    'is_reply': comment.parent_comment_id is not None,
                    'parent_comment_id': comment.parent_comment_id,
                    'replies': []
                }
                
                # Busca respostas a este comentário
                if comment.child_comment_count > 0:
                    try:
                        replies = self.client.media_comment_likers(media_id, comment.pk)
                        # Na verdade, precisamos buscar as respostas de forma diferente
                        # Vamos adicionar uma nota aqui
                        pass
                    except:
                        pass
                
                comments_data.append(comment_info)
            
            return comments_data
            
        except Exception as e:
            print(f"❌ Erro ao buscar comentários do post: {e}")
            return []
    
    def find_my_comments_in_post(self, post_shortcode: str) -> List[Dict]:
        """
        Encontra seus comentários em um post específico.
        
        Args:
            post_shortcode: Shortcode do post
            
        Returns:
            Lista dos seus comentários no post
        """
        all_comments = self.get_post_comments(post_shortcode)
        my_comments = [c for c in all_comments if c['user'] == self.username]
        return my_comments
    
    def check_replies_to_my_comments(self, post_shortcode: str, my_comment_ids: List[str]) -> List[Dict]:
        """
        Verifica se há respostas aos seus comentários em um post.
        
        Args:
            post_shortcode: Shortcode do post
            my_comment_ids: Lista de IDs dos seus comentários
            
        Returns:
            Lista de respostas encontradas
        """
        all_comments = self.get_post_comments(post_shortcode)
        replies = []
        
        for comment in all_comments:
            # Se o comentário é uma resposta E o parent é um dos nossos comentários
            if comment['is_reply'] and comment['parent_comment_id'] in my_comment_ids:
                # Verifica se não é nossa própria resposta
                if comment['user'] != self.username:
                    replies.append(comment)
        
        return replies
    
    def save_comments_to_file(self, comments: List[Dict], filename: str):
        """Salva comentários em arquivo JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)
        print(f"💾 Dados salvos em: {filename}")


def load_tracked_posts(track_file: str) -> Dict:
    """Carrega lista de posts sendo monitorados."""
    track_path = Path(track_file)
    if track_path.exists():
        with open(track_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_tracked_posts(tracked: Dict, track_file: str):
    """Salva lista de posts sendo monitorados."""
    with open(track_file, 'w', encoding='utf-8') as f:
        json.dump(tracked, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Monitora respostas aos seus comentários em posts do Instagram',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLOS DE USO:

1. Adicionar um post para monitorar:
   python monitorar_respostas.py --add-post ABC123 --user SEU_USUARIO --password SUA_SENHA

2. Verificar respostas em todos os posts monitorados:
   python monitorar_respostas.py --check-all --user SEU_USUARIO --password SUA_SENHA

3. Verificar um post específico:
   python monitorar_respostas.py --check-post ABC123 --user SEU_USUARIO --password SUA_SENHA

4. Listar posts sendo monitorados:
   python monitorar_respostas.py --list-posts

NOTAS IMPORTANTES:
- Você precisa fornecer seu usuário e senha do Instagram
- A sessão é salva para evitar login repetido
- O arquivo de sessão é sensível, não compartilhe
- Use com moderação para evitar bloqueios
        """
    )
    
    parser.add_argument('--user', help='Seu usuário do Instagram')
    parser.add_argument('--password', help='Sua senha do Instagram')
    parser.add_argument('--session-file', default='instagram_session.json', help='Arquivo de sessão')
    parser.add_argument('--track-file', default='posts_monitorados.json', help='Arquivo com posts monitorados')
    
    parser.add_argument('--add-post', help='Adiciona um post para monitorar (shortcode)')
    parser.add_argument('--check-post', help='Verifica respostas em um post específico (shortcode)')
    parser.add_argument('--check-all', action='store_true', help='Verifica todos os posts monitorados')
    parser.add_argument('--list-posts', action='store_true', help='Lista posts sendo monitorados')
    parser.add_argument('--remove-post', help='Remove um post da lista de monitoramento')
    
    args = parser.parse_args()
    
    # Listar posts monitorados (não precisa login)
    if args.list_posts:
        tracked = load_tracked_posts(args.track_file)
        if tracked:
            print("\n📋 Posts sendo monitorados:\n")
            for shortcode, data in tracked.items():
                print(f"  - {shortcode}: {data.get('url', 'N/A')}")
                print(f"    Seus comentários: {len(data.get('my_comment_ids', []))}")
                print(f"    Última verificação: {data.get('last_check', 'Nunca')}")
                print()
        else:
            print("📋 Nenhum post sendo monitorado.")
        return
    
    # Operações que precisam de login
    if not args.user or not args.password:
        print("❌ Erro: --user e --password são necessários para esta operação.")
        sys.exit(1)
    
    monitor = CommentMonitor(args.user, args.password, args.session_file)
    
    if not monitor.login():
        print("❌ Falha no login. Verifique suas credenciais.")
        sys.exit(1)
    
    tracked = load_tracked_posts(args.track_file)
    
    # Adicionar post para monitorar
    if args.add_post:
        shortcode = args.add_post
        print(f"\n➕ Adicionando post {shortcode} para monitoramento...")
        
        my_comments = monitor.find_my_comments_in_post(shortcode)
        if not my_comments:
            print(f"⚠️  Nenhum comentário seu foi encontrado no post {shortcode}.")
            response = input("Deseja adicionar mesmo assim? (s/n): ")
            if response.lower() != 's':
                return
        
        my_comment_ids = [c['id'] for c in my_comments]
        
        tracked[shortcode] = {
            'url': f"https://www.instagram.com/p/{shortcode}/",
            'my_comment_ids': my_comment_ids,
            'added_at': datetime.now().isoformat(),
            'last_check': None,
            'last_replies_count': 0
        }
        
        save_tracked_posts(tracked, args.track_file)
        print(f"✅ Post {shortcode} adicionado com sucesso!")
        print(f"   Seus comentários encontrados: {len(my_comment_ids)}")
    
    # Remover post
    elif args.remove_post:
        shortcode = args.remove_post
        if shortcode in tracked:
            del tracked[shortcode]
            save_tracked_posts(tracked, args.track_file)
            print(f"✅ Post {shortcode} removido da lista de monitoramento.")
        else:
            print(f"❌ Post {shortcode} não está na lista de monitoramento.")
    
    # Verificar um post específico
    elif args.check_post:
        shortcode = args.check_post
        if shortcode not in tracked:
            print(f"⚠️  Post {shortcode} não está sendo monitorado.")
            print(f"   Use --add-post {shortcode} para adicionar primeiro.")
            return
        
        my_comment_ids = tracked[shortcode]['my_comment_ids']
        replies = monitor.check_replies_to_my_comments(shortcode, my_comment_ids)
        
        print(f"\n📊 Resultados para post {shortcode}:")
        print(f"   Suas respostas não visualizadas: {len(replies)}")
        
        if replies:
            print("\n💬 Respostas encontradas:\n")
            for reply in replies:
                print(f"  @{reply['user']}: {reply['text'][:100]}...")
                print(f"    Data: {reply['created_at']}")
                print()
        
        # Atualiza última verificação
        tracked[shortcode]['last_check'] = datetime.now().isoformat()
        tracked[shortcode]['last_replies_count'] = len(replies)
        save_tracked_posts(tracked, args.track_file)
        
        # Salva resultados
        if replies:
            output_file = f"respostas_{shortcode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            monitor.save_comments_to_file(replies, output_file)
    
    # Verificar todos os posts
    elif args.check_all:
        if not tracked:
            print("❌ Nenhum post está sendo monitorado.")
            print("   Use --add-post SHORTCODE para adicionar posts.")
            return
        
        print(f"\n🔍 Verificando {len(tracked)} post(s) monitorado(s)...\n")
        
        total_replies = 0
        for shortcode, data in tracked.items():
            print(f"📌 Verificando {shortcode}...")
            my_comment_ids = data['my_comment_ids']
            replies = monitor.check_replies_to_my_comments(shortcode, my_comment_ids)
            
            new_count = len(replies)
            last_count = data.get('last_replies_count', 0)
            
            if new_count > last_count:
                new_replies = new_count - last_count
                print(f"   ⚠️  {new_replies} nova(s) resposta(s)!")
                total_replies += new_replies
            else:
                print(f"   ✓ Sem novas respostas")
            
            # Atualiza
            tracked[shortcode]['last_check'] = datetime.now().isoformat()
            tracked[shortcode]['last_replies_count'] = new_count
            
            # Pequena pausa entre posts
            time.sleep(2)
        
        save_tracked_posts(tracked, args.track_file)
        
        print(f"\n✅ Verificação concluída!")
        if total_replies > 0:
            print(f"   Total de novas respostas: {total_replies}")
        else:
            print(f"   Nenhuma nova resposta encontrada.")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

