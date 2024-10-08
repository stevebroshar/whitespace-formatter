better_space = python_code = __import__('better-space')
import shutil
import os
import unittest

TAB = "\t"
SPACE = " "

class FakeLogger(better_space.Logger):
    def __init__(self):
        super().__init__()
        self.entries = []

    def log(self, message):
        self.entries.append(message)

class LineConformerUnitTest(unittest.TestCase):
    def setUp(self):
        self.conformer = better_space.LineConformer()
        self.log = lambda message: message

    #
    # trim_trailing
    #

    def test_trim_trailing_removes_whitespace_from_eol(self):
        text = self.conformer.trim_trailing("  abc \t", self.log)
        self.assertEqual(text, "  abc")

    #
    # detab_line
    #

    def test_detab_line_replaces_tabs_in_line(self):
        text = self.conformer.detab_line("\ta\tb\t", self.log, 4)
        self.assertEqual(text, SPACE*4 + "a" + SPACE*3 + "b" + SPACE*3)

    def test_detab_line_adds_spaces_for_indent_that_is_space_and_tab_in_same_tab_stop(self):
        text = self.conformer.detab_line(SPACE + "\ta", self.log, 4)
        self.assertEqual(text, SPACE*4 + "a")

    def test_detab_line_adds_spaces_for_indent_that_is_tab_width_minus_one_spaces_and_tab(self):
        text = self.conformer.detab_line(SPACE*3 + "\ta", self.log, 4)
        self.assertEqual(text, SPACE*4 + "a")

    def test_detab_line_replaces_tabs_with_spaces_to_tab_stops(self):
        text = self.conformer.detab_line(" \ta  \tbc \t", self.log, 4)
        self.assertEqual(text, SPACE*4 + "a" + SPACE*3 + "bc" + SPACE*2)

    #
    # detab_leading
    #

    def test_detab_leading_leaves_non_leading_tabs(self):
        text = self.conformer.detab_leading("\ta\tb\t", self.log, 4)
        self.assertEqual(text, SPACE*4 + "a\tb\t")

    #
    # detab_code_line
    #

    def test_detab_code_replaces_all_tabs_in_line(self):
        text = self.conformer.detab_code_line("\ta\tb\t", self.log, 4)
        self.assertEqual(text, SPACE*4 + "a" + SPACE*3 + "b" + SPACE*3)

    def test_detab_code_replaces_tabs_with_spaces_to_tab_stops(self):
        text = self.conformer.detab_code_line(" \ta  \tbc \t", self.log, 4)
        self.assertEqual(text, SPACE*4 + "a" + SPACE*3 + "bc" + SPACE*2)

    # for C, C++ string and Python syntaxes
    def test_detab_code_replaces_tab_in_double_quote_string_literal_with_tab_specifier(self):
        text = self.conformer.detab_code_line('"\tXXX"', self.log, 4)
        self.assertEqual(text, r'"\tXXX"')

    # for C, C++ char and Python syntaxes
    def test_detab_code_replaces_tab_in_single_quote_string_literal_with_tab_specifier(self):
        text = self.conformer.detab_code_line("'\tXXX'", self.log, 4)
        self.assertEqual(text, r"'\tXXX'")

    # for Python syntax
    def test_deta_code_ignores_single_quote_in_double_quoted_string_literal(self):
        text = self.conformer.detab_code_line('"\'\t"', self.log, 4)
        self.assertEqual(text, '"\'\\t"')

    # for Python syntax
    def test_deta_code_ignores_double_quote_in_single_quoted_string_literal(self):
        text = self.conformer.detab_code_line("'\"\t'", self.log, 4)
        self.assertEqual(text, "'\"\\t'")

    def test_detab_code_ignores_escaped_string_delim_in_double_quote_string_literal(self):
        text = self.conformer.detab_code_line(rf'"\"{TAB}XXX"', self.log, 4)
        self.assertEqual(text, r'"\"\tXXX"')

    def test_detab_code_ignores_escaped_escape_in_double_quote_string_literal(self):
        text = self.conformer.detab_code_line(rf'"\\" "{TAB}XXX"', self.log, 4)
        self.assertEqual(text, r'"\\" "\tXXX"')

    #
    # entab_leading
    #

    def test_entab_leading_leaves_non_leading_spaces(self):
        text = self.conformer.entab_leading(4*SPACE + "a" + 5*SPACE + "b", self.log, 4)

        self.assertEqual("\ta" + 5*SPACE + "b", text)

    def test_entab_line_replaces_leading_spaces_with_tab(self):
        text = self.conformer.entab_leading(SPACE*4 + "a", self.log, 4)
        self.assertEqual(text, "\ta")

    def test_entab_line_replaces_space_and_tab_in_same_tab_stop_with_single_tab(self):
        text = self.conformer.entab_leading(SPACE + "\ta", self.log, 4)
        self.assertEqual(text, "\ta")

    def test_entab_line_replaces_max_spaces_and_tab_in_same_tab_stop_with_single_tab(self):
        text = self.conformer.entab_leading(SPACE*3 + "\ta", self.log, 4)
        self.assertEqual(text, "\ta")

    def test_entab_line_replaces_multiple_tab_stops_of_spaces_with_tabs(self):
        text = self.conformer.entab_leading(SPACE*8 + "a", self.log, 4)
        self.assertEqual(text, "\t\ta")

    def test_entab_line_replaces_multiple_tab_stops_with_mixed_space_and_tab_with_tabs(self):
        text = self.conformer.entab_leading(SPACE*3 + "\t" + SPACE*3 + "\ta", self.log, 4)
        self.assertEqual(text, "\t\ta")

    #
    # entab_line
    #

    # def test_entab_line_leaves_space_that_does_not_complete_tab_stop(self):
    #     text = self.conformer.entab_line(SPACE*5 + "a", self.log, 4)
    #     self.assertEqual(text, "\t a")

    # def test_entab_line_replaces_non_leading_tabs_based_on_tab_stops(self):
    #     text = self.conformer.entab_line("a" + SPACE*3 + "b", self.log, 4)
    #     self.assertEqual(text, "a\tb")

    # def test_entab_line_leaves_space_not_part_of_tab_stop(self):
    #     text = self.conformer.entab_line("a" + SPACE*4 + "b", self.log, 4)
    #     self.assertEqual(text, "a\t b")

    # # prevent replacing spaces with tab for code like: 'int foo' where whitespace clearly should remain space chars
    # def test_entab_line_leaves_single_space_that_completes_tab_stop(self):
    #     text = self.conformer.entab_line("abc" + SPACE + "-", self.log, 4)
    #     self.assertEqual(text, "abc" + SPACE + "-")

    # # prevent replacing spaces with tab for code like:
    # #   i   foo;
    # #   i   bar;
    # def test_entab_line_leaves_max_spaces_that_completes_tab_stop(self):
    #     text = self.conformer.entab_line("a" + SPACE*3 + "-", self.log, 4)
    #     self.assertEqual(text, "a" + SPACE*3 + "-")

    # def test_foo(self):
    #     text = self.conformer.entab_line(r'std::string s("     test	");', self.log, 4)
    #     self.assertEqual(text, 'std::string\ts("\t\ttest	");')

