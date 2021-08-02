import threading

# for type annotation only
import socket

import dearpygui.dearpygui as dpg

import client_app

INPUT_TEXT_ID = 1
CHILD_ID = 2
TEXT_ID = 3


def clear_input(sender: int) -> None:
    dpg.set_value(sender, "")


def send_input_from_button(
    sender: int, app_data: str, user_data: socket.socket
) -> None:
    client_app.send(user_data, dpg.get_value(INPUT_TEXT_ID))
    clear_input(INPUT_TEXT_ID)


def send_input(sender: int, app_data: str, user_data: socket.socket) -> None:
    client_app.send(user_data, app_data)
    clear_input(sender)


def display_messages(client: socket.socket) -> None:
    while True:
        msg = client_app.receive(client)
        if not msg:
            break
        old_value = dpg.get_value(TEXT_ID)
        if old_value == "":
            dpg.set_value(TEXT_ID, msg)
        else:
            dpg.set_value(TEXT_ID, f"{old_value}\n\n{msg}")


def start() -> None:
    client = client_app.start_client()
    dpg.setup_viewport()

    with dpg.window(label="ChattyBox") as main_window:
        dpg.add_child(id=CHILD_ID, width=480, height=200)
        # dpg.add_input_text(id=5, multiline=True, height=200, width=600, readonly=True)
        dpg.add_text(
            id=TEXT_ID,
            wrap=460,
            parent=CHILD_ID,
            tracked=True,
            track_offset=1.0,
            indent=10,
        )
        dpg.add_spacing(count=2)
        dpg.add_input_text(
            id=INPUT_TEXT_ID,
            multiline=False,
            on_enter=True,
            hint="Type here...",
            callback=send_input,
            user_data=client,
            width=436,
        )
        dpg.add_same_line()
        dpg.add_button(
            id=12,
            label="Send",
            direction=1,
            callback=send_input_from_button,
            user_data=client,
        )
        threading.Thread(target=display_messages, args=(client,), daemon=True).start()

    dpg.set_primary_window(main_window, True)
    dpg.start_dearpygui()


if __name__ == "__main__":
    start()
