import argparse
import csv
import os
import platform
import shlex
import shutil
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile

# https://github.com/per1234/inoliblist
sys.path.append('../inoliblist/')
import inoliblist  # nopep8

process_repos_with_open_pr_default = False
check_for_typos_default = False

# for data files such as the blacklists
data_folder_name = "data"
# files produced by inoliblist
input_folder_name = "input"
# files produced by inolibbuglist
output_folder_name = "output"
# repos will be cloned to this folder for the arduino-ci-script checks
work_folder_name = "work"
tools_folder_name = "tools"
scripts_folder_name = "scripts"
inoliblist_input_folder_name = input_folder_name + "/inoliblist"
inoliblist_csv_download_url = "https://per1234.github.io/inoliblist/" + inoliblist.output_filename
default_inoliblist_path = inoliblist_input_folder_name + '/' + inoliblist.output_filename
arduino_ci_script_clone_url = "https://github.com/per1234/arduino-ci-script.git"
default_arduino_ci_script_branch = "master"
arduino_ci_script_folder = tools_folder_name + "/arduino-ci-script"
arduino_ci_script_path = arduino_ci_script_folder + "/arduino-ci-script.sh"
arduino_ci_script_wrapper_path = scripts_folder_name + "/arduino-ci-script-wrapper.sh"
bash_function_wrapper_script_path = scripts_folder_name + "/function-wrapper.sh"

default_arduino_ci_script_arduino_ide_version = "1.8.6"

browser_script_extension = ".sh"
verification_failed_browser_script_filename = "verification_failed_browser_script"
owner_blacklist_filename = "owner_blacklist.csv"
repository_blacklist_filename = "repository_blacklist.csv"
inolibbuglist_filename = "inolibbuglist.csv"

default_bash_command = "bash"
# create scripts that open a maximum of this many browser tabs at a time to avoid slowing/crashing the browser
maximum_browser_tabs = 35

default_git_command = "git"

# (s) delay between deleting and creating folders
create_folder_delay = 1


class Column:
    column_counter = inoliblist.Column.count
    # This column has specialized code in create_open_in_tabs_scripts()
    arduino_library_topic_abuse = column_counter
    column_counter += 1
    i_have_open_issue = column_counter
    column_counter += 1
    blacklist = column_counter
    column_counter += 1
    i_have_open_pull_request = column_counter
    column_counter += 1
    i_am_contributor = column_counter
    column_counter += 1
    # Used to identify the start column for create_open_in_tabs_scripts()
    start_of_normal_bugs = column_counter
    cant_find = column_counter
    column_counter += 1
    status_failure = column_counter
    column_counter += 1
    not_in_root = column_counter
    column_counter += 1
    license_unrecognized = column_counter
    column_counter += 1
    typo = column_counter
    column_counter += 1
    # start check_library_structure
    incorrect_extras_folder_name = column_counter
    column_counter += 1
    incorrect_examples_folder_name = column_counter
    column_counter += 1
    stray_library_properties = column_counter
    column_counter += 1
    stray_keywords_txt = column_counter
    column_counter += 1
    stray_sketch = column_counter
    column_counter += 1
    spurious_dot_folder = column_counter
    column_counter += 1
    # this should never occur
    library_folder_doesnt_exist = column_counter
    column_counter += 1
    incorrect_src_folder_case = column_counter
    column_counter += 1
    library_not_found = column_counter
    column_counter += 1
    folder_name_has_invalid_first_character = column_counter
    column_counter += 1
    folder_name_has_invalid_character = column_counter
    column_counter += 1
    folder_name_too_long = column_counter
    column_counter += 1
    src_and_utility_folders = column_counter
    column_counter += 1
    # this should never occur
    sketch_folder_doesnt_exist = column_counter
    column_counter += 1
    incorrect_sketch_extension_case = column_counter
    column_counter += 1
    multiple_sketches = column_counter
    column_counter += 1
    sketch_name_mismatch = column_counter
    column_counter += 1
    sketch_folder_name_has_invalid_first_character = column_counter
    column_counter += 1
    sketch_folder_name_has_invalid_character = column_counter
    column_counter += 1
    sketch_folder_name_too_long = column_counter
    column_counter += 1
    # start check_library_properties
    redundant_paragraph = column_counter
    column_counter += 1
    blank_name = column_counter
    column_counter += 1
    invalid_architecture = column_counter
    column_counter += 1
    architectures_misspelled = column_counter
    column_counter += 1
    architectures_empty = column_counter
    column_counter += 1
    library_properties_folder_doesnt_exist = column_counter
    column_counter += 1
    library_properties_misspelled_filename = column_counter
    column_counter += 1
    library_properties_incorrect_filename_case = column_counter
    column_counter += 1
    missing_name = column_counter
    column_counter += 1
    missing_version = column_counter
    column_counter += 1
    missing_author = column_counter
    column_counter += 1
    missing_maintainer = column_counter
    column_counter += 1
    missing_sentence = column_counter
    column_counter += 1
    missing_paragraph = column_counter
    column_counter += 1
    missing_category = column_counter
    column_counter += 1
    missing_url = column_counter
    column_counter += 1
    library_properties_invalid_line = column_counter
    column_counter += 1
    invalid_version = column_counter
    column_counter += 1
    invalid_category = column_counter
    column_counter += 1
    url_blank = column_counter
    column_counter += 1
    url_missing_scheme = column_counter
    column_counter += 1
    dead_url = column_counter
    column_counter += 1
    includes_misspelled = column_counter
    column_counter += 1
    dot_a_linkage_misspelled = column_counter
    column_counter += 1
    precompiled_misspelled = column_counter
    column_counter += 1
    ldflags_misspelled = column_counter
    column_counter += 1
    empty_includes = column_counter
    column_counter += 1
    # start check_keywords_txt
    inconsequential_multiple_tabs = column_counter
    column_counter += 1
    keywords_txt_invalid_line = column_counter
    column_counter += 1
    inconsequential_leading_space_on_keyword_tokentype = column_counter
    column_counter += 1
    multiple_tabs = column_counter
    column_counter += 1
    leading_space_on_keyword_tokentype = column_counter
    column_counter += 1
    # this should never occur
    keywords_txt_folder_doesnt_exist = column_counter
    column_counter += 1
    keywords_txt_misspelled_filename = column_counter
    column_counter += 1
    keywords_txt_incorrect_filename_case = column_counter
    column_counter += 1
    invalid_field_separator = column_counter
    column_counter += 1
    bom_corrupted_keyword = column_counter
    column_counter += 1
    invalid_keyword = column_counter
    column_counter += 1
    invalid_keyword_tokentype = column_counter
    column_counter += 1
    leading_space_on_rsyntaxtextarea_tokentype = column_counter
    column_counter += 1
    invalid_rsyntaxtextarea_tokentype = column_counter
    column_counter += 1
    invalid_reference_link = column_counter
    column_counter += 1
    reference_link_incorrect_case = column_counter
    column_counter += 1
    # start check_library_manager_compliance
    # this is not part of check_library_manager_compliance but it is only relevant to Library Manager index libraries
    lm_but_not_in_root = column_counter
    column_counter += 1
    # this should never occur
    check_library_manager_compliance_folder_doesnt_exist = column_counter
    column_counter += 1
    exe_found = column_counter
    column_counter += 1
    dot_development_found = column_counter
    column_counter += 1
    symlink_found = column_counter
    column_counter += 1
    name_has_invalid_first_character = column_counter
    column_counter += 1
    name_has_invalid_character = column_counter
    column_counter += 1
    name_too_long = column_counter
    column_counter += 1
    # not yet implemented
    incorrect_include_syntax = column_counter
    column_counter += 1
    # not yet implemented
    arduino_h_case = column_counter
    column_counter += 1
    count = column_counter


