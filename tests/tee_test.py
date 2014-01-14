import sys
sys.path.append('../')
import tee

import unittest

import io
import os
import subprocess

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

class AvailableTestCase(unittest.TestCase):

    def test_simple(self):
        input_data = "Hello"
        expected_available = len(input_data)
        f = StringIO()
        
        f.write(input_data)
        f.seek(0)
        self.assertEqual(tee.bytes_available(f), expected_available)

    def test_file(self):
        input_data = "Hello"
        expected_available = len(input_data)
        filename = "test_file.txt"
        wf = open(filename,"w")
        rf = open(filename,"r")

        wf.write(input_data)
        wf.flush()
        self.assertEqual(tee.bytes_available(rf), expected_available)

        rf.close()        
        wf.close()
        os.remove(filename)

    def test_file_multiple(self):
        input_data1 = "Hello"
        input_data2 = "World"
        expected_available = len(input_data2)
        filename = "test_file.txt"

        wf = open(filename,"w")
        rf = open(filename,"r")

        wf.write(input_data1)
        wf.flush()
        garbage = rf.read(tee.bytes_available(rf))

        wf.write(input_data2)
        wf.flush()
        self.assertEqual(tee.bytes_available(rf), expected_available)

        rf.close()   
        wf.close()
        os.remove(filename)

    def test_backwards(self):
        input_data1 = "Hello World"
        input_data2 = "Short"
        expected_available = 0 # It is shorter than what was already written

        filename = "test_file.txt"

        wf = open(filename,"w")
        rf = open(filename,"r")

        wf.write(input_data1)
        wf.flush()
        garbage = rf.read(tee.bytes_available(rf))

        wf.seek(0)
        wf.write(input_data2)
        wf.flush()
        self.assertEqual(tee.bytes_available(rf), expected_available)

        rf.close()   
        wf.close()
        os.remove(filename)

class TeeTestCase(unittest.TestCase):

    def test_simple(self):
        input_data = "Hello World"

        pipe_stream = StringIO()
        first_output = StringIO()
        second_output = StringIO()

        pipe_stream.write("Hello World")
        pipe_stream.seek(0)

        tee.tee_pipe(pipe_stream, first_output, second_output)

        self.assertEqual(first_output.getvalue(), input_data)
        self.assertEqual(second_output.getvalue(), input_data)

    def test_file(self):
        input_data = "Hello World"

        filename = "test_file.txt"
        pipe_stream = StringIO()
        first_output = StringIO()
        second_output = open(filename, 'w')

        pipe_stream.write("Hello World")
        pipe_stream.seek(0)

        tee.tee_pipe(pipe_stream, first_output, second_output)
        second_output.close()

        result_file = open(filename, 'r')
        self.assertEqual(result_file.read(), input_data)
        result_file.close()

        os.remove(filename)

