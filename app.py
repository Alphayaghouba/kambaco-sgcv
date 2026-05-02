from flask import Flask, request, make_response, send_from_directory
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime
import random
import urllib.parse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import mm
import hashlib
import os


app = Flask(__name__)

SECRET_KEY = "sgcv_village_secret_key_2026"

def hash_password(password):
    return password  # Temporaire - sans hashage

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = 'postgresql://postgres:admin123@localhost:5432/village_db'
    conn = psycopg2.connect(
        database_url,
        cursor_factory=RealDictCursor
    )
    return conn

# ================== LISTE DES PAYS ==================
PAYS = [
    {'code': '+224', 'nom': '🇬🇳 Guinée', 'drapeau': '🇬🇳'},
    {'code': '+221', 'nom': '🇸🇳 Sénégal', 'drapeau': '🇸🇳'},
    {'code': '+223', 'nom': '🇲🇱 Mali', 'drapeau': '🇲🇱'},
    {'code': '+225', 'nom': '🇨🇮 Côte d\'Ivoire', 'drapeau': '🇨🇮'},
    {'code': '+226', 'nom': '🇧🇫 Burkina Faso', 'drapeau': '🇧🇫'},
    {'code': '+229', 'nom': '🇧🇯 Bénin', 'drapeau': '🇧🇯'},
    {'code': '+227', 'nom': '🇳🇪 Niger', 'drapeau': '🇳🇪'},
    {'code': '+228', 'nom': '🇹🇬 Togo', 'drapeau': '🇹🇬'},
    {'code': '+232', 'nom': '🇸🇱 Sierra Leone', 'drapeau': '🇸🇱'},
    {'code': '+231', 'nom': '🇱🇷 Liberia', 'drapeau': '🇱🇷'},
    {'code': '+233', 'nom': '🇬🇭 Ghana', 'drapeau': '🇬🇭'},
    {'code': '+234', 'nom': '🇳🇬 Nigeria', 'drapeau': '🇳🇬'},
    {'code': '+237', 'nom': '🇨🇲 Cameroun', 'drapeau': '🇨🇲'},
    {'code': '+241', 'nom': '🇬🇦 Gabon', 'drapeau': '🇬🇦'},
    {'code': '+242', 'nom': '🇨🇬 Congo', 'drapeau': '🇨🇬'},
    {'code': '+243', 'nom': '🇨🇩 RDC', 'drapeau': '🇨🇩'},
    {'code': '+235', 'nom': '🇹🇩 Tchad', 'drapeau': '🇹🇩'},
    {'code': '+236', 'nom': '🇨🇫 Centrafrique', 'drapeau': '🇨🇫'},
    {'code': '+213', 'nom': '🇩🇿 Algérie', 'drapeau': '🇩🇿'},
    {'code': '+216', 'nom': '🇹🇳 Tunisie', 'drapeau': '🇹🇳'},
    {'code': '+212', 'nom': '🇲🇦 Maroc', 'drapeau': '🇲🇦'},
    {'code': '+222', 'nom': '🇲🇷 Mauritanie', 'drapeau': '🇲🇷'},
    {'code': '+220', 'nom': '🇬🇲 Gambie', 'drapeau': '🇬🇲'},
    {'code': '+245', 'nom': '🇬🇼 Guinée-Bissau', 'drapeau': '🇬🇼'},
    {'code': '+240', 'nom': '🇬🇶 Guinée Équatoriale', 'drapeau': '🇬🇶'},
    {'code': '+33', 'nom': '🇫🇷 France', 'drapeau': '🇫🇷'},
    {'code': '+32', 'nom': '🇧🇪 Belgique', 'drapeau': '🇧🇪'},
    {'code': '+1', 'nom': '🇺🇸 USA/Canada', 'drapeau': '🇺🇸'},
    {'code': '+44', 'nom': '🇬🇧 Royaume-Uni', 'drapeau': '🇬🇧'},
    {'code': '+49', 'nom': '🇩🇪 Allemagne', 'drapeau': '🇩🇪'},
    {'code': '+39', 'nom': '🇮🇹 Italie', 'drapeau': '🇮🇹'},
    {'code': '+34', 'nom': '🇪🇸 Espagne', 'drapeau': '🇪🇸'},
    {'code': '+86', 'nom': '🇨🇳 Chine', 'drapeau': '🇨🇳'},
    {'code': '+971', 'nom': '🇦🇪 Émirats', 'drapeau': '🇦🇪'},
]

