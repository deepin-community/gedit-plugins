/*
* Copyright (C) 2015 The Lemon Man
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

namespace Gedit {
namespace FindInFilesPlugin {

interface IMatcher : Object {
    public abstract bool has_match (uint8 *text, size_t text_length, size_t pos, ref Range match);
}

struct Range {
    size_t from;
    size_t to;
}

struct Bookmark {
    int line_number;
    size_t line_start;
    size_t line_length;
    public const Bookmark EmptyBookmark = { 0, 0 };
}

struct Result {
    string path;
    size_t line;
    string context;
}

class FindJob {
    public signal void on_match_found (Result result);
    public signal void on_search_finished ();

    // This queue holds all the file names to scan
    private AsyncQueue<string> scan_queue = new AsyncQueue<string>();

    // The list of (hard) workers
    private List<Thread<int>> thread_workers;

    // Count how many workers are still working
    private uint running_workers = 0;

    private IMatcher? matcher = null;

    private Cancellable cancellable;

    // The actual job parameters
    public bool include_hidden;
    public bool match_whole_word;
    public bool ignore_case;
    public string? needle { get; private set; }

    int worker () {
        while (true) {
            const int ONE_SEC = 1000000;
            var tv = ONE_SEC / 2;

            var path = scan_queue.timeout_pop (tv);

            // Check for interruption
            if (cancellable.is_cancelled ())
                break;

            // If path is null then we're probably done
            if (path == null)
                break;

            // Scan the file
            scan_file (path);
        }

        // We're done, check if we're the last worker active and signal it to the user
        lock (running_workers) {
            if (0 == (--running_workers)) {
                // Run the completion callback in the main thread
                Idle.add (() => { on_search_finished (); return false; });
            }
        }

        return 0;
    }

    public FindJob (Cancellable? cancellable) {
        this.cancellable = cancellable ?? new Cancellable ();
        needle = null;
        include_hidden = false;
        match_whole_word = false;
        ignore_case = false;
    }

    public void prepare (string needle, bool is_regex) throws Error {
        // Construct the matcher instance
        if (is_regex) {
              matcher = new RegexFind (needle, ignore_case);
        } else {
              matcher = new BoyerMooreHorspool (needle, ignore_case);
        }
    }

    void start_workers_pool () {
        if (running_workers != 0) {
            return;
        }

        var online_cpus = get_num_processors ();

        for (var i = 0; i < online_cpus; i++) {
            thread_workers.append (new Thread<int> ("Worker %d".printf (i), worker));
        }

        running_workers = online_cpus;
    }

    public string extract_context (uint8 *buffer, Range range) {
        uint8 *slice = new uint8[range.to - range.from];
        Posix.memcpy (slice, buffer + range.from, range.to - range.from);
        string slice_str = (string)slice;
        return slice_str.make_valid();
    }

    public void halt () {
        if (running_workers == 0)
            return;

        cancellable.cancel ();

        foreach (var worker in thread_workers) {
            worker.join ();
        }
    }

    bool is_binary (uint8 *buffer, size_t buffer_size) {
        // Poor-man binary detection, check for NULL bytes
        return Posix.memchr (buffer, '\0', buffer_size) != null;
    }

    bool ignore_vcs_dir (FileInfo file) {
        if (file.get_file_type () == FileType.DIRECTORY) {
            var name = file.get_name ();

            if (name == ".git" ||
                name == ".bzr" ||
                name == ".svn" ||
                name == ".hg"  ||
                name == "_darcs")
                return true;
        }

        return false;
    }

    public async void execute (string root) throws Error {
        var queue = new Queue<File> ();
        var visited = new HashTable<string, bool> (str_hash, str_equal);

        start_workers_pool ();

        queue.push_tail (File.new_for_path (root));

        while (!queue.is_empty ()) {
            if (cancellable.is_cancelled ())
                break;

            var dir = queue.pop_head ();

            var e = yield dir.enumerate_children_async (FileAttribute.STANDARD_NAME,
                                                        FileQueryInfoFlags.NOFOLLOW_SYMLINKS,
                                                        Priority.DEFAULT);

            // Process the entries we got so far
            while (true) {
                var files = yield e.next_files_async (100);

                if (files == null)
                    break;

                if (cancellable.is_cancelled ())
                    break;

                foreach (var file in files) {
                    if (!include_hidden && file.get_name ()[0] == '.')
                        continue;

                    if (ignore_vcs_dir (file))
                        continue;

                    var _file = dir.resolve_relative_path (file.get_name ());

                    switch (file.get_file_type ()) {
                    case FileType.REGULAR:
                        scan_queue.push (_file.get_path ());
                        break;

                    case FileType.DIRECTORY:
                        queue.push_tail (_file);
                        visited.insert (_file.get_path (), true);
                        break;

                    case FileType.SYMBOLIC_LINK:
                        var link_dest = Posix.realpath (_file.get_path ());

                        // Follow the link only if its not broken and we didn't visit it
                        if (link_dest != null && !visited.contains (link_dest)) {
                            if (FileUtils.test (link_dest, FileTest.IS_DIR) &&
                                (!ignore_case && link_dest[0] != '.'))
                                queue.push_tail (File.new_for_path (link_dest));
                        }

                        break;
                    }
                }
            }
        }
    }

    // Returns the line number where the text span starting at 'from' and ending at 'to' lies.
    void get_line (uint8 *buffer, size_t buffer_size, ref Range span, ref Bookmark bookmark) {
        // We take an advantage by knowing that all the calls to get_line are sequential, hence
        // we save the position of the last matched line and start from there
        var line_count = bookmark.line_number;
        var line_start = bookmark.line_start;

        var ptr = buffer + bookmark.line_start;

        while (ptr < buffer + buffer_size) {
            // Find the newline
            uint8 *nl = Posix.memchr (ptr, '\n', buffer_size - (ptr - buffer));

            if (nl == null) {
                // No more newlines, consider the trailing NULL as the final newline
                nl = buffer + buffer_size + 1;
            } else {
                // Skip the '\n'
                nl++;
            }

            var line_length = nl - ptr;

            // Check if the match is within this line
            if (span.from >= line_start && span.to < line_start + line_length) {
                // Update the bookmark
                bookmark.line_number = line_count;
                bookmark.line_start = line_start;
                bookmark.line_length = line_length - 1;

                return;
            }

            line_count++;
            line_start += line_length;

            ptr = nl;
        }

        // There's no way to exit the loop, unless there's a problem in the logic above
        assert_not_reached ();
    }

    bool is_word_boundary (uint8 *buf, size_t buf_size, size_t from, size_t to) {
        unichar ch;
        bool prev, next;
        unowned string str;

        assert (to > from && to <= buf_size);

        // There's not much we can do
        if (to - from > int.MAX)
            return false;

        // Silence the warning about ch being uninitialized
        ch = '\0';

        prev = next = true;
        str = (string)(buf + from);

        // Those are being modified by the get_{prev,next}_char calls
        int start = 0;
        int end = (int)(to - from);

        // The match is on a word boundary if there are no consecutive alphanumeric
        // characters right before or after the match
        var head = str.get_char (0);
        if (start > 0 && str.get_prev_char (ref start, out ch))
            prev = head.isalnum () != ch.isalnum ();

        var tail = str.get_char (end - 1);
        if (end < buf_size && str.get_next_char (ref end, out ch))
            next = tail.isalnum () != ch.isalnum ();

        return prev && next;
    }

    void scan_file (string path) {
        MappedFile file;

        try {
            file = new MappedFile (path, false);
        }
        catch (FileError err) {
            warning (err.message);
            return;
        }

        var buffer_size = file.get_length ();
        var buffer = (uint8 *)file.get_contents ();

        // Skip binary files for obvious reasons
        if (is_binary (buffer, buffer_size))
            return;

        Range match = { 0, 0 };
        Bookmark bookmark = Bookmark.EmptyBookmark;
        var last_line = -1;

        for (size_t buffer_pos = 0; buffer_pos < buffer_size; ) {
            if (cancellable.is_cancelled ())
                break;

            // Exit when there's no match
            if (!matcher.has_match (buffer, buffer_size, buffer_pos, ref match))
                break;

            // Check if the match lies on a word boundary
            if (match_whole_word) {
                if (!is_word_boundary (buffer, buffer_size, (int)match.from, (int)match.to)) {
                    buffer_pos = match.to;
                    continue;
                }
            }

            get_line (buffer, buffer_size, ref match, ref bookmark);

            // Find out what line the match lies in
            var match_line = 1 + bookmark.line_number;

            // Notify that we got a match
            if (last_line != match_line) {
                Result res = { path, match_line, extract_context (buffer, match) };
                on_match_found (res);
            }

            last_line = match_line;

            // Keep searching past the match
            buffer_pos = match.to;
        }
    }
}

} // namespace FindInFilesPlugin
} // namespace Gedit
