<<<<<<< HEAD
#!/usr/bin/env python3
"""
📄 Creador de PDF de Ejemplo

Script para crear un PDF de ejemplo para probar el cargador de documentos.
"""

import os
from pathlib import Path

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
except ImportError:
    print("📦 Instalando reportlab...")
    os.system("pip install reportlab")
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def crear_pdf_ejemplo():
    """Crear un PDF de ejemplo con contenido sobre IA"""
    
    # Crear directorio si no existe
    uploads_dir = Path("data/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = uploads_dir / "documento_ejemplo_ia.pdf"
    
    # Crear el documento
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Contenido del documento
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Centrado
        textColor=colors.darkblue
    )
    
    story.append(Paragraph("Inteligencia Artificial: Fundamentos y Aplicaciones", title_style))
    story.append(Spacer(1, 20))
    
    # Introducción
    intro_text = """
    La Inteligencia Artificial (IA) es una rama de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana. 
    Estos sistemas pueden aprender, razonar, percibir y resolver problemas complejos.
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Sección 1: Tipos de IA
    story.append(Paragraph("Tipos de Inteligencia Artificial", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    tipos_text = """
    <b>1. IA Débil (Narrow AI):</b> Diseñada para realizar tareas específicas como reconocimiento de voz, 
    recomendaciones de productos o diagnóstico médico.<br/><br/>
    
    <b>2. IA General (AGI):</b> Inteligencia artificial que puede realizar cualquier tarea intelectual 
    que un ser humano puede hacer.<br/><br/>
    
    <b>3. IA Superinteligente:</b> IA que supera la inteligencia humana en todos los aspectos.
    """
    story.append(Paragraph(tipos_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Sección 2: Aplicaciones
    story.append(Paragraph("Aplicaciones de la IA", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    aplicaciones_text = """
    <b>• Medicina:</b> Diagnóstico de enfermedades, análisis de imágenes médicas, desarrollo de fármacos.<br/><br/>
    
    <b>• Finanzas:</b> Detección de fraudes, trading algorítmico, evaluación de riesgos.<br/><br/>
    
    <b>• Transporte:</b> Vehículos autónomos, optimización de rutas, gestión del tráfico.<br/><br/>
    
    <b>• Educación:</b> Tutores personalizados, evaluación automática, contenido adaptativo.<br/><br/>
    
    <b>• Entretenimiento:</b> Recomendaciones de contenido, generación de música y arte.
    """
    story.append(Paragraph(aplicaciones_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Sección 3: Tecnologías
    story.append(Paragraph("Tecnologías Clave", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    tecnologias_text = """
    <b>Machine Learning:</b> Algoritmos que permiten a las computadoras aprender sin ser programadas explícitamente.<br/><br/>
    
    <b>Deep Learning:</b> Subconjunto del machine learning basado en redes neuronales artificiales.<br/><br/>
    
    <b>Procesamiento de Lenguaje Natural:</b> Permite a las computadoras entender e interpretar el lenguaje humano.<br/><br/>
    
    <b>Computer Vision:</b> Capacidad de las máquinas para interpretar y analizar información visual.
    """
    story.append(Paragraph(tecnologias_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Sección 4: Desafíos
    story.append(Paragraph("Desafíos y Consideraciones Éticas", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    desafios_text = """
    <b>• Sesgo y Equidad:</b> Los sistemas de IA pueden perpetuar sesgos existentes en los datos de entrenamiento.<br/><br/>
    
    <b>• Privacidad:</b> La IA requiere grandes cantidades de datos, lo que plantea preocupaciones sobre la privacidad.<br/><br/>
    
    <b>• Transparencia:</b> Muchos sistemas de IA son "cajas negras" difíciles de interpretar.<br/><br/>
    
    <b>• Empleo:</b> La automatización puede desplazar trabajos tradicionales.<br/><br/>
    
    <b>• Seguridad:</b> Los sistemas de IA pueden ser vulnerables a ataques maliciosos.
    """
    story.append(Paragraph(desafios_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Conclusión
    story.append(Paragraph("Conclusión", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    conclusion_text = """
    La Inteligencia Artificial representa una de las tecnologías más transformadoras de nuestro tiempo. 
    Aunque presenta desafíos significativos, su potencial para mejorar la calidad de vida humana es enorme. 
    Es fundamental desarrollar la IA de manera responsable, considerando los aspectos éticos y sociales.
    """
    story.append(Paragraph(conclusion_text, styles['Normal']))
    
    # Construir el PDF
    doc.build(story)
    
    print(f"✅ PDF de ejemplo creado: {pdf_path}")
    print(f"📄 Contenido: Documento sobre Inteligencia Artificial")
    print(f"📊 Páginas: Aproximadamente 2-3 páginas")
    
    return pdf_path


def crear_pdf_tecnico():
    """Crear un PDF técnico sobre LangGraph"""
    
    uploads_dir = Path("data/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = uploads_dir / "langgraph_tecnico.pdf"
    
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,
        textColor=colors.darkgreen
    )
    
    story.append(Paragraph("LangGraph: Construyendo Agentes de IA Complejos", title_style))
    story.append(Spacer(1, 20))
    
    # Introducción
    intro_text = """
    LangGraph es una biblioteca de Python que permite construir agentes de IA complejos y sistemas de flujo de trabajo 
    utilizando grafos de estado. Es especialmente útil para crear aplicaciones de IA que requieren múltiples pasos 
    de razonamiento y coordinación entre diferentes componentes.
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Características principales
    story.append(Paragraph("Características Principales", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    features_text = """
    <b>• Grafos de Estado:</b> Permite modelar flujos de trabajo complejos como grafos dirigidos.<br/><br/>
    
    <b>• Coordinación de Agentes:</b> Facilita la comunicación y coordinación entre múltiples agentes de IA.<br/><br/>
    
    <b>• Persistencia de Estado:</b> Mantiene el estado del flujo de trabajo entre ejecuciones.<br/><br/>
    
    <b>• Integración con LangChain:</b> Se integra perfectamente con el ecosistema de LangChain.<br/><br/>
    
    <b>• Escalabilidad:</b> Permite construir sistemas distribuidos y escalables.
    """
    story.append(Paragraph(features_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Casos de uso
    story.append(Paragraph("Casos de Uso Comunes", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    casos_text = """
    <b>• Asistentes Conversacionales:</b> Agentes que mantienen contexto y pueden realizar múltiples tareas.<br/><br/>
    
    <b>• Sistemas de Investigación:</b> Automatización de procesos de investigación y análisis.<br/><br/>
    
    <b>• Flujos de Trabajo Empresariales:</b> Automatización de procesos complejos de negocio.<br/><br/>
    
    <b>• Análisis de Datos:</b> Pipelines de procesamiento y análisis de datos.<br/><br/>
    
    <b>• Generación de Contenido:</b> Sistemas que generan contenido en múltiples pasos.
    """
    story.append(Paragraph(casos_text, styles['Normal']))
    
    doc.build(story)
    
    print(f"✅ PDF técnico creado: {pdf_path}")
    print(f"📄 Contenido: Documento técnico sobre LangGraph")
    
    return pdf_path


def main():
    """Función principal"""
    print("📄 CREANDO PDFs DE EJEMPLO")
    print("=" * 40)
    
    # Crear PDFs de ejemplo
    pdf1 = crear_pdf_ejemplo()
    pdf2 = crear_pdf_tecnico()
    
    print(f"\n✅ PDFs creados exitosamente:")
    print(f"   📄 {pdf1.name}")
    print(f"   📄 {pdf2.name}")
    
    print(f"\n💡 Ahora puedes ejecutar:")
    print(f"   python cargar_pdf_simple.py")
    print(f"   para cargar estos documentos a la base de datos")


if __name__ == "__main__":
=======
#!/usr/bin/env python3
"""
📄 Creador de PDF de Ejemplo

Script para crear un PDF de ejemplo para probar el cargador de documentos.
"""

import os
from pathlib import Path

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
except ImportError:
    print("📦 Instalando reportlab...")
    os.system("pip install reportlab")
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def crear_pdf_ejemplo():
    """Crear un PDF de ejemplo con contenido sobre IA"""
    
    # Crear directorio si no existe
    uploads_dir = Path("data/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = uploads_dir / "documento_ejemplo_ia.pdf"
    
    # Crear el documento
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Contenido del documento
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Centrado
        textColor=colors.darkblue
    )
    
    story.append(Paragraph("Inteligencia Artificial: Fundamentos y Aplicaciones", title_style))
    story.append(Spacer(1, 20))
    
    # Introducción
    intro_text = """
    La Inteligencia Artificial (IA) es una rama de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana. 
    Estos sistemas pueden aprender, razonar, percibir y resolver problemas complejos.
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Sección 1: Tipos de IA
    story.append(Paragraph("Tipos de Inteligencia Artificial", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    tipos_text = """
    <b>1. IA Débil (Narrow AI):</b> Diseñada para realizar tareas específicas como reconocimiento de voz, 
    recomendaciones de productos o diagnóstico médico.<br/><br/>
    
    <b>2. IA General (AGI):</b> Inteligencia artificial que puede realizar cualquier tarea intelectual 
    que un ser humano puede hacer.<br/><br/>
    
    <b>3. IA Superinteligente:</b> IA que supera la inteligencia humana en todos los aspectos.
    """
    story.append(Paragraph(tipos_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Sección 2: Aplicaciones
    story.append(Paragraph("Aplicaciones de la IA", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    aplicaciones_text = """
    <b>• Medicina:</b> Diagnóstico de enfermedades, análisis de imágenes médicas, desarrollo de fármacos.<br/><br/>
    
    <b>• Finanzas:</b> Detección de fraudes, trading algorítmico, evaluación de riesgos.<br/><br/>
    
    <b>• Transporte:</b> Vehículos autónomos, optimización de rutas, gestión del tráfico.<br/><br/>
    
    <b>• Educación:</b> Tutores personalizados, evaluación automática, contenido adaptativo.<br/><br/>
    
    <b>• Entretenimiento:</b> Recomendaciones de contenido, generación de música y arte.
    """
    story.append(Paragraph(aplicaciones_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Sección 3: Tecnologías
    story.append(Paragraph("Tecnologías Clave", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    tecnologias_text = """
    <b>Machine Learning:</b> Algoritmos que permiten a las computadoras aprender sin ser programadas explícitamente.<br/><br/>
    
    <b>Deep Learning:</b> Subconjunto del machine learning basado en redes neuronales artificiales.<br/><br/>
    
    <b>Procesamiento de Lenguaje Natural:</b> Permite a las computadoras entender e interpretar el lenguaje humano.<br/><br/>
    
    <b>Computer Vision:</b> Capacidad de las máquinas para interpretar y analizar información visual.
    """
    story.append(Paragraph(tecnologias_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Sección 4: Desafíos
    story.append(Paragraph("Desafíos y Consideraciones Éticas", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    desafios_text = """
    <b>• Sesgo y Equidad:</b> Los sistemas de IA pueden perpetuar sesgos existentes en los datos de entrenamiento.<br/><br/>
    
    <b>• Privacidad:</b> La IA requiere grandes cantidades de datos, lo que plantea preocupaciones sobre la privacidad.<br/><br/>
    
    <b>• Transparencia:</b> Muchos sistemas de IA son "cajas negras" difíciles de interpretar.<br/><br/>
    
    <b>• Empleo:</b> La automatización puede desplazar trabajos tradicionales.<br/><br/>
    
    <b>• Seguridad:</b> Los sistemas de IA pueden ser vulnerables a ataques maliciosos.
    """
    story.append(Paragraph(desafios_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Conclusión
    story.append(Paragraph("Conclusión", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    conclusion_text = """
    La Inteligencia Artificial representa una de las tecnologías más transformadoras de nuestro tiempo. 
    Aunque presenta desafíos significativos, su potencial para mejorar la calidad de vida humana es enorme. 
    Es fundamental desarrollar la IA de manera responsable, considerando los aspectos éticos y sociales.
    """
    story.append(Paragraph(conclusion_text, styles['Normal']))
    
    # Construir el PDF
    doc.build(story)
    
    print(f"✅ PDF de ejemplo creado: {pdf_path}")
    print(f"📄 Contenido: Documento sobre Inteligencia Artificial")
    print(f"📊 Páginas: Aproximadamente 2-3 páginas")
    
    return pdf_path


def crear_pdf_tecnico():
    """Crear un PDF técnico sobre LangGraph"""
    
    uploads_dir = Path("data/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = uploads_dir / "langgraph_tecnico.pdf"
    
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,
        textColor=colors.darkgreen
    )
    
    story.append(Paragraph("LangGraph: Construyendo Agentes de IA Complejos", title_style))
    story.append(Spacer(1, 20))
    
    # Introducción
    intro_text = """
    LangGraph es una biblioteca de Python que permite construir agentes de IA complejos y sistemas de flujo de trabajo 
    utilizando grafos de estado. Es especialmente útil para crear aplicaciones de IA que requieren múltiples pasos 
    de razonamiento y coordinación entre diferentes componentes.
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Características principales
    story.append(Paragraph("Características Principales", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    features_text = """
    <b>• Grafos de Estado:</b> Permite modelar flujos de trabajo complejos como grafos dirigidos.<br/><br/>
    
    <b>• Coordinación de Agentes:</b> Facilita la comunicación y coordinación entre múltiples agentes de IA.<br/><br/>
    
    <b>• Persistencia de Estado:</b> Mantiene el estado del flujo de trabajo entre ejecuciones.<br/><br/>
    
    <b>• Integración con LangChain:</b> Se integra perfectamente con el ecosistema de LangChain.<br/><br/>
    
    <b>• Escalabilidad:</b> Permite construir sistemas distribuidos y escalables.
    """
    story.append(Paragraph(features_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Casos de uso
    story.append(Paragraph("Casos de Uso Comunes", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    casos_text = """
    <b>• Asistentes Conversacionales:</b> Agentes que mantienen contexto y pueden realizar múltiples tareas.<br/><br/>
    
    <b>• Sistemas de Investigación:</b> Automatización de procesos de investigación y análisis.<br/><br/>
    
    <b>• Flujos de Trabajo Empresariales:</b> Automatización de procesos complejos de negocio.<br/><br/>
    
    <b>• Análisis de Datos:</b> Pipelines de procesamiento y análisis de datos.<br/><br/>
    
    <b>• Generación de Contenido:</b> Sistemas que generan contenido en múltiples pasos.
    """
    story.append(Paragraph(casos_text, styles['Normal']))
    
    doc.build(story)
    
    print(f"✅ PDF técnico creado: {pdf_path}")
    print(f"📄 Contenido: Documento técnico sobre LangGraph")
    
    return pdf_path


def main():
    """Función principal"""
    print("📄 CREANDO PDFs DE EJEMPLO")
    print("=" * 40)
    
    # Crear PDFs de ejemplo
    pdf1 = crear_pdf_ejemplo()
    pdf2 = crear_pdf_tecnico()
    
    print(f"\n✅ PDFs creados exitosamente:")
    print(f"   📄 {pdf1.name}")
    print(f"   📄 {pdf2.name}")
    
    print(f"\n💡 Ahora puedes ejecutar:")
    print(f"   python cargar_pdf_simple.py")
    print(f"   para cargar estos documentos a la base de datos")


if __name__ == "__main__":
>>>>>>> 4caeba3865603c67c51ab60f71b04353770ceb47
    main() 