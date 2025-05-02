# views/main_view.py

from nicegui import ui, app, Client
from stores.store import AppState
from views.connection_view import connection_form
from views.welcome_view import welcome_view
from views.modules import modules
from datetime import datetime


def main_view(client: Client):
    store: AppState = app.state.store

    ui.query("body").style("background-color: #f5f5f5")

    # encabezado
    with ui.header().classes("bg-primary text-white"):
        ui.label("Siscont - ERPNext").classes("text-h5")
        ui.space()
        if store.connected:
            # adicionando color blanco para el label
            ui.add_head_html(
                """
                <style>
                    .q-field__label {
                        color: white !important;
                    }
                </style>
                """
            )
            modulos = list(modules.keys()) + ["Salir"]

            ui.select(
                options=modulos,
                with_input=True,
                label="Modulos",
                on_change=lambda e: on_module_change(e, store),
            ).props("filled color=white text-white").classes("text-white")

    if not store.connected:
        connection_form(store)
    elif store.selected_module and store.selected_module in modules:
        modules[store.selected_module]()  # ejecuta la vista del modulo
    else:
        welcome_view()

    # Footer
    with ui.footer().classes("bg-primary text-white"):
        ui.label(f"Tecnomática © {datetime.now().year}").classes("text-center w-full")


def on_module_change(e, store: AppState):
    if e.value == "Salir":
        store.reset()
        ui.notify("Sesión cerrada", type="info")
        ui.navigate.to("/")
    else:
        store.selected_module = e.value
        ui.navigate.to("/")
