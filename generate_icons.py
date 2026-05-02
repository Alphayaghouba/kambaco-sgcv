from PIL import Image, ImageDraw, ImageFont
import os

# Créer le dossier static s'il n'existe pas
if not os.path.exists('static'):
    os.makedirs('static')

# Tailles d'icônes
sizes = [72, 96, 128, 144, 152, 192, 512]

for size in sizes:
    # Créer une image carrée
    img = Image.new('RGB', (size, size), color='#FF6B9D')
    draw = ImageDraw.Draw(img)
    
    # Dessiner un cercle blanc au centre
    margin = size // 6
    draw.ellipse([margin, margin, size-margin, size-margin], fill='#06061a')
    
    # Ajouter du texte
    text = "K"
    try:
        font = ImageFont.truetype("arial.ttf", size//2)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size - text_width) // 2, (size - text_height) // 2 - size//10)
    draw.text(position, text, fill='#FF6B9D', font=font)
    
    # Sauvegarder
    img.save(f'static/icon-{size}.png')
    print(f'✅ Icône {size}x{size} créée')

print('\n🎉 Toutes les icônes sont créées dans le dossier static/')