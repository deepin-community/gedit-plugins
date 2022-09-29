/*
 * gedit-drawspaces-view-activatable.h
 * This file is part of gedit
 *
 * Copyright (C) 2008-2014 Ignacio Casal Quinteiro <icq@gnome.org>
 *
 * gedit is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * gedit is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with gedit. If not, see <http://www.gnu.org/licenses/>.
 */

#include "gedit-drawspaces-app-activatable.h"
#include "gedit-drawspaces-view-activatable.h"

#include <gedit/gedit-view.h>
#include <gedit/gedit-view-activatable.h>
#include <libpeas/peas-object-module.h>

typedef struct _GeditDrawspacesViewActivatablePrivate
{
	GeditView *view;
	GSettings *settings;
	guint flags;

	guint enable : 1;
} GeditDrawspacesViewActivatablePrivate;

enum
{
	PROP_0,
	PROP_VIEW
};

static void gedit_view_activatable_iface_init (GeditViewActivatableInterface *iface);

G_DEFINE_DYNAMIC_TYPE_EXTENDED (GeditDrawspacesViewActivatable,
				gedit_drawspaces_view_activatable,
				G_TYPE_OBJECT,
				0,
				G_ADD_PRIVATE_DYNAMIC (GeditDrawspacesViewActivatable)
				G_IMPLEMENT_INTERFACE_DYNAMIC (GEDIT_TYPE_VIEW_ACTIVATABLE,
							       gedit_view_activatable_iface_init))

static void
gedit_drawspaces_view_activatable_dispose (GObject *object)
{
	GeditDrawspacesViewActivatable *activatable = GEDIT_DRAWSPACES_VIEW_ACTIVATABLE (object);
	GeditDrawspacesViewActivatablePrivate *priv = gedit_drawspaces_view_activatable_get_instance_private (activatable);

	g_clear_object (&priv->view);

	G_OBJECT_CLASS (gedit_drawspaces_view_activatable_parent_class)->dispose (object);
}

static void
gedit_drawspaces_view_activatable_set_property (GObject      *object,
                                                guint         prop_id,
                                                const GValue *value,
                                                GParamSpec   *pspec)
{
	GeditDrawspacesViewActivatable *activatable = GEDIT_DRAWSPACES_VIEW_ACTIVATABLE (object);
	GeditDrawspacesViewActivatablePrivate *priv = gedit_drawspaces_view_activatable_get_instance_private (activatable);

	switch (prop_id)
	{
		case PROP_VIEW:
			priv->view = GEDIT_VIEW (g_value_dup_object (value));
			break;

		default:
			G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
			break;
	}
}

static void
gedit_drawspaces_view_activatable_get_property (GObject    *object,
                                                guint       prop_id,
                                                GValue     *value,
                                                GParamSpec *pspec)
{
	GeditDrawspacesViewActivatable *activatable = GEDIT_DRAWSPACES_VIEW_ACTIVATABLE (object);
	GeditDrawspacesViewActivatablePrivate *priv = gedit_drawspaces_view_activatable_get_instance_private (activatable);

	switch (prop_id)
	{
		case PROP_VIEW:
			g_value_set_object (value, priv->view);
			break;

		default:
			G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
			break;
	}
}

static void
gedit_drawspaces_view_activatable_class_init (GeditDrawspacesViewActivatableClass *klass)
{
	GObjectClass *object_class = G_OBJECT_CLASS (klass);

	object_class->dispose = gedit_drawspaces_view_activatable_dispose;
	object_class->set_property = gedit_drawspaces_view_activatable_set_property;
	object_class->get_property = gedit_drawspaces_view_activatable_get_property;

	g_object_class_override_property (object_class, PROP_VIEW, "view");
}

static void
gedit_drawspaces_view_activatable_class_finalize (GeditDrawspacesViewActivatableClass *klass)
{
}

static void
gedit_drawspaces_view_activatable_init (GeditDrawspacesViewActivatable *self)
{
}

static void
get_config_options (GeditDrawspacesViewActivatable *activatable)
{
	GeditDrawspacesViewActivatablePrivate *priv = gedit_drawspaces_view_activatable_get_instance_private (activatable);

	priv->enable = g_settings_get_boolean (priv->settings,
	                                       SETTINGS_KEY_SHOW_WHITE_SPACE);

	priv->flags = g_settings_get_flags (priv->settings,
	                                    SETTINGS_KEY_DRAW_SPACES);
}

