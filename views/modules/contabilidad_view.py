from nicegui import ui

def contabilidad_view():
    with ui.column().classes('p-6'):
        ui.label('Módulo de Contabilidad').classes('text-2xl text-primary')
        ui.button('Ver Reportes', on_click=lambda: ui.notify('Reportes Generados')).classes('mt-4')
