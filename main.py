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
from kivy.uix.textinput import TextInput
import time
import uuid
from copy import deepcopy
from collections import Counter
from dataclasses import dataclass, field
Window.maximize()
# Window.borderless = True

@dataclass(eq=False)
class Burger:
    name: str
    price: float
    ingredients: list[str]
    # added_ingredients: list[str] = field(default_factory=list)
    # removed_ingredients: list[str] = field(default_factory=list)
    added_ingredients: list[str] = field(default_factory=lambda: ['onion'])
    removed_ingredients: list[str] = field(default_factory=lambda: ['lettuce'])

    def __post_init__(self):
        self.ingredients = sorted(self.ingredients)

    def __hash__(self):
        return hash((self.name, tuple(self.ingredients), tuple(sorted(self.added_ingredients)), tuple(sorted(self.removed_ingredients))))

    def __eq__(self, other):
        if not isinstance(other, Burger):
            return NotImplemented
        return (self.name == other.name and
                self.ingredients == other.ingredients and
                self.added_ingredients == other.added_ingredients and
                self.removed_ingredients == other.removed_ingredients)

    def add_ingredient(self, ingredient: str):
        if ingredient not in self.ingredients and ingredient not in self.added_ingredients:
            self.added_ingredients.append(ingredient)

    def remove_ingredient(self, ingredient: str):
        if ingredient in self.ingredients and ingredient not in self.removed_ingredients:
            self.removed_ingredients.append(ingredient)
            self.ingredients.remove(ingredient)

    def display_ingredients(self):
        ingredients_display = []
        for ingredient in self.ingredients:
            if ingredient in self.removed_ingredients:
                ingredients_display.append(f"NO {ingredient}")
            else:
                ingredients_display.append(ingredient)
        for ingredient in self.added_ingredients:
            ingredients_display.append(f"ADD {ingredient}")
        return ', '.join(ingredients_display)

    def display_modifications(self):
        add_items = []
        remove_items = []
        if self.added_ingredients:
            add_items.extend(ing for ing in self.added_ingredients)
        if self.removed_ingredients:
            remove_items.extend(ing for ing in self.removed_ingredients)
        return add_items, remove_items

@dataclass
class Menu:
    burgers: list[Burger] = field(default_factory=list)

    def add_burger(self, burger: Burger):
        self.burgers.append(burger)

    def remove_burger(self, burger_name: str):
        self.burgers = [burger for burger in self.burgers if burger.name != burger_name]

    def find_burger(self, burger_name: str):
        return next((burger for burger in self.burgers if burger.name == burger_name), None)

    def display_menu(self):
        pass
        # for burger in self.burgers


class Order:
    order_id: str
    customer_name: str
    existing_orders = {}

    def __new__(cls, order_id):
        if order_id in cls.existing_orders:
            return cls.existing_orders[order_id]
        else:
            instance = super(Order, cls).__new__(cls)
            cls.existing_orders[order_id] = instance
            return instance

    def __init__(self, order_id):
        if not hasattr(self, 'initialized'):
            self.order_id = order_id
            self.burgers = []
            self.initialized = True

    def count_identical_burgers(self):

        burger_counts = Counter(self.burgers)
        return {burger: count for burger, count in burger_counts.items()}

    def add_burger(self, burger):
        self.burgers.append(burger)

    def remove_burger(self, burger):
        self.burgers.remove(burger)

    def total_price(self):
        return sum(burger.price for burger in self.burgers)

    def order_details(self):
        detail = ""
        for burger in self.burgers:
            detail += f"{burger.name}: {burger.display_ingredients()}\n"
        return detail

    # def prepare_display(self):
    #     grouped_burgers = {}
    #     for burger in self.burgers:
    #         key = (burger.name, tuple(burger.ingredients), tuple(burger.added_ingredients), tuple(burger.removed_ingredients))
    #         if key not in grouped_burgers:
    #             grouped_burgers[key] = [burger, 1]
    #         else:
    #             grouped_burgers[key][1] += 1
    #
    #     display_lines = []
    #     for (name, ingredients, added, removed), (sample_burger, count) in grouped_burgers.items():
    #         if count > 1:
    #             display_lines.append(f"{name} x{count} - ${sample_burger.price} each")
    #         else:
    #             display_lines.append(f"{name} - ${sample_burger.price}")
    #         display_lines.extend(ingredients)
    #         if added or removed:
    #             display_lines.append(sample_burger.display_modifications())
    #
    #         total_price = sample_burger.price * count
    #         display_lines.append(f"Total for these: ${total_price:.2f}")
    #         display_lines.append("")  # add a blank line for spacing
    #
    #     return "\n".join(display_lines)