# Globals
table = [[""] * Column.count]
github_login = ""
git_command = default_git_command
bash_command = default_bash_command
arduino_ci_script_branch = default_arduino_ci_script_branch
arduino_ci_script_arduino_ide_version = default_arduino_ci_script_arduino_ide_version
arduino_ci_script_application_folder = ""
browser_command = ""
process_repos_with_open_pr = process_repos_with_open_pr_default
check_for_typos = check_for_typos_default

bash_script_success_exit_status = 0
arduino_ci_script_exit_statuses = {
    "check_library_structure": {
        1: Column.incorrect_extras_folder_name,
        2: Column.incorrect_examples_folder_name,
        3: Column.stray_library_properties,
        4: Column.stray_keywords_txt,
        5: Column.stray_sketch,
        6: Column.spurious_dot_folder,
        7: Column.library_folder_doesnt_exist,
        8: Column.incorrect_src_folder_case,
        9: Column.library_not_found,
        10: Column.folder_name_has_invalid_first_character,
        11: Column.folder_name_has_invalid_character,
        12: Column.folder_name_too_long,
        13: Column.src_and_utility_folders,
        14: Column.sketch_folder_doesnt_exist,
        15: Column.incorrect_sketch_extension_case,
        16: Column.multiple_sketches,
        17: Column.sketch_name_mismatch,
        18: Column.sketch_folder_name_has_invalid_first_character,
        19: Column.sketch_folder_name_has_invalid_character,
        20: Column.sketch_folder_name_too_long
    },
    "check_library_properties": {
        1: Column.redundant_paragraph,
        2: Column.blank_name,
        3: Column.invalid_architecture,
        4: Column.architectures_misspelled,
        5: Column.architectures_empty,
        6: Column.library_properties_folder_doesnt_exist,
        7: Column.library_properties_misspelled_filename,
        8: Column.library_properties_incorrect_filename_case,
        9: Column.missing_name,
        10: Column.missing_version,
        11: Column.missing_author,
        12: Column.missing_maintainer,
        13: Column.missing_sentence,
        14: Column.missing_paragraph,
        15: Column.missing_category,
        16: Column.missing_url,
        17: Column.library_properties_invalid_line,
        18: Column.invalid_version,
        19: Column.invalid_category,
        20: Column.url_blank,
        21: Column.url_missing_scheme,
        22: Column.dead_url,
        23: Column.includes_misspelled,
        24: Column.dot_a_linkage_misspelled,
        25: Column.precompiled_misspelled,
        26: Column.ldflags_misspelled,
        27: Column.empty_includes
    },
    "check_keywords_txt": {
        1: Column.inconsequential_multiple_tabs,
        2: Column.keywords_txt_invalid_line,
        3: Column.inconsequential_leading_space_on_keyword_tokentype,
        4: Column.multiple_tabs,
        5: Column.leading_space_on_keyword_tokentype,
        6: Column.keywords_txt_folder_doesnt_exist,
        7: Column.keywords_txt_misspelled_filename,
        8: Column.keywords_txt_incorrect_filename_case,
        9: Column.invalid_field_separator,
        10: Column.bom_corrupted_keyword,
        11: Column.invalid_keyword,
        12: Column.invalid_keyword_tokentype,
        13: Column.leading_space_on_rsyntaxtextarea_tokentype,
        14: Column.invalid_rsyntaxtextarea_tokentype,
        15: Column.invalid_reference_link,
        16: Column.reference_link_incorrect_case
    },
    "check_library_manager_compliance": {
        1: Column.check_library_manager_compliance_folder_doesnt_exist,
        2: Column.exe_found,
        3: Column.dot_development_found,
        4: Column.symlink_found,
        5: Column.name_has_invalid_first_character,
        6: Column.name_has_invalid_character,
        7: Column.name_too_long,
    },
    "check_includes": {
        2: Column.incorrect_include_syntax,
        3: Column.arduino_h_case
    }
}


