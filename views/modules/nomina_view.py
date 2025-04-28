from nicegui import ui

def nomina_view():
    with ui.column().classes('p-6'):
        ui.label('Módulo de Nómina').classes('text-2xl text-primary')
        ui.button('Procesar Nómina', on_click=lambda: ui.notify('Nómina procesada')).classes('mt-4')
