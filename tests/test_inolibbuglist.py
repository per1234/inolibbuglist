# must specify UTF-8 encoding due to the non-ASCII characters in the ArduinoJSON description
# encoding: utf-8
# for making custom command line arguments work in conjunction with the unittest module
import sys
# for unit testing
import unittest

# add the parent folder to the module search path
# https://stackoverflow.com/a/20371877
import os

testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
from inolibbuglist import *  # nopep8

# parse command line arguments
argument_parser = argparse.ArgumentParser()
argument_parser.add_argument("--github_login",
                             dest="github_login",
                             help="GitHub login",
                             metavar="LOGIN"
                             )
argument_parser.add_argument("--ghtoken",
                             dest="github_token",
                             help="GitHub personal access token",
                             metavar="TOKEN"
                             )
argument_parser.add_argument("--git_command",
                             dest="git_command",
                             default=default_git_command,
                             help="Git command",
                             metavar="COMMAND"
                             )
argument_parser.add_argument("--bash_command",
                             dest="bash_command",
                             default=default_bash_command,
                             help="Command to run bash",
                             metavar="COMMAND"
                             )
argument_parser.add_argument("--browser_command",
                             dest="browser_command",
                             help="Path of your web browser",
                             metavar="COMMAND"
                             )
argument_parser.add_argument("--arduino_ci_script_branch",
                             dest="arduino_ci_script_branch",
                             default=default_arduino_ci_script_branch,
                             help="Branch of the arduino-ci-script repository to use (defaults to default branch)",
                             metavar="BRANCH"
                             )
argument_parser.add_argument("--arduino_ci_script_application_folder",
                             dest="arduino_ci_script_application_folder",
                             help="Folder to install the Arduino IDE under (or use existing installations)",
                             metavar="PATH"
                             )
argument_parser.add_argument("--arduino_ci_script_arduino_ide_version",
                             dest="arduino_ci_script_arduino_ide_version",
                             default=default_arduino_ci_script_arduino_ide_version,
                             help="Arduino IDE version to use for the check_keywords_txt() reference link checks",
                             metavar="VERSION"
                             )
argument_parser.add_argument("--verbose",
                             dest="enable_verbosity",
                             help="Enable verbose output",
                             action="store_true"
                             )

# this is needed to use command line arguments in conjunction with the unittest module
# (it uses its own command line arguments).
# https://stackoverflow.com/a/44255084/7059512
# alternative solution: https://stackoverflow.com/a/44248445/7059512
argument_parser.add_argument('unittest_args', nargs='*')
argument = argument_parser.parse_args()
sys.argv[1:] = argument.unittest_args


