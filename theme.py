from gradio.themes.soft import Soft
from gradio.themes.utils import fonts


class CustomTheme(Soft):

    def __init__(self):
        super().__init__(
            font=fonts.GoogleFont("Roboto")
        )

        white = "#FFFFFF"
        purple = "#2F1009D"
        red = "#FC5555"

        primary = white
        secondary = "#e6e6e6"
        panel_color = red
        accent = purple
        accent_soft = "#49637a28"
        
        primary_dark = "#121212"
        secondary_dark = "#242424"
        panel_color_dark = red
        accent_dark = purple
        accent_soft_dark = "#101727"
        text_color_dark = white
        example_text_color="#9F9F9F"
        primary_button_background_dark= "#F0F1F4"
        primary_button_background_hover_dark= "#000000"
        light_grey_bg = "#F2F2F2"
        super().set(
            # # LIGHT MODE
            # body_background_fill=light_grey_bg,
            # background_fill_secondary=primary,
            # panel_background_fill=panel_color,
            # border_color_primary=primary,
            # block_background_fill=secondary,
            # block_border_color=primary,
            # block_label_background_fill=primary,
            # input_background_fill="#DADFE6",
            # input_border_color=secondary,
            # button_secondary_background_fill=accent,
            # button_secondary_text_color=white,
            # color_accent_soft=accent_soft,  
            # border_color_accent_subdued=white,

            # DARK MODE
            body_background_fill_dark="#050118",
            # body_background_fill_dark='FF000000',
            # background_fill_secondary_dark=light_grey_bg,
            background_fill_secondary_dark="#050118", #chatbot background (same color for now)
            panel_background_fill_dark="#ff7f00", #turuncu
            border_color_primary_dark=primary_dark,
            block_background_fill_dark="#050118", #bg color behind the input area
            block_border_color_dark=light_grey_bg,
            # block_label_background_fill_dark=light_grey_bg,
            block_label_background_fill_dark="#050118",
            block_label_text_color_dark="#000000", #Chatbot word
            input_background_fill_dark="#050118", #input alanı!!
            input_border_color_dark=light_grey_bg, #input alanı!!
            # button_primary_background_fill_dark="#660099", #mor
            # button_primary_text_color_dark="#bbb5d8", #lila
            color_accent_soft_dark=accent_soft_dark,
            border_color_accent_subdued_dark=accent_soft_dark,
            body_text_color_dark="#FFFFFF",

            # button_primary_border_color_hover_dark:"",
            button_primary_text_color_hover_dark= primary,
            # button_primary_background_fill_hover_dark=

            button_primary_background_fill_dark=primary_button_background_dark,
            button_primary_background_fill_hover_dark=primary_button_background_hover_dark, #I MADE THİS PINK
            button_primary_text_color_dark= "#000000",
            # button_primary_text_color_dark = "#9D9D9D",

            button_secondary_background_fill_dark = "#26E3BE", # green RETRY button
            button_secondary_background_fill_hover_dark = "#A88EFF", # I MADE THIS PURPLE
            button_secondary_text_color_dark= "#000000",
            button_secondary_text_color_hover_dark= white,

            #block_radius="15px",
        )