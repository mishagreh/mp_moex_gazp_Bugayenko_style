import tkinter as tk

from config import DAY_NUMBER
from db_create_connection import *


class StatefulCanvas(tk.Canvas):

    def __init__(self, master, unfolded_profile_image, collapsed_profile_image, profile_image_maxprice, **kwargs):
        super().__init__(master, **kwargs)
        self.unfolded_profile_image = unfolded_profile_image
        self.collapsed_profile_image = collapsed_profile_image
        self.profile_image_maxprice = profile_image_maxprice
        self.image_y_coord = None


class DraggableCanvas(tk.Canvas):

    @staticmethod
    def __get_profile_images_from_db() -> list:
        """
        Retrieves current day profile images names from DB. Plus converts the files into tk.PhotoImage objects.
        """
        n = DAY_NUMBER  # number of history profiles
        with create_connection('C:/mp/mp_db.sqlite') as connection:
            read_query = f"SELECT * FROM gazp_profile_images ORDER BY date DESC LIMIT {n}"
            profile_images_from_db = execute_read_query(connection, read_query)[::-1]

        profile_images_from_db = [list(i) for i in profile_images_from_db]
        for i in profile_images_from_db:
            i[1] = tk.PhotoImage(file=f'C:/mp/mp_images/{i[1]}')
            i[2] = tk.PhotoImage(file=f'C:/mp/mp_images/{i[2]}')

        # additional data for current day empty canvas
        profile_images_from_db.append(['today',
                                       tk.PhotoImage(file='images15pxls\\image_ .png'),
                                       tk.PhotoImage(file='images15pxls\\image_ .png'),
                                       '0',
                                       '0'])

        return profile_images_from_db

    def __init__(self, master, arg1, **kwargs):
        super().__init__(master, **kwargs)
        self.day_canvases_list = []  # a list of daily canvases within draggable canvas
        self.canvas_height = 15*len(arg1[0])  # initial value for all the internal daily canvases
        self.int_canvas = None  # initial container (frame) for all the daily canvases
        self.canvas_maxprice = arg1[0][0]
        self.canvas_minprice = arg1[0][-1]
        self.profile_images_from_db = self.__get_profile_images_from_db()
        self.start_pos = 0, 0
        self.__add_internal_canvas()
        self.current_widget = None  # when hovering a mouse over an exact canvas (for events)

    def __on_drag_start(self, event) -> None:
        """
        Calculates the initial coordinates when starting dragging.
        """
        eventx = event.x_root-self.bbox("canv")[0] + self.winfo_rootx()
        eventy = event.y_root-self.bbox("canv")[1] + self.winfo_rooty()
        self.start_pos = eventx, eventy

        return

    def __on_drag_motion(self, event) -> None:
        """
        Calculates coordinate's deltas when dragging a canvas and moves it.
        """

        dx = event.x_root + self.winfo_rootx()-self.start_pos[0]
        dy = event.y_root + self.winfo_rooty()-self.start_pos[1]

        # The max(..., 0) claps it down so that it can't go off of the screen
        # upper left and lower right
        self.moveto("canv", min(dx, 0) and max(dx, -600),
                    min(dy, 0) and max(dy, -(self.canvas_height - 1000)))

        return

    def __add_internal_canvas(self) -> None:
        """
        Creates all the daily canvases. Puts canvas' objects into a list as an instance attribute.
        """
        self.int_canvas = tk.Frame(self)
        self.create_window(0, 0, anchor='nw', window=self.int_canvas, tags="canv")
        background_colors = ('#203039', '#20303F')
        for i in range(0, DAY_NUMBER+1, 1):
            day_frame = tk.Frame(self.int_canvas, width=360, height=self.canvas_height)
            day_frame.pack(side='left', anchor='nw', fill='y')

            day_canvas = StatefulCanvas(
                day_frame,
                self.profile_images_from_db[i][1],
                self.profile_images_from_db[i][2],
                self.profile_images_from_db[i][3],
                width=360, height=self.canvas_height, bg=f'{background_colors[0] if i%2 else background_colors[1]}',
                bd=0, highlightthickness=0, relief='ridge')
            day_canvas.pack(anchor='nw', fill='y')

            day_canvas.image_y_coord = \
                15*int((100*float(self.canvas_maxprice)-100*float(day_canvas.profile_image_maxprice))/5)

            day_canvas.create_image(
                0, day_canvas.image_y_coord, image=day_canvas.collapsed_profile_image, anchor='nw',
                tags='collapsed_profile_image')

            # events' bindings
            day_canvas.bind('<Enter>', self.__define_widget)  # when mouse cursor enters a widget
            day_canvas.bind('<space>', lambda event: self.__collapse_unfold(event))
            day_canvas.bind('<Button>', self.__on_drag_start)
            day_canvas.bind('<B1-Motion>', self.__on_drag_motion)
            day_canvas.bind('<Motion>', self.__horizontal_line)

            self.day_canvases_list.append(day_canvas)

        # 2 extra canvases have been added, first for current day, second just for free space in the window
        # removing the second extra canvas from the list, no need to work with it since now
        # self.day_canvases_list = self.day_canvases_list[:-1]

        return

    def __define_widget(self, event) -> None:
        """
        Defines a widget when hovering with a mouse cursor over an exact canvas.
        """
        self.current_widget = event.widget
        event.widget.focus_set()
        return

    @staticmethod
    def __collapse_unfold(event) -> None:
        """
        Changes the profile when clicking with Whitespace key.
        """
        widget = event.widget
        if widget.find_withtag("collapsed_profile_image"):
            widget.delete("collapsed_profile_image")
            widget.create_image(
                0, widget.image_y_coord, image=widget.unfolded_profile_image, anchor='nw',
                tags="unfolded_profile_image")
        else:
            widget.delete("unfolded_profile_image")
            widget.create_image(
                0, widget.image_y_coord, image=widget.collapsed_profile_image, anchor='nw',
                tags="collapsed_profile_image")

        return

    def __horizontal_line(self, event) -> None:
        """
        Draws a horizontal line across the screen.
        """

        x0 = 0
        y0 = int(event.y/15)*15
        x1 = x0 + 360
        y1 = y0 + 15

        color = '#151E40'

        for i in self.day_canvases_list:
            if i.find_withtag("horizontal"):
                i.delete('horizontal')
                i.create_rectangle(x0, y0, x1, y1, fill=color, tags='horizontal', outline=color)
                i.tag_lower('horizontal')
            else:
                i.create_rectangle(x0, y0, x1, y1, fill=color, tags="horizontal", outline=color)
                i.tag_lower('horizontal')
        return
