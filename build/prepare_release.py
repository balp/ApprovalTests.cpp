import os
import shutil
import time
import version

from utilities import read_file, check_step, replace_text_in_file, run, write_file, pushdir, popdir, \
    check_step_with_revert


class PrepareRelease:
    def __init__(self, details):
        self.details = details

    def update_features_page(self):
        features_file = '../doc/mdsource/Features.source.md'
        content = read_file(features_file)
        missing_features = F"""
## v.x.y.z

## {self.details.old_version}
"""
        if missing_features in content:
            check_step("the Features page is empty: are you sure you want this?")
        else:
            update_version = F"""
## v.x.y.z

## {self.details.new_version}
"""

            replace_text_in_file(features_file, '\n## v.x.y.z\n', update_version)

    def check_pre_conditions_for_publish(self):
        if self.details.push_to_production:
            run(["git", "branch"])
            check_step("we are on the master branch")

            run(["git", "status"])
            check_step("everything is committed")
            check_step("everything is pushed")

            run(["open", "https://github.com/approvals/ApprovalTests.cpp/commits/master"])
            check_step("the builds are passing")

            run(["open", "https://github.com/approvals/ApprovalTests.cpp/blob/master/build/relnotes_x.y.z.md"])
            run(["open", F"https://github.com/approvals/ApprovalTests.cpp/compare/{self.details.old_version}...master"])
            check_step("the release notes are ready")

        run(["open", "https://github.com/approvals/ApprovalTests.cpp/issues"])
        check_step("any issues resolved in this release are closed")

        run(["open", "https://github.com/approvals/ApprovalTests.cpp/milestones"])
        check_step("the milestone (if any) is up to date, including actual version number of release")

    def create_single_header_file(self):
        os.chdir("../ApprovalTests")
        print(os.getcwd())
        run(["java", "-version"])
        run(["java", "-jar", "../build/SingleHpp.v.0.0.2.jar", self.details.release_new_single_header])
        text = read_file(self.details.release_new_single_header)
        text = \
F"""// Approval Tests version {self.details.new_version}
// More information at: https://github.com/approvals/ApprovalTests.cpp
{text}"""
        write_file(self.details.release_new_single_header, text)

    def update_starter_project(self):
        STARTER_PATH_OLD_SINGLE_HEADER = F"{self.details.starter_project_dir}/lib/{self.details.old_single_header}"
        STARTER_PATH_NEW_SINGLE_HEADER = F"{self.details.starter_project_dir}/lib/{self.details.new_single_header}"

        # Make sure starter project folder is clean
        pushdir(self.details.starter_project_dir)
        run(["git", "clean", "-fx"])
        run(["git", "reset", "--hard"])
        popdir()

        shutil.copyfile(self.details.release_new_single_header, STARTER_PATH_NEW_SINGLE_HEADER)

        # Delete the last release:
        if os.path.exists(STARTER_PATH_OLD_SINGLE_HEADER):
            os.remove(STARTER_PATH_OLD_SINGLE_HEADER)

        # Update the version in the "redirect" header:
        replace_text_in_file(F"{self.details.starter_project_dir}/lib/ApprovalTests.hpp", self.details.old_version, self.details.new_version)

        # Update the version number in the Visual Studio project:
        replace_text_in_file(F"{self.details.starter_project_dir}/visual-studio-2017/StarterProject.vcxproj", self.details.old_single_header,
                             self.details.new_single_header)

    def check_starter_project_builds(self):
        pushdir(F"{self.details.starter_project_dir}/cmake-build-debug")
        run(["cmake", "--build", "."])
        popdir()

    def update_readme_and_docs(self):
        pushdir("..")
        replace_text_in_file("mdsource/README.source.md", self.details.old_version, self.details.new_version)
        popdir()

    def regenerate_markdown(self):
        pushdir("..")
        run(["./run_markdown_templates.sh"])
        popdir()

    def prepare_release_notes(self):
        replace_text_in_file(self.details.xxx_release_notes_path, 'v.x.y.z', self.details.new_version)
        shutil.move(self.details.xxx_release_notes_path, self.details.new_release_notes_path)

        # Make sure the above move has finished, before we create the new xxx file:
        time.sleep(1)

        shutil.copyfile(self.details.template_release_notes_path, self.details.xxx_release_notes_path)

    def add_to_git(self):
        def add():
            run(["git", "add", "."])

        self.do_things_in_starter_project_and_main(add)

    def do_things_in_starter_project_and_main(self, function):
        pushdir(self.details.starter_project_dir)
        function()
        popdir()
        pushdir(self.details.main_project_dir)
        function()
        popdir()

    def check_changes(self):
        def revert():
            run(["git", "clean", "-fx"])
            run(["git", "reset", "--hard"])

        def revert_all():
            self.do_things_in_starter_project_and_main(revert)

        def do_nothing():
            pass

        check_step_with_revert("you are happy with the changes?", do_nothing)


    def prepare_everything(self):
        self.check_pre_conditions_for_publish()
        self.create_single_header_file()
        self.update_starter_project()
        self.check_starter_project_builds()
        self.update_features_page()
        self.update_readme_and_docs()
        self.prepare_release_notes()
        self.regenerate_markdown()
        version.write_version(self.details.new_version_object)
        self.add_to_git()

        self.check_changes()