class TestInolibbuglist(unittest.TestCase):
    # NOTE: the tests are run in order sorted by method name, not in the order below

    # Turn typo checks on so the typo check tool will be installed by install_tools()
    set_check_for_typos(check_for_typos_input=True)
    # Must set the branch before calling install_tools() so that the correct branch is cloned
    set_arduino_ci_script_branch(arduino_ci_script_branch_input=argument.arduino_ci_script_branch)
    # only install tools once to make the unit tests faster
    install_tools()

    if argument.enable_verbosity:
        inoliblist.set_verbosity(enable_verbosity_input=True)

    def setUp(self):
        inoliblist.set_github_token(github_token_input=argument.github_token)
        set_github_login(github_login_input=argument.github_login)
        set_git_command(argument.git_command)
        set_bash_command(bash_command_input=argument.bash_command)
        set_arduino_ci_script_arduino_ide_version(
            arduino_ci_script_arduino_ide_version_input=argument.arduino_ci_script_arduino_ide_version
        )
        set_arduino_ci_script_application_folder(
            arduino_ci_script_application_folder_input=argument.arduino_ci_script_application_folder
        )
        set_browser_command(browser_command_input=argument.browser_command)

        set_check_for_typos(check_for_typos_input=True)

        clean_folder(output_folder_name)
        clean_folder(work_folder_name)

    # @unittest.skip("")
    def test_clean_folder(self):
        clean_folder(output_folder_name)
        # folder exists
        self.assertTrue(os.path.exists(output_folder_name))
        # folder is empty
        self.assertFalse(os.listdir(output_folder_name))

    # @unittest.skip("")
    def test_process_verification_failed_list_missing_input_file(self):
        process_verification_failed_list(verification_failed_list_path="verification_failed_list_doesnt_exist.csv")
        # folder is empty
        self.assertFalse(os.listdir(output_folder_name))

    # @unittest.skip("")
    def test_process_verification_failed_list(self):
        process_verification_failed_list(
            verification_failed_list_path="tests/" + input_folder_name + "/" + "verification_failed_list.csv")
        with open(file=output_folder_name + "/" + inoliblist.verification_failed_list_filename,
                  mode='r',
                  encoding=inoliblist.file_encoding,
                  newline=inoliblist.file_newline
                  ) as verification_failed_output:
            verification_failed_output_lines = verification_failed_output.readlines()
            self.assertEqual(len(verification_failed_output_lines), 2)
            self.assertEqual(verification_failed_output_lines[0],
                             "Repository" + inoliblist.output_file_delimiter + "Open PR\n")
            self.assertEqual(verification_failed_output_lines[1],
                             "https://github.com/per1234/MouseTo" + inoliblist.output_file_delimiter + "False\n")

    # @unittest.skip("")
    def test_process_verification_failed_list_blacklisted_repo(self):
        process_verification_failed_list(verification_failed_list_path="tests/" +
                                                                       input_folder_name + "/" +
                                                                       "verification_failed_list_blacklisted_repo.csv")
        with open(file=output_folder_name + "/" + inoliblist.verification_failed_list_filename,
                  mode='r',
                  encoding=inoliblist.file_encoding,
                  newline=inoliblist.file_newline
                  ) as verification_failed_output:
            for verification_failed_output_line in verification_failed_output:
                # create_output_file() should not write a line for the blacklisted repo
                self.assertEqual(verification_failed_output_line,
                                 "Repository" + inoliblist.output_file_delimiter + "Open PR\n")

    # @unittest.skip("")
    def test_process_verification_failed_list_open_pr(self):
        process_verification_failed_list(
            verification_failed_list_path="tests/" + input_folder_name + "/" + "verification_failed_list_open_pr.csv")
        with open(file=output_folder_name + "/" + inoliblist.verification_failed_list_filename,
                  mode='r',
                  encoding=inoliblist.file_encoding,
                  newline=inoliblist.file_newline
                  ) as verification_failed_output:
            verification_failed_output_lines = verification_failed_output.readlines()
            self.assertEqual(len(verification_failed_output_lines), 2)
            self.assertEqual(verification_failed_output_lines[0],
                             "Repository" + inoliblist.output_file_delimiter + "Open PR\n")
            self.assertEqual(verification_failed_output_lines[1],
                             "https://github.com/spapadim/XPT2046" + inoliblist.output_file_delimiter + "True\n")

    # @unittest.skip("")
    def test_write_to_verification_failed_output_file(self):
        write_to_verification_failed_output_file("foobar")
        with open(file=output_folder_name + "/" + inoliblist.verification_failed_list_filename,
                  mode='r',
                  encoding=inoliblist.file_encoding,
                  newline=inoliblist.file_newline
                  ) as verification_failed_output:
            for verification_failed_output_line in verification_failed_output:
                self.assertEqual(verification_failed_output_line, "foobar")

    # @unittest.skip("")
    def test_process_inoliblist_archived(self):
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_archived.csv")
        # The rest of the processing for this row should have been skipped for the archived repository
        self.assertEqual(get_table()[1][Column.arduino_library_topic_abuse], "")
        # Processing should have continued for the non-archived repository
        self.assertEqual(get_table()[2][Column.arduino_library_topic_abuse], "True")

    # @unittest.skip("")
    def test_process_inoliblist_arduino_library_topic_abuse(self):
        process_inoliblist(
            inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_arduino_library_topic_abuse.csv")
        # Uses arduino-library topic but a library was not found by inoliblist
        self.assertEqual(get_table()[1][Column.arduino_library_topic_abuse], "True")
        self.assertEqual(get_table()[2][Column.arduino_library_topic_abuse], "True")
        # Uses arduino-library topic but a library was found by inoliblist
        self.assertEqual(get_table()[3][Column.arduino_library_topic_abuse], "False")
        # A library was not found by inoliblist but it doesn't use the arduino-library topic
        self.assertEqual(get_table()[4][Column.arduino_library_topic_abuse], "False")
        self.assertEqual(get_table()[5][Column.arduino_library_topic_abuse], "False")

    # @unittest.skip("")
    def test_process_inoliblist_i_have_open_issue(self):
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_i_have_open_issue.csv")
        # arduino-library topic abuse and an open issue from me
        self.assertEqual(get_table()[1][Column.i_have_open_issue], "True")
        # arduino-library topic abuse and no open issue from me
        self.assertEqual(get_table()[2][Column.i_have_open_issue], "False")
        # No arduino-library topic abuse and an open issue from me
        self.assertEqual(get_table()[3][Column.i_have_open_issue], "")

    # @unittest.skip("")
    def test_process_inoliblist_blacklist(self):
        # Skip the rest of the processing after open PR found to make the unit test run faster
        set_process_repos_with_open_pr(False)
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_blacklist.csv")
        self.assertEqual(get_table()[1][Column.blacklist], "True")
        # The rest of the processing for this row should have been skipped for the blacklisted repository
        self.assertEqual(get_table()[1][Column.i_have_open_pull_request], "")
        # The rest of the processing for this row should not have been skipped for the non-blacklisted repository
        self.assertEqual(get_table()[2][Column.blacklist], "False")
        self.assertEqual(get_table()[2][Column.i_have_open_pull_request], "True")

    # @unittest.skip("")
    def test_process_inoliblist_i_have_open_pull_request_process_repos_with_open_pr_true(self):
        set_process_repos_with_open_pr(True)
        process_inoliblist(
            inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_i_have_open_pull_request.csv")
        self.assertEqual(get_table()[1][Column.i_have_open_pull_request], "True")
        # The rest of the processing for this row should not have been skipped for the repository with an open PR
        self.assertEqual(get_table()[1][Column.cant_find], "True")
        # The column value should be False for a repo with no open PR
        self.assertEqual(get_table()[2][Column.i_have_open_pull_request], "False")
        self.assertEqual(get_table()[2][Column.cant_find], "True")

    # @unittest.skip("")
    def test_process_inoliblist_i_have_open_pull_request_process_repos_with_open_pr_false(self):
        set_process_repos_with_open_pr(False)
        process_inoliblist(
            inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_i_have_open_pull_request.csv")
        self.assertEqual(get_table()[1][Column.i_have_open_pull_request], "True")
        # The rest of the processing for this row should have been skipped for the repository with an open PR
        self.assertEqual(get_table()[1][Column.cant_find], "")
        # The column value should be False for a repo with no open PR
        self.assertEqual(get_table()[2][Column.i_have_open_pull_request], "False")
        # The rest of the processing for this row should not have been skipped for the repository with no open PR
        self.assertEqual(get_table()[2][Column.cant_find], "True")

    # @unittest.skip("")
    def test_process_inoliblist_i_am_contributor(self):
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_i_am_contributor.csv")
        self.assertEqual(get_table()[1][Column.i_am_contributor], "True")
        self.assertEqual(get_table()[2][Column.i_am_contributor], "False")

    # @unittest.skip("")
    def test_process_inoliblist_cant_find(self):
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_cant_find.csv")
        self.assertEqual(get_table()[1][Column.cant_find], "True")
        self.assertEqual(get_table()[2][Column.cant_find], "False")

    # @unittest.skip("")
    def test_process_inoliblist_status_failure(self):
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_status_failure.csv")
        # Test inoliblist has "failure" in the tip_status column
        self.assertEqual(get_table()[1][Column.status_failure], "True")
        # Test inoliblist doesn't have "failure" in the tip_status column
        self.assertEqual(get_table()[2][Column.status_failure], "False")

    # @unittest.skip("")
    def test_process_inoliblist_not_in_root(self):
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_not_in_root.csv")
        # Test inoliblist must have something other than / in the library_path column
        self.assertEqual(get_table()[1][Column.not_in_root], "True")
        # Test inoliblist must have / in the library_path column
        self.assertEqual(get_table()[2][Column.not_in_root], "False")

    # @unittest.skip("")
    def test_process_inoliblist_license_unrecognized(self):
        # Test inoliblist must have "unrecognized" in the repository_license column
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_license_unrecognized.csv")
        self.assertEqual(get_table()[1][Column.license_unrecognized], "True")
        self.assertEqual(get_table()[2][Column.license_unrecognized], "False")

    # @unittest.skip("")
    def test_process_inoliblist_typo_check_for_typos_true(self):
        set_check_for_typos(check_for_typos_input=True)
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_typo.csv")
        self.assertEqual(get_table()[1][Column.typo], "True")
        self.assertEqual(get_table()[2][Column.typo], "False")

    # @unittest.skip("")
    def test_process_inoliblist_typo_check_for_typos_false(self):
        set_check_for_typos(check_for_typos_input=False)
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_typo.csv")
        self.assertEqual(get_table()[1][Column.typo], "")
        self.assertEqual(get_table()[2][Column.typo], "")

    # @unittest.skip("")
    def test_process_inoliblist_check_library_structure(self):
        process_inoliblist(
            inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_check_library_structure.csv")
        self.assertEqual(get_table()[1][Column.library_folder_doesnt_exist], "True")
        self.assertEqual(get_table()[2][Column.library_folder_doesnt_exist], "")
        # check_library_structure() should not be run on repos where the library folder is not known
        self.assertEqual(get_table()[3][Column.library_folder_doesnt_exist], "")

    # @unittest.skip("")
    def test_process_inoliblist_check_library_properties(self):
        process_inoliblist(
            inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_check_library_properties.csv")
        self.assertEqual(get_table()[1][Column.library_properties_folder_doesnt_exist], "True")
        self.assertEqual(get_table()[2][Column.library_properties_folder_doesnt_exist], "")
        # check_library_properties() should not be run on repos where the library folder is not known
        self.assertEqual(get_table()[3][Column.library_properties_folder_doesnt_exist], "")

    # @unittest.skip("")
    def test_process_inoliblist_check_keywords_txt(self):
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_check_keywords_txt.csv")
        self.assertEqual(get_table()[1][Column.keywords_txt_folder_doesnt_exist], "True")
        self.assertEqual(get_table()[2][Column.keywords_txt_folder_doesnt_exist], "")
        # check_keywords_txt() should not be run on repos where the library folder is not known
        self.assertEqual(get_table()[3][Column.keywords_txt_folder_doesnt_exist], "")

    # @unittest.skip("")
    def test_process_inoliblist_lm_but_not_in_root(self):
        # Test inoliblist must have "unrecognized" in the repository_license column
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_lm_but_not_in_root.csv")
        # Library is not in the repository root folder
        self.assertEqual(get_table()[1][Column.lm_but_not_in_root], "True")
        # Library is in the repository root folder
        self.assertEqual(get_table()[2][Column.lm_but_not_in_root], "False")
        # Not in library Manager index so the check is skipped
        self.assertEqual(get_table()[3][Column.lm_but_not_in_root], "")

    @unittest.skip("arduino-ci-script development branch must be merged to master before this will pass")
    def test_process_inoliblist_check_library_manager_compliance(self):
        process_inoliblist(
            inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_check_library_manager_compliance.csv")
        # Repository contains a .exe file
        self.assertEqual(get_table()[1][Column.exe_found], "True")
        # Repository doesn't contain a .exe file (the arduino-ci-script checks don't write False)
        self.assertEqual(get_table()[2][Column.exe_found], "")

    # @unittest.skip("")
    def test_install_tools(self):
        install_tools()
        # arduino-ci-script folder exists
        self.assertTrue(os.path.exists(arduino_ci_script_folder))
        # folder is not empty
        self.assertTrue(os.listdir(arduino_ci_script_folder))

    # @unittest.skip("")
    def test_check_for_open_pr_no_open_pr(self):
        self.assertFalse(check_for_open_pr(repository_full_name="per1234/MouseTo"))

    # @unittest.skip("")
    def test_check_for_open_pr_open_pr(self):
        self.assertTrue(check_for_open_pr(repository_full_name="spapadim/XPT2046"))

    # @unittest.skip("")
    def test_create_inolibbuglist_output_file(self):
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_archived.csv")
        create_inolibbuglist_output_file()
        self.assertTrue(os.path.isfile(output_folder_name + "/" + inolibbuglist_filename))

    # @unittest.skip("")
    def test_determine_repository_full_name(self):
        self.assertEqual(determine_repository_full_name(repository_url="https://github.com/per1234/MouseTo"),
                         "per1234/MouseTo")

    # @unittest.skip("")
    def test_determine_repository_owner(self):
        self.assertEqual(determine_repository_owner(repository_url="https://github.com/per1234/MouseTo"), "per1234")

    # @unittest.skip("")
    def test_create_open_in_tabs_scripts(self):
        process_verification_failed_list(
            verification_failed_list_path="tests/" + input_folder_name + "/" + "verification_failed_list.csv")
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_archived.csv")
        create_inolibbuglist_output_file()
        create_open_in_tabs_scripts()
        with open(
                file=(
                        output_folder_name + "/" +
                        verification_failed_browser_script_filename + '1' +
                        browser_script_extension
                ),
                mode='r',
                encoding=inoliblist.file_encoding,
                newline=inoliblist.file_newline
        ) as verification_failed_browser_script:
            for verification_failed_browser_script_line in verification_failed_browser_script:
                self.assertEqual(verification_failed_browser_script_line,
                                 "\"/c/Program Files/Mozilla Firefox/firefox.exe\""
                                 " -new-tab https://github.com/per1234/MouseTo\n")
        with open(file=output_folder_name + "/arduino_library_topic_abuse1.sh",
                  mode='r',
                  encoding=inoliblist.file_encoding,
                  newline=inoliblist.file_newline
                  ) as arduino_library_topic_abuse_browser_script:
            for arduino_library_topic_abuse_browser_script_line in arduino_library_topic_abuse_browser_script:
                self.assertEqual(arduino_library_topic_abuse_browser_script_line,
                                 "\"/c/Program Files/Mozilla Firefox/firefox.exe\""
                                 " -new-tab https://github.com/spapadim/XPT2046\n")

    # @unittest.skip("")
    def test_create_open_in_tabs_script(self):
        process_inoliblist(inoliblist_path="tests/" + input_folder_name + "/" + "inoliblist_archived.csv")
        create_inolibbuglist_output_file()
        create_open_in_tabs_script(input_filename=inolibbuglist_filename,
                                   url_column=inoliblist.Column.repository_url,
                                   inclusion_columns=[Column.arduino_library_topic_abuse],
                                   exclusion_columns=[Column.i_have_open_issue]
                                   )
        with open(file=output_folder_name + "/arduino_library_topic_abuse1.sh",
                  mode='r',
                  encoding=inoliblist.file_encoding,
                  newline=inoliblist.file_newline
                  ) as arduino_library_topic_abuse_browser_script:
            for arduino_library_topic_abuse_browser_script_line in arduino_library_topic_abuse_browser_script:
                self.assertEqual(arduino_library_topic_abuse_browser_script_line,
                                 "\"/c/Program Files/Mozilla Firefox/firefox.exe\" "
                                 "-new-tab https://github.com/spapadim/XPT2046\n"
                                 )

    # @unittest.skip("")
    def test_check_blacklist(self):
        # Owner blacklist
        self.assertTrue(check_blacklist(repository_url="https://github.com/eaconner/foobar"))
        # Repository blacklist
        self.assertTrue(check_blacklist(repository_url="https://github.com/per1234/inoliblist"))
        # Not blacklisted
        self.assertFalse(check_blacklist(repository_url="https://github.com/per1234/MouseTo"))

    # @unittest.skip("")
    def test_run_bash_command(self):
        self.assertEqual(
            run_bash_command(
                commandline=(
                        shlex.quote(arduino_ci_script_wrapper_path) + ' ' +
                        shlex.quote(arduino_ci_script_path) + ' ' +
                        shlex.quote(arduino_ci_script_application_folder) + ' ' +
                        arduino_ci_script_arduino_ide_version
                )
            ),
            bash_script_success_exit_status
        )

    # @unittest.skip("")
    def test_arduino_ci_script_wrapper_handler(self):
        self.assertEqual(
            arduino_ci_script_wrapper_handler(
                function_name="set_application_folder",
                function_parameters="argument.arduino_ci_script_application_folder"
            ),
            bash_script_success_exit_status
        )

    # @unittest.skip("")
    def test_arduino_ci_script_handler(self):
        test_arduino_ci_script_handler_row_list = [""] * Column.count
        # Run check_library_structure on a non-existent path
        arduino_ci_script_handler(function_name="check_library_structure", function_parameters="foobar/",
                                  row_list=test_arduino_ci_script_handler_row_list)
        self.assertEqual(test_arduino_ci_script_handler_row_list[Column.library_folder_doesnt_exist], "True")

    # @unittest.skip("I haven't figured how to do a unit test for subprocess_run() yet")
    # def test_subprocess_run(self):
    #     self.assertEqual(subprocess_run(command="cd", arguments="."), 0)

    # @unittest.skip("")
    def test_quote_path(self):
        if platform.system() == "Windows":
            self.assertEqual(quote_path(path="C:\\Program Files (x86)"), "\"C:\\Program Files (x86)\"")
            self.assertEqual(quote_path(path="\"C:\\Program Files (x86)\""), "\"C:\\Program Files (x86)\"")
        else:
            self.assertEqual(quote_path(path="/foo bar"), "'/foo bar'")


if __name__ == '__main__':
    unittest.main()
