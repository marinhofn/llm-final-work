"""
Script to help migrate the existing frontend to work with the new backend
"""
import os
import shutil
from pathlib import Path

def migrate_frontend():
    """Migrate frontend files to work with new backend"""
    
    # Paths
    current_dir = Path(__file__).parent
    frontend_dir = current_dir.parent
    backend_dir = current_dir
    
    print("🔄 Migrating frontend to work with new backend...")
    
    # Copy frontend files to backend directory for easier serving
    frontend_files = ["pln.html", "styles.css", "seta.png"]
    
    for file in frontend_files:
        src = frontend_dir / file
        dst = backend_dir / "static" / file
        
        if src.exists():
            # Create static directory if it doesn't exist
            dst.parent.mkdir(exist_ok=True)
            
            # Copy file
            shutil.copy2(src, dst)
            print(f"✅ Copied {file} to backend/static/")
        else:
            print(f"⚠️  {file} not found in frontend directory")
    
    # Update the frontend HTML to work with new backend
    update_frontend_html(backend_dir / "static" / "pln.html")
    
    print("\n🎉 Frontend migration completed!")
    print("\n📋 Next steps:")
    print("1. Run: python setup.py")
    print("2. Run: python document_processor.py")
    print("3. Run: python app.py")
    print("4. Open: http://localhost:5000/static/pln.html")

def update_frontend_html(html_file):
    """Update the frontend HTML to work with new backend"""
    
    if not html_file.exists():
        print(f"⚠️  HTML file not found: {html_file}")
        return
    
    # Read the current HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the system message to be more appropriate for climate assistant
    old_system_message = """'role': 'system', 
          'content': 'responda a seguinte pergunta de forma clara e concisa, contendo as leis que dizem respeito ao assunto no Brasil e aconselhe, caso necessário, a buscar um advogado'"""
    
    new_system_message = """'role': 'system', 
          'content': 'Você é um assistente especializado em mudanças climáticas e meio ambiente. Responda com base em evidências científicas e sempre cite suas fontes.'"""
    
    if old_system_message in content:
        content = content.replace(old_system_message, new_system_message)
        print("✅ Updated system message for climate assistant")
    
    # Update the title
    content = content.replace("Tributouro", "Climate Assistant")
    
    # Update the placeholder text
    content = content.replace(
        "Escreva uma mensagem para Tributouro ...",
        "Faça uma pergunta sobre mudanças climáticas ou meio ambiente..."
    )
    
    # Write the updated HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Updated HTML content for climate assistant")

if __name__ == "__main__":
    migrate_frontend()
