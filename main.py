from kivy.config import Config

Config.set("graphics", "multisamples", "8")
Config.set("graphics", "kivy_clock", "interrupt")
Config.set("kivy", "exit_on_escape", "0")

import uuid

from collections import Counter
from dataclasses import dataclass, field

from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.properties import ListProperty, StringProperty, BooleanProperty

from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDIconButton


Window.maximize()
# Window.borderless = True


@dataclass(eq=False)
class Burger:
    name: str
    price: float
    ingredients: list[str]
    added_ingredients: list[str] = field(default_factory=list)
    removed_ingredients: list[str] = field(default_factory=list)
    additional_options: list[str] = field(default_factory=list)
    button_states: dict[str] = field(default_factory=dict)
    additional_options_button_states: dict[str] = field(default_factory=dict)
    # added_ingredients: list[str] = field(default_factory=lambda: ["onion"]) testing
    # removed_ingredients: list[str] = field(default_factory=lambda: ["lettuce"])

    def __post_init__(self):
        self.ingredients = sorted(self.ingredients)

    def __hash__(self):
        return hash(
            (
                self.name,
                tuple(self.ingredients),
                tuple(sorted(self.added_ingredients)),
                tuple(sorted(self.removed_ingredients)),
            )
        )

    def __eq__(self, other):
        if not isinstance(other, Burger):
            return NotImplemented
        return (
            self.name == other.name
            and self.ingredients == other.ingredients
            and self.added_ingredients == other.added_ingredients
            and self.removed_ingredients == other.removed_ingredients
        )

    def add_ingredient(self, ingredient: str):
        if (
            ingredient not in self.ingredients
            and ingredient not in self.added_ingredients
        ):
            self.added_ingredients.append(ingredient)

    def clone(self):
        # print(f'Inside clone function, current ID is {id(self)}')
        cloned_burger = Burger(self.name, self.price, self.ingredients, added_ingredients = [], removed_ingredients = [], additional_options = [], button_states = {}, additional_options_button_states = {})
        # print(f"Cloning burger - new ID: {id(cloned_burger)}")
        return cloned_burger

    def remove_ingredient(self, ingredient: str):
        if (
            ingredient in self.ingredients
            and ingredient not in self.removed_ingredients
        ):
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
        return ", ".join(ingredients_display)

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
        return next(
            (burger for burger in self.burgers if burger.name == burger_name), None
        )

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

        instance = super(Order, cls).__new__(cls)
        cls.existing_orders[order_id] = instance
        return instance

    def __init__(self, order_id):
        if not hasattr(self, "initialized"):
            self.order_id = order_id
            self.burgers = []
            self.initialized = True

    def count_identical_burgers(self):

        burger_counts = Counter(self.burgers)
        return dict(burger_counts.items())

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
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################


