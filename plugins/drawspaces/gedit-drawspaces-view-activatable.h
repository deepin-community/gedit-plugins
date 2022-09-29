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

#ifndef __GEDIT_DRAWSPACES_VIEW_ACTIVATABLE_H__
#define __GEDIT_DRAWSPACES_VIEW_ACTIVATABLE_H__

#include <glib-object.h>

G_BEGIN_DECLS

#define GEDIT_TYPE_DRAWSPACES_VIEW_ACTIVATABLE			(gedit_drawspaces_view_activatable_get_type ())
#define GEDIT_DRAWSPACES_VIEW_ACTIVATABLE(obj)			(G_TYPE_CHECK_INSTANCE_CAST ((obj), GEDIT_TYPE_DRAWSPACES_VIEW_ACTIVATABLE, GeditDrawspacesViewActivatable))
#define GEDIT_DRAWSPACES_VIEW_ACTIVATABLE_CONST(obj)		(G_TYPE_CHECK_INSTANCE_CAST ((obj), GEDIT_TYPE_DRAWSPACES_VIEW_ACTIVATABLE, GeditDrawspacesViewActivatable const))
#define GEDIT_DRAWSPACES_VIEW_ACTIVATABLE_CLASS(klass)		(G_TYPE_CHECK_CLASS_CAST ((klass), GEDIT_TYPE_DRAWSPACES_VIEW_ACTIVATABLE, GeditDrawspacesViewActivatableClass))
#define GEDIT_IS_DRAWSPACES_VIEW_ACTIVATABLE(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), GEDIT_TYPE_DRAWSPACES_VIEW_ACTIVATABLE))
#define GEDIT_IS_DRAWSPACES_VIEW_ACTIVATABLE_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), GEDIT_TYPE_DRAWSPACES_VIEW_ACTIVATABLE))
#define GEDIT_DRAWSPACES_VIEW_ACTIVATABLE_GET_CLASS(obj)	(G_TYPE_INSTANCE_GET_CLASS ((obj), GEDIT_TYPE_DRAWSPACES_VIEW_ACTIVATABLE, GeditDrawspacesViewActivatableClass))

#define DRAWSPACES_SETTINGS_BASE   "org.gnome.gedit.plugins.drawspaces"
#define SETTINGS_KEY_SHOW_WHITE_SPACE "show-white-space"
#define SETTINGS_KEY_DRAW_SPACES   "draw-spaces"

typedef struct _GeditDrawspacesViewActivatable		GeditDrawspacesViewActivatable;
typedef struct _GeditDrawspacesViewActivatableClass	GeditDrawspacesViewActivatableClass;

struct _GeditDrawspacesViewActivatable
{
	GObject parent;
};

struct _GeditDrawspacesViewActivatableClass
{
	GObjectClass parent_class;
};

GType          gedit_drawspaces_view_activatable_get_type   (void) G_GNUC_CONST;

void           gedit_drawspaces_view_activatable_register   (GTypeModule *module);

G_END_DECLS

#endif /* __GEDIT_DRAWSPACES_VIEW_ACTIVATABLE_H__ */

/* ex:set ts=8 noet: */