def initialize_table(inoliblist_csv):
    """Fill in the first row of the table with the heading text."""
    # clear the table (necessary to avoid conflict between unit tests)
    global table
    table = [[""] * Column.count]

    # add the heading text from inoliblist
    for column_index, cell_contents in enumerate(next(inoliblist_csv)):
        table[0][column_index] = cell_contents
    table[0][Column.arduino_library_topic_abuse] = "arduino_library_topic_abuse"
    table[0][Column.i_have_open_issue] = "Open Issue"
    table[0][Column.blacklist] = "blacklist"
    table[0][Column.i_have_open_pull_request] = "Open PR"
    table[0][Column.i_am_contributor] = "Contributor"
    table[0][Column.cant_find] = "cant_find"
    table[0][Column.status_failure] = "status_failure"
    table[0][Column.not_in_root] = "not_in_root"
    table[0][Column.license_unrecognized] = "license_unrecognized"
    table[0][Column.typo] = "typo"
    table[0][Column.incorrect_extras_folder_name] = "incorrect_extras_folder_name"
    table[0][Column.incorrect_examples_folder_name] = "incorrect_examples_folder_name"
    table[0][Column.stray_library_properties] = "stray_library_properties"
    table[0][Column.stray_keywords_txt] = "stray_keywords_txt"
    table[0][Column.stray_sketch] = "stray_sketch"
    table[0][Column.spurious_dot_folder] = "spurious_dot_folder"
    table[0][Column.library_folder_doesnt_exist] = "library_folder_doesnt_exist"
    table[0][Column.incorrect_src_folder_case] = "incorrect_src_folder_case"
    table[0][Column.library_not_found] = "library_not_found"
    table[0][Column.folder_name_has_invalid_first_character] = "folder_name_has_invalid_first_character"
    table[0][Column.folder_name_has_invalid_character] = "folder_name_has_invalid_character"
    table[0][Column.folder_name_too_long] = "folder_name_too_long"
    table[0][Column.src_and_utility_folders] = "src_and_utility_folders"
    table[0][Column.sketch_folder_doesnt_exist] = "sketch_folder_doesnt_exist"
    table[0][Column.incorrect_sketch_extension_case] = "incorrect_sketch_extension_case"
    table[0][Column.multiple_sketches] = "multiple_sketches"
    table[0][Column.sketch_name_mismatch] = "sketch_name_mismatch"
    table[0][
        Column.sketch_folder_name_has_invalid_first_character] = "sketch_folder_name_has_invalid_first_character"
    table[0][Column.sketch_folder_name_has_invalid_character] = "sketch_folder_name_has_invalid_character"
    table[0][Column.sketch_folder_name_too_long] = "sketch_folder_name_too_long"
    table[0][Column.redundant_paragraph] = "redundant_paragraph"
    table[0][Column.blank_name] = "blank_name"
    table[0][Column.invalid_architecture] = "invalid_architecture"
    table[0][Column.architectures_misspelled] = "architectures_misspelled"
    table[0][Column.architectures_empty] = "architectures_empty"
    table[0][Column.library_properties_folder_doesnt_exist] = "library_properties_folder_doesnt_exist"
    table[0][Column.library_properties_misspelled_filename] = "library_properties_misspelled_filename"
    table[0][Column.library_properties_incorrect_filename_case] = "library_properties_incorrect_filename_case"
    table[0][Column.missing_name] = "missing_name"
    table[0][Column.missing_version] = "missing_version"
    table[0][Column.missing_author] = "missing_author"
    table[0][Column.missing_maintainer] = "missing_maintainer"
    table[0][Column.missing_sentence] = "missing_sentence"
    table[0][Column.missing_paragraph] = "missing_paragraph"
    table[0][Column.missing_category] = "missing_category"
    table[0][Column.missing_url] = "missing_url"
    table[0][Column.library_properties_invalid_line] = "library_properties_invalid_line"
    table[0][Column.invalid_version] = "invalid_version"
    table[0][Column.invalid_category] = "invalid_category"
    table[0][Column.url_blank] = "url_blank"
    table[0][Column.url_missing_scheme] = "url_missing_scheme"
    table[0][Column.dead_url] = "dead_url"
    table[0][Column.includes_misspelled] = "includes_misspelled"
    table[0][Column.dot_a_linkage_misspelled] = "dot_a_linkage_misspelled"
    table[0][Column.precompiled_misspelled] = "precompiled_misspelled"
    table[0][Column.ldflags_misspelled] = "ldflags_misspelled"
    table[0][Column.empty_includes] = "empty_includes"
    table[0][Column.inconsequential_multiple_tabs] = "inconsequential_multiple_tabs"
    table[0][Column.keywords_txt_invalid_line] = "keywords_txt_invalid_line"
    table[0][
        Column.inconsequential_leading_space_on_keyword_tokentype
    ] = "inconsequential_leading_space_on_keyword_tokentype"
    table[0][Column.multiple_tabs] = "multiple_tabs"
    table[0][Column.leading_space_on_keyword_tokentype] = "leading_space_on_keyword_tokentype"
    table[0][Column.keywords_txt_folder_doesnt_exist] = "keywords_txt_folder_doesnt_exist"
    table[0][Column.keywords_txt_misspelled_filename] = "keywords_txt_misspelled_filename"
    table[0][Column.keywords_txt_incorrect_filename_case] = "keywords_txt_incorrect_filename_case"
    table[0][Column.invalid_field_separator] = "invalid_field_separator"
    table[0][Column.bom_corrupted_keyword] = "bom_corrupted_keyword"
    table[0][Column.invalid_keyword] = "invalid_keyword"
    table[0][Column.invalid_keyword_tokentype] = "invalid_keyword_tokentype"
    table[0][Column.leading_space_on_rsyntaxtextarea_tokentype] = "leading_space_on_rsyntaxtextarea_tokentype"
    table[0][Column.invalid_rsyntaxtextarea_tokentype] = "invalid_rsyntaxtextarea_tokentype"
    table[0][Column.invalid_reference_link] = "invalid_reference_link"
    table[0][Column.reference_link_incorrect_case] = "reference_link_incorrect_case"
    table[0][Column.lm_but_not_in_root] = "lm_but_not_in_root"
    table[0][
        Column.check_library_manager_compliance_folder_doesnt_exist
    ] = "check_library_manager_compliance_folder_doesnt_exist"
    table[0][Column.exe_found] = "exe_found"
    table[0][Column.dot_development_found] = "dot_development_found"
    table[0][Column.symlink_found] = "symlink_found"
    table[0][Column.name_has_invalid_first_character] = "name_has_invalid_first_character"
    table[0][Column.name_has_invalid_character] = "name_has_invalid_character"
    table[0][Column.name_too_long] = "name_too_long"
    table[0][Column.incorrect_include_syntax] = "incorrect_include_syntax"
    table[0][Column.arduino_h_case] = "arduino_h_case"


