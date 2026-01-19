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
                "comment": param.comment, # NEW: Send comment to UI
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

# --- NEW FUNCTION ---
def update_parameter_comment(name, comment):
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        param = design.userParameters.itemByName(name)
        
        if param:
            param.comment = str(comment)
            return json.dumps({"message": "Comment Updated", "type": "success"})
        return json.dumps({"message": "Parameter not found", "type": "error"})
    except:
        return json.dumps({"message": "Failed to update comment", "type": "error"})

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