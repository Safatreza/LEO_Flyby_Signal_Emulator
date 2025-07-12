#!/usr/bin/env python3
"""
Cleanup script for LEO Flyby Signal Emulator
- Removes redundant files and directories
- Cleans up generated data and logs
- Ensures proper project structure
"""
import os
import shutil
import glob

def cleanup_project():
    """Clean up the project directory structure."""
    print("🧹 Starting project cleanup...")
    
    # Files and directories to remove
    cleanup_items = [
        # Python cache directories
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        ".pytest_cache",
        
        # Generated data (optional - uncomment if you want to remove)
        # "data/plots/*.png",
        # "data/plots/*.html", 
        # "data/logs/*.csv",
        # "data/logs/*.txt",
        
        # Temporary files
        "**/*.tmp",
        "**/*.temp",
        "**/.DS_Store",
        "**/Thumbs.db",
        
        # IDE files
        ".vscode",
        ".idea",
        "**/*.swp",
        "**/*.swo",
        
        # Backup files
        "**/*.bak",
        "**/*.backup",
        "**/*~"
    ]
    
    removed_count = 0
    
    for pattern in cleanup_items:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            try:
                if os.path.isfile(match):
                    os.remove(match)
                    print(f"  🗑️  Removed file: {match}")
                    removed_count += 1
                elif os.path.isdir(match):
                    shutil.rmtree(match)
                    print(f"  🗑️  Removed directory: {match}")
                    removed_count += 1
            except Exception as e:
                print(f"  ⚠️  Could not remove {match}: {e}")
    
    print(f"\n✅ Cleanup complete! Removed {removed_count} items.")
    
    # Ensure required directories exist
    required_dirs = [
        "data",
        "data/plots", 
        "data/logs",
        "demo/templates"
    ]
    
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"  📁 Ensured directory exists: {directory}")
    
    print("\n🎯 Project structure is now clean!")

def check_dependencies():
    """Check if all required dependencies are available."""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'numpy',
        'skyfield', 
        'plotly',
        'flask',
        'yaml',
        'pytest',
        'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'yaml':
                import yaml
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
    else:
        print("\n✅ All dependencies are available!")

def validate_structure():
    """Validate the project structure."""
    print("\n🏗️  Validating project structure...")
    
    required_files = [
        "README.md",
        "user_manual.md", 
        "user_guide.md",
        "requirements.txt",
        "config/sim_config.yaml",
        "demo/demo.py",
        "demo/demo_flask_app.py",
        "flyby_model/orbit_sim.py",
        "flyby_model/signal_model.py", 
        "flyby_model/tracking_sim.py",
        "api_interface/xlapi_mock.py",
        "api_interface/robot_receiver.py",
        "gui_dashboard/flask_app.py",
        "gui_dashboard/plotter.py",
        "tests/test_orbit_sim.py",
        "tests/test_signal_model.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {len(missing_files)}")
        for file in missing_files:
            print(f"    - {file}")
    else:
        print("\n✅ All required files are present!")

def main():
    """Main cleanup function."""
    print("🛰️  LEO Flyby Signal Emulator - Project Cleanup")
    print("=" * 50)
    
    cleanup_project()
    check_dependencies()
    validate_structure()
    
    print("\n🎉 Cleanup and validation complete!")
    print("\n📋 Next steps:")
    print("  1. Run the demo: python demo/demo.py")
    print("  2. Launch demo dashboard: python demo/demo_flask_app.py")
    print("  3. Run tests: pytest tests/")
    print("  4. Check the main project: python gui_dashboard/flask_app.py")

if __name__ == "__main__":
    main() 