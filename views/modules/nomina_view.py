from nicegui import ui
from db.db_nomina import get_trabajadores, get_relaciones_trabajadores, construir_tree_trabajadores

def nomina_view():
    with ui.column().classes('p-6'):
        ui.label('Módulo de Nómina').classes('text-2xl text-primary')
        ui.button('Mostrar relaciones entre tablas', on_click=modal_relaciones).classes('mt-4')
        ui.button('Procesar Nómina', on_click=lambda: ui.notify('Nómina procesada')).classes('mt-4')
        ui.button('Exportar tablas SQL server a JSON relaciones entre tablas', on_click=lambda: ui.notify('Exportados las tablas a formatos JSON y generados los doctypes JSON')).classes('mt-4')
        # ui.button('Exportar a JSON', on_click=exportar_json).classes('mt-4')


def modal_relaciones():
    relaciones = get_relaciones_trabajadores()
    tree_trabajadores = construir_tree_trabajadores(relaciones)
    
    with ui.dialog().props('max-width=600') as dialog, ui.card():
        ui.label('Relaciones entre Tablas')
        tree_data = get_relaciones_trabajadores()
        ui.tree(tree_data, label_key='label')
        ui.button('Cerrar', on_click=dialog.close)
    
    dialog.open()