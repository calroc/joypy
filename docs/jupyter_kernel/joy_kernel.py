from ipykernel.kernelbase import Kernel
from joy.library import initialize
from joy.joy import run
from joy.utils.stack import stack_to_string


class JoyKernel(Kernel):
    implementation = 'Joypy'
    implementation_version = '1.0'
    language = 'Joy'
    language_version = '0.1'
    language_info = {
        'name': 'Joy',
        'mimetype': 'text/plain',
        'file_extension': '.joy',
    }
    banner = "Echo kernel - as useful as a parrot"

    def __init__(self, *a, **b):
      self.D = initialize()
      self.S = ()
      super(JoyKernel, self).__init__(*a, **b)

    def do_execute(
      self,
      code,
      silent,
      store_history=True,
      user_expressions=None,
      allow_stdin=False,
      ):
      self.S = run(code, self.S, self.D)[0]
      if not silent:
        stream_content = {
          'name': 'stdout',
          'text': stack_to_string(self.S),
          }
        self.send_response(self.iopub_socket, 'stream', stream_content)

      return {'status': 'ok',
              # The base class increments the execution count
              'execution_count': self.execution_count,
              'payload': [],
              'user_expressions': {},
             }


if __name__ == '__main__':
  from ipykernel.kernelapp import IPKernelApp
  IPKernelApp.launch_instance(kernel_class=JoyKernel)