# ================== STYLE CSS PREMIUM ==================
STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: linear-gradient(160deg, #06061a 0%, #0d0d35 30%, #12082e 60%, #0a0a1e 100%);
        min-height: 100vh;
        color: #f0f0f5;
        line-height: 1.6;
    }
    
    .hero {
        background: linear-gradient(135deg, rgba(108, 45, 255, 0.15) 0%, rgba(255, 107, 157, 0.1) 50%, rgba(108, 45, 255, 0.08) 100%);
        padding: 70px 20px; text-align: center; position: relative;
        border-bottom: 1px solid rgba(255,107,157,0.2);
    }
    
    .hero::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at 50% 50%, rgba(255,107,157,0.08) 0%, transparent 70%);
    }
    
    .hero h1 {
        font-size: 2.8em; font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #ffb8d0 50%, #c4a0ff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        margin-bottom: 12px; position: relative;
    }
    
    .hero .emoji-big { font-size: 4em; display: block; animation: float 3s ease-in-out infinite; position: relative; }
    .hero p { font-size: 1.2em; font-weight: 400; color: #c4b5e0; position: relative; }
    
    .hero .badge {
        display: inline-block; background: linear-gradient(135deg, #FF6B9D, #c44dff); color: #fff;
        padding: 10px 24px; border-radius: 50px; margin-top: 20px; font-weight: 600; font-size: 0.9em;
        position: relative; box-shadow: 0 8px 30px rgba(255,107,157,0.3);
    }
    
    .container { max-width: 950px; margin: 0 auto; padding: 25px 15px; }
    
    .card {
        background: rgba(255,255,255,0.03); backdrop-filter: blur(20px); border-radius: 20px;
        padding: 30px 25px; margin: 20px 0; border: 1px solid rgba(255,255,255,0.08);
        transition: all 0.3s ease; box-shadow: 0 4px 30px rgba(0,0,0,0.2);
    }
    
    .card:hover { border-color: rgba(255,107,157,0.2); box-shadow: 0 10px 50px rgba(108,45,255,0.15); transform: translateY(-2px); }
    .card h2 { font-size: 1.4em; font-weight: 700; margin-bottom: 18px; color: #fff; display: flex; align-items: center; gap: 10px; }
    
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin: 20px 0; }
    
    .stat-card {
        background: rgba(255,255,255,0.04); border-radius: 16px; padding: 22px 18px; text-align: center;
        border: 1px solid rgba(255,255,255,0.06); transition: all 0.3s ease;
    }
    
    .stat-card:hover { background: rgba(255,255,255,0.07); border-color: rgba(255,107,157,0.3); }
    
    .stat-card .number {
        font-size: 2.5em; font-weight: 800;
        background: linear-gradient(135deg, #FF6B9D, #c44dff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    
    .stat-card .label { font-size: 0.85em; color: #a0a0c0; margin-top: 5px; font-weight: 500; }
    
    .btn {
        display: inline-block; padding: 12px 28px; border-radius: 50px; font-weight: 600;
        font-size: 0.95em; text-decoration: none; transition: all 0.3s ease; border: none;
        cursor: pointer; text-align: center; font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .btn-primary { background: linear-gradient(135deg, #FF6B9D, #c44dff); color: #fff; box-shadow: 0 6px 25px rgba(255,107,157,0.3); }
    .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 35px rgba(255,107,157,0.5); }
    .btn-secondary { background: rgba(255,255,255,0.08); color: #fff; border: 1px solid rgba(255,255,255,0.2); }
    .btn-secondary:hover { background: rgba(255,255,255,0.15); border-color: rgba(255,107,157,0.4); }
    .btn-success { background: linear-gradient(135deg, #00d68f, #00b87a); color: #fff; }
    .btn-danger { background: linear-gradient(135deg, #ff4757, #ff3040); color: #fff; }
    .btn-warning { background: linear-gradient(135deg, #ffa502, #ff8700); color: #fff; }
    .btn-whatsapp { background: #25D366; color: #fff; }
    .btn-pdf { background: linear-gradient(135deg, #e74c3c, #c0392b); color: #fff; }
    .btn-om { background: #FF6600; color: #fff; }
    .btn-momo { background: #FFCC00; color: #000; }
    .btn-sm { padding: 8px 18px; font-size: 0.82em; }
    .btn-xs { padding: 6px 14px; font-size: 0.75em; border-radius: 20px; }
    
    .menu-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(155px, 1fr)); gap: 12px; margin: 20px 0; }
    
    .menu-item {
        background: rgba(255,255,255,0.03); border-radius: 16px; padding: 25px 14px; text-align: center;
        text-decoration: none; color: #fff; transition: all 0.3s ease; border: 1px solid rgba(255,255,255,0.06);
    }
    
    .menu-item:hover {
        background: rgba(255,255,255,0.08); transform: translateY(-3px);
        border-color: rgba(255,107,157,0.3); box-shadow: 0 10px 30px rgba(108,45,255,0.15);
    }
    
    .menu-item .icon { font-size: 2.5em; display: block; margin-bottom: 10px; }
    .menu-item .label { font-weight: 600; font-size: 0.88em; color: #c4b5e0; }
    
    .table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 15px -5px; padding: 0 5px; }
    table { width: 100%; border-collapse: collapse; margin: 15px 0; min-width: 550px; }
    
    th {
        text-align: left; padding: 14px 12px; background: rgba(255,255,255,0.05); font-weight: 600;
        font-size: 0.82em; white-space: nowrap; color: #b0a0d0; text-transform: uppercase; letter-spacing: 1px;
    }
    th:first-child { border-radius: 12px 0 0 0; }
    th:last-child { border-radius: 0 12px 0 0; }
    td { padding: 14px 12px; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.88em; }
    tr:hover td { background: rgba(255,255,255,0.03); }
    
    input, select {
        width: 100%; padding: 14px 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.04); color: #fff; font-size: 0.95em; outline: none;
        transition: all 0.3s ease; font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    input:focus, select:focus { border-color: #FF6B9D; box-shadow: 0 0 20px rgba(255,107,157,0.2); }
    input::placeholder { color: rgba(255,255,255,0.35); }
    select option { background: #1a1a3e; color: #fff; }
    
    .phone-group { display: flex; gap: 10px; }
    .phone-group select { width: 140px; flex-shrink: 0; }
    .phone-group input { flex: 1; }
    
    .alert-success { background: rgba(0,214,143,0.12); border: 1px solid rgba(0,214,143,0.4); padding: 16px; border-radius: 12px; margin: 15px 0; font-size: 0.9em; color: #00d68f; }
    .alert-error { background: rgba(255,71,87,0.12); border: 1px solid rgba(255,71,87,0.4); padding: 16px; border-radius: 12px; margin: 15px 0; font-size: 0.9em; color: #ff6b7a; }
    .alert-info { background: rgba(108,45,255,0.12); border: 1px solid rgba(108,45,255,0.4); padding: 16px; border-radius: 12px; margin: 15px 0; font-size: 0.9em; color: #b0a0ff; }
    
    .back-link { display: inline-block; margin-top: 20px; color: #c4b5e0; text-decoration: none; font-weight: 600; font-size: 0.88em; transition: all 0.3s ease; }
    .back-link:hover { color: #FF6B9D; }
    
    .badge-paye { background: rgba(0,214,143,0.2); color: #00d68f; padding: 5px 12px; border-radius: 20px; font-size: 0.78em; font-weight: 600; }
    .badge-attente { background: rgba(255,165,2,0.2); color: #ffa502; padding: 5px 12px; border-radius: 20px; font-size: 0.78em; font-weight: 600; }
    .badge-retard { background: rgba(255,71,87,0.2); color: #ff6b7a; padding: 5px 12px; border-radius: 20px; font-size: 0.78em; font-weight: 600; }
    .badge-suspendu { background: rgba(255,165,2,0.2); color: #ffa502; padding: 5px 12px; border-radius: 20px; font-size: 0.78em; font-weight: 600; }
    
    .avatar-circle {
        width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #FF6B9D, #c44dff);
        display: flex; align-items: center; justify-content: center; font-size: 2.5em; margin: 0 auto 15px;
        border: 3px solid rgba(255,255,255,0.1);
    }
    
    .section-title { text-align: center; color: #FF6B9D; font-size: 0.75em; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 12px; font-weight: 700; }
    .filter-bar { display: flex; gap: 10px; flex-wrap: wrap; margin: 15px 0; align-items: end; }
    .filter-bar select, .filter-bar input { flex: 1; min-width: 120px; }
    .action-buttons { display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0; }
    .divider { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 20px 0; }
    .cagnotte-card { border: 2px solid #FF6B9D !important; background: rgba(255,107,157,0.05) !important; }
    
    .progress-bar { width: 100%; height: 10px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden; margin: 10px 0; }
    .progress-fill { height: 100%; background: linear-gradient(135deg, #FF6B9D, #c44dff); border-radius: 10px; transition: width 0.5s ease; }
    
    @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-20px); } }
    .footer { text-align: center; padding: 30px 15px; color: rgba(255,255,255,0.3); font-size: 0.8em; }
    
    @media (max-width: 768px) {
        .hero { padding: 50px 10px; }
        .hero h1 { font-size: 2.4em !important; line-height: 1.2; }
        .hero .emoji-big { font-size: 3em; }
        .hero p { font-size: 1.4em !important; }
        .hero .badge { font-size: 1.1em; padding: 12px 24px; }
        .container { padding: 8px 5px; max-width: 100%; }
        .card { padding: 25px 15px; border-radius: 18px; margin: 10px 0; }
        .card h2 { font-size: 1.8em !important; }
        .grid { grid-template-columns: 1fr; gap: 15px; }
        .stat-card { padding: 25px 15px; }
        .stat-card .number { font-size: 3em; }
        .stat-card .label { font-size: 1.2em; }
        .menu-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
        .menu-item { padding: 30px 12px; border-radius: 18px; }
        .menu-item .icon { font-size: 3.5em; }
        .menu-item .label { font-size: 1.2em; font-weight: 700; }
        .btn { padding: 18px 20px; font-size: 1.3em; width: 100%; display: block; border-radius: 50px; }
        .btn-sm { padding: 14px 20px; font-size: 1.15em; }
        .btn-xs { padding: 10px 16px; font-size: 1em; }
        input, select { padding: 18px 16px; font-size: 1.2em; border-radius: 14px; }
        label { font-size: 1.2em; font-weight: 600; }
        .table-wrapper { margin: 10px -10px; padding: 0 10px; }
        table { min-width: 550px; }
        th, td { padding: 16px 12px; font-size: 1em; }
        th { font-size: 0.95em; }
        .badge-paye, .badge-attente, .badge-retard, .badge-suspendu { padding: 7px 14px; font-size: 0.95em; border-radius: 25px; }
        .avatar-circle { width: 90px; height: 90px; font-size: 3em; }
        .section-title { font-size: 1em; letter-spacing: 4px; }
        .phone-group { flex-direction: column; gap: 8px; }
        .phone-group select { width: 100%; font-size: 1.2em; }
        .filter-bar { flex-direction: column; gap: 10px; }
        .filter-bar select, .filter-bar input { width: 100%; font-size: 1.1em; }
        .action-buttons { flex-direction: row; flex-wrap: wrap; gap: 8px; }
        .action-buttons .btn { width: auto; flex: 1; min-width: 80px; font-size: 1em; padding: 12px 10px; }
        h1 { font-size: 2em !important; line-height: 1.3; }
        h2 { font-size: 1.7em !important; line-height: 1.3; }
        h3 { font-size: 1.4em !important; line-height: 1.3; }
        p, li, td, span { font-size: 1.15em !important; line-height: 1.6; }
        small { font-size: 1em !important; }
        .alert-success, .alert-error, .alert-info { font-size: 1.1em; padding: 20px 18px; border-radius: 14px; }
        .back-link { font-size: 1.1em; margin-top: 25px; }
        .footer { font-size: 1em; padding: 30px 15px; }
        .progress-bar { height: 14px; border-radius: 14px; }
        .divider { margin: 25px 0; }
    }
    
    @media (max-width: 380px) {
        .hero h1 { font-size: 1.4em; }
        .hero .emoji-big { font-size: 1.8em; }
        .menu-grid { grid-template-columns: repeat(2, 1fr); gap: 8px; }
        .menu-item { padding: 15px 8px; }
        .menu-item .icon { font-size: 2em; }
        .menu-item .label { font-size: 0.85em; }
        .card { padding: 15px 10px; }
        .stat-card .number { font-size: 1.8em; }
    }
    
    @media (display-mode: standalone) {
        body { padding-top: env(safe-area-inset-top); }
    }
</style>
"""

# ================== BALISES PWA ==================
PWA_TAGS = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#FF6B9D">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="KAMBACO SGCV">
<link rel="apple-touch-icon" href="/static/icon-192.png">
<link rel="manifest" href="/manifest.json">
<script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').then(function(reg) {
            console.log('PWA OK');
        }).catch(function(err) {
            console.log('PWA Erreur:', err);
        });
    }
</script>
"""

# ================== OUTILS COMMUNS ==================
def generer_liens_partage(texte, url):
    texte_encode = urllib.parse.quote(texte)
    url_encode = urllib.parse.quote(url)
    return f"""
    <div class="action-buttons">
        <a href="https://wa.me/?text={texte_encode}%20{url_encode}" target="_blank" class="btn btn-whatsapp btn-sm">📱 WhatsApp</a>
        <button onclick="navigator.clipboard.writeText('{url}');alert('✅ Lien copié !')" class="btn btn-secondary btn-sm">📋 Copier</button>
        <a href="{url}?export=pdf" class="btn btn-pdf btn-sm">📄 PDF</a>
    </div>
    """

def get_safe_member(conn, membre_id):
    cur = conn.cursor()
    cur.execute('SELECT m.*, f.nom as famille_nom FROM membres m JOIN familles f ON m.famille_id = f.id WHERE m.id = %s', (membre_id,))
    membre = cur.fetchone()
    cur.close()
    return membre

# ================== PAGE D'ACCUEIL ==================
@app.route('/')
def accueil():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) as total FROM familles;')
    total_familles = cur.fetchone()['total']
    cur.execute('SELECT COUNT(*) as total FROM membres;')
    total_membres = cur.fetchone()['total']
    cur.execute('SELECT COALESCE(SUM(montant), 0) as total FROM cotisations WHERE statut = %s;', ('payé',))
    total_cotisations = cur.fetchone()['total']
    cur.execute("SELECT * FROM cagnottes WHERE statut = 'actif' ORDER BY id DESC LIMIT 1;")
    cagnotte_active = cur.fetchone()
    cur.close(); conn.close()
    
    cagnotte_html = ""
    if cagnotte_active:
        pourcentage = min(100, int((cagnotte_active['montant_collecte'] / cagnotte_active['montant_objectif']) * 100))
        cagnotte_html = f"""
        <div class="card cagnotte-card">
            <h2>🚨 {cagnotte_active['titre']}</h2>
            <p style="opacity:0.8; margin-bottom:10px;">{cagnotte_active['description']}</p>
            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <span>{cagnotte_active['montant_collecte']:,.0f} GNF</span>
                <span>{cagnotte_active['montant_objectif']:,.0f} GNF</span>
            </div>
            <div class="progress-bar"><div class="progress-fill" style="width:{pourcentage}%;"></div></div>
            <p style="text-align:center; font-weight:700; color:#FF6B9D;">{pourcentage}% atteint</p>
            <a href="/cagnotte/contribuer/{cagnotte_active['id']}" class="btn btn-primary btn-sm" style="margin-top:10px;">💰 Contribuer</a>
        </div>"""
    
    return f"""{STYLE}{PWA_TAGS}
    <div class="hero"><span class="emoji-big">🌍</span><h1>Cotisations Missidé KAMBACO</h1><p>Plateforme Numérique de Solidarité Communautaire</p><span class="badge">✨ Transparence • Unité • Progrès ✨</span></div>
    <div class="container">
        <div class="grid">
            <div class="stat-card"><div class="number">6</div><div class="label">🏡 Familles Fondatrices</div></div>
            <div class="stat-card"><div class="number">{total_membres}</div><div class="label">👥 Membres Inscrits</div></div>
            <div class="stat-card"><div class="number">{total_cotisations:,.0f}</div><div class="label">💰 Caisse Totale (GNF)</div></div>
        </div>
        {cagnotte_html}
        <div class="card"><h2>📋 Menu Principal</h2>
        <div class="menu-grid">
            <a href="/familles" class="menu-item"><span class="icon">🏘️</span><span class="label">Les 6 Familles</span></a>
            <a href="/membres" class="menu-item"><span class="icon">👥</span><span class="label">Tous les Membres</span></a>
            <a href="/inscription" class="menu-item"><span class="icon">📝</span><span class="label">S'inscrire</span></a>
            <a href="/cotisations" class="menu-item"><span class="icon">💰</span><span class="label">Cotisations</span></a>
            <a href="/connexion" class="menu-item"><span class="icon">🔐</span><span class="label">Se connecter</span></a>
        </div></div>
        <div class="card" style="text-align:center;"><h2>🌟 Pourquoi cette plateforme ?</h2>
        <p style="opacity:0.85; line-height:1.8;">✅ Transparence totale<br>✅ Paiement mobile facile<br>✅ Rappels automatiques<br>✅ Historique accessible<br>✅ Cagnottes urgentes</p></div>
    </div><div class="footer">🇬🇳 Missidé KAMBACO &copy; 2026</div>"""

# ================== PAGE DES FAMILLES ==================
@app.route('/familles')
def liste_familles():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute('SELECT f.*, COUNT(m.id) as nb_membres FROM familles f LEFT JOIN membres m ON f.id = m.famille_id GROUP BY f.id ORDER BY f.id;')
    familles = cur.fetchall(); cur.close(); conn.close()
    emojis = ['🏘️', '🏘️', '🏘️', '🏘️', '🏘️', '🏘️']
    html = f"""{STYLE}{PWA_TAGS}<div class="container"><div class="card"><h2>🏘️ Les Six Familles</h2><div class="grid">"""
    for i, f in enumerate(familles):
        html += f"""<div class="stat-card"><div style="font-size:2.5em;">{emojis[i]}</div><div style="font-size:1.2em; font-weight:700;">{f['nom']}</div><div class="label">{f['nb_membres']} membre(s)</div></div>"""
    html += '</div><a href="/" class="back-link">⬅ Retour</a></div></div>'
    return html

# ================== PAGE DES MEMBRES ==================
@app.route('/membres')
def liste_membres():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute('SELECT m.*, f.nom as famille_nom FROM membres m JOIN familles f ON m.famille_id = f.id ORDER BY m.id;')
    membres = cur.fetchall(); cur.close(); conn.close()
    html = f"""{STYLE}{PWA_TAGS}<div class="container"><div class="card"><h2>👥 Membres du Village</h2><div class="table-wrapper"><table><tr><th>#</th><th>Nom</th><th>Téléphone</th><th>Famille</th></tr>"""
    for m in membres:
        avatar = "👨" if m['prenom'] else "👩"
        html += f"""<tr><td>{avatar}</td><td><strong>{m['prenom'] or ''} {m['nom']}</strong></td><td>📞 {m['pays_code'] or ''}{m['telephone']}</td><td>🏡 {m['famille_nom']}</td></tr>"""
    html += '</table></div><a href="/" class="back-link">⬅ Retour</a></div></div>'
    return html

# ================== PAGE D'INSCRIPTION ==================
@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute('SELECT * FROM familles ORDER BY id;'); familles = cur.fetchall()
    message = ""; message_type = ""
    if request.method == 'POST':
        nom = request.form['nom']; prenom = request.form['prenom']; pays_code = request.form['pays_code']
        telephone = request.form['telephone']; telephone_complet = pays_code + telephone
        email = request.form['email']; password = request.form['password']
        famille_id = request.form['famille_id']
        password_hash = hash_password(password)
        try:
            cur.execute("INSERT INTO membres (nom, prenom, telephone, email, password, pays_code, famille_id, role, statut_inscription, statut_membre) VALUES (%s, %s, %s, %s, %s, %s, %s, 'membre', 'en_attente', 'actif')", 
                       (nom, prenom, telephone_complet, email, password_hash, pays_code, famille_id))
            conn.commit()
            message = f"🎉 {prenom} {nom} inscrit ! En attente de validation. Connectez-vous avec votre email et mot de passe."
            message_type = "success"
        except Exception as e:
            conn.rollback(); message = f"❌ Erreur : {e}"; message_type = "error"
    options_pays = ""; options_famille = '<option value="">-- Choisissez --</option>'
    for p in PAYS: options_pays += f'<option value="{p["code"]}">{p["drapeau"]} {p["nom"]} ({p["code"]})</option>'
    for f in familles: options_famille += f'<option value="{f["id"]}">🏡 {f["nom"]}</option>'
    alert = f'<div class="{"alert-success" if message_type=="success" else "alert-error"}">{message}</div>' if message else ""
    html = f"""{STYLE}{PWA_TAGS}<div class="container"><div class="card"><h2>📝 Inscription</h2>{alert}<form method="POST">
        <label>👤 Nom</label><br><input type="text" name="nom" required><br><br>
        <label>👤 Prénom</label><br><input type="text" name="prenom" required><br><br>
        <label>📞 Téléphone</label><br><div class="phone-group"><select name="pays_code">{options_pays}</select><input type="text" name="telephone" required></div><br>
        <label>📧 Email</label><br><input type="email" name="email" required placeholder="exemple@email.com"><br><br>
        <label>🔑 Mot de passe</label><br><div style="position:relative;"><input type="password" id="password" name="password" required placeholder="Choisissez un mot de passe" style="padding-right:50px;"><button type="button" onclick="var p=document.getElementById('password');p.type=p.type==='password'?'text':'password';" style="position:absolute;right:5px;top:50%;transform:translateY(-50%);background:none;border:none;color:#FF6B9D;font-size:1.2em;cursor:pointer;">👁️</button></div><br>
        <label>🏡 Famille</label><br><select name="famille_id">{options_famille}</select><br><br>
        <button type="submit" class="btn btn-primary">✨ S'inscrire</button></form><a href="/" class="back-link">⬅ Retour</a></div></div>"""
    cur.close(); conn.close(); return html

# ================== PAGE DES COTISATIONS (PUBLIC - UNIQUEMENT PAYÉS) ==================
@app.route('/cotisations')
def cotisations():
    annee_filtre = request.args.get('annee', '')
    conn = get_db_connection(); cur = conn.cursor()
    query = "SELECT c.*, m.nom, m.prenom, f.nom as famille_nom FROM cotisations c JOIN membres m ON c.membre_id = m.id JOIN familles f ON m.famille_id = f.id WHERE c.statut = 'payé' "
    params = []
    if annee_filtre: query += "AND c.annee = %s "; params.append(int(annee_filtre))
    query += "ORDER BY c.id DESC"
    cur.execute(query, params); cotisations_list = cur.fetchall()
    cur.execute('SELECT COALESCE(SUM(montant), 0) as total FROM cotisations WHERE statut = %s;', ('payé',)); total_caisse = cur.fetchone()['total']
    cur.execute('SELECT DISTINCT annee FROM cotisations WHERE statut = %s ORDER BY annee DESC;', ('payé',)); annees = [row['annee'] for row in cur.fetchall()]
    cur.close(); conn.close()
    options_annee = '<option value="">Toutes</option>'
    for a in annees: options_annee += f'<option value="{a}" {"selected" if str(a)==annee_filtre else ""}>{a}</option>'
    html = f"""{STYLE}{PWA_TAGS}<div class="container"><div class="card"><h2>💰 Historique des Cotisations Validées</h2>
    <div class="grid"><div class="stat-card"><div class="number" style="font-size:1.5em;">{total_caisse:,.0f} GNF</div></div>
    <div class="stat-card"><div class="number" style="font-size:1.5em;">300K</div></div>
    <div class="stat-card"><div class="number" style="font-size:1.5em;">+50K</div></div></div>
    <form method="GET" class="filter-bar"><select name="annee" onchange="this.form.submit()">{options_annee}</select></form>
    <div class="table-wrapper"><table><tr><th>Membre</th><th>Famille</th><th>Année</th><th>Montant</th><th>Pénalité</th><th>Statut</th></tr>"""
    for c in cotisations_list:
        html += f"<tr><td>{c['prenom'] or ''} {c['nom']}</td><td>{c['famille_nom']}</td><td>{c['annee']}</td><td>{c['montant']:,.0f}</td><td>{c['penalite'] or 0:,.0f}</td><td><span class='badge-paye'>✅ Payé</span></td></tr>"
    html += '</table></div><a href="/" class="back-link">⬅ Retour</a></div></div>'
    return html

# ================== CONNEXION (EMAIL + MOT DE PASSE) ==================
@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    message = ""; message_type = ""
    if request.method == 'POST':
        email = request.form['email']; password = request.form['password']
        password_hash = hash_password(password)
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute('SELECT * FROM membres WHERE email = %s AND password = %s', (email, password_hash))
        membre = cur.fetchone()
        if membre:
            if membre['statut_inscription'] == 'en_attente': message = "⏳ Compte en attente de validation."; message_type = "error"
            elif membre['statut_membre'] == 'suspendu': message = "🚫 Compte suspendu."; message_type = "error"
            else:
                message = f"✅ Bienvenue {membre['prenom'] or ''} {membre['nom']} !"
                message_type = "success"
                if membre['role'] == 'admin':
                    message += '<br><br><a href="/admin" class="btn btn-primary">👑 Panneau Admin</a>'
                elif membre['role'] == 'tresorier':
                    message += '<br><br><a href="/tresorier" class="btn btn-primary">💼 Panneau Trésorier</a> | <a href="/membre/' + str(membre['id']) + '" class="btn btn-secondary btn-sm">👤 Mon Espace Membre</a>'
                else:
                    message += f'<br><br><a href="/membre/{membre["id"]}" class="btn btn-primary">👤 Mon Tableau de Bord</a>'
        else:
            message = "❌ Email ou mot de passe incorrect."; message_type = "error"
        cur.close(); conn.close()
    alert = f'<div class="{"alert-success" if message_type=="success" else "alert-error"}">{message}</div>' if message else ""
    return f"""{STYLE}{PWA_TAGS}<div class="container"><div class="card"><h2>🔐 Connexion</h2>{alert}
        <form method="POST">
        <label>📧 Email</label><br><input type="email" name="email" required placeholder="votre@email.com"><br><br>
        <label>🔑 Mot de passe</label><br><input type="password" name="password" required placeholder="Votre mot de passe"><br><br>
        <button type="submit" class="btn btn-primary">🔐 Se connecter</button></form>
        <p style="text-align:center; margin-top:15px;">Pas encore inscrit ? <a href="/inscription" style="color:#FF6B9D;">S'inscrire</a></p>
        <a href="/" class="back-link">⬅ Retour</a></div></div>"""

# ================== TABLEAU DE BORD MEMBRE (UNIQUEMENT PAYÉS) ==================
@app.route('/membre/<int:membre_id>')
def tableau_de_bord_membre(membre_id):
    conn = get_db_connection(); cur = conn.cursor()
    membre = get_safe_member(conn, membre_id)
    if not membre: cur.close(); conn.close(); return f"{STYLE}<div class='container'><div class='card'><h2>❌ Membre non trouvé</h2></div></div>"
    cur.execute("SELECT * FROM cotisations WHERE membre_id = %s AND statut = 'payé' ORDER BY annee DESC", (membre_id,)); cotisations_list = cur.fetchall()
    cur.execute('SELECT COALESCE(SUM(montant), 0) as total FROM cotisations WHERE membre_id = %s AND statut = %s', (membre_id, 'payé')); total_paye = cur.fetchone()['total']
    cur.execute("SELECT * FROM cotisations WHERE membre_id = %s AND statut = 'en_attente' ORDER BY annee DESC", (membre_id,)); en_attente = cur.fetchall()
    cur.close(); conn.close()
    html = f"""{STYLE}{PWA_TAGS}<div class="container"><div class="card" style="text-align:center;"><div class="avatar-circle">👤</div><h1>{membre['prenom'] or ''} {membre['nom']}</h1><p>🏡 {membre['famille_nom']} | 📞 {membre['telephone']}</p></div>
    <div class="grid"><div class="stat-card"><div class="number">{len(cotisations_list)}</div><div class="label">📋 Cotisations Validées</div></div>
    <div class="stat-card"><div class="number">{total_paye:,.0f}</div><div class="label">💰 Total Payé</div></div>
    <div class="stat-card"><div class="number">300K</div><div class="label">💳 / An</div></div></div>
    <div style="text-align:center;"><a href="/paiement/{membre_id}" class="btn btn-primary">💳 Payer</a></div>"""
    if en_attente:
        html += f"""<div class="card"><h2>⏳ En attente de validation ({len(en_attente)})</h2><div class="table-wrapper"><table><tr><th>Année</th><th>Montant</th><th>Pénalité</th><th>Statut</th></tr>"""
        for c in en_attente:
            html += f"<tr><td>{c['annee']}</td><td>{c['montant']:,.0f}</td><td>{c['penalite'] or 0:,.0f}</td><td><span class='badge-attente'>⏳ En attente</span></td></tr>"
        html += '</table></div></div>'
    html += f"""<div class="card"><h2>📋 Mes Cotisations Validées</h2><div class="table-wrapper"><table><tr><th>Année</th><th>Montant</th><th>Pénalité</th><th>Statut</th></tr>"""
    for c in cotisations_list:
        html += f"<tr><td>{c['annee']}</td><td>{c['montant']:,.0f}</td><td>{c['penalite'] or 0:,.0f}</td><td><span class='badge-paye'>✅ Payé</span></td></tr>"
    html += '</table></div><a href="/" class="back-link">⬅ Retour</a></div></div>'
    return html

# ================== PAGE DE PAIEMENT (TOUT EN ATTENTE SAUF ESPÈCES) ==================
@app.route('/paiement/<int:membre_id>', methods=['GET', 'POST'])
def paiement(membre_id):
    conn = get_db_connection(); cur = conn.cursor()
    membre = get_safe_member(conn, membre_id)
    if not membre: cur.close(); conn.close(); return f"{STYLE}<div class='container'><div class='card'><h2>❌ Membre non trouvé</h2></div></div>"
    message = ""; message_type = ""
    if request.method == 'POST':
        annee = int(request.form['annee']); mode_paiement = request.form['mode_paiement']
        penalite = 50000 if annee < date.today().year else 0; montant_total = 300000 + penalite
        statut = 'en_attente'  # Tout passe en attente de validation
        try:
            cur.execute('INSERT INTO cotisations (membre_id, annee, montant, penalite, statut, date_paiement) VALUES (%s, %s, %s, %s, %s, NOW())', (membre_id, annee, montant_total, penalite, statut))
            conn.commit()
            message = f"✅ {montant_total:,.0f} GNF enregistré ! Le trésorier doit valider votre paiement."
            message_type = "success"
        except Exception as e: conn.rollback(); message = f"❌ {e}"; message_type = "error"
    cur.close(); conn.close()
    alert = f'<div class="{"alert-success" if message_type=="success" else "alert-error"}">{message}</div>' if message else ""
    return f"""{STYLE}{PWA_TAGS}<div class="container"><div class="card"><h2>💳 Paiement</h2><p>👤 {membre['prenom'] or ''} {membre['nom']} | 🏡 {membre['famille_nom']}</p>{alert}
    <div class="grid"><div class="stat-card" style="border:2px solid #FF6B9D;"><div>📌 Base</div><div class="number" style="font-size:2em;">300K</div></div>
    <div class="stat-card" style="border:2px solid #ffa502;"><div>⚠️ Pénalité</div><div class="number" style="font-size:2em;color:#ffa502;">+50K</div></div></div>
    <div class="alert-info">ℹ️ Tous les paiements sont validés par le trésorier avant d'apparaître dans l'historique public.</div>
    <form method="POST"><label>📅 Année</label><br><select name="annee"><option value="2026">2026</option><option value="2025">2025 (+50K)</option></select><br><br>
    <label>💳 Mode</label><br><select name="mode_paiement"><option value="Orange Money">🟠 Orange Money</option><option value="MTN MoMo">🟡 MTN MoMo</option><option value="Espèces">💵 Espèces</option></select><br><br>
    <button type="submit" class="btn btn-primary">💰 Payer</button></form>
    <a href="/membre/{membre_id}" class="back-link">⬅ Retour</a></div></div>"""

# ================== TRÉSORIER ==================
@app.route('/tresorier')
def tableau_de_bord_tresorier():
    annee_filtre = request.args.get('annee', ''); export_pdf = request.args.get('export', '')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(montant), 0) as total FROM cotisations WHERE statut = 'payé';"); total_valide = cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) FROM cotisations WHERE statut = 'en_attente';"); nb_en_attente = cur.fetchone()['count']
    cur.execute("SELECT id FROM membres WHERE role = 'tresorier' LIMIT 1;")
    tresorier = cur.fetchone()
    tresorier_id = tresorier['id'] if tresorier else None
    query = "SELECT c.*, m.nom, m.prenom, m.telephone, f.nom as famille_nom FROM cotisations c JOIN membres m ON c.membre_id = m.id JOIN familles f ON m.famille_id = f.id "
    params = []
    if annee_filtre: query += "WHERE c.annee = %s "; params.append(int(annee_filtre))
    query += "ORDER BY c.id DESC"
    cur.execute(query, params); cotisations_list = cur.fetchall()
    cur.execute('SELECT DISTINCT annee FROM cotisations ORDER BY annee DESC;'); annees = [row['annee'] for row in cur.fetchall()]
    cur.close(); conn.close()
    if export_pdf == 'pdf': return generer_pdf_cotisations(cotisations_list, total_valide, annee_filtre)
    options_annee = '<option value="">Toutes</option>'
    for a in annees: options_annee += f'<option value="{a}" {"selected" if str(a)==annee_filtre else ""}>{a}</option>'
    html = f"""{STYLE}{PWA_TAGS}<div class="container"><div class="card" style="text-align:center;"><div class="avatar-circle">💼</div><h1>Tableau Trésorier</h1></div>
    <div class="grid"><div class="stat-card"><div class="number">{total_valide:,.0f}</div><div class="label">✅ Caisse</div></div>
    <div class="stat-card"><div class="number">{nb_en_attente}</div><div class="label">⏳ À Valider</div></div></div>"""
    if tresorier_id: html += f'<div style="text-align:center; margin:10px 0;"><a href="/membre/{tresorier_id}" class="btn btn-secondary">👤 Mon Espace Cotisation</a></div>'
    html += f"""<div class="card"><h2>💼 Paiements</h2><form method="GET" class="filter-bar"><select name="annee" onchange="this.form.submit()">{options_annee}</select></form>
    {generer_liens_partage("📊 Rapport", request.url)}<div class="table-wrapper"><table><tr><th>Membre</th><th>Tél</th><th>Famille</th><th>Année</th><th>Montant</th><th>Pénalité</th><th>Statut</th><th>Action</th></tr>"""
    for c in cotisations_list:
        badge = '<span class="badge-paye">✅</span>' if c['statut']=='payé' else '<span class="badge-attente">⏳</span>'
        action = f'<a href="/tresorier/valider/{c["id"]}" class="btn btn-success btn-xs">✅</a>' if c['statut']=='en_attente' else ""
        html += f"<tr><td>{c['prenom'] or ''} {c['nom']}</td><td>{c['telephone']}</td><td>{c['famille_nom']}</td><td>{c['annee']}</td><td>{c['montant']:,.0f}</td><td>{c['penalite'] or 0:,.0f}</td><td>{badge}</td><td>{action}</td></tr>"
    html += '</table></div><a href="/" class="back-link">⬅ Retour</a></div></div>'
    return html

@app.route('/tresorier/valider/<int:cotisation_id>')
def valider_paiement_tresorier(cotisation_id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE cotisations SET statut = 'payé', date_paiement = NOW() WHERE id = %s", (cotisation_id,)); conn.commit(); cur.close(); conn.close()
    return f"{STYLE}<div class='container'><div class='card'><div class='alert-success'><h2>✅ Validé !</h2></div><a href='/tresorier' class='btn btn-primary'>💼 Retour</a></div></div>"

# ================== EXPORT PDF MEMBRES ==================
def generer_pdf_membres(membres_list, tri, recherche):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    elements = []
    styles = getSampleStyleSheet()
    titre = "Liste des Membres du Village"
    if recherche: titre += f' (Recherche: "{recherche}")'
    elements.append(Paragraph(titre, styles['Title']))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(f"Tri : {tri} | Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Paragraph(f"Total : {len(membres_list)} membre(s)", styles['Heading2']))
    elements.append(Spacer(1, 10*mm))
    data = [['ID', 'Nom', 'Téléphone', 'Email', 'Famille', 'Rôle', 'Statut']]
    for m in membres_list:
        data.append([str(m['id']), f"{m['prenom'] or ''} {m['nom']}", m['telephone'], m.get('email', ''), m['famille_nom'], m['role'], m['statut_membre']])
    table = Table(data, repeatRows=1, colWidths=[8*mm, 40*mm, 30*mm, 40*mm, 30*mm, 25*mm, 22*mm])
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B9D')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('FONTSIZE', (0, 0), (-1, -1), 7), ('ALIGN', (0, 0), (-1, 0), 'CENTER'), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f0ff')])]))
    elements.append(table)
    elements.append(Spacer(1, 15*mm))
    elements.append(Paragraph("Missidé KAMBACO — Système de Gestion des Cotisations Villageoises", styles['Normal']))
    doc.build(elements); buffer.seek(0)
    response = make_response(buffer.getvalue()); response.headers['Content-Type'] = 'application/pdf'; response.headers['Content-Disposition'] = 'attachment; filename=liste_membres.pdf'
    return response

# ================== ADMIN ==================
@app.route('/admin')
def tableau_de_bord_admin():
    annee_filtre = request.args.get('annee', ''); export_pdf = request.args.get('export', '')
    tri_membres = request.args.get('tri', 'nom'); recherche = request.args.get('recherche', '')
    export_membres_pdf = request.args.get('export_membres', '')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(montant), 0) as total FROM cotisations WHERE statut = 'payé';"); total_valide = cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) FROM cotisations WHERE statut = 'en_attente';"); nb_attente = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) FROM membres WHERE statut_inscription = 'en_attente';"); nb_inscriptions = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) FROM membres;"); nb_membres = cur.fetchone()['count']
    query = "SELECT c.*, m.nom, m.prenom, m.telephone, m.id as membre_id, m.statut_membre, f.nom as famille_nom FROM cotisations c JOIN membres m ON c.membre_id = m.id JOIN familles f ON m.famille_id = f.id "; params = []
    if annee_filtre: query += "WHERE c.annee = %s "; params.append(int(annee_filtre))
    query += "ORDER BY c.id DESC"
    cur.execute(query, params); cotisations_list = cur.fetchall()
    cur.execute("SELECT m.*, f.nom as famille_nom FROM membres m JOIN familles f ON m.famille_id = f.id WHERE m.statut_inscription = 'en_attente' ORDER BY m.id;"); inscriptions = cur.fetchall()
    ordre_sql = "ORDER BY m.nom ASC, m.prenom ASC"
    if tri_membres == 'famille': ordre_sql = "ORDER BY f.nom ASC, m.nom ASC"
    elif tri_membres == 'statut': ordre_sql = "ORDER BY m.statut_membre ASC, m.nom ASC"
    elif tri_membres == 'id': ordre_sql = "ORDER BY m.id ASC"
    membres_query = "SELECT m.*, f.nom as famille_nom FROM membres m JOIN familles f ON m.famille_id = f.id "; membres_params = []
    if recherche:
        membres_query += "WHERE (LOWER(m.nom) LIKE %s OR LOWER(m.prenom) LIKE %s OR m.telephone LIKE %s OR LOWER(COALESCE(m.email, '')) LIKE %s) "
        like_recherche = f"%{recherche.lower()}%"; membres_params.extend([like_recherche, like_recherche, like_recherche, like_recherche])
    membres_query += ordre_sql
    cur.execute(membres_query, membres_params); tous_membres = cur.fetchall()
    cur.execute("SELECT id, nom, prenom, telephone, role FROM membres WHERE statut_membre = 'actif' ORDER BY id;"); tous_actifs = cur.fetchall()
    cur.execute("SELECT id, nom, prenom, telephone FROM membres WHERE role = 'tresorier';"); tresorier_actuel = cur.fetchone()
    cur.execute("SELECT * FROM cagnottes ORDER BY id DESC;"); cagnottes = cur.fetchall()
    cur.execute('SELECT DISTINCT annee FROM cotisations ORDER BY annee DESC;'); annees = [row['annee'] for row in cur.fetchall()]
    cur.execute("SELECT id FROM membres WHERE role = 'admin' LIMIT 1;"); admin = cur.fetchone()
    admin_id = admin['id'] if admin else None
    if export_membres_pdf == 'oui': membres_pdf = list(tous_membres); cur.close(); conn.close(); return generer_pdf_membres(membres_pdf, tri_membres, recherche)
    cur.close(); conn.close()
    if export_pdf == 'pdf': return generer_pdf_cotisations(cotisations_list, total_valide, annee_filtre)
    options_annee = '<option value="">Toutes</option>'
    for a in annees: options_annee += f'<option value="{a}" {"selected" if str(a)==annee_filtre else ""}>{a}</option>'
    options_tri = f"""<option value="nom" {"selected" if tri_membres=='nom' else ""}>📋 Trier par Nom</option><option value="famille" {"selected" if tri_membres=='famille' else ""}>🏡 Trier par Famille</option><option value="statut" {"selected" if tri_membres=='statut' else ""}>📊 Trier par Statut</option><option value="id" {"selected" if tri_membres=='id' else ""}>🔢 Trier par Date d'inscription</option>"""
    tresorier_html = f"<p>💼 Trésorier : <strong>{tresorier_actuel['prenom'] or ''} {tresorier_actuel['nom']}</strong> ({tresorier_actuel['telephone']})</p>" if tresorier_actuel else "<p>⚠️ Aucun trésorier</p>"
    options_tresorier = ""
    for m in tous_actifs:
        if m['role'] != 'tresorier': options_tresorier += f'<option value="{m["id"]}">{m["prenom"] or ""} {m["nom"]} ({m["telephone"]}) [{m["role"]}]</option>'
    html = f"""{STYLE}{PWA_TAGS}<div class="container">
    <div class="card" style="text-align:center;border:2px solid #FF6B9D;"><div class="avatar-circle">👑</div><div class="section-title">Espace Administrateur</div><h1>Panneau de Contrôle</h1></div>
    <div class="grid">
        <div class="stat-card"><div class="number">{total_valide:,.0f}</div><div class="label">💰 Caisse Validée</div></div>
        <div class="stat-card"><div class="number">{nb_attente}</div><div class="label">⏳ Paiements à Valider</div></div>
        <div class="stat-card"><div class="number">{nb_inscriptions}</div><div class="label">📝 Inscriptions</div></div>
        <div class="stat-card"><div class="number">{nb_membres}</div><div class="label">👥 Total Membres</div></div>
    </div>"""
    if admin_id: html += f'<div style="text-align:center; margin:10px 0;"><a href="/membre/{admin_id}" class="btn btn-secondary">👤 Mon Espace Cotisation</a></div>'
    html += f"""<div class="card"><h2>💼 Gestion du Trésorier</h2>{tresorier_html}
    <form method="POST" action="/admin/changer-tresorier"><label>🔄 Sélectionner le nouveau trésorier :</label><br><select name="nouveau_tresorier_id" style="margin:10px 0;">{options_tresorier}</select><br><button type="submit" class="btn btn-warning">🔄 Changer le Trésorier</button></form></div>
    <div class="card"><h2>🚨 Cagnottes Urgentes</h2><form method="POST" action="/admin/creer-cagnotte"><div class="grid"><div><label>📌 Titre</label><br><input type="text" name="titre" required></div><div><label>📝 Description</label><br><input type="text" name="description"></div><div><label>🎯 Objectif (GNF)</label><br><input type="number" name="montant_objectif" required></div><div><label>📅 Date fin</label><br><input type="date" name="date_fin"></div></div><button type="submit" class="btn btn-primary">🚀 Lancer la Cagnotte</button></form><hr class="divider"><h3>Cagnottes existantes</h3>"""
    for cag in cagnottes:
        pct = min(100, int((cag['montant_collecte'] / cag['montant_objectif']) * 100)) if cag['montant_objectif'] else 0
        statut_badge = '<span class="badge-paye">Actif</span>' if cag['statut']=='actif' else '<span class="badge-retard">Clôturé</span>'
        html += f"""<div class="card" style="margin:10px 0;"><strong>{cag['titre']}</strong> {statut_badge}<br><span style="font-size:1.2em; font-weight:700;">{cag['montant_collecte']:,.0f}</span> / {cag['montant_objectif']:,.0f} GNF ({pct}%)<div class="progress-bar"><div class="progress-fill" style="width:{pct}%;"></div></div><div class="action-buttons"><a href="/cagnotte/contribuer/{cag['id']}" class="btn btn-primary btn-xs">💰 Contribuer</a> <a href="/admin/cloturer-cagnotte/{cag['id']}" class="btn btn-secondary btn-xs">🔒 Clôturer</a></div></div>"""
    html += """</div><div class="card"><h2>📝 Inscriptions en Attente de Validation</h2>"""
    if not inscriptions: html += '<div class="alert-info">✅ Aucune.</div>'
    else:
        html += '<div class="table-wrapper"><table><tr><th>Nom</th><th>Tél</th><th>Email</th><th>Famille</th><th>Actions</th></tr>'
        for m in inscriptions: html += f"""<tr><td><strong>{m['prenom'] or ''} {m['nom']}</strong></td><td>{m['telephone']}</td><td>{m.get('email', '')}</td><td>🏡 {m['famille_nom']}</td><td><div class="action-buttons"><a href='/admin/valider-inscription/{m['id']}' class='btn btn-success btn-xs'>✅</a> <a href='/admin/rejeter-inscription/{m['id']}' class='btn btn-danger btn-xs'>❌</a></div></td></tr>"""
        html += '</table></div>'
    html += f"""</div><div class="card"><h2>👥 Gestion des Membres ({len(tous_membres)} membres)</h2><form method="GET" action="/admin" class="filter-bar"><input type="text" name="recherche" placeholder="🔍 Rechercher..." value="{recherche}"><select name="tri" onchange="this.form.submit()">{options_tri}</select><button type="submit" class="btn btn-primary btn-sm">🔍</button><a href="/admin" class="btn btn-secondary btn-sm">🔄</a><a href="/admin?export_membres=oui&tri={tri_membres}&recherche={recherche}" class="btn btn-pdf btn-sm">📄 PDF</a></form><div class="table-wrapper"><table><tr><th>ID</th><th>Nom</th><th>Tél</th><th>Email</th><th>Mot de passe</th><th>Famille</th><th>Rôle</th><th>Statut</th><th>Actions</th></tr>"""
    for m in tous_membres:
        badge_statut = '<span class="badge-paye">Actif</span>' if m['statut_membre'] == 'actif' else '<span class="badge-suspendu">Suspendu</span>'
        role_badge = ''
        if m['role'] == 'admin': role_badge = '<span style="color:#FF6B9D;">👑 Admin</span>'
        elif m['role'] == 'tresorier': role_badge = '<span style="color:#ffa502;">💼 Trésorier</span>'
        elif m['role'] == 'chef_famille': role_badge = '<span style="color:#c4b5e0;">🏡 Chef</span>'
        else: role_badge = '<span style="opacity:0.7;">👤 Membre</span>'
        actions = ""
        if m['role'] != 'admin':
            if m['statut_membre'] == 'actif': actions += f"<a href='/admin/suspendre/{m['id']}' class='btn btn-warning btn-xs'>⏸️</a> "
            else: actions += f"<a href='/admin/reactiver/{m['id']}' class='btn btn-success btn-xs'>▶️</a> "
            actions += f"<a href='/admin/supprimer/{m['id']}' class='btn btn-danger btn-xs' onclick=\"return confirm('Supprimer ?')\">🗑️</a>"
        else: actions = '<span style="opacity:0.5;">Protégé</span>'
        html += f"""<tr><td>{m['id']}</td><td><strong>{m['prenom'] or ''} {m['nom']}</strong></td><td>{m['telephone']}</td><td>{m.get('email', '')}</td><td>{(m.get('password') or '***')[:20]}...</td><td>🏡 {m['famille_nom']}</td><td>{role_badge}</td><td>{badge_statut}</td><td><div class="action-buttons">{actions}</div></td></tr>"""
    html += """</table></div></div><div class="card"><h2>💼 Historique des Paiements</h2><form method="GET" action="/admin" class="filter-bar"><select name="annee" onchange="this.form.submit()">""" + options_annee + """</select><a href="/admin" class="btn btn-secondary btn-sm">🔄 Reset</a></form>""" + generer_liens_partage("📊 Rapport", request.url.split('?')[0] + "?export=pdf&annee=" + annee_filtre) + """<div class="table-wrapper"><table><tr><th>Membre</th><th>Tél</th><th>Famille</th><th>Année</th><th>Montant</th><th>Pénalité</th><th>Statut</th><th>Action</th></tr>"""
    for c in cotisations_list:
        badge = '<span class="badge-paye">✅ Payé</span>' if c['statut'] == 'payé' else ('<span class="badge-attente">⏳ Attente</span>' if c['statut'] == 'en_attente' else '<span class="badge-retard">⚠️ Retard</span>')
        penalite = f"{c['penalite']:,.0f} GNF" if c['penalite'] else "-"
        action = f'<a href="/admin/valider-paiement/{c["id"]}" class="btn btn-success btn-xs">✅ Valider</a>' if c['statut'] == 'en_attente' else ""
        html += f"<tr><td><strong>{c['prenom'] or ''} {c['nom']}</strong></td><td>{c['telephone']}</td><td>🏡 {c['famille_nom']}</td><td>{c['annee']}</td><td>{c['montant']:,.0f} GNF</td><td>{penalite}</td><td>{badge}</td><td>{action}</td></tr>"
    html += """</table></div></div><a href="/" class="back-link">⬅ Retour à l'accueil</a></div>"""
    return html

# ================== ACTIONS ADMIN ==================
@app.route('/admin/valider-inscription/<int:membre_id>')
def valider_inscription(membre_id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE membres SET statut_inscription = 'valide' WHERE id = %s", (membre_id,)); conn.commit(); cur.close(); conn.close()
    return f"{STYLE}<div class='container'><div class='card'><div class='alert-success'><h2>✅ Validé</h2></div><a href='/admin' class='btn btn-primary'>👑 Retour</a></div></div>"

@app.route('/admin/rejeter-inscription/<int:membre_id>')
def rejeter_inscription(membre_id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM membres WHERE id = %s", (membre_id,)); conn.commit(); cur.close(); conn.close()
    return f"{STYLE}<div class='container'><div class='card'><div class='alert-error'><h2>❌ Rejeté</h2></div><a href='/admin' class='btn btn-primary'>👑 Retour</a></div></div>"

@app.route('/admin/suspendre/<int:membre_id>')
def suspendre_membre(membre_id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE membres SET statut_membre = 'suspendu' WHERE id = %s AND role != 'admin'", (membre_id,)); conn.commit(); cur.close(); conn.close()
    return f"{STYLE}<div class='container'><div class='card'><div class='alert-info'><h2>⏸️ Suspendu</h2></div><a href='/admin' class='btn btn-primary'>👑 Retour</a></div></div>"

@app.route('/admin/reactiver/<int:membre_id>')
def reactiver_membre(membre_id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE membres SET statut_membre = 'actif' WHERE id = %s", (membre_id,)); conn.commit(); cur.close(); conn.close()
    return f"{STYLE}<div class='container'><div class='card'><div class='alert-success'><h2>▶️ Réintégré</h2></div><a href='/admin' class='btn btn-primary'>👑 Retour</a></div></div>"

@app.route('/admin/supprimer/<int:membre_id>')
def supprimer_membre(membre_id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM cotisations WHERE membre_id = %s", (membre_id,))
    cur.execute("DELETE FROM contributions_cagnotte WHERE membre_id = %s", (membre_id,))
    cur.execute("DELETE FROM membres WHERE id = %s AND role != 'admin'", (membre_id,)); conn.commit(); cur.close(); conn.close()
    return f"{STYLE}<div class='container'><div class='card'><div class='alert-error'><h2>🗑️ Supprimé</h2></div><a href='/admin' class='btn btn-primary'>👑 Retour</a></div></div>"

@app.route('/admin/valider-paiement/<int:cotisation_id>')
def admin_valider_paiement(cotisation_id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE cotisations SET statut = 'payé', date_paiement = NOW() WHERE id = %s", (cotisation_id,)); conn.commit(); cur.close(); conn.close()
    return f"{STYLE}<div class='container'><div class='card'><div class='alert-success'><h2>✅ Validé</h2></div><a href='/admin' class='btn btn-primary'>👑 Retour</a></div></div>"

@app.route('/admin/changer-tresorier', methods=['POST'])
def changer_tresorier():
    nouveau_id = request.form['nouveau_tresorier_id']
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE membres SET role = 'membre' WHERE role = 'tresorier'")
    cur.execute("UPDATE membres SET role = 'tresorier' WHERE id = %s", (nouveau_id,)); conn.commit(); cur.close(); conn.close()
    return f"{STYLE}<div class='container'><div class='card'><div class='alert-success'><h2>🔄 Trésorier changé</h2></div><a href='/admin' class='btn btn-primary'>👑 Retour</a></div></div>"

@app.route('/admin/creer-cagnotte', methods=['POST'])
def creer_cagnotte():
    titre = request.form['titre']; description = request.form['description']; montant = float(request.form['montant_objectif']); date_fin = request.form['date_fin'] or None
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO cagnottes (titre, description, montant_objectif, date_fin) VALUES (%s, %s, %s, %s)", (titre, description, montant, date_fin)); conn.commit(); cur.close(); conn.close()
    return f"{STYLE}<div class='container'><div class='card'><div class='alert-success'><h2>🚀 Cagnotte lancée</h2></div><a href='/admin' class='btn btn-primary'>👑 Retour</a></div></div>"

@app.route('/admin/cloturer-cagnotte/<int:cagnotte_id>')
def cloturer_cagnotte(cagnotte_id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE cagnottes SET statut = 'cloture' WHERE id = %s", (cagnotte_id,)); conn.commit(); cur.close(); conn.close()
    return f"{STYLE}<div class='container'><div class='card'><div class='alert-info'><h2>🔒 Clôturée</h2></div><a href='/admin' class='btn btn-primary'>👑 Retour</a></div></div>"

# ================== CONTRIBUTION CAGNOTTE ==================
@app.route('/cagnotte/contribuer/<int:cagnotte_id>', methods=['GET', 'POST'])
def contribuer_cagnotte(cagnotte_id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT * FROM cagnottes WHERE id = %s", (cagnotte_id,)); cagnotte = cur.fetchone()
    if not cagnotte: cur.close(); conn.close(); return f"{STYLE}<div class='container'><div class='card'><h2>❌ Cagnotte introuvable</h2></div></div>"
    message = ""; message_type = ""; montant_choisi = 0
    if request.method == 'POST':
        telephone = request.form['telephone']; montant = float(request.form['montant']); operateur = request.form.get('operateur', '')
        cur.execute("SELECT id, nom, prenom FROM membres WHERE telephone = %s", (telephone,)); membre = cur.fetchone()
        if membre:
            cur.execute("INSERT INTO contributions_cagnotte (cagnotte_id, membre_id, montant) VALUES (%s, %s, %s)", (cagnotte_id, membre['id'], montant))
            cur.execute("UPDATE cagnottes SET montant_collecte = montant_collecte + %s WHERE id = %s", (montant, cagnotte_id))
            conn.commit()
            if operateur == 'om': message = f"🟠 Redirigez vers Orange Money pour payer {montant:,.0f} GNF au 620320388."
            elif operateur == 'momo': message = f"🟡 Redirigez vers MTN MoMo pour payer {montant:,.0f} GNF au 620239287."
            else: message = f"✅ {montant:,.0f} GNF enregistré !"
            message_type = "success"
        else: message = "❌ Numéro non reconnu."; message_type = "error"
        montant_choisi = montant
    cur.close(); conn.close()
    alert = f'<div class="{"alert-success" if message_type=="success" else "alert-error"}">{message}</div>' if message else ""
    pct = min(100, int((cagnotte['montant_collecte'] / cagnotte['montant_objectif']) * 100)) if cagnotte['montant_objectif'] else 0
    return f"""{STYLE}{PWA_TAGS}<div class="container"><div class="card cagnotte-card"><h2>🚨 {cagnotte['titre']}</h2><p>{cagnotte['description']}</p>
    <div style="display:flex;justify-content:space-between;"><span>{cagnotte['montant_collecte']:,.0f} GNF</span><span>{cagnotte['montant_objectif']:,.0f} GNF</span></div>
    <div class="progress-bar"><div class="progress-fill" style="width:{pct}%;"></div></div><p style="text-align:center;">{pct}%</p>{alert}
    <form method="POST"><label>📞 Votre téléphone</label><br><input type="text" name="telephone" required><br><br>
    <label>💰 Montant (GNF)</label><br><input type="number" name="montant" required min="5000" step="5000"><br><br>
    <div class="action-buttons"><button type="submit" name="operateur" value="om" class="btn btn-om">🟠 Orange Money</button><button type="submit" name="operateur" value="momo" class="btn btn-momo">🟡 MTN MoMo</button></div></form><a href="/" class="back-link">⬅ Retour</a></div></div>"""

# ================== PDF COTISATIONS ==================
def generer_pdf_cotisations(cotisations_list, total_valide, annee_filtre):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    elements = []; styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Rapport Cotisations {annee_filtre or 'Toutes'}", styles['Title']))
    elements.append(Paragraph(f"Total : {total_valide:,.0f} GNF", styles['Heading2']))
    elements.append(Paragraph(f"Export : {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 10*mm))
    data = [['Membre', 'Famille', 'Année', 'Montant', 'Statut']]
    for c in cotisations_list: data.append([f"{c['prenom'] or ''} {c['nom']}", c['famille_nom'], str(c['annee']), f"{c['montant']:,.0f} GNF", c['statut']])
    table = Table(data, repeatRows=1); table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B9D')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
    elements.append(table); doc.build(elements); buffer.seek(0)
    response = make_response(buffer.getvalue()); response.headers['Content-Type'] = 'application/pdf'; response.headers['Content-Disposition'] = 'attachment; filename=rapport.pdf'
    return response

@app.route('/membre/<int:membre_id>/pdf')
def export_pdf_membre(membre_id):
    conn = get_db_connection(); cur = conn.cursor()
    membre = get_safe_member(conn, membre_id)
    if not membre: cur.close(); conn.close(); return "Non trouvé", 404
    cur.execute('SELECT * FROM cotisations WHERE membre_id = %s ORDER BY annee DESC', (membre_id,)); cotisations_list = cur.fetchall()
    cur.execute('SELECT COALESCE(SUM(montant), 0) as total FROM cotisations WHERE membre_id = %s AND statut = %s', (membre_id, 'payé')); total = cur.fetchone()['total']
    cur.close(); conn.close()
    buffer = BytesIO(); doc = SimpleDocTemplate(buffer, pagesize=A4); elements = []; styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Relevé de {membre['prenom'] or ''} {membre['nom']}", styles['Title']))
    elements.append(Paragraph(f"Total payé : {total:,.0f} GNF", styles['Heading2']))
    data = [['Année', 'Montant', 'Statut']]
    for c in cotisations_list: data.append([str(c['annee']), f"{c['montant']:,.0f} GNF", c['statut']])
    table = Table(data); table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c44dff')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
    elements.append(table); doc.build(elements); buffer.seek(0)
    response = make_response(buffer.getvalue()); response.headers['Content-Type'] = 'application/pdf'; response.headers['Content-Disposition'] = f'attachment; filename=mes_cotisations_{membre_id}.pdf'
    return response

# ================== ROUTES PWA ==================
@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# ================== DÉMARRAGE ==================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)