class FileConformerUnitTest(unittest.TestCase):
    def setUp(self):
        self.conformer = better_space.FileConformer(FakeLogger())
        self.test_file_path = "__testfile"

    def tearDown(self):
        if os.path.isfile(self.test_file_path):
            os.remove(self.test_file_path)

    def test_conform_lines_performs_operation(self):
        self.conformer.text = "a\nb\nc"

        self.conformer.conform_lines([lambda line, log : "==>" + line + "<=="])

        self.assertEqual("==>a<==\n==>b<==\n==>c<==", self.conformer.text)

    def test_conform_lines_performs_each_operation(self):
        self.conformer.text = "ab"

        self.conformer.conform_lines([lambda line, log : line.replace("a", "x"), lambda line, log : line.replace("b", "y")])

        self.assertEqual("xy", self.conformer.text)

    def test_conform_lines_preserves_empty_last_line(self):
        self.conformer.text = "a\nb\nc\n"

        self.conformer.conform_lines([lambda line, log : line.replace("b", "x")])

        self.assertEqual("a\nx\nc\n", self.conformer.text)

    def test_load_from_file_loads_text_from_file(self):
        with open(self.test_file_path, "w") as f: f.write("Abc123\nDef456\n")

        self.conformer.load_from_file(self.test_file_path, "utf-8")

        self.assertEqual("Abc123\nDef456\n", self.conformer.text)

    def test_save_to_file_saves_to_file_loaded(self):
        with open(self.test_file_path, "w") as f: f.write("Abc123")
        self.conformer.load_from_file(self.test_file_path, "utf-8")
        self.conformer.text = "Def456"

        self.conformer.save_to_file()

        with open(self.test_file_path) as f: text = f.read()
        self.assertEqual("Def456", text)

    def test_is_modified_is_false_for_unmodified_text(self):
        with open(self.test_file_path, "w") as f: f.write("Abc123")
        self.conformer.load_from_file(self.test_file_path, "utf-8")

        self.assertEqual(False, self.conformer.is_modified)

    def test_is_modified_is_true_for_modified_text(self):
        with open(self.test_file_path, "w") as f: f.write("Abc123")
        self.conformer.load_from_file(self.test_file_path, "utf-8")

        self.conformer.text = "different"

        self.assertEqual(True, self.conformer.is_modified)

