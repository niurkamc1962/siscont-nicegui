from nicegui import ui, app
from datetime import datetime
from config.modules import modules
from stores.store import AppState


async def base_layout(content_function, store: AppState, active_module: str = None):
    """Renderiza layout común con header, contenido dinámico y footer."""

    ui.query("body").style("background-color: #f5f5f5")

    # Header
    with ui.header().classes("bg-primary text-white"):
        ui.label("Siscont - ERPNext").classes("text-h5")
        ui.space()

        if store.connected:
            modulos = list(modules.keys()) + ["Salir"]
            ui.select(
                options=modulos,
                value=active_module or store.selected_module,
                label="Módulos",
                with_input=True,
                on_change=lambda e: on_module_change(e, store),
            ).props("filled color=white text-white").classes("text-white")

    # Contenido dinámico
    await content_function()

    # Footer
    with ui.footer().classes("bg-primary text-white"):
        ui.label(f"Tecnomática © {datetime.now().year}").classes("text-center w-full")


async def on_module_change(e, store: AppState):
    if e.value == "Salir":
        store.reset()
        # Limpiar storage de usuario
        app.storage.user.clear()  # Esto borrará todos los datos de sesión
        ui.notify("Sesión cerrada", type="info")
        ui.navigate.to('/')
    else:
        store.selected_module = e.value
        app.storage.user['selected_module'] = e.value
        app.storage.user['last_activity'] = datetime.now().isoformat()
        ui.navigate.to(f"/modulo/{e.value}")