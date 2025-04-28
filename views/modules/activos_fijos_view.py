from nicegui import ui

def activos_fijos_view():
    with ui.column().classes('p-6'):
        ui.label('Módulo de Activos Fijos').classes('text-2xl text-primary')
        ui.button('Registrar Activo', on_click=lambda: ui.notify('Activo registrado')).classes('mt-4')
