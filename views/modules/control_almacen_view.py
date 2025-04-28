from nicegui import ui

def control_almacen_view():
    with ui.column().classes('p-6'):
        ui.label('Módulo de Control de Almacen').classes('text-2xl text-primary')
        ui.button('Registrar Almance', on_click=lambda: ui.notify('Almacen registrado')).classes('mt-4')
