project(
  'gedit-plugins', 'c', # vala is added below if needed, with add_languages().
  version: '40.1',
  meson_version: '>= 0.50'
)

gnome = import('gnome')
i18n = import('i18n')
pkg = import('pkgconfig')
python = import('python')

# Paths
root_include_dir = include_directories('.')

srcdir = meson.current_source_dir()

libdir = join_paths(get_option('prefix'), get_option('libdir'))
datadir = join_paths(get_option('prefix'), get_option('datadir'))

pkglibdir = join_paths(libdir, 'gedit')
pkgdatadir = join_paths(datadir, 'gedit')

appstreamdir = join_paths(datadir, 'metainfo')
glibdir = join_paths(datadir, 'glib-2.0')
localedir = join_paths(datadir, 'locale')

# Dependencies in common for all plugins
libpeas_dep = dependency('libpeas-1.0', version: '>= 1.14.1')
gedit_dep = dependency('gedit', version: '>= 40.0')

appstream_util = find_program('appstream-util', required: false)

# config.h
config_h = configuration_data()
config_h.set_quoted('GETTEXT_PACKAGE', meson.project_name())

configure_file(
  output: 'config.h',
  configuration: config_h
)

# Options
enabled_plugins = []
disabled_plugins = []
extra_languages = []
all_plugins = {
  'bookmarks': {'language': 'c'},
  'bracketcompletion': {'language': 'python'},
  'charmap': {'language': 'python'},
  'codecomment': {'language': 'python'},
  'colorpicker': {'language': 'python'},
  'colorschemer': {'language': 'python'},
  'commander': {'language': 'python'},
  'drawspaces': {'language': 'c'},
  'findinfiles': {'language': 'vala'},
  'git': {'language': 'python'},
  'joinlines': {'language': 'python'},
  'multiedit': {'language': 'python'},
  'sessionsaver': {'language': 'python'},
  'smartspaces': {'language': 'python'},
  'synctex': {'language': 'python'},
  'terminal': {'language': 'python'},
  'textsize': {'language': 'python'},
  'translate': {'language': 'python'},
  'wordcompletion': {'language': 'c'},
}

foreach plugin_name, plugin_metadata : all_plugins
  if get_option('plugin_@0@'.format(plugin_name))
    enabled_plugins += plugin_name

    plugin_language = plugin_metadata.get('language')
    if plugin_language != 'c'
      extra_languages += plugin_language
    endif
  else
    disabled_plugins += plugin_name
  endif
endforeach

if 'python' in extra_languages
  python3 = python.find_installation('python3')
endif

if 'vala' in extra_languages
  add_languages('vala', required: true)
endif

subdir('po')
subdir('plugins')
subdir('help')

meson.add_install_script(
  'build-aux/meson/post_install.py',
  libdir,
  datadir
)

# Summary message

summary = [
  'Configuration:',
  '',
  '        gedit-plugins version @0@'.format(meson.project_version()),
  '',
  '        Prefix: @0@'.format(get_option('prefix')),
  '',
  '        Enabled plugins:'
]

foreach plugin_name : enabled_plugins
  summary += '                ' + plugin_name
endforeach

summary += [
  '',
  '        Disabled plugins:'
]

foreach plugin_name : disabled_plugins
  summary += '                ' + plugin_name
endforeach

summary += ''

message('\n'.join(summary))