def main():
    inoliblist.set_github_token(github_token_input=argument.github_token)
    inoliblist.set_verbosity(enable_verbosity_input=argument.enable_verbosity)

    inoliblist.logger.info("Starting")

    set_github_login(github_login_input=argument.github_login)
    set_git_command(git_command_input=argument.git_command)
    set_bash_command(bash_command_input=argument.bash_command)
    set_arduino_ci_script_branch(arduino_ci_script_branch_input=argument.arduino_ci_script_branch)
    set_arduino_ci_script_arduino_ide_version(
        arduino_ci_script_arduino_ide_version_input=argument.arduino_ci_script_arduino_ide_version
    )
    set_arduino_ci_script_application_folder(
        arduino_ci_script_application_folder_input=argument.arduino_ci_script_application_folder
    )
    set_browser_command(browser_command_input=argument.browser_command)

    clean_folder(output_folder_name)
    clean_folder(inoliblist_input_folder_name)
    clean_folder(work_folder_name)

    process_verification_failed_list(
        verification_failed_list_path=input_folder_name + "/" + inoliblist.verification_failed_list_filename)

    # download inoliblist.csv
    urllib.request.urlretrieve(url=inoliblist_csv_download_url, filename=default_inoliblist_path)
    install_tools()
    process_inoliblist(inoliblist_path=default_inoliblist_path)
    create_inolibbuglist_output_file()

    create_open_in_tabs_scripts()


def set_github_login(github_login_input):
    global github_login
    github_login = github_login_input


def set_git_command(git_command_input):
    global git_command
    git_command = git_command_input


def set_bash_command(bash_command_input):
    global bash_command
    bash_command = bash_command_input


def set_arduino_ci_script_branch(arduino_ci_script_branch_input):
    global arduino_ci_script_branch
    arduino_ci_script_branch = arduino_ci_script_branch_input


def set_arduino_ci_script_arduino_ide_version(arduino_ci_script_arduino_ide_version_input):
    global arduino_ci_script_arduino_ide_version
    arduino_ci_script_arduino_ide_version = arduino_ci_script_arduino_ide_version_input


def set_arduino_ci_script_application_folder(arduino_ci_script_application_folder_input):
    global arduino_ci_script_application_folder
    arduino_ci_script_application_folder = arduino_ci_script_application_folder_input


def set_browser_command(browser_command_input):
    global browser_command
    browser_command = browser_command_input


def set_process_repos_with_open_pr(process_repos_with_open_pr_input):
    global process_repos_with_open_pr
    process_repos_with_open_pr = process_repos_with_open_pr_input


def set_check_for_typos(check_for_typos_input):
    global check_for_typos
    check_for_typos = check_for_typos_input


def process_verification_failed_list(verification_failed_list_path):
    """Output a list of whether I have an open PR in the repos that failed inoliblist library verification"""
    inoliblist.logger.info("Processing verification failed list")
    try:
        with open(file=verification_failed_list_path,
                  mode='r',
                  encoding=inoliblist.file_encoding,
                  newline=inoliblist.file_newline
                  ) as verification_failed_input_file:
            # write column headings
            write_to_verification_failed_output_file("Repository" + inoliblist.output_file_delimiter + "Open PR\n")
            for verification_failed_url in verification_failed_input_file:
                inoliblist.logger.info(verification_failed_url)
                if check_blacklist(repository_url=verification_failed_url):
                    inoliblist.logger.info("Skipping: Repository is blacklisted")
                    continue
                i_have_open_pull_request = check_for_open_pr(
                    determine_repository_full_name(repository_url=verification_failed_url)
                )
                if i_have_open_pull_request is None:
                    inoliblist.logger.warning("Skipping: Unable to access repository")
                    continue
                write_to_verification_failed_output_file(
                    write_string=verification_failed_url.rstrip() + inoliblist.output_file_delimiter + str(
                        i_have_open_pull_request) + '\n')
    except FileNotFoundError:
        inoliblist.logger.warning("Verification failed list " + verification_failed_list_path + " not found")