class BurgerApp(MDApp):
    def __init__(self, **kwargs):
        super(BurgerApp, self).__init__(**kwargs)

        self.menu = self.populate_menu()
        self.current_order = None
        self.existing_orders = []
        self.button_states = {}

    def create_main_layout(self):
        layout = MDGridLayout(
            orientation="tb-lr", rows=2, padding=[10, 10, 10, 10], spacing=10
        )
        top_layout = self.create_top_layout()

        layout.add_widget(top_layout)

        bottom_layout = self.create_bottom_layout()

        layout.add_widget(bottom_layout)

        return layout

    def create_top_layout(self):
        layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=0.9,
            padding=[10, 10, 10, 10],
            spacing=10,
        )
        order_layout = MDGridLayout(
            orientation="tb-lr", cols=5, rows=2, padding=[10, 10, 10, 10], spacing=10
        )

        # Orders
        for i in range(1, 6):  # 5 orders on screen at a time
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
                    text="",
                    on_release=self.do_nothing,
                    _no_ripple_effect=True,
                    size_hint_y=1,
                    _min_width=200,
                    _min_height=150,
                ),
            )
            order_layout.add_widget(getattr(self, f"order_{i}"))
            order_layout.add_widget(getattr(self, f"order_{i}_button"))

        layout.add_widget(order_layout)
        return layout

    def create_bottom_layout(self):
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
            on_release=lambda x: self.open_add_order_popup(),
        )
        button_layout.add_widget(_blank)
        button_layout.add_widget(button)
        button_layout.add_widget(_blank2)
        bottom_layout.add_widget(button_layout)
        return bottom_layout

    def do_nothing(self, *args):
        pass

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"

        layout = self.create_main_layout()
        return layout

    def open_modify_item_popup(self, burger):
        layout = MDGridLayout(orientation="tb-lr", rows=2, padding=[10, 10, 10, 10], spacing=10)
        inner_layout = MDGridLayout(orientation="lr-tb", cols=4, padding=[10, 10, 10, 10], spacing=10)
        for ingredient in burger.ingredients:
            ingredient_label, add_button, normal_button, remove_button = self.create_modify_item_row(ingredient)
            inner_layout.add_widget(ingredient_label)
            inner_layout.add_widget(remove_button)
            inner_layout.add_widget(normal_button)
            inner_layout.add_widget(add_button)
            burger.button_states[ingredient] = {
                'EXTRA': add_button,
                'NORMAL': normal_button,
                'NONE': remove_button
            }
        for option in self.get_default_options():
            default_button, spacer, spacer2, option_button = self.create_default_options_row(option)
            inner_layout.add_widget(default_button)
            inner_layout.add_widget(option_button)
            inner_layout.add_widget(spacer)
            inner_layout.add_widget(spacer2)
            burger.additional_options_button_states[option] = {
                'OPTION': option_button,
                'NONE': default_button,
                }

        layout.add_widget(inner_layout)
        confirm_button = MDFlatButton(text="Confirm", _no_ripple_effect=True, size_hint=(1,0.1), line_color='white',
                                    on_release=lambda x, burger=burger: self.confirm_modifications(burger=burger))
        layout.add_widget(confirm_button)
        self.modify_item_popup = Popup(content=layout, size_hint=(0.4, 0.8), separator_height=0,
                                    title='Modify ' + burger.name, overlay_color=(0, 0, 0, 0))
        self.modify_item_popup.open()

    def confirm_modifications(self, burger):
        order_modifications = {}
        additional_options = {}
        for ingredient, buttons in burger.button_states.items():
            for modifier, button in buttons.items():
                if button.is_selected:
                    order_modifications[ingredient] = modifier
                    button.state = 'normal'
                    break
        for options, butts in burger.additional_options_button_states.items():
            for something, button in butts.items():
                print(something, button)
        for ingredient, modifier in order_modifications.items():
            if modifier == 'EXTRA':
                burger.added_ingredients.append(ingredient)
            elif modifier == 'NONE':
                burger.removed_ingredients.append(ingredient)
        # for option, state in
        self.add_item_to_order(burger)
        self.modify_item_popup.dismiss()
        burger.button_states.clear()

    def create_modify_item_row(self, ingredient):
        ingredient_label = MDLabel(text=ingredient)
        add_button = ToggleMDFlatButton(text='EXTRA', group=ingredient)
        normal_button = ToggleMDFlatButton(text='NORMAL', group=ingredient)
        remove_button = ToggleMDFlatButton(text='NONE', group=ingredient)
        return ingredient_label, add_button, normal_button, remove_button


    def create_default_options_row(self, option):
        unique_group_name = f'option_{option}'
        default_button = ToggleMDFlatButton(text='None', default_state='None', group=unique_group_name)
        spacer = MDBoxLayout(orientation='horizontal', size_hint_x=None, width=100)
        spacer2 = MDBoxLayout(orientation='horizontal')
        option_button = ToggleMDFlatButton(text=option, default_state='None', group=unique_group_name)
        return default_button, spacer, spacer2, option_button


    def open_add_order_popup(self):
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

        self.add_order_popup = Popup(
            content=layout,
            overlay_color=(0, 0, 0, 0),
            separator_height=0,
            size_hint=(0.4, 0.8),
            # on_dismiss=self.reset_order_id,
        )
        self.add_order_popup.open()

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
                    on_release=lambda x, burger=burger: self.add_item_to_order(burger.clone()),
                )
            )
            layout.add_widget(
                MDFlatButton(
                    text="Modify",
                    _min_height=60,
                    line_color="white",
                    on_release=lambda x, burger=burger: self.open_modify_item_popup(burger.clone()),
                )
            )

    def add_item_to_order(self, burger: Burger):
        print(f"Inside add_item_to_order ID of burger object: {id(burger)}")
        print("burger, added ing:", burger.added_ingredients,"\n","removed ing",burger.removed_ingredients,"\n")
        if self.current_order is None:
            self.current_order = Order(order_id=str(uuid.uuid4()))
        self.current_order.add_burger(burger)
        # print(self.current_order.burgers)
        self.update_right_side_order_contents()

    def update_right_side_order_contents(self):
        self.clear_right_side_widgets()

        identical_burgers = self.current_order.count_identical_burgers()

        display_info = []
        for burger, count in identical_burgers.items():
            name = burger.name
            single_item_price = burger.price
            price = single_item_price * count
            display_info.append((name, single_item_price, count, price))

        for index, (name, single_item_price, count, price) in enumerate(
            display_info, start=1
        ):
            item_attr = getattr(self, f"item_{index}", None)
            if item_attr:
                item_attr.text = f"{name} {single_item_price} * {count} = {price}"

    def clear_right_side_widgets(self):
        for i in range(1, 11):  # Magic numbers yo
            item_attr = getattr(self, f"item_{i}", None)
            if item_attr:
                item_attr.text = ""

    def confirm_order(self, _):
        # print("\ninside confirm_order")
        # for order in self.orders:
        #     if order['order_id'] == self.order_id:
        self.existing_orders.append(self.current_order)
        self.current_order = None  # reset current order when we close the order menu
        customer_name = self.name_text_input.text or None
        if customer_name is not None:
            self.current_order.customer_name == customer_name

        self.update_order()
        self.add_order_popup.dismiss()

    def get_order_instance(self, order_id):
        return Order(order_id)

    def update_order_widget(self, order_widget, order_button, order_instance):
        order_string = self.construct_order_display(order_instance)
        order_widget.text = order_string
        order_button.text = 'Order Complete'
        order_button.line_color = 'white'
        order_button.on_release = (
            lambda order_id=order_instance.order_id: self.order_complete(
                order_id=order_id
            )
        )

    def construct_order_display(self, order_instance):
        order_string = ""
        identical_burgers = order_instance.count_identical_burgers()
        for burger, count in identical_burgers.items(): # COLOR
            order_string += f"[color=#ffff00]\n{burger.name}[/color] x{count}\n[size=14]{self.get_ingredient_modifications(burger)}[/size]\n"
        return order_string

    def get_ingredient_modifications(self, burger):
        add_items, remove_items = burger.display_modifications()
        modified_ingredients = []
        for entry in self.menu.burgers:
            if entry.name == burger.name:
                for ing in entry.ingredients:
                    if ing in remove_items:
                        modified_ingredients.append(f"[color=ff0000]NO {ing}[/color]")
                    elif ing in add_items:
                        modified_ingredients.append(f"[color=00ff00]EXTRA {ing}[/color]")
                    else:
                        modified_ingredients.append(ing)
        return "\n".join(modified_ingredients)

    def update_order(self):
        for index, order in enumerate(self.existing_orders, start=1):
            order_id = order.order_id
            order_instance = self.get_order_instance(order_id)
            order_widget_attr = getattr(self, f"order_{index}", None)
            order_button_attr = getattr(self, f"order_{index}_button", None)

            if order_widget_attr and order_button_attr:
                self.update_order_widget(
                    order_widget_attr, order_button_attr, order_instance
                )
            else:
                break
        self.clean_completed_orders()

    def clean_completed_orders(self):
        num_orders = len(self.existing_orders)
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
                    extra_order_button.line_color = [0, 0, 0, 0]
                    extra_order_button.text = ""
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

    def get_default_options(self):

        default_options = ['Gluten Free Bun', 'Vegan', 'Plain']
        return default_options

    def populate_menu(self):
        menu = Menu()
        burgers_data = [
        ("The Revolt (Single)", 12.00, ["Two Patties", "Rebel Sauce", "One Cheese", "Arugula", "Roma Tomato"]),
        ("The Revolt (Double)", 14.00, ["Two Patties", "Rebel Sauce", "Two Cheese", "Arugula", "Roma Tomato"]),
        ("The Hexxor", 14.00, ["Two Patties", "Avocado Bacon Sauce", "Cheese", "Arugula", "Red Onion"]),
        ("The Sham-moo", 14.00, ["Vegan Patty", "Tomato Pesto", "Arugula"]),
        ("Hot Texan", 5.00, ["Hot dog", "Chili Sauce", "Mustard", "Onion"])
        ]
        for name, price, ingredients in burgers_data:
            burger = Burger(name, price, ingredients)
            menu.add_burger(burger)

        return menu

