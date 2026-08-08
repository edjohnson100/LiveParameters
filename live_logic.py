# live_logic.py
import adsk.core, adsk.fusion, traceback
import json
import re
import os

def _read_manifest_version():
    manifest_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'LiveParameters.manifest')
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('version', '')
    except Exception:
        return ''

ADDIN_VERSION = _read_manifest_version()

# Host-side store for user-imported themes -- separate from the built-in
# Light/Dark/Sepia themes baked into live_index.html. Per-machine, gitignored
# (same pattern as LiveUtilities/GridfinityGeneratorPlus's imported_themes.json):
# survives a restart or a localStorage wipe.
IMPORTED_THEMES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'imported_themes.json')

def load_imported_themes():
    if not os.path.exists(IMPORTED_THEMES_PATH):
        return {}
    try:
        with open(IMPORTED_THEMES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_imported_theme(theme_id, theme_vars):
    themes = load_imported_themes()
    themes[theme_id] = theme_vars
    with open(IMPORTED_THEMES_PATH, 'w', encoding='utf-8') as f:
        json.dump(themes, f, indent=2)

def delete_imported_theme(theme_id):
    themes = load_imported_themes()
    if theme_id in themes:
        del themes[theme_id]
        with open(IMPORTED_THEMES_PATH, 'w', encoding='utf-8') as f:
            json.dump(themes, f, indent=2)

def clear_imported_themes():
    """Used by Factory Reset Theme Cache -- wipes every host-persisted
    imported theme, not just localStorage, so a reset actually resets."""
    if os.path.exists(IMPORTED_THEMES_PATH):
        os.remove(IMPORTED_THEMES_PATH)

def _themes_dialog_dir():
    root = os.path.dirname(os.path.realpath(__file__))
    themes_dir = os.path.join(root, 'resources', 'themes')
    return themes_dir if os.path.isdir(themes_dir) else os.path.join(root, 'resources')

def export_theme_logic(file_type, content, default_name):
    app = adsk.core.Application.get()
    ui = app.userInterface
    fileDialog = ui.createFileDialog()
    fileDialog.title = 'Export Theme'
    if file_type == 'css':
        fileDialog.filter = 'CSS Files (*.css);;All Files (*.*)'
    else:
        fileDialog.filter = 'JSON Files (*.json);;All Files (*.*)'
    fileDialog.initialDirectory = _themes_dialog_dir()
    fileDialog.initialFilename = default_name
    if fileDialog.showSave() == adsk.core.DialogResults.DialogOK:
        try:
            with open(fileDialog.filename, 'w', encoding='utf-8') as f:
                f.write(content)
            ui.messageBox(f'Theme exported to {fileDialog.filename}')
        except Exception as e:
            ui.messageBox(f'Failed to save theme:\n{str(e)}')

def import_theme_logic(file_type):
    app = adsk.core.Application.get()
    ui = app.userInterface
    fileDialog = ui.createFileDialog()
    fileDialog.title = 'Import Theme'
    if file_type == 'css':
        fileDialog.filter = 'CSS Files (*.css);;All Files (*.*)'
    else:
        fileDialog.filter = 'JSON Files (*.json);;All Files (*.*)'
    fileDialog.initialDirectory = _themes_dialog_dir()
    if fileDialog.showOpen() == adsk.core.DialogResults.DialogOK:
        try:
            with open(fileDialog.filename, 'r', encoding='utf-8') as f:
                content = f.read()
            return json.dumps({"file_type": file_type, "content": content})
        except Exception as e:
            ui.messageBox(f'Failed to read theme:\n{str(e)}')
    return None

# General-purpose host-side settings file (palette geometry, and anything
# else added later). Per-machine, gitignored -- separate from
# imported_themes.json, which is theme-import-specific.
CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')

def _load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}

def _save_config(updates):
    config_data = _load_config()
    config_data.update(updates)
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
    except OSError:
        pass

def _save_palette_geometry(palette):
    # Fusion's Palette has no resize/move event -- width/height/left/top/
    # dockingState are only readable on demand, so this is called at the two
    # points the palette's lifecycle actually gives us: the user closing it
    # and the add-in being stopped (right before palette.deleteMe()).
    try:
        _save_config({'palette_geometry': {
            'width': palette.width,
            'height': palette.height,
            'left': palette.left,
            'top': palette.top,
            'docking_state': int(palette.dockingState),
        }})
    except RuntimeError:
        pass

def _restore_palette_geometry(palette):
    geometry = _load_config().get('palette_geometry', {})
    try:
        if 'left' in geometry:
            palette.left = geometry['left']
        if 'top' in geometry:
            palette.top = geometry['top']
        if 'docking_state' in geometry:
            palette.dockingState = geometry['docking_state']
    except RuntimeError:
        pass

def scan_parameters():
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        if not design:
            return json.dumps({"error": "No design active", "addin_version": ADDIN_VERSION, "imported_themes": load_imported_themes()})

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
            "parameters": param_data,
            "addin_version": ADDIN_VERSION,
            "imported_themes": load_imported_themes()
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