# live_logic.py
import adsk.core, adsk.fusion, traceback
import json
import re

def scan_parameters():
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        if not design: 
            return json.dumps({"error": "No design active"})

        clean_name = re.sub(r'\s+v\d+$', '', app.activeDocument.name)

        param_data = []
        for param in design.userParameters:
            safe_val = 0
            try:
                safe_val = param.value
            except:
                pass

            param_data.append({
                "name": param.name,
                "expression": param.expression,
                "value": safe_val, 
                "unit": param.unit,
                "comment": param.comment, 
                "isFavorite": getattr(param, "isFavorite", False)
            })
        
        return json.dumps({
            "doc_name": clean_name,
            "parameters": param_data
        })
    except:
        return json.dumps({"error": "Failed to scan parameters"})

def validate_expression(expression, unit):
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        if not design: return False
        return design.unitsManager.isValidExpression(expression, unit)
    except:
        return False

def update_parameter(name, expression):
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        param = design.userParameters.itemByName(name)
        
        if not param:
            return json.dumps({"message": "Parameter not found", "type": "error"})

        if not validate_expression(expression, param.unit):
            return json.dumps({
                "message": f"Invalid value for unit ({param.unit})", 
                "type": "error"
            })

        param.expression = str(expression)
        return json.dumps({"message": "Updated", "type": "success"})

    except Exception as e:
        return json.dumps({"message": f"Error: {str(e)}", "type": "error"})

def toggle_favorite(name):
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        param = design.userParameters.itemByName(name)
        if param:
            param.isFavorite = not param.isFavorite
    except:
        pass
    return scan_parameters()

def update_parameter_attributes(old_name, new_name, comment):
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        
        # 1. Retrieve by OLD name
        param = design.userParameters.itemByName(old_name)
        if not param:
            return json.dumps({"message": "Parameter not found", "type": "error"})
            
        # 2. Handle Rename (if changed)
        if old_name != new_name:
            # Check for conflict in ALL parameters (User + Model)
            existing = design.allParameters.itemByName(new_name)
            if existing and existing.name != old_name:
                 return json.dumps({"message": f"Name '{new_name}' already in use", "type": "error"})
            
            try:
                param.name = new_name
            except Exception as e:
                return json.dumps({"message": "Invalid Name (Avoid spaces/symbols)", "type": "error"})
        
        # 3. Update Comment
        # Re-fetch by NEW name to ensure we have the valid object reference
        param = design.userParameters.itemByName(new_name)
        if param:
            param.comment = str(comment)

        # 4. Return Success + Full Scan
        scan_result = json.loads(scan_parameters())
        return json.dumps({
            "message": "Saved", 
            "type": "success",
            "doc_name": scan_result.get('doc_name'),
            "parameters": scan_result.get('parameters')
        })

    except Exception as e:
        return json.dumps({"message": f"Failed: {str(e)}", "type": "error"})

def create_parameter(name, unit, expression, comment):
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        if not design: return json.dumps({"message": "No design active", "type": "error"})

        if design.allParameters.itemByName(name):
            return json.dumps({"message": f"Parameter '{name}' already exists", "type": "error"})

        if not validate_expression(expression, unit):
            return json.dumps({
                "message": f"Invalid expression for unit ({unit})", 
                "type": "error"
            })

        real_val = adsk.core.ValueInput.createByString(expression)
        design.userParameters.add(name, real_val, unit, comment)
        
        scan_result = json.loads(scan_parameters())
        return json.dumps({
            "message": f"Created '{name}'", 
            "type": "success",
            "doc_name": scan_result.get('doc_name'),
            "parameters": scan_result.get('parameters')
        })

    except Exception as e:
        return json.dumps({"message": f"Failed: {str(e)}", "type": "error"})

def delete_parameter(name):
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        if not design: return json.dumps({"message": "No design active", "type": "error"})

        param = design.userParameters.itemByName(name)
        if not param:
            return json.dumps({"message": "Parameter not found", "type": "error"})
        
        is_deleted = param.deleteMe()
        
        if is_deleted:
            scan_result = json.loads(scan_parameters())
            return json.dumps({
                "message": f"Deleted '{name}'", 
                "type": "success",
                "doc_name": scan_result.get('doc_name'),
                "parameters": scan_result.get('parameters')
            })
        else:
            return json.dumps({
                "message": f"Could not delete '{name}'. It is likely in use.", 
                "type": "error"
            })

    except Exception as e:
        return json.dumps({"message": f"Error: {str(e)}", "type": "error"})