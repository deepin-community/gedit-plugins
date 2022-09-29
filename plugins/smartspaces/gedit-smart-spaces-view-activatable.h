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

#ifndef GEDIT_SMART_SPACES_VIEW_ACTIVATABLE_H
#define GEDIT_SMART_SPACES_VIEW_ACTIVATABLE_H

#include <libpeas/peas.h>

G_BEGIN_DECLS

#define GEDIT_TYPE_SMART_SPACES_VIEW_ACTIVATABLE             (gedit_smart_spaces_view_activatable_get_type ())
#define GEDIT_SMART_SPACES_VIEW_ACTIVATABLE(obj)             (G_TYPE_CHECK_INSTANCE_CAST ((obj), GEDIT_TYPE_SMART_SPACES_VIEW_ACTIVATABLE, GeditSmartSpacesViewActivatable))
#define GEDIT_SMART_SPACES_VIEW_ACTIVATABLE_CLASS(klass)     (G_TYPE_CHECK_CLASS_CAST ((klass), GEDIT_TYPE_SMART_SPACES_VIEW_ACTIVATABLE, GeditSmartSpacesViewActivatableClass))
#define GEDIT_IS_SMART_SPACES_VIEW_ACTIVATABLE(obj)          (G_TYPE_CHECK_INSTANCE_TYPE ((obj), GEDIT_TYPE_SMART_SPACES_VIEW_ACTIVATABLE))
#define GEDIT_IS_SMART_SPACES_VIEW_ACTIVATABLE_CLASS(klass)  (G_TYPE_CHECK_CLASS_TYPE ((klass), GEDIT_TYPE_SMART_SPACES_VIEW_ACTIVATABLE))
#define GEDIT_SMART_SPACES_VIEW_ACTIVATABLE_GET_CLASS(obj)   (G_TYPE_INSTANCE_GET_CLASS ((obj), GEDIT_TYPE_SMART_SPACES_VIEW_ACTIVATABLE, GeditSmartSpacesViewActivatableClass))

typedef struct _GeditSmartSpacesViewActivatable         GeditSmartSpacesViewActivatable;
typedef struct _GeditSmartSpacesViewActivatableClass    GeditSmartSpacesViewActivatableClass;
typedef struct _GeditSmartSpacesViewActivatablePrivate  GeditSmartSpacesViewActivatablePrivate;

struct _GeditSmartSpacesViewActivatable
{
	GObject parent;

	GeditSmartSpacesViewActivatablePrivate *priv;
};

struct _GeditSmartSpacesViewActivatableClass
{
	GObjectClass parent_class;
};

GType	gedit_smart_spaces_view_activatable_get_type	(void);

G_MODULE_EXPORT
void	peas_register_types				(PeasObjectModule *module);

G_END_DECLS

#endif /* GEDIT_SMART_SPACES_VIEW_ACTIVATABLE_H */