class ToggleMDFlatButton(MDFlatButton):
    selected_color = StringProperty('white')
    normal_color = ListProperty([0, 0, 0, 1])
    group = StringProperty(None)
    default_state = StringProperty()
    is_selected = BooleanProperty(False)


    def __init__(self, default_state='NORMAL', **kwargs):
        self.default_state = default_state
        super().__init__(**kwargs)
        self.theme_text_color = 'Custom'
        self._no_ripple_effect = True

        if self.text == self.default_state:
            self.md_bg_color = [1, 1, 1, 1]  # white
            self.text_color = [0, 0, 0, 1]   # black
            self.is_selected = True
        else:
            self.md_bg_color = [0, 0, 0, 1]
            self.text_color = [1, 1, 1, 1]
            self.opacity = 0.2

    def on_release(self, *args):
        super().on_release()
        parent = self.parent
        for child in parent.children:
            if isinstance(child, ToggleMDFlatButton) and child.group == self.group:
                if child != self:
                    child.md_bg_color = [0, 0, 0, 1]
                    child.text_color = [1, 1, 1, 1]
                    child.opacity = 0.2
                    child.is_selected = False
                else:
                    child.md_bg_color = [1, 1, 1, 1]
                    child.text_color = [0, 0, 0, 1]
                    child.opacity = 1
                    child.is_selected = True


if __name__ == "__main__":
    app = BurgerApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("Exiting...")