class ProcessTestCase(unittest.TestCase):

    def test_stdout(self):
        input_data = "Hello World"

        stdout_file = "stdout_test.txt"
        f = open(stdout_file, 'w')
        f.write(input_data)
        f.close()

        command = "python other_process.py " + stdout_file
        proc = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)

        stdout_result_file = "tee_stdout.txt"
        with open(stdout_result_file, 'w') as stdout_result:
            tee.tee_process(proc, stdout_result)

        with open(stdout_result_file, 'r') as stdout_result:
            self.assertEqual(stdout_result.read(), input_data)

        # There isn't a good way to check the output of stdout/stderr with
        # redirecting them to somewhere else, which defeats the purpose of 
        # this test.

        os.remove(stdout_file)
        os.remove(stdout_result_file)

    def test_stderr(self):
        input_data = "Hello World"

        stdout_file = "stdout_test.txt"
        f = open(stdout_file, 'w')
        f.close()

        stderr_file = "stderr_test.txt"
        f = open(stderr_file, 'w')
        f.write(input_data)
        f.close()

        command = "python other_process.py " + stdout_file + " " + stderr_file
        proc = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)

        stderr_result_file = "tee_stderr.txt"
        with open(stderr_result_file, 'w') as stderr_result:
            tee.tee_process(proc, stderr_file=stderr_result)

        with open(stderr_result_file, 'r') as stderr_result:
            self.assertEqual(stderr_result.read(), input_data)

        os.remove(stdout_file)
        os.remove(stderr_file)
        os.remove(stderr_result_file)

    def test_both(self):
        input_data = "Hello World"

        stdout_file = "stdout_test.txt"
        f = open(stdout_file, 'w')
        f.write(input_data)
        f.close()

        stderr_file = "stderr_test.txt"
        f = open(stderr_file, 'w')
        f.write(input_data)
        f.close()

        command = "python other_process.py " + stdout_file + " " + stderr_file
        proc = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)

        stdout_result_file = "tee_stdout.txt"
        stderr_result_file = "tee_stderr.txt"
        with open(stdout_result_file, 'w') as stdout_result, \
            open(stderr_result_file, 'w') as stderr_result:

            tee.tee_process(proc, stdout_result, stderr_result)

        with open(stdout_result_file, 'r') as stdout_result:
            self.assertEqual(stdout_result.read(), input_data)  

        with open(stderr_result_file, 'r') as stderr_result:
            self.assertEqual(stderr_result.read(), input_data)

        os.remove(stdout_file)
        os.remove(stderr_file)
        os.remove(stdout_result_file)
        os.remove(stderr_result_file)

    def test_combined(self):
        input_data = "Hello World"

        stdout_file = "stdout_test.txt"
        f = open(stdout_file, 'w')
        f.write(input_data)
        f.close()

        stderr_file = "stderr_test.txt"
        f = open(stderr_file, 'w')
        f.write(input_data)
        f.close()

        command = "python other_process.py " + stdout_file + " " + stderr_file
        proc = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)

        combined_result_file = "tee_combined.txt"
        with open(combined_result_file, 'w') as combined_result:

            tee.tee_process(proc, combined_result, combined_result)

        with open(combined_result_file, 'r') as combined_result:
            self.assertEqual(combined_result.read(), input_data + input_data)

        os.remove(stdout_file)
        os.remove(stderr_file)
        os.remove(combined_result_file)

    def test_large(self):
        command = "python other_process.py a_tale_of_two_cities.txt adventures_of_huckleberry_finn.txt"
        proc = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)

        stdout_result_file = "tee_stdout.txt"
        stderr_result_file = "tee_stderr.txt"
        with open(stdout_result_file, 'w') as stdout_result, \
            open(stderr_result_file, 'w') as stderr_result:

            tee.tee_process(proc, stdout_result, stderr_result)

        os.remove(stdout_result_file)
        os.remove(stderr_result_file)
  
    def test_large_combined(self):
        command = "python other_process.py a_tale_of_two_cities.txt adventures_of_huckleberry_finn.txt"
        proc = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)

        combined_result_file = "tee_combined.txt"
        with open(combined_result_file, 'w') as combined_result:

            tee.tee_process(proc, combined_result, combined_result)

        os.remove(combined_result_file)

    def test_large_random(self):
        command = "python other_process.py a_tale_of_two_cities.txt adventures_of_huckleberry_finn.txt 2"
        proc = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)

        stdout_result_file = "tee_stdout.txt"
        stderr_result_file = "tee_stderr.txt"
        with open(stdout_result_file, 'w') as stdout_result, \
            open(stderr_result_file, 'w') as stderr_result:

            tee.tee_process(proc, stdout_result, stderr_result)

        os.remove(stdout_result_file)
        os.remove(stderr_result_file)

    def test_large_combined_random(self):
        command = "python other_process.py a_tale_of_two_cities.txt adventures_of_huckleberry_finn.txt 2"
        proc = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)

        combined_result_file = "tee_combined.txt"
        with open(combined_result_file, 'w') as combined_result:

            tee.tee_process(proc, combined_result, combined_result)

        os.remove(combined_result_file)

def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(AvailableTestCase))
    suite.addTest(loader.loadTestsFromTestCase(TeeTestCase))
    suite.addTest(loader.loadTestsFromTestCase(ProcessTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