def write_to_verification_failed_output_file(write_string):
    with open(file=output_folder_name + "/" + inoliblist.verification_failed_list_filename,
              mode='a',
              encoding=inoliblist.file_encoding,
              newline=inoliblist.file_newline
              ) as verification_failed_output_file:
        verification_failed_output_file.write(write_string)


def check_blacklist(repository_url):
    repository_owner = determine_repository_owner(repository_url=repository_url)
    with open(file=data_folder_name + "/" + owner_blacklist_filename,
              mode='r',
              encoding=inoliblist.file_encoding,
              newline=inoliblist.file_newline
              ) as owner_blacklist_file:
        owner_blacklist_csv = csv.reader(owner_blacklist_file,
                                         delimiter=inoliblist.output_file_delimiter,
                                         quotechar=inoliblist.output_file_quotechar)
        for owner_blacklist_row in owner_blacklist_csv:
            if owner_blacklist_row[0].strip().lower() == repository_owner.lower():
                # the owner of the repository is blacklisted
                inoliblist.logger.info("Owner " + repository_owner + " is blacklisted.")
                return True

    repository_full_name = determine_repository_full_name(repository_url=repository_url)
    with open(file=data_folder_name + "/" + repository_blacklist_filename,
              mode='r',
              encoding=inoliblist.file_encoding,
              newline=inoliblist.file_newline
              ) as repository_blacklist_file:
        repository_blacklist_csv = csv.reader(repository_blacklist_file,
                                              delimiter=inoliblist.output_file_delimiter,
                                              quotechar=inoliblist.output_file_quotechar)
        for repository_blacklist_row in repository_blacklist_csv:
            if repository_blacklist_row[0].strip().lower() == repository_full_name.lower():
                # the repository is blacklisted
                inoliblist.logger.info("Repository " + repository_full_name + " is blacklisted.")
                return True
    # the repository is not blacklisted
    return False


def determine_repository_owner(repository_url):
    return repository_url.split('/')[3].strip()


def check_for_open_pr(repository_full_name):
    i_have_open_pull_request = False
    page_number = 1
    additional_pages = True
    while additional_pages:
        try:
            get_github_api_response_return = inoliblist.get_github_api_response(
                request="repos/" +
                        repository_full_name +
                        "/pulls",
                request_parameters="state=open",
                page_number=page_number)
            json_data = list(get_github_api_response_return["json_data"])

            for pull_request in json_data:
                if pull_request["user"]["login"] == github_login:
                    i_have_open_pull_request = True
                    break
            if i_have_open_pull_request:
                break
            additional_pages = get_github_api_response_return["additional_pages"]
            page_number += 1
        except urllib.error.HTTPError:
            # there was an unrecoverable HTTP error but this could have been caused by the repo being
            # deleted since inoliblist was created so just skip the repo
            inoliblist.logger.warning("HTTP error while checking if I have an open pull request")
            return None
    return i_have_open_pull_request


def determine_repository_full_name(repository_url):
    return repository_url.split('/')[3] + "/" + repository_url.split('/')[4].strip()


def clean_folder(folder_path):
    if os.path.exists(folder_path):
        # delete the folder
        shutil.rmtree(folder_path, onerror=onerror)
        time.sleep(create_folder_delay)
    # create the folder
    os.makedirs(folder_path)


def get_table():
    """Return the table global variable. Used by the unit tests to check the value."""
    return table


