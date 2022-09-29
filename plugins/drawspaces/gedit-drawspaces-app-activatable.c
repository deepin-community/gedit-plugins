/*
 * Copyright (C) 2008-2014 Ignacio Casal Quinteiro <icq@gnome.org>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 */

#include "config.h"
#include "gedit-drawspaces-app-activatable.h"
#include "gedit-drawspaces-view-activatable.h"

#include <gedit/gedit-app.h>
#include <gedit/gedit-app-activatable.h>
#include <gedit/gedit-debug.h>
#include <gio/gio.h>
#include <glib/gi18n-lib.h>
#include <libpeas-gtk/peas-gtk-configurable.h>

typedef struct _GeditDrawspacesAppActivatablePrivate
{
	GeditApp *app;
} GeditDrawspacesAppActivatablePrivate;

typedef struct _DrawspacesConfigureWidget DrawspacesConfigureWidget;

struct _DrawspacesConfigureWidget
{
	GSettings *settings;
	guint flags;

	GtkWidget *content;

	GtkWidget *draw_tabs;
	GtkWidget *draw_spaces;
	GtkWidget *draw_newline;
	GtkWidget *draw_nbsp;
	GtkWidget *draw_leading;
	GtkWidget *draw_text;
	GtkWidget *draw_trailing;
};

enum
{
	PROP_0,
	PROP_APP
};

static void gedit_app_activatable_iface_init (GeditAppActivatableInterface *iface);
static void peas_gtk_configurable_iface_init (PeasGtkConfigurableInterface *iface);

G_DEFINE_DYNAMIC_TYPE_EXTENDED (GeditDrawspacesAppActivatable,
				gedit_drawspaces_app_activatable,
				G_TYPE_OBJECT,
				0,
				G_ADD_PRIVATE_DYNAMIC (GeditDrawspacesAppActivatable)
				G_IMPLEMENT_INTERFACE_DYNAMIC (GEDIT_TYPE_APP_ACTIVATABLE,
							       gedit_app_activatable_iface_init)
				G_IMPLEMENT_INTERFACE_DYNAMIC (PEAS_GTK_TYPE_CONFIGURABLE,
							       peas_gtk_configurable_iface_init))

static void
gedit_drawspaces_app_activatable_dispose (GObject *object)
{
	GeditDrawspacesAppActivatable *activatable = GEDIT_DRAWSPACES_APP_ACTIVATABLE (object);
	GeditDrawspacesAppActivatablePrivate *priv = gedit_drawspaces_app_activatable_get_instance_private (activatable);

	g_clear_object (&priv->app);

	G_OBJECT_CLASS (gedit_drawspaces_app_activatable_parent_class)->dispose (object);
}

static void
gedit_drawspaces_app_activatable_set_property (GObject      *object,
                                               guint         prop_id,
                                               const GValue *value,
                                               GParamSpec   *pspec)
{
	GeditDrawspacesAppActivatable *activatable = GEDIT_DRAWSPACES_APP_ACTIVATABLE (object);
	GeditDrawspacesAppActivatablePrivate *priv = gedit_drawspaces_app_activatable_get_instance_private (activatable);

	switch (prop_id)
	{
		case PROP_APP:
			priv->app = GEDIT_APP (g_value_dup_object (value));
			break;

		default:
			G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
			break;
	}
}

static void
gedit_drawspaces_app_activatable_get_property (GObject    *object,
                                               guint       prop_id,
                                               GValue     *value,
                                               GParamSpec *pspec)
{
	GeditDrawspacesAppActivatable *activatable = GEDIT_DRAWSPACES_APP_ACTIVATABLE (object);
	GeditDrawspacesAppActivatablePrivate *priv = gedit_drawspaces_app_activatable_get_instance_private (activatable);

	switch (prop_id)
	{
		case PROP_APP:
			g_value_set_object (value, priv->app);
			break;

		default:
			G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
			break;
	}
}

static void
gedit_drawspaces_app_activatable_class_init (GeditDrawspacesAppActivatableClass *klass)
{
	GObjectClass *object_class = G_OBJECT_CLASS (klass);

	object_class->dispose = gedit_drawspaces_app_activatable_dispose;
	object_class->set_property = gedit_drawspaces_app_activatable_set_property;
	object_class->get_property = gedit_drawspaces_app_activatable_get_property;

	g_object_class_override_property (object_class, PROP_APP, "app");
}

