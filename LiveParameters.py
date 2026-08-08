# LiveParameters.py
import adsk.core, adsk.fusion, traceback
import json
import os
import importlib 
from pathlib import Path

from . import live_logic
importlib.reload(live_logic)

app = None
ui = None
handlers = []
palette_id = 'EdJ_LiveParams_Palette_v1'
command_id = 'EdJLiveParamsCmd'

class MyCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # 1. CLEANUP OLD INSTANCES
            old = ui.palettes.itemById(palette_id)
            if old:
                live_logic._save_palette_geometry(old)
                old.deleteMe()

            # 2. ROBUST PATH CONSTRUCTION
            script_folder = os.path.dirname(os.path.realpath(__file__))
            html_path = os.path.join(script_folder, 'resources', 'live_index.html')

            if not os.path.exists(html_path):
                ui.messageBox(f'Error: HTML file not found at:\n{html_path}')
                return

            url = 'file:///' + html_path.replace('\\', '/')

            # 3. CREATE PALETTE (restoring saved size, default 360x400)
            geometry = live_logic._load_config().get('palette_geometry', {})
            width = geometry.get('width', 360)
            height = geometry.get('height', 400)

            palette = ui.palettes.add(palette_id, 'Live Parameters', url, True, True, True, width, height)
            palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight
            live_logic._restore_palette_geometry(palette)

            # 4. ATTACH HANDLERS
            onHtmlEvent = MyHTMLEventHandler()
            palette.incomingFromHTML.add(onHtmlEvent)
            handlers.append(onHtmlEvent)
            
            onClose = MyPaletteCloseHandler()
            palette.closed.add(onClose)
            handlers.append(onClose)
            
            palette.isVisible = True

        except:
            if ui: ui.messageBox('Execute Failed:\n{}'.format(traceback.format_exc()))

class MyHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    
    # --- UPDATED SAFETY CHECK ---
    def is_unsafe(self, palette):
        # 'SelectCommand' is the default idle state.
        cmd = ui.activeCommand
        if cmd != 'SelectCommand':
            # 1. Check for Auto-Save/Commit (Transient)
            if cmd == 'CommitCommand': 
                msg = "Fusion is busy.\n\nPlease try again."
            
            # 2. Check for "Sticky" Tools (Rectangle, Line, Extrude, etc)
            else:
                msg = f"-- ERROR --\n\nCommand '{cmd}' is active.\n\nClick the Canvas > Press ESC."
            
            # Send Error to UI
            if palette:
                palette.sendInfoToHTML('notification', json.dumps({
                    'message': msg,
                    'type': 'error'
                }))
            return True # It IS unsafe
        return False # It IS safe

    def notify(self, args):
        try:
            html_args = adsk.core.HTMLEventArgs.cast(args)
            data = json.loads(html_args.data)
            action = data.get('action')
            palette = ui.palettes.itemById(palette_id)
            
            # 1. ALWAYS ALLOW REFRESH (Safe to read data anytime)
            if action == 'refresh_data':
                payload = live_logic.scan_parameters()
                if palette: palette.sendInfoToHTML('update_ui', payload)
                return

            elif action == 'export_theme':
                live_logic.export_theme_logic(data.get('file_type'), data.get('content'), data.get('default_name'))
                return

            elif action == 'import_theme':
                content = live_logic.import_theme_logic(data.get('file_type'))
                if content and palette:
                    palette.sendInfoToHTML('theme_imported', content)
                return

            elif action == 'save_imported_theme':
                theme_id = data.get('id')
                theme_vars = data.get('vars')
                if theme_id and isinstance(theme_vars, dict):
                    live_logic.save_imported_theme(theme_id, theme_vars)
                return

            elif action == 'remove_imported_theme':
                theme_id = data.get('id')
                if theme_id:
                    live_logic.delete_imported_theme(theme_id)
                return

            elif action == 'reset_imported_themes':
                live_logic.clear_imported_themes()
                return

            # 2. BLOCK WRITES IF UNSAFE
            # This prevents "Ghost Parameters" that vanish after Extrude/Preview operations.
            if self.is_unsafe(palette):
                return

            # 3. PROCEED WITH WRITE OPERATIONS
            if action == 'update_param':
                payload = live_logic.update_parameter(data.get('name'), data.get('value'))
                result = json.loads(payload)
                if palette and result.get('type') == 'error':
                    palette.sendInfoToHTML('notification', payload)

            elif action == 'update_attributes':
                payload = live_logic.update_parameter_attributes(
                    data.get('old_name'), 
                    data.get('new_name'), 
                    data.get('comment')
                )
                if palette: 
                    palette.sendInfoToHTML('notification', payload)
                    result = json.loads(payload)
                    if result.get('type') == 'success':
                         palette.sendInfoToHTML('update_ui', payload)
            
            elif action == 'toggle_favorite':
                payload = live_logic.toggle_favorite(data.get('name'))
                if palette: palette.sendInfoToHTML('update_ui', payload)

            elif action == 'create_param':
                payload = live_logic.create_parameter(
                    data.get('name'), data.get('unit'), data.get('expression'), data.get('comment')
                )
                if palette: 
                    palette.sendInfoToHTML('notification', payload)
                    palette.sendInfoToHTML('update_ui', payload)

            elif action == 'delete_param':
                payload_str = live_logic.delete_parameter(data.get('name'))
                payload_data = json.loads(payload_str)
                if palette:
                    palette.sendInfoToHTML('notification', payload_str)
                    if payload_data.get('type') == 'success':
                        palette.sendInfoToHTML('update_ui', payload_str)

        except:
            if ui: ui.messageBox('HTML Event Failed:\n{}'.format(traceback.format_exc()))

