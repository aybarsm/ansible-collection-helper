from ansible.plugins.callback.default import CallbackModule

class CallbackModule(CallbackModule):
    """
    Custom Callback Plugin to suppress output for skipped tasks 
    when '__no_output_on_skip' is set to True.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'aybarsm.helper.diy'
    CALLBACK_NEEDS_ENABLED = False

    # def __getattr__(self, item):
    #     super(CallbackModule, self).item()

    # def v2_on_any(self, *args, **kwargs):
    #     super(CallbackModule, self).v2_on_any(*args, **kwargs)

    # def v2_runner_on_failed(self, result, ignore_errors=False):
    #     super(CallbackModule, self).v2_runner_on_failed(result, ignore_errors)
    
    # def v2_runner_on_ok(self, result):
    #     super(CallbackModule, self).v2_runner_on_ok(result)
    
    # def v2_runner_on_skipped(self, result):
    #     super(CallbackModule, self).v2_runner_on_skipped(result)

    # def v2_runner_on_unreachable(self, result):
    #     super(CallbackModule, self).v2_runner_on_unreachable(result)

    def v2_playbook_on_task_start(self, task, is_conditional):
        super(CallbackModule, self).v2_playbook_on_task_start(task, is_conditional)