def process_inoliblist(inoliblist_path):
    global table

    # install the Arduino IDE for check_keywords_txt's reference link check
    # if the IDE version is already installed to arduino_ci_script_application_folder then it will not be reinstalled
    arduino_ci_script_wrapper_handler(function_name="install_ide",
                                      function_parameters=arduino_ci_script_arduino_ide_version)

    with open(file=inoliblist_path,
              mode='r',
              encoding=inoliblist.file_encoding,
              newline=inoliblist.file_newline
              ) as inoliblist_file:
        inoliblist_csv = csv.reader(inoliblist_file,
                                    delimiter=inoliblist.output_file_delimiter,
                                    quotechar=inoliblist.output_file_quotechar)

        initialize_table(inoliblist_csv)

        # process inoliblist
        for inoliblist_row_list in inoliblist_csv:
            # initialize the row list
            inolibbuglist_row_list = [""] * Column.count

            # fill the row for the inoliblist columns
            for column_index, cell_contents in enumerate(inoliblist_row_list):
                inolibbuglist_row_list[column_index] = cell_contents

            inoliblist.logger.info(inolibbuglist_row_list[inoliblist.Column.repository_url])

            # is it archived?
            if inolibbuglist_row_list[inoliblist.Column.archived] == "True":
                inoliblist.logger.info("Skipping: archived")
                # no point in doing anything further for this row, save the row and go on to the next one
                # append this row to the table
                table.append(inolibbuglist_row_list)
                continue

            # is the repo blacklisted?
            inolibbuglist_row_list[Column.blacklist] = str(
                check_blacklist(repository_url=inolibbuglist_row_list[inoliblist.Column.repository_url]))
            if inolibbuglist_row_list[Column.blacklist] == "True":
                inoliblist.logger.info("Skipping: blacklisted")
                # no point in doing anything further for this row, save the row and go on to the next one
                # append this row to the table
                table.append(inolibbuglist_row_list)
                continue

            # detect inappropriate use of the "arduino-library" topic
            if (
                    inolibbuglist_row_list[inoliblist.Column.library_path] == '' and
                    inolibbuglist_row_list[inoliblist.Column.github_topics].find("arduino-library") != -1
            ):
                inoliblist.logger.info("arduino-library topic abuse detected")
                inolibbuglist_row_list[Column.arduino_library_topic_abuse] = "True"

                # check if I have open issues in this repo
                # I'm only doing this for the "arduino-library" topic abuse repos because
                # that's the only problem I need to open an issue for so I can avoid the extra API requests
                i_have_open_issue = False
                page_number = 1
                additional_pages = True
                while additional_pages:
                    try:
                        get_github_api_response_return = inoliblist.get_github_api_response(
                            request="repos/" +
                                    inolibbuglist_row_list[inoliblist.Column.repository_owner] + "/" +
                                    inolibbuglist_row_list[inoliblist.Column.repository_name] +
                                    "/issues",
                            request_parameters="state=open",
                            page_number=page_number)
                        json_data = list(get_github_api_response_return["json_data"])

                        for issue in json_data:
                            if issue["user"]["login"] == github_login:
                                inoliblist.logger.info("I have an open issue")
                                i_have_open_issue = True
                                break
                        if i_have_open_issue:
                            break

                        additional_pages = get_github_api_response_return["additional_pages"]
                        page_number += 1
                    except urllib.error.HTTPError:
                        # there was an unrecoverable HTTP error but this could have been caused by the repo being
                        # deleted since inoliblist was created so carry on
                        inoliblist.logger.warning("HTTP error while checking if I have an open issue")
                        i_have_open_issue = ""
                        break
                inolibbuglist_row_list[Column.i_have_open_issue] = str(i_have_open_issue)
            else:
                inolibbuglist_row_list[Column.arduino_library_topic_abuse] = "False"

            # do I have an open PR?
            i_have_open_pull_request = check_for_open_pr(
                inolibbuglist_row_list[inoliblist.Column.repository_owner] + "/" +
                inolibbuglist_row_list[inoliblist.Column.repository_name]
            )
            if i_have_open_pull_request is not None:
                inolibbuglist_row_list[Column.i_have_open_pull_request] = str(i_have_open_pull_request)
                if (
                        inolibbuglist_row_list[Column.i_have_open_pull_request] == "True" and not (
                        process_repos_with_open_pr)
                ):
                    inoliblist.logger.info("Skipping: Open PR")
                    # no point in doing anything further for this row, save the row and go on to the next one
                    # append this row to the table
                    table.append(inolibbuglist_row_list)
                    continue

            # am I a contributor?
            i_am_contributor = False
            page_number = 1
            additional_pages = True
            while additional_pages:
                try:
                    get_github_api_response_return = inoliblist.get_github_api_response(
                        request="repos/" +
                                inolibbuglist_row_list[inoliblist.Column.repository_owner] + "/" +
                                inolibbuglist_row_list[inoliblist.Column.repository_name] +
                                "/contributors",
                        page_number=page_number)
                    json_data = list(get_github_api_response_return["json_data"])

                    for contributor in json_data:
                        if contributor["login"] == github_login:
                            inoliblist.logger.info("I'm a contributor")
                            i_am_contributor = True
                            break
                    if i_am_contributor:
                        break

                    additional_pages = get_github_api_response_return["additional_pages"]
                    page_number += 1
                except urllib.error.HTTPError:
                    # there was an unrecoverable HTTP error but this could have been caused by the repo being
                    # deleted since inoliblist was created so carry on
                    inoliblist.logger.warning("HTTP error while checking if I'm a contributor")
                    i_am_contributor = ""
                    break
            inolibbuglist_row_list[Column.i_am_contributor] = str(i_am_contributor)

            # library was not found by inoliblist in the root or one subfolder level down
            if inolibbuglist_row_list[inoliblist.Column.library_path] == '':
                inoliblist.logger.info("Library was not found by inoliblist")
                inolibbuglist_row_list[Column.cant_find] = "True"
            else:
                inolibbuglist_row_list[Column.cant_find] = "False"

            # library's status is failure
            if inolibbuglist_row_list[inoliblist.Column.tip_status] == "failure":
                inoliblist.logger.info("Last commit has failed status")
                inolibbuglist_row_list[Column.status_failure] = "True"
            else:
                inolibbuglist_row_list[Column.status_failure] = "False"

            # library not in repo root (it's better to point arduino-ci-script's check_library_structure()
            # to the library path so it can detect other issues not already identified by inoliblist
            if inolibbuglist_row_list[inoliblist.Column.library_path] != '/':
                inoliblist.logger.info("Library not in repo root")
                inolibbuglist_row_list[Column.not_in_root] = "True"
            else:
                inolibbuglist_row_list[Column.not_in_root] = "False"

            # unrecognized license
            if (
                    inolibbuglist_row_list[inoliblist.Column.repository_license] ==
                    inoliblist.unrecognized_license_identifier
            ):
                inoliblist.logger.info("Unrecognized license")
                inolibbuglist_row_list[Column.license_unrecognized] = "True"
            else:
                inolibbuglist_row_list[Column.license_unrecognized] = "False"

            # tests indicate that downloading the .zip and unzipping it is significantly faster than a
            # shallow clone
            # deleting the repo is also significantly faster
            # download the GitHub .zip file
            inoliblist.logger.info("Downloading the library.")
            try:
                urllib.request.urlretrieve(url=(inolibbuglist_row_list[inoliblist.Column.repository_url] +
                                                "/archive/" +
                                                inolibbuglist_row_list[
                                                    inoliblist.Column.repository_default_branch] +
                                                ".zip"
                                                ),
                                           filename=(work_folder_name + '/' +
                                                     inolibbuglist_row_list[
                                                         inoliblist.Column.repository_name] +
                                                     ".zip"
                                                     )
                                           )
            except urllib.error.HTTPError:
                # no point in doing anything further for this row, save the row and go on to the next one
                # append this row to the table
                inoliblist.logger.warning("Unable to download the library.")
                table.append(inolibbuglist_row_list)
                continue

            # unzip the file
            with zipfile.ZipFile(work_folder_name + '/' +
                                 inolibbuglist_row_list[inoliblist.Column.repository_name] + ".zip",
                                 "r"
                                 ) as zip_ref:
                zip_ref.extractall(work_folder_name)
                # for some idiotic reason, the folder extracted from the GitHub generated .zip file doesn't
                # always match {repo name}-{branch name}
                # for example, https://github.com/EnviroDIY/GPRSbee should be GPRSbee-v1.2_hacked but
                # actually it's GPRSbee-1.2_hacked
                # zip_ref.namelist()[0] includes a trailing slash
                repository_installation_path = work_folder_name + '/' + zip_ref.namelist()[0]

            if check_for_typos:
                # check for typos
                codespell_exit_status = subprocess_run(command="codespell",
                                                       arguments=shlex.quote(
                                                           repository_installation_path)
                                                       )
                if codespell_exit_status != 0:
                    inoliblist.logger.info("Typo found")
                    inolibbuglist_row_list[Column.typo] = "True"
                else:
                    inolibbuglist_row_list[Column.typo] = "False"

            # run the arduino-ci-script checks
            # check_library_structure(), check_library_properties(), and check_keywords_txt require a known
            # library path
            if inolibbuglist_row_list[inoliblist.Column.library_path] != "":
                if inolibbuglist_row_list[inoliblist.Column.library_path] != "/":
                    library_path = repository_installation_path + inolibbuglist_row_list[
                        inoliblist.Column.library_path] + '/'
                else:
                    library_path = repository_installation_path
                arduino_ci_script_handler(function_name="check_library_structure",
                                          function_parameters=shlex.quote(library_path),
                                          row_list=inolibbuglist_row_list
                                          )
                arduino_ci_script_handler(function_name="check_library_properties",
                                          function_parameters=shlex.quote(library_path),
                                          row_list=inolibbuglist_row_list
                                          )
                arduino_ci_script_handler(function_name="check_keywords_txt",
                                          function_parameters=shlex.quote(library_path),
                                          row_list=inolibbuglist_row_list
                                          )
            # These checks are only relevant for libraries in the Library Manager index
            if inolibbuglist_row_list[inoliblist.Column.in_library_manager_index] == "True":
                if inolibbuglist_row_list[inoliblist.Column.library_path] != "/":
                    inolibbuglist_row_list[Column.lm_but_not_in_root] = "True"
                else:
                    inolibbuglist_row_list[Column.lm_but_not_in_root] = "False"
                arduino_ci_script_handler(function_name="check_library_manager_compliance",
                                          function_parameters=shlex.quote(repository_installation_path),
                                          row_list=inolibbuglist_row_list
                                          )
            # not yet implemented
            # arduino_ci_script_handler(function_name="check_includes",
            #                          function_parameters=shlex.quote(repository_installation_path),
            #                          row_list=inolibbuglist_row_list
            #                          )

            # clean out the work folder
            clean_folder(work_folder_name)

            # append this row to the table
            table.append(inolibbuglist_row_list)


