from nicegui import ui
# from db.db_nomina import get_trabajadores, get_relaciones_trabajadores, construir_tree_trabajadores
# from stores.store import app_state
from db.db_nomina import construir_tree_trabajadores
from services.nomina_services import fetch_relaciones_trabajadores


def nomina_view():
    with ui.column().classes('p-6'):
        ui.label('Módulo de Nómina').classes('text-2xl text-primary')
        ui.button('Mostrar relaciones entre tablas', on_click=modal_relaciones).classes('mt-4')
        ui.button('Procesar Nómina', on_click=lambda: ui.notify('Nómina procesada')).classes('mt-4')
        ui.button('Exportar tablas SQL server a JSON relaciones entre tablas', on_click=lambda: ui.notify('Exportados las tablas a formatos JSON y generados los doctypes JSON')).classes('mt-4')
        # ui.button('Exportar a JSON', on_click=exportar_json).classes('mt-4')


async def modal_relaciones():
    relaciones = await fetch_relaciones_trabajadores()
    print('RELACIONES:', relaciones)
    tree_trabajadores = construir_tree_trabajadores(relaciones)
    print('TREE', tree_trabajadores)
    
    with ui.dialog().props('max-width=600') as dialog, ui.card():
        ui.label('Relaciones entre Tablas')
        ui.tree(tree_trabajadores, label_key='label')  # Corregido aquí: se mostrará el árbol
        ui.button('Cerrar', on_click=dialog.close)

    dialog.open()
