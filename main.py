from kivy.config import Config

# Config.set('kivy', 'keyboard_mode', 'systemanddock')

# Config.set('graphics', 'show_cursor', '0')
Config.set("graphics", "multisamples", "8")
Config.set("graphics", "kivy_clock", "interrupt")
Config.set("kivy", "exit_on_escape", "0")

from kivy.core.window import Window

# from kivy.modules import monitor, inspector
from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.popup import Popup
from kivy.clock import Clock

import time
import uuid

Window.maximize()
Window.borderless = True


class BurgerApp(MDApp):
    def __init__(self, **kwargs):
        super(BurgerApp, self).__init__(**kwargs)
        self.inventory = self.create_inventory()
        self.orders = []
        self.order_id = None

    def create_main_layout(self):
        # Top layout
        layout = MDGridLayout(
            orientation="tb-lr", rows=2, padding=[10, 10, 10, 10], spacing=10
        )
        top_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=0.9,
            padding=[10, 10, 10, 10],
            spacing=10,
        )
        order_layout = MDGridLayout(
            orientation="tb-lr", cols=6, rows=2, padding=[10, 10, 10, 10], spacing=10
        )

        # Orders
        for i in range(1, 7):
            setattr(
                self,
                f"order_{i}",
                MDLabel(
                    text="",
                    padding=(50, 50, 50, 50),
                    font_style="H5",
                    markup=True,
                    size_hint_y=0.8,
                ),
            )
            setattr(
                self,
                f"order_{i}_button",
                MDFlatButton(
                    text="test",
                    on_release=self.do_nothing,
                    _no_ripple_effect=True,
                    size_hint_y=1,
                    _min_width=200,
                    _min_height=150,
                ),
            )
            order_layout.add_widget(getattr(self, f"order_{i}"))
            order_layout.add_widget(getattr(self, f"order_{i}_button"))

        top_layout.add_widget(order_layout)

        layout.add_widget(top_layout)

        # Bottom layout
        bottom_layout = MDBoxLayout(orientation="horizontal", size_hint_y=0.1)
        button_layout = MDGridLayout(orientation="lr-tb", cols=3)
        _blank = MDBoxLayout(orientation="horizontal")
        _blank2 = MDBoxLayout(orientation="horizontal")
        button = MDFlatButton(
            text="[size=20]Order[/size]",
            size_hint_y=1,
            _min_width=500,
            _min_height=250,
            line_color="white",
            padding=(0, 0, 0, 150),
            on_release=lambda x: self.add_order_popup(),
        )
        button_layout.add_widget(_blank)
        button_layout.add_widget(button)
        button_layout.add_widget(_blank2)
        bottom_layout.add_widget(button_layout)

        layout.add_widget(bottom_layout)

        return layout

    def do_nothing(self, *args):
        pass

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        layout = self.create_main_layout()
        return layout

    def create_inventory(self):
        inventory = [
            {
                "name": "Classic Double Smash",
                "price": 9.99,
                "description": "Two patties, American cheese, lettuce, tomato, onion, pickles, burger sauce",
            },
            {
                "name": "Bacon Blue Smash",
                "price": 11.50,
                "description": "Two patties, blue cheese, bacon, caramelized onions, garlic aioli",
            },
            {
                "name": "Spicy Jalapeño Smash",
                "price": 10.75,
                "description": "Two patties, pepper jack cheese, jalapeños, crispy onions, chipotle mayo",
            },
        ]
        return inventory

    def add_order_popup(self):
        layout = MDGridLayout(
            orientation="tb-lr", rows=2, padding=[10, 10, 10, 10], spacing=10
        )
        inner_layout = MDGridLayout(
            orientation="lr-tb", cols=3, padding=[10, 10, 10, 10], spacing=10
        )
        left_layout = MDGridLayout(
            orientation="lr-tb", rows=10, cols=3, padding=[10, 10, 10, 10], spacing=10
        )
        self.add_inventory_to_order_popup(left_layout)

        inner_layout.add_widget(left_layout)

        right_layout = MDGridLayout(
            orientation="tb-lr", rows=10, cols=2, padding=[10, 10, 10, 10], spacing=10
        )
        self.populate_order_popup_right_layout(right_layout)

        inner_layout.add_widget(right_layout)

        layout.add_widget(inner_layout)

        button_layout = MDGridLayout(orientation="lr-tb", cols=1, size_hint_y=0.1)
        button = MDFlatButton(
            text="Confirm", line_color="white", on_release=self.confirm_order
        )
        button_layout.add_widget(button)

        layout.add_widget(button_layout)

        popup = Popup(
            content=layout,
            overlay_color=(0, 0, 0, 0),
            separator_height=0,
            size_hint=(0.4, 0.8),
            on_dismiss=self.reset_order_id,
        )
        popup.open()

    def confirm_order(self, _):
        self.update_order()

    def update_order(self):
        #  update the widgets according to existing orders
        for index, order in enumerate(self.orders, start=1):
            order_widget_attr = getattr(self, f"order_{index}", None)
            order_button_attr = getattr(self, f"order_{index}_button", None)
            if order_widget_attr and order_button_attr:
                order_string = ""
                for item in order["items"]:
                    for entry in self.inventory:
                        if entry["name"] == item["name"]:
                            order_string += f"\n{item['name']} x{item['quantity']}\n[size=18]{entry['description']}[/size]\n"
                order_widget_attr.text = order_string
                order_button_attr.on_release = lambda order_id=order[
                    "order_id"
                ]: self.order_is_complete(order_id=order_id)
            else:
                # stop updating - it's an extra widget
                break

        #  clear any redundant widgets
        num_orders = len(self.orders)
        total_widgets = (
            len(
                [
                    attr
                    for attr in dir(self)
                    if "order_" in attr and not "_button" in attr
                ]
            )
            // 2
        )
        if num_orders < total_widgets:
            for extra_index in range(num_orders + 1, total_widgets + 1):
                extra_order_widget = getattr(self, f"order_{extra_index}", None)
                extra_order_button = getattr(self, f"order_{extra_index}_button", None)
                if extra_order_widget and extra_order_button:
                    extra_order_widget.text = ""
                    extra_order_button.on_release = self.do_nothing

    def order_is_complete(self, order_id=None):

        self.orders = [order for order in self.orders if order["order_id"] != order_id]

        Clock.schedule_once(lambda dt: self.update_order(), 0.1)


    def reset_order_id(self, _):
        self.order_id = None

    def populate_order_popup_right_layout(self, layout):
        for i in range(1, 11):
            setattr(self, f"item_{i}", MDLabel(text=""))
            layout.add_widget(getattr(self, f"item_{i}"))

    def add_inventory_to_order_popup(self, layout):
        for item in self.inventory:
            name = item["name"]
            price = item["price"]
            layout.add_widget(
                MDLabel(
                    text=f"{name}  {price}",
                    adaptive_height=False,
                    size_hint_y=None,
                    height=60,
                )
            )
            layout.add_widget(
                MDFlatButton(
                    text="Add",
                    _min_height=60,
                    line_color="white",
                    on_release=lambda x, name=name, price=price: self.add_item_to_order(
                        name, price, 1
                    ),
                )
            )

            layout.add_widget(
                MDFlatButton(
                    text="Modify",
                    _min_height=60,
                    line_color="white",
                )
            )

    def add_item_to_order(self, name, price, quantity):
        if self.order_id is None:
            # initialize a new order if no current order id is found
            self.order_id = str(uuid.uuid4())
            self.orders.append(
                {
                    "order_id": self.order_id,
                    "items": [{"name": name, "price": price, "quantity": quantity}],
                }
            )
        else:
            # find the existing order with the current order id
            order = next(
                (order for order in self.orders if order["order_id"] == self.order_id),
                None,
            )
            if order is not None:
                # check if the item already exists in the order
                item = next(
                    (item for item in order["items"] if item["name"] == name), None
                )
                if item:
                    #  item exists, increment the quantity
                    item["quantity"] += quantity
                else:
                    # item does not exist, add a new item to the order
                    order["items"].append(
                        {"name": name, "price": price, "quantity": quantity}
                    )
            else:
                # order_id is not None but no matching order is found
                self.orders.append(
                    {
                        "order_id": self.order_id,
                        "items": [{"name": name, "price": price, "quantity": quantity}],
                    }
                )
        self.update_right_side_order_contents()

    def update_right_side_order_contents(self):
        order = next(
            (order for order in self.orders if order["order_id"] == self.order_id), None
        )
        if order is not None:
            for index, item in enumerate(order["items"], start=1):
                name = item["name"]
                single_item_price = item["price"]
                quantity = item["quantity"]
                price = single_item_price * quantity
                # get the attribute by index
                item_attr = getattr(self, f"item_{index}", None)
                if item_attr:
                    item_attr.text = (
                        f"{name} {single_item_price} * {quantity} = {price}"
                    )


if __name__ == "__main__":
    app = BurgerApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("Exiting...")
