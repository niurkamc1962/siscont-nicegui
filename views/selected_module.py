from nicegui import app
from stores.store import AppState
from config.modules import modules
from views.base_layout import base_layout


async def selected_module(module_name: str):
    store: AppState = app.state.store
    store.selected_module = module_name  # guarda el módulo actual

    async def module_content():
        if module_name in modules:
            await modules[module_name]()
        else:
            from nicegui import ui
            ui.label("Módulo no encontrado").classes("text-red-500 text-xl")

    await base_layout(module_content, store, active_module=module_name)
