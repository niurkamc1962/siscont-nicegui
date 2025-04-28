# views/selected_module.py

from nicegui import app
from nicegui import ui


def selected_module(module_name: str):
    with ui.column().classes('items-center justify-center h-screen'):
        ui.label(f'Seleccionaste el módulo: {module_name}').classes('text-2xl text-primary')
        ui.button('Volver al inicio', on_click=lambda: ui.navigate.to('/')).classes('mt-4')
