/*
 * Copyright (C) 2020 Sébastien Wilmet <swilmet@gnome.org>
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

#include "gedit-smart-spaces-view-activatable.h"
#include <gedit/gedit-view.h>
#include <gedit/gedit-view-activatable.h>

struct _GeditSmartSpacesViewActivatablePrivate
{
	GeditView *view;
};

enum
{
	PROP_0,
	PROP_VIEW
};

static void gedit_view_activatable_iface_init (GeditViewActivatableInterface *iface);

G_DEFINE_DYNAMIC_TYPE_EXTENDED (GeditSmartSpacesViewActivatable,
				gedit_smart_spaces_view_activatable,
				G_TYPE_OBJECT,
				0,
				G_ADD_PRIVATE_DYNAMIC (GeditSmartSpacesViewActivatable)
				G_IMPLEMENT_INTERFACE_DYNAMIC (GEDIT_TYPE_VIEW_ACTIVATABLE,
							       gedit_view_activatable_iface_init))

static void
gedit_smart_spaces_view_activatable_get_property (GObject    *object,
                                                  guint       prop_id,
                                                  GValue     *value,
                                                  GParamSpec *pspec)
{
	GeditSmartSpacesViewActivatable *activatable = GEDIT_SMART_SPACES_VIEW_ACTIVATABLE (object);

	switch (prop_id)
	{
		case PROP_VIEW:
			g_value_set_object (value, activatable->priv->view);
			break;

		default:
			G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
			break;
	}
}

static void
gedit_smart_spaces_view_activatable_set_property (GObject      *object,
                                                  guint         prop_id,
                                                  const GValue *value,
                                                  GParamSpec   *pspec)
{
	GeditSmartSpacesViewActivatable *activatable = GEDIT_SMART_SPACES_VIEW_ACTIVATABLE (object);

	switch (prop_id)
	{
		case PROP_VIEW:
			g_assert (activatable->priv->view == NULL);
			activatable->priv->view = GEDIT_VIEW (g_value_dup_object (value));
			break;

		default:
			G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
			break;
	}
}

static void
gedit_smart_spaces_view_activatable_dispose (GObject *object)
{
	GeditSmartSpacesViewActivatable *activatable = GEDIT_SMART_SPACES_VIEW_ACTIVATABLE (object);

	g_clear_object (&activatable->priv->view);

	G_OBJECT_CLASS (gedit_smart_spaces_view_activatable_parent_class)->dispose (object);
}

static void
gedit_smart_spaces_view_activatable_class_init (GeditSmartSpacesViewActivatableClass *klass)
{
	GObjectClass *object_class = G_OBJECT_CLASS (klass);

	object_class->get_property = gedit_smart_spaces_view_activatable_get_property;
	object_class->set_property = gedit_smart_spaces_view_activatable_set_property;
	object_class->dispose = gedit_smart_spaces_view_activatable_dispose;

	g_object_class_override_property (object_class, PROP_VIEW, "view");
}

static void
gedit_smart_spaces_view_activatable_class_finalize (GeditSmartSpacesViewActivatableClass *klass)
{
}

static void
gedit_smart_spaces_view_activatable_init (GeditSmartSpacesViewActivatable *activatable)
{
	activatable->priv = gedit_smart_spaces_view_activatable_get_instance_private (activatable);
}

static void
gedit_smart_spaces_view_activatable_activate (GeditViewActivatable *activatable)
{
	GeditSmartSpacesViewActivatable *self = GEDIT_SMART_SPACES_VIEW_ACTIVATABLE (activatable);

	gtk_source_view_set_smart_backspace (GTK_SOURCE_VIEW (self->priv->view), TRUE);
}

static void
gedit_smart_spaces_view_activatable_deactivate (GeditViewActivatable *activatable)
{
	GeditSmartSpacesViewActivatable *self = GEDIT_SMART_SPACES_VIEW_ACTIVATABLE (activatable);

	gtk_source_view_set_smart_backspace (GTK_SOURCE_VIEW (self->priv->view), FALSE);
}

static void
gedit_view_activatable_iface_init (GeditViewActivatableInterface *iface)
{
	iface->activate = gedit_smart_spaces_view_activatable_activate;
	iface->deactivate = gedit_smart_spaces_view_activatable_deactivate;
}

G_MODULE_EXPORT void
peas_register_types (PeasObjectModule *module)
{
	gedit_smart_spaces_view_activatable_register_type (G_TYPE_MODULE (module));

	peas_object_module_register_extension_type (module,
						    GEDIT_TYPE_VIEW_ACTIVATABLE,
						    GEDIT_TYPE_SMART_SPACES_VIEW_ACTIVATABLE);
}
