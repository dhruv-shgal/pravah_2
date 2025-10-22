#!/usr/bin/env python3
"""
Simple test script to verify API syntax and basic functionality
"""

def test_api_syntax():
    """Test if API files have valid syntax"""
    apis = [
        ('plantation_api.py', 'Tree Planting API'),
        ('waste_api.py', 'Waste Collection API'),
        ('animal_feeding_api.py', 'Animal Feeding API')
    ]
    
    results = []
    
    for api_file, api_name in apis:
        try:
            with open(api_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Try to compile the code
            compile(code, api_file, 'exec')
            results.append(f"✅ {api_name}: Syntax OK")
            
        except SyntaxError as e:
            results.append(f"❌ {api_name}: Syntax Error - {e}")
        except FileNotFoundError:
            results.append(f"⚠️ {api_name}: File not found")
        except Exception as e:
            results.append(f"❌ {api_name}: Error - {e}")
    
    return results

def test_model_files():
    """Check if model files exist"""
    import os
    
    models = [
        ('plantation_yolov11.pt', 'Tree Planting Model'),
        ('waste_collection_yolov11.pt', 'Waste Collection Model'),
        ('animal_feeding_yolov11.pt', 'Animal Feeding Model')
    ]
    
    results = []
    
    for model_file, model_name in models:
        if os.path.exists(model_file):
            size = os.path.getsize(model_file) / (1024 * 1024)  # Size in MB
            results.append(f"✅ {model_name}: Found ({size:.1f} MB)")
        else:
            results.append(f"❌ {model_name}: Not found")
    
    return results

def main():
    """Run all tests"""
    print("🧪 Eco-Connect API Testing")
    print("=" * 40)
    
    print("\n📝 Testing API Syntax:")
    syntax_results = test_api_syntax()
    for result in syntax_results:
        print(f"  {result}")
    
    print("\n🤖 Checking Model Files:")
    model_results = test_model_files()
    for result in model_results:
        print(f"  {result}")
    
    print("\n📋 Summary:")
    syntax_ok = sum(1 for r in syntax_results if r.startswith("✅"))
    models_ok = sum(1 for r in model_results if r.startswith("✅"))
    
    print(f"  APIs with valid syntax: {syntax_ok}/3")
    print(f"  Model files found: {models_ok}/3")
    
    if syntax_ok == 3:
        print("\n🎉 All APIs have valid syntax!")
    else:
        print("\n⚠️ Some APIs have syntax issues - check above")
    
    if models_ok == 3:
        print("🎉 All model files found!")
    else:
        print("⚠️ Some model files missing - AI verification may not work")

if __name__ == "__main__":
    main()