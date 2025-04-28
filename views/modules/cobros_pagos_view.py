from nicegui import ui

def cobros_pagos_view():
    with ui.column().classes('p-6'):
        ui.label('Módulo de Cobros y Pagos').classes('text-2xl text-primary')
        ui.button('Registrar Cobro y Pago', on_click=lambda: ui.notify('Cobro Pago registrado')).classes('mt-4')