def install_tools():
    clean_folder(tools_folder_name)
    if check_for_typos:
        # install codespell
        subprocess_run(command="pip", arguments="install codespell")

    # clone arduino-ci-script to the tools folder
    subprocess_run(command=quote_path(git_command),
                   arguments="clone --branch " +
                             arduino_ci_script_branch +
                             " --depth 1 " +
                             arduino_ci_script_clone_url + ' ' +
                             quote_path(arduino_ci_script_folder)
                   )


def subprocess_run(command, arguments):
    if platform.system() == "Windows":
        use_shell = False
    else:
        # it's necessary to do shell=True on Linux to run Git
        use_shell = True
    commandline = command + ' ' + arguments
    result = subprocess.run(commandline, shell=use_shell)
    return result.returncode


def quote_path(path):
    if platform.system() == "Windows":
        # Can't use shlex.quote() on Windows because it uses single quotes, which are not supported
        if not path.startswith('"'):
            path = '"' + path + '"'
    else:
        path = shlex.quote(path)
    return path


def arduino_ci_script_handler(function_name, function_parameters, row_list):
    check_library_structure_return = arduino_ci_script_wrapper_handler(function_name=function_name,
                                                                       function_parameters=function_parameters)
    if check_library_structure_return != bash_script_success_exit_status:
        row_list[arduino_ci_script_exit_statuses[function_name][check_library_structure_return]] = "True"