static void
gedit_drawspaces_app_activatable_class_finalize (GeditDrawspacesAppActivatableClass *klass)
{
}

static void
gedit_drawspaces_app_activatable_init (GeditDrawspacesAppActivatable *self)
{
}

static void
gedit_drawspaces_app_activatable_activate (GeditAppActivatable *activatable)
{
}

static void
gedit_drawspaces_app_activatable_deactivate (GeditAppActivatable *activatable)
{
}

static void
gedit_app_activatable_iface_init (GeditAppActivatableInterface *iface)
{
	iface->activate = gedit_drawspaces_app_activatable_activate;
	iface->deactivate = gedit_drawspaces_app_activatable_deactivate;
}

static void
widget_destroyed (GtkWidget *obj, gpointer widget_pointer)
{
	DrawspacesConfigureWidget *widget = (DrawspacesConfigureWidget *)widget_pointer;

	gedit_debug (DEBUG_PLUGINS);

	g_object_unref (widget->settings);
	g_slice_free (DrawspacesConfigureWidget, widget_pointer);

	gedit_debug_message (DEBUG_PLUGINS, "END");
}

static void
set_flag (DrawspacesConfigureWidget *widget, guint flag, gboolean active)
{
	widget->flags = active ? widget->flags | flag : widget->flags & ~flag;
	g_settings_set_flags (widget->settings,
			      SETTINGS_KEY_DRAW_SPACES,
			      widget->flags);
}

static void
on_draw_tabs_toggled (GtkToggleButton           *button,
		      DrawspacesConfigureWidget *widget)
{
	set_flag (widget, GEDIT_DRAW_SPACES_TAB, gtk_toggle_button_get_active (button));
}

static void
on_draw_spaces_toggled (GtkToggleButton           *button,
			DrawspacesConfigureWidget *widget)
{
	set_flag (widget, GEDIT_DRAW_SPACES_SPACE, gtk_toggle_button_get_active (button));
}

static void
on_draw_newline_toggled (GtkToggleButton           *button,
			 DrawspacesConfigureWidget *widget)
{
	set_flag (widget, GEDIT_DRAW_SPACES_NEWLINE, gtk_toggle_button_get_active (button));
}

static void
on_draw_nbsp_toggled (GtkToggleButton           *button,
		      DrawspacesConfigureWidget *widget)
{
	set_flag (widget, GEDIT_DRAW_SPACES_NBSP, gtk_toggle_button_get_active (button));
}

static void
on_draw_leading_toggled (GtkToggleButton           *button,
			 DrawspacesConfigureWidget *widget)
{
	set_flag (widget, GEDIT_DRAW_SPACES_LEADING, gtk_toggle_button_get_active (button));
}

static void
on_draw_text_toggled (GtkToggleButton           *button,
		      DrawspacesConfigureWidget *widget)
{
	set_flag (widget, GEDIT_DRAW_SPACES_TEXT, gtk_toggle_button_get_active (button));
}

static void
on_draw_trailing_toggled (GtkToggleButton           *button,
			  DrawspacesConfigureWidget *widget)
{
	set_flag (widget, GEDIT_DRAW_SPACES_TRAILING, gtk_toggle_button_get_active (button));
}

