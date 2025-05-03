# views/main_view.py

from aiohttp import TraceRequestEndParams
from nicegui import ui, app, Client
from stores.store import AppState, app_state
from views.connection_view import connection_form
from views.welcome_view import welcome_view
from views.modules import modules
from views.base_layout import base_layout
from datetime import datetime


def main_view(client: Client):
    store: AppState = app.state.store
    
    # Restaurar estado desde user storage
    if app.storage.user.get('connected', False):
        store.connected = True
        store.selected_module = app.storage.user.get('selected_module')
        store.db_params = app.storage.user.get('db_params')
        store.ip_server = app.storage.user.get('ip_server')
    else:
        store.reset()

    def page_content():
        if not store.connected:
            connection_form(store)
        elif store.selected_module and store.selected_module in modules:
            modules[store.selected_module]()
        else:
            welcome_view()

    base_layout(page_content, store, active_module=store.selected_module)

