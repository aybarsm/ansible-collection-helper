from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):
    """
    Custom Callback Plugin to suppress output for skipped tasks 
    when '__no_output_on_skip' is set to True.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'no_output_on_skip'
    CALLBACK_NEEDS_ENABLED = False

    def v2_runner_item_on_skipped(self, result):
        """
        Override the default behavior for skipped items.
        Suppress output if the task has '__no_output_on_skip' set to True.
        """
        # Check if '__no_output_on_skip' is set in the task result
        if result._task.vars.get("__no_output_on_skip", False):
            return  # Suppress the skipped output

        # Call the parent method to display the skipped message
        super().v2_runner_item_on_skipped(result)

    def v2_runner_on_skipped(self, result):
        """
        Override the default behavior for skipped tasks.
        Suppress output if the task has '__no_output_on_skip' set to True.
        """
        # Check if '__no_output_on_skip' is set in the task result
        if result._task.vars.get("__no_output_on_skip", False):
            return  # Suppress the skipped output

        # Call the parent method to display the skipped message
        super().v2_runner_on_skipped(result)