class FileSelectUnitTest(unittest.TestCase):
    def setUp(self):
        self.select = better_space.FileSelect()

    def test_depth_limit_prohibits_negative_value(self):
        with self.assertRaises(better_space.AppException):
            self.select.depth_limit = -1
 
class FileProcessorUnitTest(unittest.TestCase):
    def setUp(self):
        self.processor = better_space.FileProcessor(FakeLogger())
        self.test_dir_path = "__testdir"
        self.test_file_path = self.__get_test_file_path("a")
        self.tearDown()
        os.mkdir(self.test_dir_path)

    def tearDown(self):
        if os.path.isdir(self.test_dir_path):
            shutil.rmtree(self.test_dir_path)

    def __write_binary_file(self, path):
        with open(path, "wb") as f:
            for byte in [123, 3, 255, 0, 100]:
                f.write(byte.to_bytes(1))

    def __get_test_file_path(self, file_name):
        return os.path.join(self.test_dir_path, file_name)

    def __create_file(self, path):
        with open(path, "w") as f: f.write(f"test file: {path}")

    def test_detect_encoding_returns_utf8_for_utf8_content(self):
        with open(self.test_file_path, "w", encoding="utf-8") as f: f.write("Abc123")
        self.assertEqual("utf-8", self.processor.detect_encoding_or_none(self.test_file_path))

    def test_detect_encoding_returns_utf16_for_utf16_content(self):
        with open(self.test_file_path, "w", encoding="utf-16") as f: f.write("Abc123")
        self.assertEqual("utf-16", self.processor.detect_encoding_or_none(self.test_file_path))

    def test_detect_encoding_returns_None_for_binary_content(self):
        self.__write_binary_file(self.test_file_path)
        self.assertEqual(None, self.processor.detect_encoding_or_none(self.test_file_path))

    def test_find_files_returns_empty_for_empty(self):
        file_paths = self.processor.find_files([])

        self.assertEqual(0, len(file_paths))

    def test_find_files_fails_for_no_match(self):
        self.assertRaises(better_space.AppException, self.processor.find_files, ["notthere"])

    def test_find_files_finds_file_by_name(self):
        self.__create_file(self.test_file_path)
        
        file_paths = self.processor.find_files([self.test_file_path])

        self.assertEqual({self.test_file_path: "utf-8"}, file_paths)

    def test_find_files_finds_files_by_pattern(self):
        file_path_a = self.__get_test_file_path("a.c")
        file_path_b = self.__get_test_file_path("a.h")
        self.__create_file(file_path_a)
        self.__create_file(file_path_b)
        
        file_paths = self.processor.find_files([self.__get_test_file_path("a.*")])

        self.assertCountEqual([file_path_a, file_path_b], file_paths)

    def test_find_files_finds_files_in_dir(self):
        file_path_a = self.__get_test_file_path("a.c")
        file_path_b = self.__get_test_file_path("a.h")
        self.__create_file(file_path_a)
        self.__create_file(file_path_b)
        
        file_paths = self.processor.find_files([self.test_dir_path])

        self.assertCountEqual([file_path_a, file_path_b], file_paths)

    def test_find_files_filters_dir_files(self):
        file_path_a = self.__get_test_file_path("a.c")
        file_path_b = self.__get_test_file_path("a.h")
        self.__create_file(file_path_a)
        self.__create_file(file_path_b)
        file_select = better_space.FileSelect()
        file_select.match_patterns = ["*.c"]

        file_paths = self.processor.find_files([self.test_dir_path], file_select)

        self.assertCountEqual([file_path_a], file_paths)

    def test_find_files_does_not_have_duplicates_for_overlapping_matching_patterns(self):
        file_path_a = self.__get_test_file_path("a.c")
        file_path_b = self.__get_test_file_path("a.h")
        self.__create_file(file_path_a)
        self.__create_file(file_path_b)
        file_select = better_space.FileSelect()
        file_select.match_patterns = ["*.c", "a.*"]
        
        file_paths = self.processor.find_files([self.test_dir_path], file_select)

        self.assertCountEqual([file_path_a, file_path_b], file_paths)

    def test_find_files_fails_for_binary_file(self):
        self.__write_binary_file(self.test_file_path)
        
        self.assertRaises(better_space.AppException, self.processor.find_files, [self.test_file_path])

    def test_find_files_does_not_match_binary_file(self):
        self.__write_binary_file(self.test_file_path)
    
        file_paths = self.processor.find_files([self.test_dir_path])

        self.assertCountEqual([], file_paths)

    def test_find_files_selects_files_in_subdirectory(self):
        root_dir_file_path = self.__get_test_file_path("a")
        child_dir_path = self.__get_test_file_path("child-dir")
        child_dir_file_path = os.path.join(child_dir_path, "child-dir-file")
        self.__create_file(root_dir_file_path)
        os.mkdir(child_dir_path)
        self.__create_file(child_dir_file_path)
        
        file_paths = self.processor.find_files([self.test_dir_path])

        self.assertCountEqual([root_dir_file_path, child_dir_file_path], file_paths)

    def test_find_files_selects_subdirectory_files_via_matching(self):
        child_dir_path = self.__get_test_file_path("child-dir")
        child_dir_file_path = os.path.join(child_dir_path, "child-dir-file.ext")
        os.mkdir(child_dir_path)
        self.__create_file(child_dir_file_path)
        self.__create_file(child_dir_file_path + ".a")
        self.__create_file(child_dir_file_path + ".b")
        file_select = better_space.FileSelect()
        file_select.match_patterns = ["*.ext"]
        
        file_paths = self.processor.find_files([self.test_dir_path], file_select)

        self.assertCountEqual([child_dir_file_path], file_paths)

    def test_find_files_recurses_multiple_subdirectory_levels(self):
        root_file_path = self.__get_test_file_path("root-file")
        child_dir_path = self.__get_test_file_path("child-dir")
        child_dir_file_path = os.path.join(child_dir_path, "child-dir-file")
        grandchild_dir_path = os.path.join(child_dir_path, "grandchild-dir")
        grandchild_dir_file_path = os.path.join(grandchild_dir_path, "grand-file")
        os.makedirs(grandchild_dir_path)
        self.__create_file(root_file_path)
        self.__create_file(child_dir_file_path)
        self.__create_file(grandchild_dir_file_path)
        
        file_paths = self.processor.find_files([self.test_dir_path])

        self.assertCountEqual([root_file_path, child_dir_file_path, grandchild_dir_file_path], file_paths)

    def test_find_files_selects_only_root_files_for_depth_limit_0(self):
        root_file_path = self.__get_test_file_path("root-file")
        child_dir_path = self.__get_test_file_path("child-dir")
        child_dir_file_path = os.path.join(child_dir_path, "child-dir-file")
        grandchild_dir_path = os.path.join(child_dir_path, "grandchild-dir")
        grandchild_dir_file_path = os.path.join(grandchild_dir_path, "grand-file")
        os.makedirs(grandchild_dir_path)
        self.__create_file(root_file_path)
        self.__create_file(child_dir_file_path)
        self.__create_file(grandchild_dir_file_path)
        file_select = better_space.FileSelect()
        file_select.depth_limit = 0
        
        file_paths = self.processor.find_files([self.test_dir_path], file_select)

        self.assertCountEqual([root_file_path], file_paths)

    def test_find_files_selects_root_and_child_files_for_depth_limit_1(self):
        root_file_path = self.__get_test_file_path("root-file")
        child_dir_path = self.__get_test_file_path("child-dir")
        child_dir_file_path = os.path.join(child_dir_path, "child-dir-file")
        grandchild_dir_path = os.path.join(child_dir_path, "grandchild-dir")
        grandchild_dir_file_path = os.path.join(grandchild_dir_path, "grand-file")
        os.makedirs(grandchild_dir_path)
        self.__create_file(root_file_path)
        self.__create_file(child_dir_file_path)
        self.__create_file(grandchild_dir_file_path)
        file_select = better_space.FileSelect()
        file_select.depth_limit = 1
        
        file_paths = self.processor.find_files([self.test_dir_path], file_select)

        self.assertCountEqual([root_file_path, child_dir_file_path], file_paths)

if __name__ == '__main__':
    unittest.main()