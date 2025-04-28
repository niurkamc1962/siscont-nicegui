from nicegui import ui

def inventarios_view():
    with ui.column().classes('p-6'):
        ui.label('Módulo de Inventarios').classes('text-2xl text-primary')
        ui.button('Registrar Inventario', on_click=lambda: ui.notify('Inventario registrado')).classes('mt-4')
