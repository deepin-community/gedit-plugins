/*
 * gedit-bookmarks-message-remove.c
 * This file is part of gedit
 *
 * Copyright (C) 2011 - Paolo Borelli
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
 * along with gedit; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor,
 * Boston, MA  02110-1301  USA
 */

#include <gtk/gtk.h>
#include <gedit/gedit-view.h>
#include "gedit-bookmarks-message-remove.h"

enum
{
	PROP_0,

	PROP_VIEW,
	PROP_ITER,
};

struct _GeditBookmarksMessageRemovePrivate
{
	GeditView *view;
	GtkTextIter *iter;
};

G_DEFINE_TYPE_WITH_PRIVATE (GeditBookmarksMessageRemove, gedit_bookmarks_message_remove, GEDIT_TYPE_MESSAGE)

static void
gedit_bookmarks_message_remove_finalize (GObject *obj)
{
	GeditBookmarksMessageRemove *msg = GEDIT_BOOKMARKS_MESSAGE_REMOVE (obj);

	if (msg->priv->view)
	{
		g_object_unref (msg->priv->view);
	}
	if (msg->priv->iter)
	{
		g_object_unref (msg->priv->iter);
	}

	G_OBJECT_CLASS (gedit_bookmarks_message_remove_parent_class)->finalize (obj);
}

static void
gedit_bookmarks_message_remove_get_property (GObject    *obj,
                                             guint       prop_id,
                                             GValue     *value,
                                             GParamSpec *pspec)
{
	GeditBookmarksMessageRemove *msg;

	msg = GEDIT_BOOKMARKS_MESSAGE_REMOVE (obj);

	switch (prop_id)
	{
		case PROP_VIEW:
			g_value_set_object (value, msg->priv->view);
			break;
		case PROP_ITER:
			g_value_set_boxed (value, msg->priv->iter);
			break;
	}
}

static void
gedit_bookmarks_message_remove_set_property (GObject      *obj,
                                             guint         prop_id,
                                             GValue const *value,
                                             GParamSpec   *pspec)
{
	GeditBookmarksMessageRemove *msg;

	msg = GEDIT_BOOKMARKS_MESSAGE_REMOVE (obj);

	switch (prop_id)
	{
		case PROP_VIEW:
		{
			if (msg->priv->view)
			{
				g_object_unref (msg->priv->view);
			}
			msg->priv->view = g_value_dup_object (value);
			break;
		}
		case PROP_ITER:
		{
			if (msg->priv->iter)
			{
				g_boxed_free (GTK_TYPE_TEXT_ITER, msg->priv->iter);
			}
			msg->priv->iter = g_boxed_copy (GTK_TYPE_TEXT_ITER, value);
			break;
		}
	}
}

static void
gedit_bookmarks_message_remove_class_init (GeditBookmarksMessageRemoveClass *klass)
{
	GObjectClass *object_class = G_OBJECT_CLASS(klass);

	object_class->finalize = gedit_bookmarks_message_remove_finalize;

	object_class->get_property = gedit_bookmarks_message_remove_get_property;
	object_class->set_property = gedit_bookmarks_message_remove_set_property;

	g_object_class_install_property (object_class,
	                                 PROP_VIEW,
	                                 g_param_spec_object ("view",
	                                                      "View",
	                                                      "View",
	                                                      GEDIT_TYPE_VIEW,
	                                                      G_PARAM_READWRITE |
	                                                      G_PARAM_CONSTRUCT |
	                                                      G_PARAM_STATIC_STRINGS));

	g_object_class_install_property (object_class,
	                                 PROP_ITER,
	                                 g_param_spec_boxed ("iter",
	                                                      "Iter",
	                                                      "Iter",
	                                                      GTK_TYPE_TEXT_ITER,
	                                                      G_PARAM_READWRITE |
	                                                      G_PARAM_CONSTRUCT |
	                                                      G_PARAM_STATIC_STRINGS));
}

static void
gedit_bookmarks_message_remove_init (GeditBookmarksMessageRemove *message)
{
	message->priv = gedit_bookmarks_message_remove_get_instance_private (message);
}
