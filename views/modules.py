# views/modules.py

from nicegui import ui

def get_module_choices():
    return [
        {'label': 'Contabilidad', 'value': 'contabilidad'},
        {'label': 'Inventario', 'value': 'inventario'},
        {'label': 'Ventas', 'value': 'ventas'},
    ]

modules = {
    'contabilidad': type('', (), {'render': lambda: ui.label('Vista Contabilidad').classes('text-h6')}),
    'inventario': type('', (), {'render': lambda: ui.label('Vista Inventario').classes('text-h6')}),
    'ventas': type('', (), {'render': lambda: ui.label('Vista Ventas').classes('text-h6')}),
}
