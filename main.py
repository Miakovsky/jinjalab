import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from jinja2 import * #Environment, PackageLoader, 
from urllib.parse import parse_qs

class MySiteHandler(SimpleHTTPRequestHandler):
    env = Environment(
        loader=PackageLoader('main'),
        autoescape=select_autoescape()
    )
    extensions_map={
        '.manifest': 'text/cache-manifest',
	'.html': 'text/html',
        '.png': 'image/png',
	'.jpg': 'image/jpg',
	'.svg':	'image/svg+xml',
	'.css':	'text/css',
	'.js':	'application/x-javascript',
	'': 'application/octet-stream',
    }

    def do_GET(self):
        if self.path == "/":
            self.render_index()
        elif self.path == "/about":
            self.render_about()
        elif self.path == "/games":
            self.render_games()
        elif self.path == "/news":
            self.render_news()
        elif self.path.startswith('/media/'):
            super().do_GET()
        else:
            self.render_404()
    
    def render_index(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        body = self.env.get_template('main.html').render()
        self.wfile.write(body.encode('utf-8'))

    def render_games(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        body = self.env.get_template('games.html').render(games=self.load_games())
        self.wfile.write(body.encode('utf-8'))

    def render_about(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        body = self.env.get_template('about.html').render()
        self.wfile.write(body.encode('utf-8'))
    
    def render_news(self, message=""):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        body = self.env.get_template('news.html').render(news=self.load_news())
        self.wfile.write(body.encode('utf-8'))
    
    def render_404(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('<h1>Not found</h1>'.encode('utf-8'))

    def load_games(self):
        with open("media/json/games.json", encoding='utf-8') as f:
            games = json.load(f)
            return games
    
    def load_news(self):
        with open("media/json/news.json", encoding='utf-8') as f:
            news = json.load(f)
            return news
    
    def load_emails(self):
        with open("media/json/emails.json", encoding='utf-8') as f:
            emaillist = []
            emails = json.load(f)
            print(emails)
            for email in emails:
                emaillist.append(email.get("email", []))
            return emails

    def register_email(self, email, email_list):
        with open("media/json/emails.json", 'w', encoding='utf-8') as f:
            data = []
            for e in email_list:
                data.append(e)
            data.append({"email": email})
            json.dump(data, f)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)
        print("Данные получены, точнее: ", data)
        entered = data.get('email', [''])[0]
        elist = self.load_emails()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        allemails = []
        for e in elist:
            allemails.append(e.get('email', ['']))
        if entered in allemails:
            body = self.env.get_template('news.html').render(message = f"Почта {entered} уже подписана!", news=self.load_news())
        elif entered == "":
            body = self.env.get_template('news.html').render(message = f"Пожалуйста, заполните поле.", news=self.load_news())
        else:
            body = self.env.get_template('news.html').render(message = f"Спасибо за подписку! Новости будут приходить на почту {entered}!", news=self.load_news())
            self.register_email(entered, elist)
        self.wfile.write(body.encode('utf-8'))
        #self.wfile.write(f"<html><body><h1>Спасибо за подписку! {data.get('email', [''])[0]}!</h1></body></html>".encode("utf-8"))
        
    
def run():
    httpd = HTTPServer(('', 8000), MySiteHandler)
    print('Server start')
    httpd.serve_forever()

if __name__ == '__main__':
    run()