# views/main_view.py

from nicegui import ui, app, Client
from stores.store import AppState
from views.connection_view import connection_form
from views.welcome_view import welcome_view
from views.modules import modules, get_module_choices
from datetime import datetime

def main_view(client: Client):
    store: AppState = app.state.store

    ui.query('body').style('background-color: #f5f5f5')

    # encabezado
    with ui.header().classes('bg-primary text-white'):
        ui.label('Siscont - ERPNext').classes('text-h5')
        ui.space()
        if store.connected:
            # Título para el menú
            ui.label('MENU').classes('text-h5 text-center text-white')
            ui.select(
                options=[(m['label'], m['value']) for m in get_module_choices()] + [('Salir', 'salir')],
                on_change=lambda e: on_module_change(e, store)
            ).props('filled label="Módulos"')

    # with ui.page_sticky(position='top'): # quitar esto para que cada vista controle su espacio
    if not store.connected:
        connection_form(store)
    elif store.selected_module in modules:
        modules[store.selected_module].render()
    else:
        welcome_view()

    # Footer
    with ui.footer().classes('bg-primary text-white'):
        ui.label(f'Tecnomática © {datetime.now().year}').classes('text-center w-full')

def on_module_change(e, store: AppState):
    if e.value == 'salir':
        store.reset()
        ui.notify('Sesión cerrada', type='info')
        ui.navigate.to('/')
    else:
        store.selected_module = e.value
        ui.navigate.to('/')
