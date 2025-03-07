import os
import sys
import unittest
from unittest import mock

from mkdocs.structure.files import File, Files, _sort_files, get_files
from mkdocs.tests.base import PathAssertionMixin, load_config, tempdir


class TestFiles(PathAssertionMixin, unittest.TestCase):
    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_src_path_windows(self):
        f = File('foo\\a.md', '/path/to/docs', '/path/to/site', use_directory_urls=False)
        self.assertEqual(f.src_uri, 'foo/a.md')
        self.assertEqual(f.src_path, 'foo\\a.md')
        f.src_uri = 'foo/b.md'
        self.assertEqual(f.src_uri, 'foo/b.md')
        self.assertEqual(f.src_path, 'foo\\b.md')
        f.src_path = 'foo/c.md'
        self.assertEqual(f.src_uri, 'foo/c.md')
        self.assertEqual(f.src_path, 'foo\\c.md')
        f.src_path = 'foo\\d.md'
        self.assertEqual(f.src_uri, 'foo/d.md')
        self.assertEqual(f.src_path, 'foo\\d.md')
        f.src_uri = 'foo\\e.md'
        self.assertEqual(f.src_uri, 'foo\\e.md')
        self.assertEqual(f.src_path, 'foo\\e.md')

    def test_sort_files(self):
        self.assertEqual(
            _sort_files(['b.md', 'bb.md', 'a.md', 'index.md', 'aa.md']),
            ['index.md', 'a.md', 'aa.md', 'b.md', 'bb.md'],
        )

        self.assertEqual(
            _sort_files(['b.md', 'index.html', 'a.md', 'index.md']),
            ['index.html', 'index.md', 'a.md', 'b.md'],
        )

        self.assertEqual(
            _sort_files(['a.md', 'index.md', 'b.md', 'index.html']),
            ['index.html', 'index.md', 'a.md', 'b.md'],
        )

        self.assertEqual(
            _sort_files(['.md', '_.md', 'a.md', 'index.md', '1.md']),
            ['index.md', '.md', '1.md', '_.md', 'a.md'],
        )

        self.assertEqual(
            _sort_files(['a.md', 'b.md', 'a.md']),
            ['a.md', 'a.md', 'b.md'],
        )

        self.assertEqual(
            _sort_files(['A.md', 'B.md', 'README.md']),
            ['README.md', 'A.md', 'B.md'],
        )

    def test_md_file(self):
        for use_directory_urls in True, False:
            with self.subTest(use_directory_urls=use_directory_urls):
                f = File('foo.md', '/path/to/docs', '/path/to/site', use_directory_urls)
                self.assertEqual(f.src_uri, 'foo.md')
                self.assertPathsEqual(f.abs_src_path, '/path/to/docs/foo.md')
                if use_directory_urls:
                    self.assertEqual(f.dest_uri, 'foo/index.html')
                    self.assertPathsEqual(f.abs_dest_path, '/path/to/site/foo/index.html')
                    self.assertEqual(f.url, 'foo/')
                else:
                    self.assertEqual(f.dest_uri, 'foo.html')
                    self.assertPathsEqual(f.abs_dest_path, '/path/to/site/foo.html')
                    self.assertEqual(f.url, 'foo.html')
                self.assertEqual(f.name, 'foo')
                self.assertTrue(f.is_documentation_page())
                self.assertFalse(f.is_static_page())
                self.assertFalse(f.is_media_file())
                self.assertFalse(f.is_javascript())
                self.assertFalse(f.is_css())

    def test_md_file_nested(self):
        for use_directory_urls in True, False:
            with self.subTest(use_directory_urls=use_directory_urls):
                f = File('foo/bar.md', '/path/to/docs', '/path/to/site', use_directory_urls)
                self.assertEqual(f.src_uri, 'foo/bar.md')
                self.assertPathsEqual(f.abs_src_path, '/path/to/docs/foo/bar.md')
                if use_directory_urls:
                    self.assertEqual(f.dest_uri, 'foo/bar/index.html')
                    self.assertPathsEqual(f.abs_dest_path, '/path/to/site/foo/bar/index.html')
                    self.assertEqual(f.url, 'foo/bar/')
                else:
                    self.assertEqual(f.dest_uri, 'foo/bar.html')
                    self.assertPathsEqual(f.abs_dest_path, '/path/to/site/foo/bar.html')
                    self.assertEqual(f.url, 'foo/bar.html')
                self.assertEqual(f.name, 'bar')
                self.assertTrue(f.is_documentation_page())
                self.assertFalse(f.is_static_page())
                self.assertFalse(f.is_media_file())
                self.assertFalse(f.is_javascript())
                self.assertFalse(f.is_css())

    def test_md_index_file(self):
        for use_directory_urls in True, False:
            with self.subTest(use_directory_urls=use_directory_urls):
                f = File('index.md', '/path/to/docs', '/path/to/site', use_directory_urls)
                self.assertEqual(f.src_uri, 'index.md')
                self.assertPathsEqual(f.abs_src_path, '/path/to/docs/index.md')
                self.assertEqual(f.dest_uri, 'index.html')
                self.assertPathsEqual(f.abs_dest_path, '/path/to/site/index.html')
                if use_directory_urls:
                    self.assertEqual(f.url, './')
                else:
                    self.assertEqual(f.url, 'index.html')
                self.assertEqual(f.name, 'index')
                self.assertTrue(f.is_documentation_page())
                self.assertFalse(f.is_static_page())
                self.assertFalse(f.is_media_file())
                self.assertFalse(f.is_javascript())
                self.assertFalse(f.is_css())

    def test_md_readme_index_file(self):
        for use_directory_urls in True, False:
            with self.subTest(use_directory_urls=use_directory_urls):
                f = File('README.md', '/path/to/docs', '/path/to/site', use_directory_urls)
                self.assertEqual(f.src_uri, 'README.md')
                self.assertPathsEqual(f.abs_src_path, '/path/to/docs/README.md')
                self.assertEqual(f.dest_uri, 'index.html')
                self.assertPathsEqual(f.abs_dest_path, '/path/to/site/index.html')
                if use_directory_urls:
                    self.assertEqual(f.url, './')
                else:
                    self.assertEqual(f.url, 'index.html')
                self.assertEqual(f.name, 'index')
                self.assertTrue(f.is_documentation_page())
                self.assertFalse(f.is_static_page())
                self.assertFalse(f.is_media_file())
                self.assertFalse(f.is_javascript())
                self.assertFalse(f.is_css())

    def test_md_index_file_nested(self):
        for use_directory_urls in True, False:
            with self.subTest(use_directory_urls=use_directory_urls):
                f = File('foo/index.md', '/path/to/docs', '/path/to/site', use_directory_urls)
                self.assertEqual(f.src_uri, 'foo/index.md')
                self.assertPathsEqual(f.abs_src_path, '/path/to/docs/foo/index.md')
                self.assertEqual(f.dest_uri, 'foo/index.html')
                self.assertPathsEqual(f.abs_dest_path, '/path/to/site/foo/index.html')
                if use_directory_urls:
                    self.assertEqual(f.url, 'foo/')
                else:
                    self.assertEqual(f.url, 'foo/index.html')
                self.assertEqual(f.name, 'index')
                self.assertTrue(f.is_documentation_page())
                self.assertFalse(f.is_static_page())
                self.assertFalse(f.is_media_file())
                self.assertFalse(f.is_javascript())
                self.assertFalse(f.is_css())

    def test_static_file(self):
        for use_directory_urls in True, False:
            with self.subTest(use_directory_urls=use_directory_urls):
                f = File('foo/bar.html', '/path/to/docs', '/path/to/site', use_directory_urls)
                self.assertEqual(f.src_uri, 'foo/bar.html')
                self.assertPathsEqual(f.abs_src_path, '/path/to/docs/foo/bar.html')
                self.assertEqual(f.dest_uri, 'foo/bar.html')
                self.assertPathsEqual(f.abs_dest_path, '/path/to/site/foo/bar.html')
                self.assertEqual(f.url, 'foo/bar.html')
                self.assertEqual(f.name, 'bar')
                self.assertFalse(f.is_documentation_page())
                self.assertTrue(f.is_static_page())
                self.assertFalse(f.is_media_file())
                self.assertFalse(f.is_javascript())
                self.assertFalse(f.is_css())

    def test_media_file(self):
        for use_directory_urls in True, False:
            with self.subTest(use_directory_urls=use_directory_urls):
                f = File('foo/bar.jpg', '/path/to/docs', '/path/to/site', use_directory_urls)
                self.assertEqual(f.src_uri, 'foo/bar.jpg')
                self.assertPathsEqual(f.abs_src_path, '/path/to/docs/foo/bar.jpg')
                self.assertEqual(f.dest_uri, 'foo/bar.jpg')
                self.assertPathsEqual(f.abs_dest_path, '/path/to/site/foo/bar.jpg')
                self.assertEqual(f.url, 'foo/bar.jpg')
                self.assertEqual(f.name, 'bar')
                self.assertFalse(f.is_documentation_page())
                self.assertFalse(f.is_static_page())
                self.assertTrue(f.is_media_file())
                self.assertFalse(f.is_javascript())
                self.assertFalse(f.is_css())

    def test_javascript_file(self):
        for use_directory_urls in True, False:
            with self.subTest(use_directory_urls=use_directory_urls):
                f = File('foo/bar.js', '/path/to/docs', '/path/to/site', use_directory_urls)
                self.assertEqual(f.src_uri, 'foo/bar.js')
                self.assertPathsEqual(f.abs_src_path, '/path/to/docs/foo/bar.js')
                self.assertEqual(f.dest_uri, 'foo/bar.js')
                self.assertPathsEqual(f.abs_dest_path, '/path/to/site/foo/bar.js')
                self.assertEqual(f.url, 'foo/bar.js')
                self.assertEqual(f.name, 'bar')
                self.assertFalse(f.is_documentation_page())
                self.assertFalse(f.is_static_page())
                self.assertTrue(f.is_media_file())
                self.assertTrue(f.is_javascript())
                self.assertFalse(f.is_css())

    def test_css_file(self):
        for use_directory_urls in True, False:
            with self.subTest(use_directory_urls=use_directory_urls):
                f = File('foo/bar.css', '/path/to/docs', '/path/to/site', use_directory_urls)
                self.assertEqual(f.src_uri, 'foo/bar.css')
                self.assertPathsEqual(f.abs_src_path, '/path/to/docs/foo/bar.css')
                self.assertEqual(f.dest_uri, 'foo/bar.css')
                self.assertPathsEqual(f.abs_dest_path, '/path/to/site/foo/bar.css')
                self.assertEqual(f.url, 'foo/bar.css')
                self.assertEqual(f.name, 'bar')
                self.assertFalse(f.is_documentation_page())
                self.assertFalse(f.is_static_page())
                self.assertTrue(f.is_media_file())
                self.assertFalse(f.is_javascript())
                self.assertTrue(f.is_css())

    def test_file_name_with_space(self):
        f = File('foo bar.md', '/path/to/docs', '/path/to/site', use_directory_urls=False)
        self.assertEqual(f.src_uri, 'foo bar.md')
        self.assertPathsEqual(f.abs_src_path, '/path/to/docs/foo bar.md')
        self.assertEqual(f.dest_uri, 'foo bar.html')
        self.assertPathsEqual(f.abs_dest_path, '/path/to/site/foo bar.html')
        self.assertEqual(f.url, 'foo%20bar.html')
        self.assertEqual(f.name, 'foo bar')

    def test_file_name_with_custom_dest_uri(self):
        for use_directory_urls in True, False:
            with self.subTest(use_directory_urls=use_directory_urls):
                f = File(
                    'stuff/foo.md',
                    src_dir='/path/to/docs',
                    dest_dir='/path/to/site',
                    use_directory_urls=use_directory_urls,
                    dest_uri='stuff/1-foo/index.html',
                )
                self.assertEqual(f.src_uri, 'stuff/foo.md')
                self.assertPathsEqual(f.abs_src_path, '/path/to/docs/stuff/foo.md')
                self.assertEqual(f.dest_uri, 'stuff/1-foo/index.html')
                self.assertPathsEqual(f.abs_dest_path, '/path/to/site/stuff/1-foo/index.html')
                if use_directory_urls:
                    self.assertEqual(f.url, 'stuff/1-foo/')
                else:
                    self.assertEqual(f.url, 'stuff/1-foo/index.html')
                self.assertEqual(f.name, 'foo')

    def test_files(self):
        fs = [
            File('index.md', '/path/to/docs', '/path/to/site', use_directory_urls=True),
            File('foo/bar.md', '/path/to/docs', '/path/to/site', use_directory_urls=True),
            File('foo/bar.html', '/path/to/docs', '/path/to/site', use_directory_urls=True),
            File('foo/bar.jpg', '/path/to/docs', '/path/to/site', use_directory_urls=True),
            File('foo/bar.js', '/path/to/docs', '/path/to/site', use_directory_urls=True),
            File('foo/bar.css', '/path/to/docs', '/path/to/site', use_directory_urls=True),
        ]
        files = Files(fs)
        self.assertEqual(list(files), fs)
        self.assertEqual(len(files), 6)
        self.assertEqual(files.documentation_pages(), [fs[0], fs[1]])
        self.assertEqual(files.static_pages(), [fs[2]])
        self.assertEqual(files.media_files(), [fs[3], fs[4], fs[5]])
        self.assertEqual(files.javascript_files(), [fs[4]])
        self.assertEqual(files.css_files(), [fs[5]])
        self.assertEqual(files.get_file_from_path('foo/bar.jpg'), fs[3])
        self.assertEqual(files.get_file_from_path('foo/bar.jpg'), fs[3])
        self.assertEqual(files.get_file_from_path('missing.jpg'), None)
        self.assertTrue(fs[2].src_uri in files.src_uris)
        extra_file = File('extra.md', '/path/to/docs', '/path/to/site', use_directory_urls=True)
        self.assertFalse(extra_file.src_uri in files.src_uris)
        files.append(extra_file)
        self.assertEqual(len(files), 7)
        self.assertTrue(extra_file.src_uri in files.src_uris)
        self.assertEqual(files.documentation_pages(), [fs[0], fs[1], extra_file])
        files.remove(fs[1])
        self.assertEqual(files.documentation_pages(), [fs[0], extra_file])

    @tempdir(
        files=[
            'favicon.ico',
            'index.md',
        ]
    )
    @tempdir(
        files=[
            'base.html',
            'favicon.ico',
            'style.css',
            'foo.md',
            'README',
            '.ignore.txt',
            '.ignore/file.txt',
            'foo/.ignore.txt',
            'foo/.ignore/file.txt',
        ]
    )
    def test_add_files_from_theme(self, tdir, ddir):
        config = load_config(docs_dir=ddir, theme={'name': None, 'custom_dir': tdir})
        env = config.theme.get_env()
        files = get_files(config)
        self.assertEqual(
            [file.src_uri for file in files],
            ['index.md', 'favicon.ico'],
        )
        files.add_files_from_theme(env, config)
        self.assertEqual(
            [file.src_uri for file in files],
            ['index.md', 'favicon.ico', 'style.css'],
        )
        # Ensure theme file does not override docs_dir file
        self.assertEqual(
            files.get_file_from_path('favicon.ico').abs_src_path,
            os.path.normpath(os.path.join(ddir, 'favicon.ico')),
        )

    def test_get_relative_url_use_directory_urls(self):
        to_files = [
            'index.md',
            'foo/index.md',
            'foo/bar/index.md',
            'foo/bar/baz/index.md',
            'foo.md',
            'foo/bar.md',
            'foo/bar/baz.md',
        ]
        to_file_urls = [
            './',
            'foo/',
            'foo/bar/',
            'foo/bar/baz/',
            'foo/',
            'foo/bar/',
            'foo/bar/baz/',
        ]

        from_file = File('img.jpg', '/path/to/docs', '/path/to/site', use_directory_urls=True)
        self.assertEqual(from_file.url, 'img.jpg')

        expected = [
            'img.jpg',  # img.jpg relative to .
            '../img.jpg',  # img.jpg relative to foo/
            '../../img.jpg',  # img.jpg relative to foo/bar/
            '../../../img.jpg',  # img.jpg relative to foo/bar/baz/
            '../img.jpg',  # img.jpg relative to foo
            '../../img.jpg',  # img.jpg relative to foo/bar
            '../../../img.jpg',  # img.jpg relative to foo/bar/baz
        ]
        for i, filename in enumerate(to_files):
            file = File(filename, '/path/to/docs', '/path/to/site', use_directory_urls=True)
            self.assertEqual(file.url, to_file_urls[i])
            self.assertEqual(from_file.url_relative_to(file.url), expected[i])
            self.assertEqual(from_file.url_relative_to(file), expected[i])

        from_file = File('foo/img.jpg', '/path/to/docs', '/path/to/site', use_directory_urls=True)
        self.assertEqual(from_file.url, 'foo/img.jpg')

        expected = [
            'foo/img.jpg',  # foo/img.jpg relative to .
            'img.jpg',  # foo/img.jpg relative to foo/
            '../img.jpg',  # foo/img.jpg relative to foo/bar/
            '../../img.jpg',  # foo/img.jpg relative to foo/bar/baz/
            'img.jpg',  # foo/img.jpg relative to foo
            '../img.jpg',  # foo/img.jpg relative to foo/bar
            '../../img.jpg',  # foo/img.jpg relative to foo/bar/baz
        ]
        for i, filename in enumerate(to_files):
            file = File(filename, '/path/to/docs', '/path/to/site', use_directory_urls=True)
            self.assertEqual(file.url, to_file_urls[i])
            self.assertEqual(from_file.url_relative_to(file.url), expected[i])
            self.assertEqual(from_file.url_relative_to(file), expected[i])

        from_file = File('index.html', '/path/to/docs', '/path/to/site', use_directory_urls=True)
        self.assertEqual(from_file.url, './')

        expected = [
            './',  # . relative to .
            '../',  # . relative to foo/
            '../../',  # . relative to foo/bar/
            '../../../',  # . relative to foo/bar/baz/
            '../',  # . relative to foo
            '../../',  # . relative to foo/bar
            '../../../',  # . relative to foo/bar/baz
        ]
        for i, filename in enumerate(to_files):
            file = File(filename, '/path/to/docs', '/path/to/site', use_directory_urls=True)
            self.assertEqual(file.url, to_file_urls[i])
            self.assertEqual(from_file.url_relative_to(file.url), expected[i])
            self.assertEqual(from_file.url_relative_to(file), expected[i])

        from_file = File('file.md', '/path/to/docs', '/path/to/site', use_directory_urls=True)
        self.assertEqual(from_file.url, 'file/')

        expected = [
            'file/',  # file relative to .
            '../file/',  # file relative to foo/
            '../../file/',  # file relative to foo/bar/
            '../../../file/',  # file relative to foo/bar/baz/
            '../file/',  # file relative to foo
            '../../file/',  # file relative to foo/bar
            '../../../file/',  # file relative to foo/bar/baz
        ]
        for i, filename in enumerate(to_files):
            file = File(filename, '/path/to/docs', '/path/to/site', use_directory_urls=True)
            self.assertEqual(file.url, to_file_urls[i])
            self.assertEqual(from_file.url_relative_to(file.url), expected[i])
            self.assertEqual(from_file.url_relative_to(file), expected[i])

    def test_get_relative_url(self):
        to_files = [
            'index.md',
            'foo/index.md',
            'foo/bar/index.md',
            'foo/bar/baz/index.md',
            'foo.md',
            'foo/bar.md',
            'foo/bar/baz.md',
        ]
        to_file_urls = [
            'index.html',
            'foo/index.html',
            'foo/bar/index.html',
            'foo/bar/baz/index.html',
            'foo.html',
            'foo/bar.html',
            'foo/bar/baz.html',
        ]

        from_file = File('img.jpg', '/path/to/docs', '/path/to/site', use_directory_urls=False)
        self.assertEqual(from_file.url, 'img.jpg')

        expected = [
            'img.jpg',  # img.jpg relative to .
            '../img.jpg',  # img.jpg relative to foo/
            '../../img.jpg',  # img.jpg relative to foo/bar/
            '../../../img.jpg',  # img.jpg relative to foo/bar/baz/
            'img.jpg',  # img.jpg relative to foo.html
            '../img.jpg',  # img.jpg relative to foo/bar.html
            '../../img.jpg',  # img.jpg relative to foo/bar/baz.html
        ]
        for i, filename in enumerate(to_files):
            with self.subTest(from_file=from_file.src_path, to_file=filename):
                file = File(filename, '/path/to/docs', '/path/to/site', use_directory_urls=False)
                self.assertEqual(file.url, to_file_urls[i])
                self.assertEqual(from_file.url_relative_to(file.url), expected[i])
                self.assertEqual(from_file.url_relative_to(file), expected[i])

        from_file = File('foo/img.jpg', '/path/to/docs', '/path/to/site', use_directory_urls=False)
        self.assertEqual(from_file.url, 'foo/img.jpg')

        expected = [
            'foo/img.jpg',  # foo/img.jpg relative to .
            'img.jpg',  # foo/img.jpg relative to foo/
            '../img.jpg',  # foo/img.jpg relative to foo/bar/
            '../../img.jpg',  # foo/img.jpg relative to foo/bar/baz/
            'foo/img.jpg',  # foo/img.jpg relative to foo.html
            'img.jpg',  # foo/img.jpg relative to foo/bar.html
            '../img.jpg',  # foo/img.jpg relative to foo/bar/baz.html
        ]
        for i, filename in enumerate(to_files):
            with self.subTest(from_file=from_file.src_path, to_file=filename):
                file = File(filename, '/path/to/docs', '/path/to/site', use_directory_urls=False)
                self.assertEqual(file.url, to_file_urls[i])
                self.assertEqual(from_file.url_relative_to(file.url), expected[i])
                self.assertEqual(from_file.url_relative_to(file), expected[i])

        from_file = File('index.html', '/path/to/docs', '/path/to/site', use_directory_urls=False)
        self.assertEqual(from_file.url, 'index.html')

        expected = [
            'index.html',  # index.html relative to .
            '../index.html',  # index.html relative to foo/
            '../../index.html',  # index.html relative to foo/bar/
            '../../../index.html',  # index.html relative to foo/bar/baz/
            'index.html',  # index.html relative to foo.html
            '../index.html',  # index.html relative to foo/bar.html
            '../../index.html',  # index.html relative to foo/bar/baz.html
        ]
        for i, filename in enumerate(to_files):
            with self.subTest(from_file=from_file.src_path, to_file=filename):
                file = File(filename, '/path/to/docs', '/path/to/site', use_directory_urls=False)
                self.assertEqual(file.url, to_file_urls[i])
                self.assertEqual(from_file.url_relative_to(file.url), expected[i])
                self.assertEqual(from_file.url_relative_to(file), expected[i])

        from_file = File('file.html', '/path/to/docs', '/path/to/site', use_directory_urls=False)
        self.assertEqual(from_file.url, 'file.html')

        expected = [
            'file.html',  # file.html relative to .
            '../file.html',  # file.html relative to foo/
            '../../file.html',  # file.html relative to foo/bar/
            '../../../file.html',  # file.html relative to foo/bar/baz/
            'file.html',  # file.html relative to foo.html
            '../file.html',  # file.html relative to foo/bar.html
            '../../file.html',  # file.html relative to foo/bar/baz.html
        ]
        for i, filename in enumerate(to_files):
            with self.subTest(from_file=from_file.src_path, to_file=filename):
                file = File(filename, '/path/to/docs', '/path/to/site', use_directory_urls=False)
                self.assertEqual(file.url, to_file_urls[i])
                self.assertEqual(from_file.url_relative_to(file.url), expected[i])
                self.assertEqual(from_file.url_relative_to(file), expected[i])

    @tempdir(
        files=[
            'index.md',
            'readme.md',
            'bar.css',
            'bar.html',
            'bar.jpg',
            'bar.js',
            'bar.md',
            '.dotfile',
            'templates/foo.html',
        ]
    )
    def test_get_files(self, tdir):
        config = load_config(docs_dir=tdir, extra_css=['bar.css'], extra_javascript=['bar.js'])
        files = get_files(config)
        self.assertIsInstance(files, Files)
        self.assertEqual(
            [f.src_uri for f in files if f.inclusion.is_included()],
            ['index.md', 'bar.css', 'bar.html', 'bar.jpg', 'bar.js', 'bar.md', 'readme.md'],
        )
        self.assertEqual(
            [f.src_uri for f in files if f.inclusion.is_excluded()],
            ['.dotfile', 'templates/foo.html'],
        )

    @tempdir(
        files=[
            'README.md',
            'foo.md',
        ]
    )
    def test_get_files_include_readme_without_index(self, tdir):
        config = load_config(docs_dir=tdir)
        files = get_files(config)
        self.assertIsInstance(files, Files)
        self.assertEqual([f.src_uri for f in files], ['README.md', 'foo.md'])

    @tempdir(
        files=[
            'index.md',
            'README.md',
            'foo.md',
        ]
    )
    def test_get_files_exclude_readme_with_index(self, tdir):
        config = load_config(docs_dir=tdir)
        with self.assertLogs('mkdocs') as cm:
            files = get_files(config)
        self.assertRegex(
            '\n'.join(cm.output),
            r"^WARNING:mkdocs.structure.files:"
            r"Excluding 'README.md' from the site because it conflicts with 'index.md'.$",
        )
        self.assertIsInstance(files, Files)
        self.assertEqual([f.src_uri for f in files], ['index.md', 'foo.md'])

    @tempdir()
    @tempdir(files={'test.txt': 'source content'})
    def test_copy_file(self, src_dir, dest_dir):
        file = File('test.txt', src_dir, dest_dir, use_directory_urls=False)
        dest_path = os.path.join(dest_dir, 'test.txt')
        self.assertPathNotExists(dest_path)
        file.copy_file()
        self.assertPathIsFile(dest_path)

    @tempdir(files={'test.txt': 'source content'})
    def test_copy_file_same_file(self, dest_dir):
        file = File('test.txt', dest_dir, dest_dir, use_directory_urls=False)
        dest_path = os.path.join(dest_dir, 'test.txt')
        file.copy_file()
        self.assertPathIsFile(dest_path)
        with open(dest_path, encoding='utf-8') as f:
            self.assertEqual(f.read(), 'source content')

    @tempdir(files={'test.txt': 'destination content'})
    @tempdir(files={'test.txt': 'source content'})
    def test_copy_file_clean_modified(self, src_dir, dest_dir):
        file = File('test.txt', src_dir, dest_dir, use_directory_urls=False)
        file.is_modified = mock.Mock(return_value=True)
        dest_path = os.path.join(dest_dir, 'test.txt')
        file.copy_file(dirty=False)
        self.assertPathIsFile(dest_path)
        with open(dest_path, encoding='utf-8') as f:
            self.assertEqual(f.read(), 'source content')

    @tempdir(files={'test.txt': 'destination content'})
    @tempdir(files={'test.txt': 'source content'})
    def test_copy_file_dirty_modified(self, src_dir, dest_dir):
        file = File('test.txt', src_dir, dest_dir, use_directory_urls=False)
        file.is_modified = mock.Mock(return_value=True)
        dest_path = os.path.join(dest_dir, 'test.txt')
        file.copy_file(dirty=True)
        self.assertPathIsFile(dest_path)
        with open(dest_path, encoding='utf-8') as f:
            self.assertEqual(f.read(), 'source content')

    @tempdir(files={'test.txt': 'destination content'})
    @tempdir(files={'test.txt': 'source content'})
    def test_copy_file_dirty_not_modified(self, src_dir, dest_dir):
        file = File('test.txt', src_dir, dest_dir, use_directory_urls=False)
        file.is_modified = mock.Mock(return_value=False)
        dest_path = os.path.join(dest_dir, 'test.txt')
        file.copy_file(dirty=True)
        self.assertPathIsFile(dest_path)
        with open(dest_path, encoding='utf-8') as f:
            self.assertEqual(f.read(), 'destination content')

    def test_files_append_remove_src_paths(self):
        fs = [
            File('index.md', '/path/to/docs', '/path/to/site', use_directory_urls=True),
            File('foo/bar.md', '/path/to/docs', '/path/to/site', use_directory_urls=True),
            File('foo/bar.html', '/path/to/docs', '/path/to/site', use_directory_urls=True),
            File('foo/bar.jpg', '/path/to/docs', '/path/to/site', use_directory_urls=True),
            File('foo/bar.js', '/path/to/docs', '/path/to/site', use_directory_urls=True),
            File('foo/bar.css', '/path/to/docs', '/path/to/site', use_directory_urls=True),
        ]
        files = Files(fs)
        self.assertEqual(len(files), 6)
        self.assertEqual(len(files.src_uris), 6)
        extra_file = File('extra.md', '/path/to/docs', '/path/to/site', use_directory_urls=True)
        self.assertFalse(extra_file.src_uri in files.src_uris)
        files.append(extra_file)
        self.assertEqual(len(files), 7)
        self.assertEqual(len(files.src_uris), 7)
        self.assertTrue(extra_file.src_uri in files.src_uris)
        files.remove(extra_file)
        self.assertEqual(len(files), 6)
        self.assertEqual(len(files.src_uris), 6)
        self.assertFalse(extra_file.src_uri in files.src_uris)
