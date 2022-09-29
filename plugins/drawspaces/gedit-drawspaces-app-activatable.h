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

#ifndef __GEDIT_DRAWSPACES_APP_ACTIVATABLE_H__
#define __GEDIT_DRAWSPACES_APP_ACTIVATABLE_H__

#include <glib-object.h>
#include <libpeas/peas-object-module.h>

G_BEGIN_DECLS

#define GEDIT_TYPE_DRAWSPACES_APP_ACTIVATABLE			(gedit_drawspaces_app_activatable_get_type ())
#define GEDIT_DRAWSPACES_APP_ACTIVATABLE(obj)			(G_TYPE_CHECK_INSTANCE_CAST ((obj), GEDIT_TYPE_DRAWSPACES_APP_ACTIVATABLE, GeditDrawspacesAppActivatable))
#define GEDIT_DRAWSPACES_APP_ACTIVATABLE_CONST(obj)		(G_TYPE_CHECK_INSTANCE_CAST ((obj), GEDIT_TYPE_DRAWSPACES_APP_ACTIVATABLE, GeditDrawspacesAppActivatable const))
#define GEDIT_DRAWSPACES_APP_ACTIVATABLE_CLASS(klass)		(G_TYPE_CHECK_CLASS_CAST ((klass), GEDIT_TYPE_DRAWSPACES_APP_ACTIVATABLE, GeditDrawspacesAppActivatableClass))
#define GEDIT_IS_DRAWSPACES_APP_ACTIVATABLE(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), GEDIT_TYPE_DRAWSPACES_APP_ACTIVATABLE))
#define GEDIT_IS_DRAWSPACES_APP_ACTIVATABLE_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), GEDIT_TYPE_DRAWSPACES_APP_ACTIVATABLE))
#define GEDIT_DRAWSPACES_APP_ACTIVATABLE_GET_CLASS(obj)		(G_TYPE_INSTANCE_GET_CLASS ((obj), GEDIT_TYPE_DRAWSPACES_APP_ACTIVATABLE, GeditDrawspacesAppActivatableClass))

typedef struct _GeditDrawspacesAppActivatable		GeditDrawspacesAppActivatable;
typedef struct _GeditDrawspacesAppActivatableClass	GeditDrawspacesAppActivatableClass;

struct _GeditDrawspacesAppActivatable
{
	GObject parent;
};

struct _GeditDrawspacesAppActivatableClass
{
	GObjectClass parent_class;
};

enum _GeditDrawSpacesFlags {
	GEDIT_DRAW_SPACES_SPACE      = 1 << 0,
	GEDIT_DRAW_SPACES_TAB        = 1 << 1,
	GEDIT_DRAW_SPACES_NEWLINE    = 1 << 2,
	GEDIT_DRAW_SPACES_NBSP       = 1 << 3,
	GEDIT_DRAW_SPACES_LEADING    = 1 << 4,
	GEDIT_DRAW_SPACES_TEXT       = 1 << 5,
	GEDIT_DRAW_SPACES_TRAILING   = 1 << 6,
	GEDIT_DRAW_SPACES_ALL        = 0x7f
};

GType                   gedit_drawspaces_app_activatable_get_type   (void) G_GNUC_CONST;

G_MODULE_EXPORT void    peas_register_types                         (PeasObjectModule *module);

G_END_DECLS

#endif /* __GEDIT_DRAWSPACES_APP_ACTIVATABLE_H__ */
