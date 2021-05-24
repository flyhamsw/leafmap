"""Main module."""

import os
import ipyleaflet
from ipyleaflet import Marker, MarkerCluster, TileLayer, WidgetControl
from .basemaps import basemap_tiles
from .common import *
from .legends import builtin_legends


class Map(ipyleaflet.Map):
    """The Map class inherits ipyleaflet.Map. The arguments you can pass to the Map can be found at https://ipyleaflet.readthedocs.io/en/latest/api_reference/map.html. By default, the Map will add Google Maps as the basemap. Set add_google_map = False to use OpenStreetMap as the basemap.

    Returns:
        object: ipyleaflet map object.
    """

    def __init__(self, **kwargs):

        if "center" not in kwargs:
            kwargs["center"] = [40, -100]

        if "zoom" not in kwargs:
            kwargs["zoom"] = 4

        if "scroll_wheel_zoom" not in kwargs:
            kwargs["scroll_wheel_zoom"] = True

        if "attribution_control" not in kwargs:
            kwargs["attribution_control"] = False

        super().__init__(**kwargs)
        self.baseclass = "ipyleaflet"
        self.toolbar = None
        self.toolbar_button = None
        self.tool_output = None
        self.tool_output_ctrl = None
        self.layer_control = None

        if "height" not in kwargs:
            self.layout.height = "600px"
        else:
            self.layout.height = kwargs["height"]

        if "layers_control" not in kwargs:
            kwargs["layers_control"] = False
        if kwargs["layers_control"]:
            self.add_control(ipyleaflet.LayersControl(position="topright"))

        if "fullscreen_control" not in kwargs:
            kwargs["fullscreen_control"] = True
        if kwargs["fullscreen_control"]:
            self.add_control(ipyleaflet.FullScreenControl())

        if "draw_control" not in kwargs:
            kwargs["draw_control"] = True
        if kwargs["draw_control"]:
            draw_control = ipyleaflet.DrawControl(
                marker={"shapeOptions": {"color": "#3388ff"}},
                rectangle={"shapeOptions": {"color": "#3388ff"}},
                circle={"shapeOptions": {"color": "#3388ff"}},
                circlemarker={},
                edit=True,
                remove=True,
                position="topleft",
            )
            self.add_control(draw_control)

        if "measure_control" not in kwargs:
            kwargs["measure_control"] = True
        if kwargs["measure_control"]:
            self.add_control(ipyleaflet.MeasureControl(position="topleft"))

        if "scale_control" not in kwargs:
            kwargs["scale_control"] = True
        if kwargs["scale_control"]:
            self.add_control(ipyleaflet.ScaleControl(position="bottomleft"))

        if "google_map" not in kwargs:
            layer = ipyleaflet.TileLayer(
                url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                attribution="Google",
                name="Google Maps",
            )
            self.add_layer(layer)
        else:
            if kwargs["google_map"].upper() == "ROADMAP":
                layer = ipyleaflet.TileLayer(
                    url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                    attribution="Google",
                    name="Google Maps",
                )
            elif kwargs["google_map"].upper() == "HYBRID":
                layer = ipyleaflet.TileLayer(
                    url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                    attribution="Google",
                    name="Google Satellite",
                )
            elif kwargs["google_map"].upper() == "TERRAIN":
                layer = ipyleaflet.TileLayer(
                    url="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
                    attribution="Google",
                    name="Google Terrain",
                )
            elif kwargs["google_map"].upper() == "SATELLITE":
                layer = ipyleaflet.TileLayer(
                    url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                    attribution="Google",
                    name="Google Satellite",
                )
            else:
                layer = ipyleaflet.TileLayer(
                    url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                    attribution="Google",
                    name="Google Maps",
                )
            self.add_layer(layer)

        if "toolbar_control" not in kwargs:
            kwargs["toolbar_control"] = True
        if kwargs["toolbar_control"]:
            from .toolbar import main_toolbar

            main_toolbar(self)

        if "use_voila" not in kwargs:
            kwargs["use_voila"] = False

    def set_center(self, lon, lat, zoom=None):
        """Centers the map view at a given coordinates with the given zoom level.

        Args:
            lon (float): The longitude of the center, in degrees.
            lat (float): The latitude of the center, in degrees.
            zoom (int, optional): The zoom level, from 1 to 24. Defaults to None.
        """
        self.center = (lat, lon)
        if zoom is not None:
            self.zoom = zoom

    def get_scale(self):
        """Returns the approximate pixel scale of the current map view, in meters.

        Returns:
            float: Map resolution in meters.
        """
        import math

        zoom_level = self.zoom
        # Reference: https://blogs.bing.com/maps/2006/02/25/map-control-zoom-levels-gt-resolution
        resolution = 156543.04 * math.cos(0) / math.pow(2, zoom_level)
        return resolution

    def add_basemap(self, basemap="HYBRID"):
        """Adds a basemap to the map.

        Args:
            basemap (str, optional): Can be one of string from ee_basemaps. Defaults to 'HYBRID'.
        """
        try:
            if (
                basemap in basemap_tiles.keys()
                and basemap_tiles[basemap] not in self.layers
            ):
                self.add_layer(basemap_tiles[basemap])

        except Exception:
            raise ValueError(
                "Basemap can only be one of the following:\n  {}".format(
                    "\n  ".join(basemap_tiles.keys())
                )
            )

    def find_layer(self, name):
        """Finds layer by name

        Args:
            name (str): Name of the layer to find.

        Returns:
            object: ipyleaflet layer object.
        """
        layers = self.layers

        for layer in layers:
            if layer.name == name:
                return layer

        return None

    def find_layer_index(self, name):
        """Finds layer index by name

        Args:
            name (str): Name of the layer to find.

        Returns:
            int: Index of the layer with the specified name
        """
        layers = self.layers

        for index, layer in enumerate(layers):
            if layer.name == name:
                return index

        return -1

    def layer_opacity(self, name, value=1.0):
        """Changes layer opacity.

        Args:
            name (str): The name of the layer to change opacity.
            value (float, optional): The opacity value to set. Defaults to 1.0.
        """
        layer = self.find_layer(name)
        try:
            layer.opacity = value
        except Exception as e:
            raise Exception(e)

    def add_wms_layer(
        self,
        url,
        layers,
        name=None,
        attribution="",
        format="image/jpeg",
        transparent=False,
        opacity=1.0,
        shown=True,
        **kwargs,
    ):
        """Add a WMS layer to the map.

        Args:
            url (str): The URL of the WMS web service.
            layers (str): Comma-separated list of WMS layers to show.
            name (str, optional): The layer name to use on the layer control. Defaults to None.
            attribution (str, optional): The attribution of the data layer. Defaults to ''.
            format (str, optional): WMS image format (use ‘image/png’ for layers with transparency). Defaults to 'image/jpeg'.
            transparent (bool, optional): If True, the WMS service will return images with transparency. Defaults to False.
            opacity (float, optional): The opacity of the layer. Defaults to 1.0.
            shown (bool, optional): A flag indicating whether the layer should be on by default. Defaults to True.
        """

        if name is None:
            name = str(layers)

        try:
            wms_layer = ipyleaflet.WMSLayer(
                url=url,
                layers=layers,
                name=name,
                attribution=attribution,
                format=format,
                transparent=transparent,
                opacity=opacity,
                visible=shown,
                **kwargs,
            )
            self.add_layer(wms_layer)

        except Exception as e:
            print("Failed to add the specified WMS TileLayer.")
            raise Exception(e)

    def add_tile_layer(
        self,
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        name="Untitled",
        attribution="",
        opacity=1.0,
        shown=True,
        **kwargs,
    ):
        """Adds a TileLayer to the map.

        Args:
            url (str, optional): The URL of the tile layer. Defaults to 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'.
            name (str, optional): The layer name to use for the layer. Defaults to 'Untitled'.
            attribution (str, optional): The attribution to use. Defaults to ''.
            opacity (float, optional): The opacity of the layer. Defaults to 1.
            shown (bool, optional): A flag indicating whether the layer should be on by default. Defaults to True.
        """
        try:
            tile_layer = TileLayer(
                url=url,
                name=name,
                attribution=attribution,
                opacity=opacity,
                visible=shown,
                **kwargs,
            )
            self.add_layer(tile_layer)

        except Exception as e:
            print("Failed to add the specified TileLayer.")
            raise Exception(e)

    def add_COG_layer(
        self,
        url,
        name="Untitled",
        attribution="",
        opacity=1.0,
        shown=True,
        titiler_endpoint="https://api.cogeo.xyz/",
        **kwargs,
    ):
        """Adds a COG TileLayer to the map.

        Args:
            url (str): The URL of the COG tile layer.
            name (str, optional): The layer name to use for the layer. Defaults to 'Untitled'.
            attribution (str, optional): The attribution to use. Defaults to ''.
            opacity (float, optional): The opacity of the layer. Defaults to 1.
            shown (bool, optional): A flag indicating whether the layer should be on by default. Defaults to True.
            titiler_endpoint (str, optional): Titiler endpoint. Defaults to "https://api.cogeo.xyz/".
        """
        tile_url = get_COG_tile(url, titiler_endpoint, **kwargs)
        center = get_COG_center(url, titiler_endpoint)  # (lon, lat)
        self.add_tile_layer(tile_url, name, attribution, opacity, shown)
        self.set_center(lon=center[0], lat=center[1], zoom=10)

    def add_COG_mosaic(
        self,
        links,
        name="Untitled",
        attribution="",
        opacity=1.0,
        shown=True,
        titiler_endpoint="https://api.cogeo.xyz/",
        username="anonymous",
        overwrite=False,
        show_footprints=False,
        verbose=True,
        **kwargs,
    ):
        """Add a virtual mosaic of COGs to the map.

        Args:
            links (list): A list of links pointing to COGs.
            name (str, optional): The layer name to use for the layer. Defaults to 'Untitled'.
            attribution (str, optional): The attribution to use. Defaults to ''.
            opacity (float, optional): The opacity of the layer. Defaults to 1.
            shown (bool, optional): A flag indicating whether the layer should be on by default. Defaults to True.
            titiler_endpoint (str, optional): Titiler endpoint. Defaults to "https://api.cogeo.xyz/".
            username (str, optional): The username to create mosaic using the titiler endpoint. Defaults to 'anonymous'.
            overwrite (bool, optional): Whether or not to replace existing layer with the same layer name. Defaults to False.
            show_footprints (bool, optional): Whether or not to show footprints of COGs. Defaults to False.
            verbose (bool, optional): Whether or not to print descriptions. Defaults to True.
        """
        layername = name.replace(" ", "_")
        tile = get_COG_mosaic(
            links,
            titiler_endpoint=titiler_endpoint,
            username=username,
            layername=layername,
            overwrite=overwrite,
            verbose=verbose,
        )
        self.add_tile_layer(tile, name, attribution, opacity, shown)

        if show_footprints:
            if verbose:
                print(
                    f"Generating footprints of {len(links)} COGs. This might take a while ..."
                )
            coords = []
            for link in links:
                coord = get_COG_bounds(link)
                if coord is not None:
                    coords.append(coord)
            fc = coords_to_geojson(coords)

            geo_json = ipyleaflet.GeoJSON(
                data=fc,
                style={
                    "opacity": 1,
                    "dashArray": "1",
                    "fillOpacity": 0,
                    "weight": 1,
                },
                name="Footprints",
            )

            self.add_layer(geo_json)
            center = get_center(fc)
            if verbose:
                print("The footprint layer has been added.")
        else:
            center = get_COG_center(links[0], titiler_endpoint)

        self.set_center(center[0], center[1], zoom=6)

    def add_STAC_layer(
        self,
        url,
        bands=None,
        name="Untitled",
        attribution="",
        opacity=1.0,
        shown=True,
        titiler_endpoint="https://api.cogeo.xyz/",
        **kwargs,
    ):
        """Adds a STAC TileLayer to the map.

        Args:
            url (str): The URL of the COG tile layer.
            name (str, optional): The layer name to use for the layer. Defaults to 'Untitled'.
            attribution (str, optional): The attribution to use. Defaults to ''.
            opacity (float, optional): The opacity of the layer. Defaults to 1.
            shown (bool, optional): A flag indicating whether the layer should be on by default. Defaults to True.
            titiler_endpoint (str, optional): Titiler endpoint. Defaults to "https://api.cogeo.xyz/".
        """
        tile_url = get_STAC_tile(url, bands, titiler_endpoint, **kwargs)
        center = get_STAC_center(url, titiler_endpoint)
        self.add_tile_layer(tile_url, name, attribution, opacity, shown)
        self.set_center(lon=center[0], lat=center[1], zoom=10)

    def add_minimap(self, zoom=5, position="bottomright"):
        """Adds a minimap (overview) to the ipyleaflet map.

        Args:
            zoom (int, optional): Initial map zoom level. Defaults to 5.
            position (str, optional): Position of the minimap. Defaults to "bottomright".
        """

        minimap = ipyleaflet.Map(
            zoom_control=False,
            attribution_control=False,
            zoom=zoom,
            center=self.center,
            layers=[basemap_tiles["ROADMAP"]],
        )
        minimap.layout.width = "150px"
        minimap.layout.height = "150px"
        ipyleaflet.link((minimap, "center"), (self, "center"))
        minimap_control = WidgetControl(widget=minimap, position=position)
        self.add_control(minimap_control)

    def add_maker_cluster(self, event="click", add_marker=True):
        """Captures user inputs and add markers to the map.

        Args:
            event (str, optional): [description]. Defaults to 'click'.
            add_marker (bool, optional): If True, add markers to the map. Defaults to True.

        Returns:
            object: a marker cluster.
        """
        coordinates = []
        markers = []
        marker_cluster = MarkerCluster(name="Marker Cluster")
        self.last_click = []
        self.all_clicks = []
        if add_marker:
            self.add_layer(marker_cluster)

        def handle_interaction(**kwargs):
            latlon = kwargs.get("coordinates")

            if event == "click" and kwargs.get("type") == "click":
                coordinates.append(latlon)
                self.last_click = latlon
                self.all_clicks = coordinates
                if add_marker:
                    markers.append(Marker(location=latlon))
                    marker_cluster.markers = markers
            elif kwargs.get("type") == "mousemove":
                pass

        # cursor style: https://www.w3schools.com/cssref/pr_class_cursor.asp
        self.default_style = {"cursor": "crosshair"}
        self.on_interaction(handle_interaction)

    def split_map(self, left_layer="HYBRID", right_layer="ESRI"):
        """Adds split map.

        Args:
            left_layer (str, optional): The layer tile layer. Defaults to 'HYBRID'.
            right_layer (str, optional): The right tile layer. Defaults to 'ESRI'.
        """
        try:
            if left_layer in basemap_tiles.keys():
                left_layer = basemap_tiles[left_layer]

            if right_layer in basemap_tiles.keys():
                right_layer = basemap_tiles[right_layer]

            control = ipyleaflet.SplitMapControl(
                left_layer=left_layer, right_layer=right_layer
            )
            self.add_control(control)

        except Exception as e:
            print("The provided layers are invalid!")
            raise ValueError(e)

    def basemap_demo(self):
        """A demo for using geemap basemaps."""
        dropdown = widgets.Dropdown(
            options=list(basemap_tiles.keys()),
            value="HYBRID",
            description="Basemaps",
        )

        def on_click(change):
            basemap_name = change["new"]
            old_basemap = self.layers[-1]
            self.substitute_layer(old_basemap, basemap_tiles[basemap_name])

        dropdown.observe(on_click, "value")
        basemap_control = WidgetControl(widget=dropdown, position="topright")
        self.add_control(basemap_control)

    def add_legend(
        self,
        legend_title="Legend",
        legend_dict=None,
        legend_keys=None,
        legend_colors=None,
        position="bottomright",
        builtin_legend=None,
        layer_name=None,
        **kwargs,
    ):
        """Adds a customized basemap to the map.

        Args:
            legend_title (str, optional): Title of the legend. Defaults to 'Legend'.
            legend_dict (dict, optional): A dictionary containing legend items as keys and color as values. If provided, legend_keys and legend_colors will be ignored. Defaults to None.
            legend_keys (list, optional): A list of legend keys. Defaults to None.
            legend_colors (list, optional): A list of legend colors. Defaults to None.
            position (str, optional): Position of the legend. Defaults to 'bottomright'.
            builtin_legend (str, optional): Name of the builtin legend to add to the map. Defaults to None.
            layer_name (str, optional): Layer name of the legend to be associated with. Defaults to None.

        """
        import pkg_resources
        from IPython.display import display

        pkg_dir = os.path.dirname(
            pkg_resources.resource_filename("leafmap", "leafmap.py")
        )
        legend_template = os.path.join(pkg_dir, "data/template/legend.html")

        if "min_width" not in kwargs.keys():
            min_width = None
        if "max_width" not in kwargs.keys():
            max_width = None
        else:
            max_width = kwargs["max_width"]
        if "min_height" not in kwargs.keys():
            min_height = None
        else:
            min_height = kwargs["min_height"]
        if "max_height" not in kwargs.keys():
            max_height = None
        else:
            max_height = kwargs["max_height"]
        if "height" not in kwargs.keys():
            height = None
        else:
            height = kwargs["height"]
        if "width" not in kwargs.keys():
            width = None
        else:
            width = kwargs["width"]

        if width is None:
            max_width = "300px"
        if height is None:
            max_height = "400px"

        if not os.path.exists(legend_template):
            print("The legend template does not exist.")
            return

        if legend_keys is not None:
            if not isinstance(legend_keys, list):
                print("The legend keys must be a list.")
                return
        else:
            legend_keys = ["One", "Two", "Three", "Four", "ect"]

        if legend_colors is not None:
            if not isinstance(legend_colors, list):
                print("The legend colors must be a list.")
                return
            elif all(isinstance(item, tuple) for item in legend_colors):
                try:
                    legend_colors = [rgb_to_hex(x) for x in legend_colors]
                except Exception as e:
                    print(e)
            elif all(
                (item.startswith("#") and len(item) == 7) for item in legend_colors
            ):
                pass
            elif all((len(item) == 6) for item in legend_colors):
                pass
            else:
                print("The legend colors must be a list of tuples.")
                return
        else:
            legend_colors = [
                "#8DD3C7",
                "#FFFFB3",
                "#BEBADA",
                "#FB8072",
                "#80B1D3",
            ]

        if len(legend_keys) != len(legend_colors):
            print("The legend keys and values must be the same length.")
            return

        allowed_builtin_legends = builtin_legends.keys()
        if builtin_legend is not None:
            if builtin_legend not in allowed_builtin_legends:
                print(
                    "The builtin legend must be one of the following: {}".format(
                        ", ".join(allowed_builtin_legends)
                    )
                )
                return
            else:
                legend_dict = builtin_legends[builtin_legend]
                legend_keys = list(legend_dict.keys())
                legend_colors = list(legend_dict.values())

        if legend_dict is not None:
            if not isinstance(legend_dict, dict):
                print("The legend dict must be a dictionary.")
                return
            else:
                legend_keys = list(legend_dict.keys())
                legend_colors = list(legend_dict.values())
                if all(isinstance(item, tuple) for item in legend_colors):
                    try:
                        legend_colors = [rgb_to_hex(x) for x in legend_colors]
                    except Exception as e:
                        print(e)

        allowed_positions = [
            "topleft",
            "topright",
            "bottomleft",
            "bottomright",
        ]
        if position not in allowed_positions:
            print(
                "The position must be one of the following: {}".format(
                    ", ".join(allowed_positions)
                )
            )
            return

        header = []
        content = []
        footer = []

        with open(legend_template) as f:
            lines = f.readlines()
            lines[3] = lines[3].replace("Legend", legend_title)
            header = lines[:6]
            footer = lines[11:]

        for index, key in enumerate(legend_keys):
            color = legend_colors[index]
            if not color.startswith("#"):
                color = "#" + color
            item = "      <li><span style='background:{};'></span>{}</li>\n".format(
                color, key
            )
            content.append(item)

        legend_html = header + content + footer
        legend_text = "".join(legend_html)

        try:

            legend_output_widget = widgets.Output(
                layout={
                    # "border": "1px solid black",
                    "max_width": max_width,
                    "min_width": min_width,
                    "max_height": max_height,
                    "min_height": min_height,
                    "height": height,
                    "width": width,
                    "overflow": "scroll",
                }
            )
            legend_control = WidgetControl(
                widget=legend_output_widget, position=position
            )
            legend_widget = widgets.HTML(value=legend_text)
            with legend_output_widget:
                display(legend_widget)

            self.legend_widget = legend_output_widget
            self.legend_control = legend_control
            self.add_control(legend_control)

        except Exception as e:
            raise Exception(e)

    def add_colorbar(
        self,
        colors,
        vmin=0,
        vmax=1.0,
        index=None,
        caption="",
        categorical=False,
        step=None,
        height="45px",
        transparent_bg=False,
        position="bottomright",
        layer_name=None,
        **kwargs,
    ):
        """Add a branca colorbar to the map.

        Args:
            colors (list): The set of colors to be used for interpolation. Colors can be provided in the form: * tuples of RGBA ints between 0 and 255 (e.g: (255, 255, 0) or (255, 255, 0, 255)) * tuples of RGBA floats between 0. and 1. (e.g: (1.,1.,0.) or (1., 1., 0., 1.)) * HTML-like string (e.g: “#ffff00) * a color name or shortcut (e.g: “y” or “yellow”)
            vmin (int, optional): The minimal value for the colormap. Values lower than vmin will be bound directly to colors[0].. Defaults to 0.
            vmax (float, optional): The maximal value for the colormap. Values higher than vmax will be bound directly to colors[-1]. Defaults to 1.0.
            index (list, optional):The values corresponding to each color. It has to be sorted, and have the same length as colors. If None, a regular grid between vmin and vmax is created.. Defaults to None.
            caption (str, optional): The caption for the colormap. Defaults to "".
            categorical (bool, optional): Whether or not to create a categorical colormap. Defaults to False.
            step (int, optional): The step to split the LinearColormap into a StepColormap. Defaults to None.
            height (str, optional): The height of the colormap widget. Defaults to "45px".
            transparent_bg (bool, optional): Whether to use transparent background for the colormap widget. Defaults to True.
            position (str, optional): The position for the colormap widget. Defaults to "bottomright".
            layer_name (str, optional): Layer name of the colorbar to be associated with. Defaults to None.

        """
        from box import Box
        from branca.colormap import LinearColormap

        output = widgets.Output()
        output.layout.height = height

        if "width" in kwargs.keys():
            output.layout.width = kwargs["width"]

        if isinstance(colors, Box):
            try:
                colors = list(colors["default"])
            except Exception as e:
                print("The provided color list is invalid.")
                raise Exception(e)

        if all(len(color) == 6 for color in colors):
            colors = ["#" + color for color in colors]

        colormap = LinearColormap(
            colors=colors, index=index, vmin=vmin, vmax=vmax, caption=caption
        )

        if categorical:
            if step is not None:
                colormap = colormap.to_step(step)
            elif index is not None:
                colormap = colormap.to_step(len(index) - 1)
            else:
                colormap = colormap.to_step(3)

        colormap_ctrl = WidgetControl(
            widget=output,
            position=position,
            transparent_bg=transparent_bg,
            **kwargs,
        )
        with output:
            output.clear_output()
            display(colormap)

        self.colorbar = colormap_ctrl
        self.add_control(colormap_ctrl)

    def image_overlay(self, url, bounds, name):
        """Overlays an image from the Internet or locally on the map.

        Args:
            url (str): http URL or local file path to the image.
            bounds (tuple): bounding box of the image in the format of (lower_left(lat, lon), upper_right(lat, lon)), such as ((13, -130), (32, -100)).
            name (str): name of the layer to show on the layer control.
        """
        from base64 import b64encode
        from PIL import Image, ImageSequence
        from io import BytesIO

        try:
            if not url.startswith("http"):

                if not os.path.exists(url):
                    print("The provided file does not exist.")
                    return

                ext = os.path.splitext(url)[1][1:]  # file extension
                image = Image.open(url)

                f = BytesIO()
                if ext.lower() == "gif":
                    frames = []
                    # Loop over each frame in the animated image
                    for frame in ImageSequence.Iterator(image):
                        frame = frame.convert("RGBA")
                        b = BytesIO()
                        frame.save(b, format="gif")
                        frame = Image.open(b)
                        frames.append(frame)
                    frames[0].save(
                        f,
                        format="GIF",
                        save_all=True,
                        append_images=frames[1:],
                        loop=0,
                    )
                else:
                    image.save(f, ext)

                data = b64encode(f.getvalue())
                data = data.decode("ascii")
                url = "data:image/{};base64,".format(ext) + data
            img = ipyleaflet.ImageOverlay(url=url, bounds=bounds, name=name)
            self.add_layer(img)
        except Exception as e:
            raise Exception(e)

    def video_overlay(self, url, bounds, name):
        """Overlays a video from the Internet on the map.

        Args:
            url (str): http URL of the video, such as "https://www.mapbox.com/bites/00188/patricia_nasa.webm"
            bounds (tuple): bounding box of the video in the format of (lower_left(lat, lon), upper_right(lat, lon)), such as ((13, -130), (32, -100)).
            name (str): name of the layer to show on the layer control.
        """
        try:
            video = ipyleaflet.VideoOverlay(url=url, bounds=bounds, name=name)
            self.add_layer(video)
        except Exception as e:
            raise Exception(e)

    # def to_html(
    #     self,
    #     outfile,
    #     title="My Map",
    #     width="100%",
    #     height="880px",
    #     add_layer_control=True,
    # ):
    #     """Saves the map as a HTML file.

    #     Args:
    #         outfile (str): The output file path to the HTML file.
    #         title (str, optional): The title of the HTML file. Defaults to 'My Map'.
    #         width (str, optional): The width of the map in pixels or percentage. Defaults to '100%'.
    #         height (str, optional): The height of the map in pixels. Defaults to '880px'.
    #         add_layer_control (bool, optional): Whether to add the LayersControl. Defaults to True.

    #     """
    #     try:

    #         if not outfile.endswith(".html"):
    #             print("The output file must end with .html")
    #             return

    #         out_dir = os.path.dirname(outfile)
    #         if not os.path.exists(out_dir):
    #             os.makedirs(out_dir)

    #         if add_layer_control and self.layer_control is None:
    #             layer_control = ipyleaflet.LayersControl(position="topright")
    #             self.layer_control = layer_control
    #             self.add_control(layer_control)

    #         before_width = self.layout.width
    #         before_height = self.layout.height

    #         if not isinstance(width, str):
    #             print("width must be a string.")
    #             return
    #         elif width.endswith("px") or width.endswith("%"):
    #             pass
    #         else:
    #             print("width must end with px or %")
    #             return

    #         if not isinstance(height, str):
    #             print("height must be a string.")
    #             return
    #         elif not height.endswith("px"):
    #             print("height must end with px")
    #             return

    #         self.layout.width = width
    #         self.layout.height = height

    #         self.save(outfile, title=title)

    #         self.layout.width = before_width
    #         self.layout.height = before_height

    #     except Exception as e:
    #         raise Exception(e)

    # def to_image(self, outfile=None, monitor=1):
    #     """Saves the map as a PNG or JPG image.

    #     Args:
    #         outfile (str, optional): The output file path to the image. Defaults to None.
    #         monitor (int, optional): The monitor to take the screenshot. Defaults to 1.
    #     """
    #     if outfile is None:
    #         outfile = os.path.join(os.getcwd(), "my_map.png")

    #     if outfile.endswith(".png") or outfile.endswith(".jpg"):
    #         pass
    #     else:
    #         print("The output file must be a PNG or JPG image.")
    #         return

    #     work_dir = os.path.dirname(outfile)
    #     if not os.path.exists(work_dir):
    #         os.makedirs(work_dir)

    #     screenshot = screen_capture(outfile, monitor)
    #     self.screenshot = screenshot

    def toolbar_reset(self):
        """Reset the toolbar so that no tool is selected."""
        toolbar_grid = self.toolbar
        for tool in toolbar_grid.children:
            tool.value = False

    def add_raster(
        self,
        image,
        bands=None,
        layer_name=None,
        colormap=None,
        x_dim="x",
        y_dim="y",
    ):
        """Adds a local raster dataset to the map.

        Args:
            image (str): The image file path.
            bands (int or list, optional): The image bands to use. It can be either a nubmer (e.g., 1) or a list (e.g., [3, 2, 1]). Defaults to None.
            layer_name (str, optional): The layer name to use for the raster. Defaults to None.
            colormap (str, optional): The name of the colormap to use for the raster, such as 'gray' and 'terrain'. More can be found at https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html. Defaults to None.
            x_dim (str, optional): The x dimension. Defaults to 'x'.
            y_dim (str, optional): The y dimension. Defaults to 'y'.
        """
        try:
            import xarray_leaflet

        except Exception:
            # import platform
            # if platform.system() != "Windows":
            #     # install_from_github(
            #     #     url='https://github.com/davidbrochart/xarray_leaflet')
            #     check_install('xarray_leaflet')
            #     import xarray_leaflet
            # else:
            raise ImportError(
                "You need to install xarray_leaflet first. See https://github.com/davidbrochart/xarray_leaflet"
            )

        import warnings
        import numpy as np
        import rioxarray

        # import xarray as xr
        import matplotlib.pyplot as plt

        warnings.simplefilter("ignore")

        if not os.path.exists(image):
            print("The image file does not exist.")
            return

        if colormap is None:
            colormap = plt.cm.inferno

        if layer_name is None:
            layer_name = "Layer_" + random_string()

        if isinstance(colormap, str):
            colormap = plt.cm.get_cmap(name=colormap)

        da = rioxarray.open_rasterio(image, masked=True)

        # print(da.rio.nodata)

        multi_band = False
        if len(da.band) > 1:
            multi_band = True
            if bands is None:
                bands = [3, 2, 1]
        else:
            bands = 1

        if multi_band:
            da = da.rio.write_nodata(0)
        else:
            da = da.rio.write_nodata(np.nan)
        da = da.sel(band=bands)

        # crs = da.rio.crs
        # nan = da.attrs['nodatavals'][0]
        # da = da / da.max()
        # # if multi_band:
        # da = xr.where(da == nan, np.nan, da)
        # da = da.rio.write_nodata(0)
        # da = da.rio.write_crs(crs)

        if multi_band and type(bands) == list:
            layer = da.leaflet.plot(self, x_dim=x_dim, y_dim=y_dim, rgb_dim="band")
        else:
            layer = da.leaflet.plot(self, x_dim=x_dim, y_dim=y_dim, colormap=colormap)

        layer.name = layer_name

    def add_shapefile(
        self,
        in_shp,
        layer_name="Untitled",
        style={},
        hover_style={},
        style_callback=None,
        fill_colors=["black"],
        info_mode="on_hover",
    ):
        """Adds a shapefile to the map.

        Args:
            in_shp (str): The input file path to the shapefile.
            layer_name (str, optional): The layer name to be used.. Defaults to "Untitled".
            style (dict, optional): A dictionary specifying the style to be used. Defaults to {}.
            hover_style (dict, optional): Hover style dictionary. Defaults to {}.
            style_callback (function, optional): Styling function that is called for each feature, and should return the feature style. This styling function takes the feature as argument. Defaults to None.
            fill_colors (list, optional): The random colors to use for filling polygons. Defaults to ["black"].
            info_mode (str, optional): Displays the attributes by either on_hover or on_click. Any value other than "on_hover" or "on_click" will be treated as None. Defaults to "on_hover".

        Raises:
            FileNotFoundError: The provided shapefile could not be found.
        """
        in_shp = os.path.abspath(in_shp)
        if not os.path.exists(in_shp):
            raise FileNotFoundError("The provided shapefile could not be found.")

        geojson = shp_to_geojson(in_shp)
        self.add_geojson(
            geojson,
            layer_name,
            style,
            hover_style,
            style_callback,
            fill_colors,
            info_mode,
        )

    def add_geojson(
        self,
        in_geojson,
        layer_name="Untitled",
        style={},
        hover_style={},
        style_callback=None,
        fill_colors=["black"],
        info_mode="on_hover",
    ):
        """Adds a GeoJSON file to the map.

        Args:
            in_geojson (str | dict): The file path or http URL to the input GeoJSON or a dictionary containing the geojson.
            layer_name (str, optional): The layer name to be used.. Defaults to "Untitled".
            style (dict, optional): A dictionary specifying the style to be used. Defaults to {}.
            hover_style (dict, optional): Hover style dictionary. Defaults to {}.
            style_callback (function, optional): Styling function that is called for each feature, and should return the feature style. This styling function takes the feature as argument. Defaults to None.
            fill_colors (list, optional): The random colors to use for filling polygons. Defaults to ["black"].
            info_mode (str, optional): Displays the attributes by either on_hover or on_click. Any value other than "on_hover" or "on_click" will be treated as None. Defaults to "on_hover".
        Raises:
            FileNotFoundError: The provided GeoJSON file could not be found.
        """
        import json
        import random
        import requests

        try:

            if isinstance(in_geojson, str):

                if in_geojson.startswith("http"):
                    data = requests.get(in_geojson).json()
                else:
                    in_geojson = os.path.abspath(in_geojson)
                    if not os.path.exists(in_geojson):
                        raise FileNotFoundError(
                            "The provided GeoJSON file could not be found."
                        )

                    with open(in_geojson, encoding="utf-8") as f:
                        data = json.load(f)
            elif isinstance(in_geojson, dict):
                data = in_geojson
            else:
                raise TypeError("The input geojson must be a type of str or dict.")
        except Exception as e:
            raise Exception(e)

        if not style:
            style = {
                # "stroke": True,
                "color": "#000000",
                "weight": 1,
                "opacity": 1,
                # "fill": True,
                # "fillColor": "#ffffff",
                "fillOpacity": 0.1,
                # "dashArray": "9"
                # "clickable": True,
            }
        elif "weight" not in style:
            style["weight"] = 1

        if not hover_style:
            hover_style = {"weight": style["weight"] + 1, "fillOpacity": 0.5}

        def random_color(feature):
            return {
                "color": "black",
                "fillColor": random.choice(fill_colors),
            }

        toolbar_button = widgets.ToggleButton(
            value=True,
            tooltip="Toolbar",
            icon="info",
            layout=widgets.Layout(
                width="28px", height="28px", padding="0px 0px 0px 4px"
            ),
        )

        close_button = widgets.ToggleButton(
            value=False,
            tooltip="Close the tool",
            icon="times",
            # button_style="primary",
            layout=widgets.Layout(
                height="28px", width="28px", padding="0px 0px 0px 4px"
            ),
        )

        html = widgets.HTML()
        html.layout.margin = "0px 10px 0px 10px"
        html.layout.max_height = "250px"
        html.layout.max_width = "250px"

        output_widget = widgets.VBox(
            [widgets.HBox([toolbar_button, close_button]), html]
        )
        info_control = WidgetControl(widget=output_widget, position="bottomright")

        if info_mode in ["on_hover", "on_click"]:
            self.add_control(info_control)

        def toolbar_btn_click(change):
            if change["new"]:
                close_button.value = False
                output_widget.children = [
                    widgets.VBox([widgets.HBox([toolbar_button, close_button]), html])
                ]
            else:
                output_widget.children = [widgets.HBox([toolbar_button, close_button])]

        toolbar_button.observe(toolbar_btn_click, "value")

        def close_btn_click(change):
            if change["new"]:
                toolbar_button.value = False
                if info_control in self.controls:
                    self.remove_control(info_control)
                output_widget.close()

        close_button.observe(close_btn_click, "value")

        def update_html(feature, **kwargs):

            value = [
                "<h5><b>{}: </b>{}</h5>".format(prop, feature["properties"][prop])
                for prop in feature["properties"].keys()
            ][:-1]

            value = """{}""".format("".join(value))
            html.value = value

        if style_callback is None:
            style_callback = random_color

        geojson = ipyleaflet.GeoJSON(
            data=data,
            style=style,
            hover_style=hover_style,
            style_callback=style_callback,
            name=layer_name,
        )

        if info_mode == "on_hover":
            geojson.on_hover(update_html)
        elif info_mode == "on_click":
            geojson.on_click(update_html)

        self.add_layer(geojson)

    def add_kml(
        self,
        in_kml,
        layer_name="Untitled",
        style={},
        hover_style={},
        style_callback=None,
        fill_colors=["black"],
        info_mode="on_hover",
    ):
        """Adds a GeoJSON file to the map.

        Args:
            in_kml (str): The input file path to the KML.
            layer_name (str, optional): The layer name to be used.. Defaults to "Untitled".
            style (dict, optional): A dictionary specifying the style to be used. Defaults to {}.
            hover_style (dict, optional): Hover style dictionary. Defaults to {}.
            style_callback (function, optional): Styling function that is called for each feature, and should return the feature style. This styling function takes the feature as argument. Defaults to None.
            fill_colors (list, optional): The random colors to use for filling polygons. Defaults to ["black"].
            info_mode (str, optional): Displays the attributes by either on_hover or on_click. Any value other than "on_hover" or "on_click" will be treated as None. Defaults to "on_hover".

        Raises:
            FileNotFoundError: The provided KML file could not be found.
        """

        in_kml = os.path.abspath(in_kml)
        if not os.path.exists(in_kml):
            raise FileNotFoundError("The provided KML file could not be found.")
        self.add_vector(
            in_kml,
            layer_name,
            style=style,
            hover_style=hover_style,
            style_callback=style_callback,
            fill_colors=fill_colors,
            info_mode=info_mode,
        )

    def add_vector(
        self,
        filename,
        layer_name="Untitled",
        bbox=None,
        mask=None,
        rows=None,
        style={},
        hover_style={},
        style_callback=None,
        fill_colors=["black"],
        info_mode="on_hover",
        **kwargs,
    ):
        """Adds any geopandas-supported vector dataset to the map.

        Args:
            filename (str): Either the absolute or relative path to the file or URL to be opened, or any object with a read() method (such as an open file or StringIO).
            layer_name (str, optional): The layer name to use. Defaults to "Untitled".
            bbox (tuple | GeoDataFrame or GeoSeries | shapely Geometry, optional): Filter features by given bounding box, GeoSeries, GeoDataFrame or a shapely geometry. CRS mis-matches are resolved if given a GeoSeries or GeoDataFrame. Cannot be used with mask. Defaults to None.
            mask (dict | GeoDataFrame or GeoSeries | shapely Geometry, optional): Filter for features that intersect with the given dict-like geojson geometry, GeoSeries, GeoDataFrame or shapely geometry. CRS mis-matches are resolved if given a GeoSeries or GeoDataFrame. Cannot be used with bbox. Defaults to None.
            rows (int or slice, optional): Load in specific rows by passing an integer (first n rows) or a slice() object.. Defaults to None.
            style (dict, optional): A dictionary specifying the style to be used. Defaults to {}.
            hover_style (dict, optional): Hover style dictionary. Defaults to {}.
            style_callback (function, optional): Styling function that is called for each feature, and should return the feature style. This styling function takes the feature as argument. Defaults to None.
            fill_colors (list, optional): The random colors to use for filling polygons. Defaults to ["black"].
            info_mode (str, optional): Displays the attributes by either on_hover or on_click. Any value other than "on_hover" or "on_click" will be treated as None. Defaults to "on_hover".

        """
        if not filename.startswith("http"):
            filename = os.path.abspath(filename)

        ext = os.path.splitext(filename)[1].lower()
        if ext == ".shp":
            self.add_shapefile(
                filename,
                layer_name,
                style,
                hover_style,
                style_callback,
                fill_colors,
                info_mode,
            )
        elif ext in [".json", ".geojson"]:
            self.add_geojson(
                filename,
                layer_name,
                style,
                hover_style,
                style_callback,
                fill_colors,
                info_mode,
            )
        else:
            geojson = vector_to_geojson(
                filename,
                bbox=bbox,
                mask=mask,
                rows=rows,
                epsg="4326",
                **kwargs,
            )

            self.add_geojson(
                geojson,
                layer_name,
                style,
                hover_style,
                style_callback,
                fill_colors,
                info_mode,
            )

    def add_xy_data(
        self,
        in_csv,
        x="longitude",
        y="latitude",
        label=None,
        layer_name="Marker cluster",
    ):
        """Adds points from a CSV file containing lat/lon information and display data on the map.

        Args:
            in_csv (str): The file path to the input CSV file.
            x (str, optional): The name of the column containing longitude coordinates. Defaults to "longitude".
            y (str, optional): The name of the column containing latitude coordinates. Defaults to "latitude".
            label (str, optional): The name of the column containing label information to used for marker popup. Defaults to None.
            layer_name (str, optional): The layer name to use. Defaults to "Marker cluster".

        Raises:
            FileNotFoundError: The specified input csv does not exist.
            ValueError: The specified x column does not exist.
            ValueError: The specified y column does not exist.
            ValueError: The specified label column does not exist.
        """
        import pandas as pd

        if not in_csv.startswith("http") and (not os.path.exists(in_csv)):
            raise FileNotFoundError("The specified input csv does not exist.")

        df = pd.read_csv(in_csv)
        col_names = df.columns.values.tolist()

        if x not in col_names:
            raise ValueError(f"x must be one of the following: {', '.join(col_names)}")

        if y not in col_names:
            raise ValueError(f"y must be one of the following: {', '.join(col_names)}")

        if label is not None and (label not in col_names):
            raise ValueError(
                f"label must be one of the following: {', '.join(col_names)}"
            )

        self.default_style = {"cursor": "wait"}

        points = list(zip(df[y], df[x]))

        if label is not None:
            labels = df[label]
            markers = [
                Marker(
                    location=point,
                    draggable=False,
                    popup=widgets.HTML(str(labels[index])),
                )
                for index, point in enumerate(points)
            ]
        else:
            markers = [Marker(location=point, draggable=False) for point in points]

        marker_cluster = MarkerCluster(markers=markers, name=layer_name)
        self.add_layer(marker_cluster)

        self.default_style = {"cursor": "default"}