def arduino_ci_script_wrapper_handler(function_name, function_parameters):
    command = (shlex.quote(arduino_ci_script_wrapper_path) + ' ' +
               shlex.quote(arduino_ci_script_path) + ' ' +
               shlex.quote(arduino_ci_script_application_folder) + ' ' +
               arduino_ci_script_arduino_ide_version + "; " +
               function_name + ' ' +
               function_parameters
               )
    if platform.system() == "Windows":
        commandline = quote_path(bash_function_wrapper_script_path) + ' ' + command
    else:
        # everything after -c must be wrapped in quotes
        commandline = "-c " + '"' + "source " + command + '"'
    return run_bash_command(commandline)


def run_bash_command(commandline):
    commandline = quote_path(bash_command) + ' ' + commandline
    inoliblist.logger.info("Running command: " + commandline)
    # this makes it work on both Windows and Linux
    commandline = shlex.split(commandline)

    script_pipe = subprocess.Popen(commandline,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    stdout, stderr = script_pipe.communicate()

    # ISO-8859-1 should make the code compatible with any encoding, though it may not actually be rendered correctly
    stdout = stdout.decode("ISO-8859-1")
    if stdout != "":
        inoliblist.logger.info("stdout: " + stdout)
    stderr = stderr.decode("ISO-8859-1")
    if stderr != "":
        inoliblist.logger.info("stderr: " + stderr)
    inoliblist.logger.info("exit status: " + str(script_pipe.returncode))

    return script_pipe.returncode


def create_inolibbuglist_output_file():
    with open(file=output_folder_name + "/" + inolibbuglist_filename,
              mode='w',
              encoding=inoliblist.file_encoding,
              newline=inoliblist.file_newline
              ) as inolibbuglist_file:
        inolibbuglist_csv = csv.writer(inolibbuglist_file,
                                       delimiter=inoliblist.output_file_delimiter,
                                       quotechar=inoliblist.output_file_quotechar)
        # write the table to the output file
        inolibbuglist_csv.writerows(table)


def create_open_in_tabs_scripts():
    # create the scripts for the verification failed list
    if os.path.isfile(output_folder_name + "/" + inoliblist.verification_failed_list_filename):
        # I don't need to worry about the blacklist here because process_verification_failed_list already filters out
        # any on the blacklist
        if process_repos_with_open_pr:
            exclusion_columns = []
        else:
            exclusion_columns = [1]

        create_open_in_tabs_script(input_filename=inoliblist.verification_failed_list_filename,
                                   url_column=0,
                                   inclusion_columns=[True],
                                   exclusion_columns=exclusion_columns,
                                   output_filename=verification_failed_browser_script_filename
                                   )
    else:
        inoliblist.logger.warning("Output file from verification failed list processing not found.")

    # create the scripts for the "arduino-library" topic abuse
    create_open_in_tabs_script(input_filename=inolibbuglist_filename,
                               url_column=inoliblist.Column.repository_url,
                               inclusion_columns=[Column.arduino_library_topic_abuse],
                               exclusion_columns=[Column.i_have_open_issue]
                               )

    # create scripts for the rest of the columns
    if process_repos_with_open_pr:
        exclusion_columns = [Column.blacklist]
    else:
        exclusion_columns = [Column.i_have_open_pull_request, Column.blacklist]

    for column_number in range(Column.start_of_normal_bugs, Column.count):
        create_open_in_tabs_script(input_filename=inolibbuglist_filename,
                                   url_column=inoliblist.Column.repository_url,
                                   inclusion_columns=[column_number],
                                   exclusion_columns=exclusion_columns
                                   )


def create_open_in_tabs_script(input_filename, url_column, inclusion_columns, exclusion_columns, output_filename=None):
    with open(file=output_folder_name + "/" + input_filename,
              mode='r',
              encoding=inoliblist.file_encoding,
              newline=inoliblist.file_newline
              ) as input_file:
        input_csv = csv.reader(input_file,
                               delimiter=inoliblist.output_file_delimiter,
                               quotechar=inoliblist.output_file_quotechar)
        # read the column heading row
        input_row = next(input_csv)
        if output_filename is None:
            # use the first inclusion column heading text as the filename
            output_filename = input_row[inclusion_columns[0]]

        # setting it above the threshold value to always trigger the filename increment on the first result
        # (to avoid confusing debug output)
        tabs_count = maximum_browser_tabs + 1
        filename_count = 0
        for input_row in input_csv:
            excluded_from_list = False
            for inclusion_column in inclusion_columns:
                # any inclusion column mismatch excludes the row
                if inclusion_column is not True and input_row[inclusion_column] != "True":
                    excluded_from_list = True
                    break
            for exclusion_column in exclusion_columns:
                # any exclusion column match excludes the row
                if input_row[exclusion_column] == "True":
                    excluded_from_list = True
                    break
            if excluded_from_list:
                # go on to the next row
                continue
            tabs_count += 1
            if tabs_count > maximum_browser_tabs:
                filename_count += 1
                tabs_count = 0
                inoliblist.logger.info("Creating open-in-tabs script: " +
                                       output_filename +
                                       str(filename_count) +
                                       browser_script_extension
                                       )
            with open(file=(output_folder_name +
                            "/" +
                            output_filename +
                            str(filename_count) +
                            browser_script_extension),
                      mode='a',
                      encoding=inoliblist.file_encoding,
                      newline=inoliblist.file_newline
                      ) as browser_script_file:
                browser_script_file.write(browser_command + " " +
                                          input_row[url_column] + '\n'
                                          )


def onerror(func, path, _exc_info):
    """
    Error handler for ``shutil.rmtree``.
    https://stackoverflow.com/a/2656405

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)


# only execute the following code if the script is run directly, not imported
if __name__ == '__main__':
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
    argument = argument_parser.parse_args()

    # run program
    main()
