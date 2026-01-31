from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def exportar_ficha_pdf(sistema, nombre_archivo=None):
    if nombre_archivo is None:
        nombre_archivo = f"{sistema['personaje']['nombre']}_ficha.pdf"

    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    ancho, alto = letter

    y = alto - 50

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Ficha de {sistema['personaje']['nombre']}")
    y -= 30

    # Stats
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "📊 STATS:")
    y -= 20
    c.setFont("Helvetica", 10)
    for stat, valor in sistema["stats"].items():
        c.drawString(60, y, f"{stat}: {valor}")
        y -= 15

    # Inventario
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "📦 INVENTARIO:")
    y -= 20
    c.setFont("Helvetica", 10)
    for obj in sistema["inventario"]:
        c.drawString(60, y, f"{obj['nombre']} ({obj['categoria']})")
        y -= 15

    # Títulos
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "🏆 TÍTULOS:")
    y -= 20
    c.setFont("Helvetica", 10)
    for t in sistema["titulos"]:
        c.drawString(60, y, f"{t['nombre']}: {t.get('descripcion','')}")
        y -= 15

    # Maldiciones
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "☠️ MALDICIONES:")
    y -= 20
    c.setFont("Helvetica", 10)
    for m in sistema["maldiciones"]:
        c.drawString(60, y, f"{m['nombre']}: {m.get('descripcion','')}")
        y -= 15

    # Historia
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "📚 HISTORIA:")
    y -= 20
    c.setFont("Helvetica", 10)
    for clave, valor in sistema["historia"].items():
        c.drawString(60, y, f"{clave}: {valor}")
        y -= 15

    c.save()
    print(f"✅ Ficha exportada como '{nombre_archivo}'")