class MyDocActivatedHandler(adsk.core.DocumentEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        try:
            palette = ui.palettes.itemById(palette_id)
            if palette and palette.isVisible:
                payload = live_logic.scan_parameters()
                palette.sendInfoToHTML('update_ui', payload)
        except: pass 

class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        cmd = args.command
        onExec = MyCommandExecuteHandler()
        cmd.execute.add(onExec)
        handlers.append(onExec)

class MyPaletteCloseHandler(adsk.core.UserInterfaceGeneralEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        palette = ui.palettes.itemById(palette_id)
        if palette:
            live_logic._save_palette_geometry(palette)

def run(context):
    global ui, app
    app = adsk.core.Application.get()
    ui = app.userInterface
    
    if ui.commandDefinitions.itemById(command_id):
        ui.commandDefinitions.itemById(command_id).deleteMe()

    script_folder = os.path.dirname(os.path.realpath(__file__))
    res_dir = os.path.join(script_folder, 'resources')
    
    cmdDef = ui.commandDefinitions.addButtonDefinition(command_id, 'Live Parameters', 'A persistent palette for managing User Parameters in real-time.', res_dir)
    
    # toolClip: explicit reference, not relying on Fusion's resourceFolder auto-pickup
    tool_clip_path = os.path.join(res_dir, 'toolClip.png')
    if os.path.exists(tool_clip_path):
        cmdDef.toolClipFilename = tool_clip_path

    onCreated = MyCommandCreatedHandler()
    cmdDef.commandCreated.add(onCreated)
    handlers.append(onCreated)
    
    panel = ui.allToolbarPanels.itemById('SolidModifyPanel')
    if panel:
        ctrl = panel.controls.addCommand(cmdDef)
        ctrl.isPromoted = True
        
    onDocActivated = MyDocActivatedHandler()
    app.documentActivated.add(onDocActivated)
    handlers.append(onDocActivated)

def stop(context):
    try:
        palette = ui.palettes.itemById(palette_id)
        if palette:
            live_logic._save_palette_geometry(palette)
            palette.deleteMe()
        if ui.commandDefinitions.itemById(command_id): ui.commandDefinitions.itemById(command_id).deleteMe()
        panel = ui.allToolbarPanels.itemById('SolidModifyPanel')
        if panel and panel.controls.itemById(command_id): panel.controls.itemById(command_id).deleteMe()
    except: pass