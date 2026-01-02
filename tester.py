import os
import subprocess
import filecmp
import shutil

class CompilerTestRunner:
    def __init__(self, compiler_path='compiler.py'):
        self.compiler_path = compiler_path
        # Look for folders starting with 'T' (e.g., T01, T02...)
        self.test_folders = sorted([f for f in os.listdir('.') if f.startswith('T') and os.path.isdir(f)])
        self.total_tests = len(self.test_folders)
        self.passed_tests = 0

    def run_tests(self):
        print(f"🧪 Starting Compiler Test Suite")
        print(f"Total Test Folders: {self.total_tests}")
        print("-" * 40)

        for test_folder in self.test_folders:
            print(f"\n🔍 Running Test: {test_folder}")
            result = self._run_single_test(test_folder)
            
            if result:
                self.passed_tests += 1
                print(f"✅ {test_folder} PASSED")
            else:
                print(f"❌ {test_folder} FAILED")

        self._print_summary()

    def _run_single_test(self, test_folder):
        # Paths for the expected files inside the test folder
        folder_input = os.path.join(test_folder, 'input.txt')
        expected_parse_tree = os.path.join(test_folder, 'parse_tree.txt')
        expected_syntax_errors = os.path.join(test_folder, 'syntax_errors.txt')

        # Paths for the temporary/generated files in the root
        root_input = 'input.txt'
        root_parse_tree = 'parse_tree.txt'
        root_syntax_errors = 'syntax_errors.txt'

        # 1. SETUP: Copy the test input to the root as 'input.txt'
        if os.path.exists(folder_input):
            shutil.copy(folder_input, root_input)
        else:
            print(f"❗ input.txt missing in {test_folder}")
            return False

        # 2. EXECUTE: Run compiler (it will read root_input and generate output in root)
        try:
            # Note: We do NOT pass the path args, compiler reads 'input.txt' by default
            subprocess.run(['python', self.compiler_path], 
                           capture_output=True, text=True, timeout=10)
        except subprocess.TimeoutExpired:
            print(f"❗ Timeout in {test_folder}")
            self._cleanup_files([root_input, root_parse_tree, root_syntax_errors])
            return False

        # 3. VERIFY: Compare generated root files with expected folder files
        parse_tree_match = self._compare_files(root_parse_tree, expected_parse_tree)
        syntax_errors_match = self._compare_files(root_syntax_errors, expected_syntax_errors)

        if not parse_tree_match:
            print(f"   -> Parse Tree Mismatch")
        if not syntax_errors_match:
            print(f"   -> Syntax Errors Mismatch")

        # 4. TEARDOWN: Clean up the files created in root
        self._cleanup_files([root_input, root_parse_tree, root_syntax_errors])

        return parse_tree_match and syntax_errors_match

    def _compare_files(self, generated_file, expected_file):
        """
        Compare two files ignoring leading/trailing whitespace/newlines.
        """
        # If expected file is empty/missing and generated file is missing, it's a match
        if not os.path.exists(expected_file) and not os.path.exists(generated_file):
            return True
        
        # If both exist, read and compare stripped content
        if os.path.exists(generated_file) and os.path.exists(expected_file):
            try:
                with open(generated_file, 'r', encoding='utf-8') as f1, \
                     open(expected_file, 'r', encoding='utf-8') as f2:
                    # .strip() removes whitespace/newlines from start and end
                    return f1.read().strip() == f2.read().strip()
            except Exception as e:
                print(f"Error comparing files: {e}")
                return False
        
        # If one exists and the other doesn't
        return False

    def _cleanup_files(self, files):
        for file in files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception as e:
                    print(f"Warning: Could not remove {file}: {e}")

    def _print_summary(self):
        print("\n" + "=" * 40)
        print(f"🏁 Test Summary")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed Tests: {self.passed_tests}")
        print(f"Failed Tests: {self.total_tests - self.passed_tests}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.2f}%")
        print("=" * 40)

if __name__ == '__main__':
    test_runner = CompilerTestRunner()
    test_runner.run_tests()