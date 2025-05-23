# views/main_view.py

from aiohttp import TraceRequestEndParams
from nicegui import ui, app, Client
from stores.store import AppState, app_state
from views.connection_view import connection_form
from views.welcome_view import welcome_view
from config.modules import modules
from views.base_layout import base_layout

async def main_view(client: Client):
    store: AppState = app.state.store

    # Inicialización segura del estado
    async def initialize_store():
        if not store.connected:
            user_data = app.storage.user.get('data', {})
            if user_data.get('connected'):
                try:
                    store.connected = True
                    store.db_params = user_data.get('db_params')
                    store.selected_module = user_data.get('selected_module')
                    store.ip_server = user_data.get('ip_server')
                    return True
                except Exception as e:
                    print(f"Error restoring session: {e}")
                    store.reset()
                    return False
            else:
                store.reset()
                return False
        return True

    # Verificar conexión antes de continuar
    is_initialized = await initialize_store()
    if not is_initialized:
        await connection_form(store)
        return

    async def page_content():
        if not store.connected:
            await connection_form(store)
        else:
            with ui.row().classes('w-full h-screen'):
                # Menú lateral
                with ui.column().classes('w-56 bg-gray-50 h-full border-r p-2'):
                    ui.label('Módulos').classes('text-xl font-bold p-2')

                    for module_name in modules.keys():
                        is_active = store.selected_module == module_name
                        ui.button(
                            module_name,
                            icon='folder',
                            on_click=lambda _, m=module_name: set_active_module(m)
                        ).props('flat') \
                            .classes('w-full justify-start text-left') \
                            .style(f'background-color: {"#E3F2FD" if is_active else "transparent"}')

                    ui.space()
                    ui.button('Salir', icon='logout', on_click=logout) \
                        .props('flat color=negative') \
                        .classes('w-full justify-start mt-auto mb-2')

                # Área de contenido
                with ui.scroll_area().classes('w-full h-full'):
                    if store.selected_module and store.selected_module in modules:
                        await modules[store.selected_module]()
                    else:
                        await welcome_view()

    def set_active_module(module_name):
        store.selected_module = module_name
        app.storage.user['data'] = {
            'connected': True,
            'selected_module': module_name,
            'db_params': store.db_params,
            'ip_server': store.ip_server
        }

    def logout():
        store.reset()
        app.storage.user.clear()
        ui.navigate.to('/')

    await base_layout(page_content, store)