static inline void
parse_flags (guint                        flags,
             GtkSourceSpaceTypeFlags     *type,
             GtkSourceSpaceLocationFlags *location)
{
	*type = GTK_SOURCE_SPACE_TYPE_NONE;
	*location = GTK_SOURCE_SPACE_LOCATION_NONE;

	if (flags & GEDIT_DRAW_SPACES_SPACE)
		*type |= GTK_SOURCE_SPACE_TYPE_SPACE;
	if (flags & GEDIT_DRAW_SPACES_TAB)
		*type |= GTK_SOURCE_SPACE_TYPE_TAB;
	if (flags & GEDIT_DRAW_SPACES_NEWLINE)
		*type |= GTK_SOURCE_SPACE_TYPE_NEWLINE;
	if (flags & GEDIT_DRAW_SPACES_NBSP)
		*type |= GTK_SOURCE_SPACE_TYPE_NBSP;

	if (flags & GEDIT_DRAW_SPACES_LEADING)
		*location |= GTK_SOURCE_SPACE_LOCATION_LEADING;
	if (flags & GEDIT_DRAW_SPACES_TEXT)
		*location |= GTK_SOURCE_SPACE_LOCATION_INSIDE_TEXT;
	if (flags & GEDIT_DRAW_SPACES_TRAILING)
		*location |= GTK_SOURCE_SPACE_LOCATION_TRAILING;
}

static void
draw_spaces (GeditDrawspacesViewActivatable *activatable)
{
	GeditDrawspacesViewActivatablePrivate *priv = gedit_drawspaces_view_activatable_get_instance_private (activatable);
	GtkSourceSpaceDrawer *drawer;
	GtkSourceSpaceTypeFlags type;
	GtkSourceSpaceLocationFlags location;

	parse_flags (priv->flags, &type, &location);

	drawer = gtk_source_view_get_space_drawer (GTK_SOURCE_VIEW (priv->view));

	/* Clear all existing spaces in the matrix before setting */
	gtk_source_space_drawer_set_types_for_locations (drawer, GTK_SOURCE_SPACE_LOCATION_ALL, 0);
	gtk_source_space_drawer_set_types_for_locations (drawer, location, type);
	gtk_source_space_drawer_set_enable_matrix (drawer, priv->enable);
}

static void
on_draw_spaces_changed (GSettings                      *settings,
                        const gchar                    *key,
                        GeditDrawspacesViewActivatable *activatable)
{
	GeditDrawspacesViewActivatablePrivate *priv = gedit_drawspaces_view_activatable_get_instance_private (activatable);

	priv->flags = g_settings_get_flags (priv->settings,
	                                    SETTINGS_KEY_DRAW_SPACES);

	draw_spaces (activatable);
}

static void
on_show_white_space_changed (GSettings                      *settings,
                             const gchar                    *key,
                             GeditDrawspacesViewActivatable *activatable)
{
	GeditDrawspacesViewActivatablePrivate *priv = gedit_drawspaces_view_activatable_get_instance_private (activatable);

	priv->enable = g_settings_get_boolean (settings, key);

	draw_spaces (activatable);
}

static void
gedit_drawspaces_view_activatable_window_activate (GeditViewActivatable *activatable)
{
	GeditDrawspacesViewActivatablePrivate *priv;

	priv = gedit_drawspaces_view_activatable_get_instance_private (GEDIT_DRAWSPACES_VIEW_ACTIVATABLE (activatable));
	priv->settings = g_settings_new (DRAWSPACES_SETTINGS_BASE);

	get_config_options (GEDIT_DRAWSPACES_VIEW_ACTIVATABLE (activatable));

	if (priv->enable)
	{
		draw_spaces (GEDIT_DRAWSPACES_VIEW_ACTIVATABLE (activatable));
	}

	g_signal_connect (priv->settings,
	                  "changed::show-white-space",
	                  G_CALLBACK (on_show_white_space_changed),
	                  activatable);
	g_signal_connect (priv->settings,
	                  "changed::draw-spaces",
	                  G_CALLBACK (on_draw_spaces_changed),
	                  activatable);
}

static void
gedit_drawspaces_view_activatable_window_deactivate (GeditViewActivatable *activatable)
{
	GeditDrawspacesViewActivatablePrivate *priv;

	priv = gedit_drawspaces_view_activatable_get_instance_private (GEDIT_DRAWSPACES_VIEW_ACTIVATABLE (activatable));

	priv->enable = FALSE;
	draw_spaces (GEDIT_DRAWSPACES_VIEW_ACTIVATABLE (activatable));

	g_clear_object (&priv->settings);
}

static void
gedit_view_activatable_iface_init (GeditViewActivatableInterface *iface)
{
	iface->activate = gedit_drawspaces_view_activatable_window_activate;
	iface->deactivate = gedit_drawspaces_view_activatable_window_deactivate;
}

void
gedit_drawspaces_view_activatable_register (GTypeModule *module)
{
	gedit_drawspaces_view_activatable_register_type (module);

	peas_object_module_register_extension_type (PEAS_OBJECT_MODULE (module),
						    GEDIT_TYPE_VIEW_ACTIVATABLE,
						    GEDIT_TYPE_DRAWSPACES_VIEW_ACTIVATABLE);
}

/* ex:set ts=8 noet: */