static DrawspacesConfigureWidget *
get_configuration_widget (GeditDrawspacesAppActivatable *activatable)
{
	DrawspacesConfigureWidget *widget = NULL;
	GtkBuilder *builder;

	gchar *root_objects[] = {
		"content",
		NULL
	};

	widget = g_slice_new (DrawspacesConfigureWidget);
	widget->settings = g_settings_new (DRAWSPACES_SETTINGS_BASE);
	widget->flags = g_settings_get_flags (widget->settings,
					      SETTINGS_KEY_DRAW_SPACES);

	builder = gtk_builder_new ();
	gtk_builder_set_translation_domain (builder, GETTEXT_PACKAGE);
	gtk_builder_add_objects_from_resource (builder, "/org/gnome/gedit/plugins/drawspaces/ui/gedit-drawspaces-configurable.ui",
	                                       root_objects, NULL);
	widget->content = GTK_WIDGET (gtk_builder_get_object (builder, "content"));
	g_object_ref (widget->content);
	widget->draw_tabs = GTK_WIDGET (gtk_builder_get_object (builder, "check_button_draw_tabs"));
	widget->draw_spaces = GTK_WIDGET (gtk_builder_get_object (builder, "check_button_draw_spaces"));
	widget->draw_newline = GTK_WIDGET (gtk_builder_get_object (builder, "check_button_draw_new_lines"));
	widget->draw_nbsp = GTK_WIDGET (gtk_builder_get_object (builder, "check_button_draw_nbsp"));
	widget->draw_leading = GTK_WIDGET (gtk_builder_get_object (builder, "check_button_draw_leading"));
	widget->draw_text = GTK_WIDGET (gtk_builder_get_object (builder, "check_button_draw_text"));
	widget->draw_trailing = GTK_WIDGET (gtk_builder_get_object (builder, "check_button_draw_trailing"));
	g_object_unref (builder);

	gtk_toggle_button_set_active (GTK_TOGGLE_BUTTON (widget->draw_tabs),
				      widget->flags & GEDIT_DRAW_SPACES_TAB);
	gtk_toggle_button_set_active (GTK_TOGGLE_BUTTON (widget->draw_spaces),
				      widget->flags & GEDIT_DRAW_SPACES_SPACE);
	gtk_toggle_button_set_active (GTK_TOGGLE_BUTTON (widget->draw_newline),
				      widget->flags & GEDIT_DRAW_SPACES_NEWLINE);
	gtk_toggle_button_set_active (GTK_TOGGLE_BUTTON (widget->draw_nbsp),
				      widget->flags & GEDIT_DRAW_SPACES_NBSP);

	gtk_toggle_button_set_active (GTK_TOGGLE_BUTTON (widget->draw_leading),
				      widget->flags & GEDIT_DRAW_SPACES_LEADING);
	gtk_toggle_button_set_active (GTK_TOGGLE_BUTTON (widget->draw_text),
				      widget->flags & GEDIT_DRAW_SPACES_TEXT);
	gtk_toggle_button_set_active (GTK_TOGGLE_BUTTON (widget->draw_trailing),
				      widget->flags & GEDIT_DRAW_SPACES_TRAILING);

	g_signal_connect (widget->draw_tabs,
			  "toggled",
			  G_CALLBACK (on_draw_tabs_toggled),
			  widget);
	g_signal_connect (widget->draw_spaces,
			  "toggled",
			  G_CALLBACK (on_draw_spaces_toggled),
			  widget);
	g_signal_connect (widget->draw_newline,
			  "toggled",
			  G_CALLBACK (on_draw_newline_toggled),
			  widget);
	g_signal_connect (widget->draw_nbsp,
			  "toggled",
			  G_CALLBACK (on_draw_nbsp_toggled),
			  widget);
	g_signal_connect (widget->draw_leading,
			  "toggled",
			  G_CALLBACK (on_draw_leading_toggled),
			  widget);
	g_signal_connect (widget->draw_text,
			  "toggled",
			  G_CALLBACK (on_draw_text_toggled),
			  widget);
	g_signal_connect (widget->draw_trailing,
			  "toggled",
			  G_CALLBACK (on_draw_trailing_toggled),
			  widget);

	g_signal_connect (widget->content,
			  "destroy",
			  G_CALLBACK (widget_destroyed),
			  widget);

	return widget;
}

static GtkWidget *
gedit_drawspaces_app_activatable_create_configure_widget (PeasGtkConfigurable *configurable)
{
	DrawspacesConfigureWidget *widget;

	widget = get_configuration_widget (GEDIT_DRAWSPACES_APP_ACTIVATABLE (configurable));

	return widget->content;
}

static void
peas_gtk_configurable_iface_init (PeasGtkConfigurableInterface *iface)
{
	iface->create_configure_widget = gedit_drawspaces_app_activatable_create_configure_widget;
}

G_MODULE_EXPORT void
peas_register_types (PeasObjectModule *module)
{
	gedit_drawspaces_app_activatable_register_type (G_TYPE_MODULE (module));
	gedit_drawspaces_view_activatable_register (G_TYPE_MODULE (module));

	peas_object_module_register_extension_type (module,
	                                            GEDIT_TYPE_APP_ACTIVATABLE,
	                                            GEDIT_TYPE_DRAWSPACES_APP_ACTIVATABLE);
	peas_object_module_register_extension_type (module,
	                                            PEAS_GTK_TYPE_CONFIGURABLE,
	                                            GEDIT_TYPE_DRAWSPACES_APP_ACTIVATABLE);
}

/* ex:set ts=8 noet: */
