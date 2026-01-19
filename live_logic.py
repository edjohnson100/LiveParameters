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

# --- UPDATED: HANDLES RENAME & COMMENT ---
def update_parameter_attributes(old_name, new_name, comment):
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        param = design.userParameters.itemByName(old_name)
        
        if not param:
            return json.dumps({"message": "Parameter not found", "type": "error"})
            
        # 1. Handle Rename if needed
        if old_name != new_name:
            # Check for conflict
            if design.userParameters.itemByName(new_name):
                 return json.dumps({"message": f"Name '{new_name}' already taken", "type": "error"})
            try:
                param.name = new_name
            except:
                return json.dumps({"message": "Invalid Name (Avoid spaces/symbols)", "type": "error"})
        
        # 2. Update Comment
        param.comment = str(comment)

        # 3. Return Success + Full Scan (since name changed, list order might change)
        scan_result = json.loads(scan_parameters())
        return json.dumps({
            "message": "Parameter Saved", 
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

        if design.userParameters.itemByName(name):
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