class BurgerApp(MDApp):
    def __init__(self, **kwargs):
        super(BurgerApp, self).__init__(**kwargs)

        self.menu = self.populate_menu()
        self.current_order = None
        self.existing_orders = []

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
            orientation="tb-lr", cols=4, rows=2, padding=[10, 10, 10, 10], spacing=10
        )

        # Orders
        for i in range(1, 5): # 4 orders on screen at a time
            setattr(
                self,
                f"order_{i}",
                MDLabel(
                    text="",
                    padding=(50, 50, 50, 50),
                    font_style="H6",
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

        self.name_text_input = TextInput()

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
            # on_dismiss=self.reset_order_id,
        )
        popup.open()

    def add_inventory_to_order_popup(self, layout):
        for burger in self.menu.burgers:
            layout.add_widget(
                MDLabel(
                    text=f"{burger.name}  ${burger.price}",
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
                    on_release=lambda x, burger=burger: self.add_item_to_order(burger)
                )
            )

            layout.add_widget(
                MDFlatButton(
                    text="Modify",
                    _min_height=60,
                    line_color="white",
                    on_release=lambda x, burger=burger: self.open_modify_item_popup(
                        burger
                    ),
                )
            )

    def add_item_to_order(self, burger: Burger):
        if self.current_order is None:
            self.current_order = Order(order_id=str(uuid.uuid4()))
        self.current_order.add_burger(burger)
        # print(self.current_order.burgers)

    def confirm_order(self, _):
        # print("\ninside confirm_order")
        # for order in self.orders:
        #     if order['order_id'] == self.order_id:
        self.existing_orders.append(self.current_order)
        self.current_order = None # reset current order when we close the order menu
        customer_name = self.name_text_input.text or None
        if customer_name is not None:
            self.current_order.customer_name == customer_name


        self.update_order()

    def update_order(self):
        for index, order in enumerate(self.existing_orders, start=1):
            order_id = order.order_id
            order_instance = Order(order_id)

            order_widget_attr = getattr(self, f"order_{index}", None)
            order_button_attr = getattr(self, f"order_{index}_button", None)
            if order_widget_attr and order_button_attr:
                order_string = ""
                identical_burgers = order_instance.count_identical_burgers()

                for burger, count in identical_burgers.items():
                    item_name = burger.name
                    add_items, remove_items = burger.display_modifications()

                    for entry in self.menu.burgers:
                        if entry.name == item_name:
                            modified_ingredients = []
                            for ing in entry.ingredients:
                                modified = ing
                                if ing in remove_items:
                                    modified = f"[color=ff0000]NO {ing}[/color]"
                                elif ing in add_items:
                                    modified = f"[color=00ff00]ADD {ing}[/color]"
                                modified_ingredients.append(modified)

                            ingredients = "\n".join(modified_ingredients)
                            order_string += f"\n{item_name} x{count}\n[size=14]{ingredients}[/size]\n"

                order_widget_attr.text = order_string
                order_button_attr.on_release = lambda order_id=order_id: self.order_complete(order_id=order_id)
            else:
                break
        self.clean_completed_orders()

    def clean_completed_orders(self):
        num_orders = len(self.existing_orders)
        total_widgets = (len([attr for attr in dir(self) if "order_" in attr and not "_button" in attr]) // 2)
        if num_orders < total_widgets:
            for extra_index in range(num_orders + 1, total_widgets + 1):
                extra_order_widget = getattr(self, f"order_{extra_index}", None)
                extra_order_button = getattr(self, f"order_{extra_index}_button", None)
                if extra_order_widget and extra_order_button:
                    extra_order_widget.text = ""
                    extra_order_button.on_release = self.do_nothing

    def reset_order_id(self):
        pass

    def order_complete(self, order_id=None):
        self.current_order = None
        for order in self.existing_orders:

            if order.order_id == order_id:
                self.existing_orders.remove(order)
                self.update_order()


    def populate_order_popup_right_layout(self, layout):
        for i in range(1, 11):
            setattr(self, f"item_{i}", MDLabel(text=""))
            layout.add_widget(getattr(self, f"item_{i}"))

    def populate_menu(self):
        menu = Menu()
        burgers_data = [
            ("Classic Smash", 9.99, ["patty", "cheese", "lettuce", "onion"]),
            ("Spicy Jalapeño Smash", 10.75, ["patty", "pepper jack cheese", "jalapeños", "crispy onions", "chipotle mayo"]),

        ]

        for name, price, ingredients in burgers_data:
            burger = Burger(name, price, ingredients)
            menu.add_burger(burger)

        return menu

if __name__ == "__main__":
    app = BurgerApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("Exiting...")
