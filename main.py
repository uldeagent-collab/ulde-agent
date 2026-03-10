import os
import anthropic
import schedule
import time
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Config desde variables de entorno
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
EMAIL_TO = os.environ.get("EMAIL_TO", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")

client = anthropic.Anthropic()
SYSTEM_PROMPT = """Eres UldeAgent, un agente de prospección inteligente para Barranquilla, Colombia.
Tu misión es buscar negocios locales (restaurantes, tiendas, clínicas, talleres, etc.) que probablemente 
NO tengan página web o necesiten servicios de IA.

Para cada empresa encontrada, genera:
1. Nombre del negocio
2. Tipo de negocio
3. Sector/barrio en Barranquilla
4. Por qué necesita página web o IA
5. Mensaje de WhatsApp listo para enviar ofreciendo tus servicios

Responde siempre en español, de forma clara y organizada.
Genera exactamente 10 prospectos por reporte."""

def buscar_empresas():
    """Tarea principal: buscar empresas y generar reporte"""
    print(f"\n{'='*50}")
    print(f"🤖 UldeAgent ejecutando tarea: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user",
                "content": f"""Busca en Google Maps, directorios locales y redes sociales 10 negocios en Barranquilla, Colombia 
                que no tengan página web o tengan presencia digital muy débil.
                
                Busca en sectores como: El Prado, Manga, Riomar, Villa Country, Centro, Recreo, Alameda.
                Tipos de negocio: restaurantes, peluquerías, talleres mecánicos, ferreterías, clínicas, 
                consultorios médicos, tiendas de ropa, gimnasios, panaderías, papelerías.
                
                Fecha del reporte: {datetime.now().strftime('%d/%m/%Y')}
                
                Para cada uno genera también un mensaje de WhatsApp personalizado listo para copiar y enviar."""
            }]
        )

        # Extraer texto de la respuesta
        reporte = ""
        for block in response.content:
            if block.type == "text":
                reporte += block.text

        print(reporte)

        # Guardar reporte en archivo
        filename = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(f"/tmp/{filename}", "w", encoding="utf-8") as f:
            f.write(f"REPORTE ULDEAGENT - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write("="*50 + "\n\n")
            f.write(reporte)

        print(f"\n✅ Reporte guardado: {filename}")

        # Enviar por email si está configurado
        if EMAIL_TO and EMAIL_FROM and EMAIL_PASSWORD:
            enviar_email(reporte, filename)

        return reporte

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def enviar_email(contenido, filename):
    """Enviar reporte por email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = f"🤖 UldeAgent - Reporte diario {datetime.now().strftime('%d/%m/%Y')}"

        body = f"""
Buenos días!

Tu agente UldeAgent completó la búsqueda diaria de prospectos en Barranquilla.

{contenido}

---
Enviado automáticamente por UldeAgent 🤖
        """
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"📧 Reporte enviado a {EMAIL_TO}")
    except Exception as e:
        print(f"❌ Error enviando email: {e}")

def ejecutar_ahora():
    """Ejecuta el agente inmediatamente al iniciar"""
    print("🚀 UldeAgent iniciado - Ejecutando primera búsqueda...")
    buscar_empresas()

# Programar tareas automáticas
schedule.every().day.at("07:00").do(buscar_empresas)  # Todos los días a las 7am

if __name__ == "__main__":
    print("🤖 UldeAgent corriendo 24/7 en tu servidor...")
    print("📅 Búsqueda programada: todos los días a las 7:00 AM")
    print("="*50)
    
    # Ejecutar inmediatamente al iniciar
    ejecutar_ahora()
    
    # Mantener corriendo
    while True:
        schedule.run_pending()
        time.sleep(60)
